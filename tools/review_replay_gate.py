"""Run a trusted replay argv and verify its private, revision-bound observation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from delivery_evidence import manifest


def replay(target, review, evidence, command):
    target, review, evidence = Path(target).resolve(), Path(review).resolve(), Path(evidence).resolve()
    if target == evidence or target in evidence.parents:
        raise ValueError('Replay evidence must stay outside the target.')
    evidence.mkdir(parents=True, exist_ok=True)
    artifact = evidence / 'review-replay.json'
    if artifact.exists() or artifact.is_symlink():
        raise ValueError('Replay must produce fresh evidence, not adopt an existing file.')
    expected = manifest(target)['digest']
    original = review.read_bytes()
    selected = json.loads(original)
    subprocess.run(command, cwd=target, check=True)
    if not artifact.is_file() or artifact.is_symlink():
        raise ValueError('Trusted replay did not produce review-replay.json.')
    if artifact.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('Replay observation exceeds 32 MiB.')
    result = json.loads(artifact.read_text())
    if not isinstance(result, dict):
        raise ValueError('Replay observation must be an object.')
    if (result.get('schema_version') != 1
            or result.get('selected_review_sha256') != hashlib.sha256(original).hexdigest()
            or result.get('target_digest') != expected
            or manifest(target)['digest'] != expected
            or review.read_bytes() != original
            or result.get('snapshot_sha256') != selected['context']['snapshotSha256']):
        raise ValueError('Replay observation source/review/data binding mismatch.')
    response = result.get('response')
    if not isinstance(response, dict) or not isinstance(response.get('answer'), dict) or not isinstance(response.get('trace'), dict) or not response['trace']:
        raise ValueError('An actual traced answer observation is required.')
    trace = response['trace']
    if response.get('error') or not isinstance(response['answer'].get('summary'), str) or any(not isinstance(trace.get(k), dict) for k in ('activationScores','activationPaths')):
        raise ValueError('Replay did not return a usable activation trace.')
    submitted = result.get('replayed_request')
    if not isinstance(submitted, dict) or any(submitted.get(k) != selected['request'].get(k) for k in ('query','options','scope')) or response.get('request', {}).get('query') != selected['request']['query']:
        raise ValueError('Replay observation belongs to a different question/settings.')
    before = selected['response']['retrieval'].get('graphSequence')
    after = response.get('retrieval', {}).get('graphSequence')
    if type(before) is not int or type(after) is not int or before != after:
        raise ValueError('Original graph version is unavailable or changed during replay.')
    # This attests file bindings and command completion, not semantic correctness.
    print(json.dumps({'status':'observed_not_semantically_accepted', 'artifact':str(artifact), 'target_digest':expected}))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', required=True); p.add_argument('--review', required=True)
    p.add_argument('--evidence', required=True); p.add_argument('command', nargs=argparse.REMAINDER)
    args = p.parse_args(); command = args.command
    if command and command[0] == '--': command = command[1:]
    if not command: p.error('Trusted replay argv required after --')
    try:
        replay(args.target, args.review, args.evidence, command)
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({'status':'replay_evidence_rejected','reason':str(error)}))
        return 2


if __name__ == '__main__': raise SystemExit(main())
