"""Version-bound local evidence and actual Chrome adapter. Standard library only."""
import hashlib
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import functools
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import threading
import time

from development_loop import execute, save


class Halt(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message
        super().__init__(message)


def git(root, *args):
    return subprocess.check_output(['git', *args], cwd=root, text=True, timeout=30).strip()


def manifest(root):
    """Content identity stable across commit; ignored outputs never enter it."""
    names = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root).split(b'\0')
    files = {}
    for name in sorted(set(names) - {b''}):
        p = root / os.fsdecode(name)
        if not p.exists() and not p.is_symlink():
            continue
        if p.is_symlink():
            data, mode = os.fsencode(os.readlink(p)), 'symlink'
        elif p.is_file():
            data, mode = p.read_bytes(), oct(p.stat().st_mode & 0o777)
        else:
            continue
        files[os.fsdecode(name)] = {'sha256': hashlib.sha256(data).hexdigest(), 'mode': mode}
    encoded = json.dumps(files, sort_keys=True).encode()
    return {'digest': hashlib.sha256(encoded).hexdigest(), 'files': files}


def fingerprint(paths):
    return {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}


class Budget:
    def __init__(self, state, persist, seconds, cycles):
        self.state, self.persist = state, persist
        if 'budget' not in state:
            state['budget'] = {'started_at': time.time(), 'deadline': time.time() + seconds,
                               'seconds': seconds, 'max_cycles': cycles, 'cycles': 0}
            persist()
        if time.time() + 1 < state['budget'].get('last_seen', state['budget']['started_at']):
            raise Halt('budget_exhausted', 'Wall clock moved backwards across restart; allowance is not replenished.')
        self.start_mono, self.start_wall = time.monotonic(), time.time()

    def remaining(self, cap=None, reserve=0):
        b = self.state['budget']
        # Neither downtime, restart, backwards wall-clock changes nor a longer
        # invocation allowance can silently replenish the persisted run.
        now = max(time.time(), self.start_wall + time.monotonic() - self.start_mono,
                  b.get('last_seen', b['started_at']))
        b['last_seen'] = now
        self.persist()
        left = int(b['deadline'] - now) - reserve
        if left <= 0:
            raise Halt('budget_exhausted', 'Cumulative run deadline exhausted; explicit new authorization required.')
        return min(left, cap) if cap else left

    def cycle(self):
        b = self.state['budget']
        if b['cycles'] >= b['max_cycles']:
            raise Halt('budget_exhausted', 'Cumulative repair-cycle limit reached.')
        self.remaining()
        b['cycles'] += 1
        self.persist()
        return b['cycles']



_EXECUTABLES = {}


def environment_identity():
    # Bind effective inherited environment without recording credential values.
    encoded = json.dumps(dict(os.environ), sort_keys=True).encode()
    return {'inherited_sha256': hashlib.sha256(encoded).hexdigest(),
            'python': sys.version, 'python_executable': str(Path(sys.executable).resolve()),
            'platform': platform.platform(),
            'locale': {key: os.environ.get(key) for key in ['LANG', 'LC_ALL', 'TZ']}}


def executable_identity(argv0, cwd):
    candidate = Path(argv0)
    if not candidate.is_absolute():
        candidate = (Path(cwd) / candidate) if '/' in argv0 else Path(shutil.which(argv0) or argv0)
    candidate = candidate.resolve()
    if not candidate.is_file():
        return {'path': str(candidate), 'missing': True}
    stat = candidate.stat()
    key = (str(candidate), stat.st_size, stat.st_mtime_ns)
    if key not in _EXECUTABLES:
        h = hashlib.sha256()
        with candidate.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        _EXECUTABLES[key] = {'path': str(candidate), 'sha256': h.hexdigest(), 'bytes': stat.st_size}
    return dict(_EXECUTABLES[key])


class Recorder:
    def __init__(self, root, state, persist, budget, folder, guard):
        self.root, self.state, self.persist = root, state, persist
        self.budget, self.folder, self.guard = budget, folder, guard
        folder.mkdir(parents=True, exist_ok=True)

    def command(self, argv, label, *, cwd=None, prompt=None, cap=300, reserve=0):
        self.guard()
        before = manifest(self.root)
        record = {'argv': argv, 'cwd': str(cwd or self.root), 'input_digest': before['digest'],
                  'started_at': time.time(), 'environment': environment_identity(),
                  'executable': executable_identity(argv[0], cwd or self.root),
                  'project_environment_binding': self.state.get('environment_binding'),
                  'log': str(self.folder / (label + '.log'))}
        save(self.folder / (label + '.input.json'), before)
        try:
            code = execute(argv, cwd or self.root, Path(record['log']), self.budget.remaining(cap, reserve), prompt)
        except subprocess.TimeoutExpired:
            record['exit_code'], record['ended_at'] = 'timeout', time.time()
            save(self.folder / (label + '-execution.json'), record)
            raise Halt('budget_exhausted', 'Phase timeout: ' + label)
        record.update(exit_code=code, ended_at=time.time())
        record['environment_after'] = environment_identity()
        save(self.folder / (label + '-execution.json'), record)
        self.guard()
        if record['environment'] != record['environment_after']:
            raise Halt('changes_requested', 'Effective environment changed during command; evidence invalid.')
        return code


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'pre' and dict(attrs).get('id') == 'results':
            self.active = True

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def browser_run(recorder, executable, directory, label='browser', entry='index.html'):
    """Start a trusted project harness on loopback; Chrome executes its JS."""
    directory = directory.resolve()
    if not (directory / entry).is_file() or not (directory / entry).resolve().is_relative_to(directory):
        raise Halt('capability_blocked', 'Browser harness entry missing or outside harness directory.')
    version_file = recorder.folder / (label + '-version.log')
    try:
        code = recorder.command([executable, '--version'], label + '-version', cap=20)
    except (OSError, Halt) as error:
        if isinstance(error, Halt) and error.status != 'capability_blocked':
            raise
        raise Halt('capability_blocked', 'Actual browser executable unavailable: ' + str(error))
    if code:
        raise Halt('capability_blocked', 'Cannot identify actual browser version.')
    def harness_hashes():
        return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(directory.rglob('*')) if p.is_file()}
    before_harness = harness_hashes()
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        argv = [executable, '--headless=new', '--no-first-run', '--no-default-browser-check',
                '--user-data-dir=' + str(recorder.folder / (label + '-profile')),
                '--virtual-time-budget=5000', '--dump-dom',
                'http://127.0.0.1:%d/%s' % (server.server_port, entry)]
        if recorder.command(argv, label + '-dom', cap=90):
            raise Halt('capability_blocked', 'Actual browser failed; inspect captured browser output.')
        if harness_hashes() != before_harness:
            raise Halt('changes_requested', 'Generated browser harness changed during execution; evidence invalid.')
        parser = ResultParser()
        parser.feed((recorder.folder / (label + '-dom.log')).read_text())
        try:
            result = json.loads(''.join(parser.parts))
        except (ValueError, TypeError) as error:
            raise Halt('capability_blocked', 'Browser did not return structured #results: ' + str(error))
        save(recorder.folder / (label + '-result.json'), result)
        save(recorder.folder / (label + '-binding.json'), {
            'browser_version': version_file.read_text().strip(), 'engine': 'actual Chrome headless',
            'harness': before_harness,
            'target_digest': manifest(recorder.root)['digest'],
            'result_sha256': hashlib.sha256((recorder.folder / (label + '-result.json')).read_bytes()).hexdigest()})
        return result
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
