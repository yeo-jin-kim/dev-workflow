"""Controller-owned branch publication and exact-head push CI. Never merges targets."""
import json
import hashlib
from pathlib import Path
import re
import time

from development_loop import save, valid_review
from delivery_evidence import Halt, git, manifest, environment_identity


def repository_identity(url):
    value = re.sub(r'^git@github.com:', 'https://github.com/', url.strip())
    value = value.removesuffix('.git').rstrip('/')
    return value.removeprefix('https://github.com/') if value.startswith('https://github.com/') else value


class Publisher:
    def __init__(self, recorder, config, contract, state, persist):
        self.r, self.config, self.contract = recorder, config, contract
        self.state, self.persist = state, persist
        self.root = recorder.root

    def capture(self, argv, label):
        original, n = label, 0
        while (self.r.folder / (label + '.log')).exists():
            n += 1
            label = original + '-%03d' % n
        code = self.r.command(argv, label, cap=60)
        read_only = (argv[:2] in [['gh', 'repo'], ['gh', 'workflow'], ['gh', 'run']]
                     or argv[:2] == ['git', 'ls-remote'])
        key = json.dumps(argv[:3])
        retries = self.state.setdefault('infrastructure_retries', {})
        if code and read_only and retries.get(key, 0) < 1:
            retries[key] = retries.get(key, 0) + 1
            self.persist()
            label += '-retry'
            code = self.r.command(argv, label, cap=60)
        if code:
            raise Halt('publication_blocked', 'Command failed after bounded recovery: ' + label)
        return (self.r.folder / (label + '.log')).read_text().strip()

    def remote_head(self, branch):
        output = self.capture(['git', 'ls-remote', self.config['remote'], 'refs/heads/' + branch], 'remote-' + branch.replace('/', '_'))
        return output.split()[0] if output else None

    def preflight(self):
        cfg = self.config
        if cfg.get('mode', 'branch_report') != 'branch_report':
            raise Halt('decision_required', 'This implementation supports branch_report; optional PR mode is not enabled.')
        if cfg['head'] == cfg['base'] or git(self.root, 'branch', '--show-current') != cfg['head']:
            raise Halt('publication_blocked', 'Target must be the configured dedicated branch, distinct from base.')
        if repository_identity(git(self.root, 'remote', 'get-url', cfg['remote'])) != cfg['repository']:
            raise Halt('publication_blocked', 'Remote identity differs from configured repository.')
        if not cfg.get('required_gates'):
            raise Halt('decision_required', 'Explicit required push gates are required by this delivery profile.')
        for gate in cfg['required_gates']:
            if gate.get('event', 'push') != 'push':
                raise Halt('decision_required', 'Required gate is PR-only; choose an authorized push gate without bypassing repository policy.')
        actual = self.capture(['gh', 'repo', 'view', cfg['repository'], '--json', 'nameWithOwner,viewerPermission'], 'github-capability')
        if json.loads(actual)['nameWithOwner'].lower() != cfg['repository'].lower():
            raise Halt('publication_blocked', 'GitHub repository capability does not match.')
        if json.loads(actual).get('viewerPermission') not in {'ADMIN', 'MAINTAIN', 'WRITE'}:
            raise Halt('publication_blocked', 'Authenticated account lacks configured repository write permission.')
        workflows = json.loads(self.capture(['gh', 'workflow', 'list', '--repo', cfg['repository'], '--json', 'name,state,path'], 'workflow-capability'))
        active = {w['name'] for w in workflows if w.get('state') == 'active'}
        if any(g['workflow'] not in active for g in cfg['required_gates']):
            raise Halt('capability_blocked', 'A required remote workflow is unavailable/inactive before worker execution.')
        base = self.remote_head(cfg['base'])
        if not base:
            raise Halt('publication_blocked', 'Configured target base does not exist remotely.')
        if 'base_sha' not in self.state:
            # Preflight requires a recorded baseline actually containing target base.
            if git(self.root, 'merge-base', 'HEAD', base) != base:
                raise Halt('decision_required', 'Prepare candidate on current target base before execution.')
            self.state.update(base_sha=base, remote_head=self.remote_head(cfg['head']))
            self.persist()

    def scope(self):
        changed = git(self.root, 'diff', '--name-only', self.state['baseline_head']).splitlines()
        changed += git(self.root, 'ls-files', '--others', '--exclude-standard').splitlines()
        allowed = set(self.contract['allowed_paths'])
        staged = set(git(self.root, 'diff', '--cached', '--name-only').splitlines())
        if staged - set(changed):
            raise Halt('publication_blocked', 'Index contains changes not represented by reviewed working files.')
        extra = (set(changed) | staged) - allowed
        if extra:
            raise Halt('decision_required', 'Changes outside authorized paths: ' + ', '.join(sorted(extra)))
        for name in set(changed):
            path = self.root / name
            if path.is_symlink() or '.local' in Path(name).parts:
                raise Halt('publication_blocked', 'Publication excludes symlinks/private evidence: ' + name)
        return sorted(set(changed))

    def refresh_base(self):
        """Merge new target only in isolated candidate; force fresh checks/review."""
        base = self.remote_head(self.config['base'])
        if base == self.state['base_sha']:
            return False
        if not base:
            raise Halt('decision_required', 'Remote base disappeared.')
        if git(self.root, 'status', '--porcelain'):
            raise Halt('decision_required', 'Target moved while candidate has uncommitted work; preserve it for integration decision.')
        self.capture(['git', 'fetch', self.config['remote'], self.config['base']], 'fetch-moved-base')
        if self.r.command(['git', 'merge', '--no-edit', base], 'integrate-moved-base', cap=60):
            raise Halt('decision_required', 'New target conflicts with candidate; conflict preserved for owner decision.')
        self.state['base_sha'] = base
        self.state['baseline_head'] = base
        self.state.pop('accepted_digest', None)
        self.state.pop('accepted_parent', None)
        self.persist()
        return True

    def publish(self, incomplete=False):
        cfg, state = self.config, self.state
        if git(self.root, 'branch', '--show-current') != cfg['head'] or repository_identity(git(self.root, 'remote', 'get-url', cfg['remote'])) != cfg['repository']:
            raise Halt('publication_blocked', 'Branch/remote identity changed since preflight.')
        if not incomplete:
            try:
                review_ok = valid_review(state.get('last_review', {}), self.contract['criteria'])
            except (AttributeError, TypeError):
                review_ok = False
            if not review_ok:
                raise Halt('changes_requested', 'Current independent review does not pass; old acceptance cannot authorize publication.')
        digest_key = 'publication_safety_digest' if incomplete else 'accepted_digest'
        parent_key = 'publication_parent' if incomplete else 'accepted_parent'
        if manifest(self.root)['digest'] != state.get(digest_key):
            raise Halt('changes_requested', 'Candidate changed since independent review; revalidation required.')
        expected_environment = state.get('publication_safety_environment' if incomplete else 'accepted_environment')
        if expected_environment != environment_identity():
            raise Halt('changes_requested', 'Effective environment changed after review; revalidation required.')
        if not incomplete and state.get('accepted_dependency_binding') != state.get('environment_binding'):
            raise Halt('changes_requested', 'Dependency probe changed after review.')
        paths = self.scope()
        parent = state[parent_key]
        head = git(self.root, 'rev-parse', 'HEAD')
        marker = 'Workflow-Run: ' + state['run_id']
        if head == parent:
            if git(self.root, 'status', '--porcelain'):
                if not paths:
                    raise Halt('publication_blocked', 'No authorized task paths to commit.')
                self.capture(['git', 'add', '--all', '--', *paths], 'stage-reviewed-paths')
                self.capture(['git', 'commit', '-m', self.contract['id'] + '\n\n' + marker], 'commit-reviewed')
                head = git(self.root, 'rev-parse', 'HEAD')
        elif marker not in git(self.root, 'log', '-1', '--format=%B') or git(self.root, 'rev-parse', 'HEAD^') != parent:
            # An unrecorded commit may be ours after a crash, but not someone else's.
            if state.get('published_sha') != head:
                raise Halt('decision_required', 'Unexpected HEAD movement since review; do not publish stale approval.')
        if manifest(self.root)['digest'] != state[digest_key]:
            raise Halt('changes_requested', 'Commit hooks changed reviewed contents.')
        if git(self.root, 'status', '--porcelain'):
            raise Halt('publication_blocked', 'Committed tree/index differs from reviewed working files; no push.')
        state['candidate_sha'] = head
        self.persist()
        if self.refresh_base():
            raise Halt('changes_requested', 'Target advanced; integrated candidate requires fresh checks and review.')
        actual = self.remote_head(cfg['head'])
        if actual not in (state.get('remote_head'), head):
            raise Halt('decision_required', 'Published branch moved externally; expected revision no longer matches.')
        if actual != head:
            self.capture(['git', '-c', 'credential.helper=', '-c', 'credential.helper=!gh auth git-credential',
                          'push', cfg['remote'], 'HEAD:refs/heads/' + cfg['head']], 'push-reviewed')
        if self.remote_head(cfg['head']) != head:
            raise Halt('publication_blocked', 'Remote branch does not equal reviewed commit.')
        state.update(published_sha=head, remote_head=head)
        self.persist()
        return head

    def ci(self, head, cap=300):
        cfg = self.config
        end = time.monotonic() + min(cap, self.r.budget.remaining())
        poll = 0
        while time.monotonic() < end:
            self.r.guard()
            self.r.budget.remaining()
            if self.remote_head(cfg['head']) != head:
                raise Halt('decision_required', 'Remote candidate changed while waiting for CI.')
            if self.remote_head(cfg['base']) != self.state['base_sha']:
                if self.refresh_base():
                    return {'status': 'base_moved', 'head': head}
            raw = self.capture(['gh', 'run', 'list', '--repo', cfg['repository'], '--branch', cfg['head'],
                                '--commit', head, '--event', 'push', '--limit', '100', '--json',
                                'databaseId,name,status,conclusion,headSha,event,headBranch'], 'ci-list-%d' % poll)
            runs = json.loads(raw)
            found, pending, failed = [], False, False
            for gate in cfg['required_gates']:
                matches = [r for r in runs if r['headSha'] == head and r['event'] == 'push'
                           and r['headBranch'] == cfg['head'] and r['name'] == gate['workflow']]
                if not matches:
                    pending = True
                    continue
                run = max(matches, key=lambda x: x['databaseId'])
                if run['status'] != 'completed':
                    pending = True
                    continue
                detail = json.loads(self.capture(['gh', 'run', 'view', str(run['databaseId']), '--repo', cfg['repository'],
                                                  '--json', 'headSha,event,jobs'], 'ci-detail-%d-%s' % (poll, run['databaseId'])))
                jobs = [j for j in detail['jobs'] if j['name'] == gate['job']]
                okay = (detail['headSha'] == head and detail['event'] == 'push' and run['conclusion'] == 'success'
                        and jobs and all(j['conclusion'] == 'success' for j in jobs))
                found.append({'gate': gate, 'run': run, 'jobs': jobs, 'passed': bool(okay)})
                if not okay:
                    failed = True
                    self.r.command(['gh', 'run', 'view', str(run['databaseId']), '--repo', cfg['repository'], '--log-failed'],
                                   'ci-failed-%s' % run['databaseId'], cap=60)
            result = {'status': 'failed' if failed else 'pending' if pending else 'success', 'head': head,
                      'base': self.state['base_sha'], 'gates': found}
            save(self.r.folder / ('ci-result-%d.json' % poll), result)
            self.state['last_ci'] = result
            self.persist()
            if failed or not pending:
                return result
            poll += 1
            time.sleep(min(5, max(0, end - time.monotonic())))
        raise Halt('budget_exhausted', 'Required push CI remains pending at phase deadline; no acceptance claimed.')

    def report(self, status, message, ci=None):
        """Idempotent versioned external report; resume recovers orphan receipts."""
        state, cfg = self.state, self.config
        head = state.get('published_sha') or state.get('candidate_sha') or git(self.root, 'rev-parse', 'HEAD')
        base = state.get('base_sha')
        identity = {'schema_version': 2, 'run_id': state['run_id'], 'status': status,
                    'message': message, 'head': head, 'base': base,
                    'contents': manifest(self.root)['digest'], 'ci': ci,
                    'review': state.get('last_review')}
        report_id = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
        folder = Path(state['state_dir']) / 'reports'
        folder.mkdir(exist_ok=True)
        path = folder / (report_id + '.json')
        if path.exists():
            report = json.loads(path.read_text())
            if report.get('identity') != identity:
                raise Halt('publication_blocked', 'Existing immutable report identity does not match.')
        else:
            verification = []
            for attempt in state.get('attempts', []):
                evidence = Path(attempt['folder'])
                checks = [json.loads(p.read_text()) for p in sorted(evidence.glob('check-*-execution.json'))]
                browser = evidence / 'browser-result.json'
                verification.append({'cycle': attempt['cycle'], 'checks': checks,
                                     'browser': json.loads(browser.read_text()) if browser.exists() else None,
                                     'evidence_directory': str(evidence)})
            report = {'identity': identity, 'report_id': report_id, 'status': status, 'message': message,
                      'repository': cfg['repository'], 'source_branch': cfg['head'], 'source_sha': head,
                      'target_branch': cfg['base'], 'target_sha': base,
                      'reviewed_digest': state.get('accepted_digest'),
                      'change_summary': self.contract.get('goal', self.contract['id']),
                      'implementation_summaries': state.get('implementation_summaries', []),
                      'compare_url': 'https://github.com/%s/compare/%s...%s' % (cfg['repository'], base, head),
                      'diff_summary': git(self.root, 'diff', '--stat', base or state['baseline_head']),
                      'attempts': state.get('attempts', []), 'review': state.get('last_review'), 'ci': ci,
                      'verification': verification, 'budget': dict(state['budget']),
                      'parent_budget': state.get('parent_budget'), 'origin_status': state.get('origin_status'),
                      'format_resolution': state.get('format_resolution'), 'findings': state.get('handoff'),
                      'environment_binding': state.get('environment_binding'),
                      'proposed_action': 'Owner may authorize merging the exact source revision into the recorded target only after all gates pass; revalidate if either moves.',
                      'limits': ['No monetary meter or OS-level isolation claim.', 'Browser harness coverage is project-defined, not a complete UI audit.',
                                 'No PR created; no automatic target merge.'], 'created_at': time.time()}
            # Complete JSON is atomically written once. A crash before state/MD
            # persistence is recovered using the deterministic identity above.
            save(path, report)
        markdown = path.with_suffix('.md')
        if not markdown.exists():
            review_summary = '; '.join('%s=%s' % (r.get('id'), r.get('passed')) for r in (report.get('review') or {}).get('criteria', []))
            text = '# Merge decision report\n\nStatus: **%s**\n\n%s\n\nChange: %s\n\nSource: `%s` (`%s`)\nTarget: `%s` (`%s`)\n\n[Compare](%s)\n\n```text\n%s\n```\n\nIndependent review: %s\n\nPush CI: %s\n\nEvidence: `%s`\n\n%s\n\nLimits: %s\n' % (
                report['status'], report['message'], report['change_summary'], report['source_branch'], report['source_sha'],
                report['target_branch'], report['target_sha'], report['compare_url'], report['diff_summary'],
                review_summary or 'Not accepted / unavailable', (report.get('ci') or {}).get('status', 'Not accepted / unavailable'),
                str(path), report['proposed_action'], ' '.join(report['limits']))
            temporary = markdown.with_suffix('.md.tmp')
            temporary.write_text(text)
            temporary.replace(markdown)
        state['report'] = str(path)
        self.persist()
        return report
