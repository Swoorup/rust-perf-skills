#!/usr/bin/env python3
"""Verify reviewed snapshot identity, revision, clean state, paths and literal anchors."""
import argparse
import json
from pathlib import Path
import subprocess


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def verify(root, manifest):
    problems = []
    for key in ('repository', 'commit'):
        if not manifest.get(key):
            problems.append(f'unknown snapshot {key}; rediscover and record provenance')
    if manifest.get('commit') and git(root, 'rev-parse', 'HEAD') != manifest['commit']:
        problems.append('snapshot revision differs; rediscover implementation')
    if manifest.get('repository') and git(root, 'remote', 'get-url', 'origin').removesuffix('.git') != manifest['repository'].removesuffix('.git'):
        problems.append('repository identity differs (compare reviewed origin URLs)')
    if git(root, 'status', '--porcelain'):
        problems.append('checkout dirty; HEAD does not fully identify current source')
    if not manifest.get('anchors'):
        problems.append('no anchors supplied')
    for anchor in manifest.get('anchors', []):
        path = (root / anchor['path']).resolve()
        if not path.is_relative_to(root.resolve()):
            problems.append('anchor path escapes checkout')
        elif not path.is_file():
            problems.append(f'missing path: {anchor["path"]}')
        elif not anchor.get('contains') or anchor['contains'] not in path.read_text():
            problems.append(f'missing literal symbol: {anchor["path"]}: {anchor.get("contains")}')
    return problems


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--manifest', type=Path, default=Path(__file__).resolve().parent.parent / 'references/project-anchors.json')
    a = p.parse_args()
    try:
        problems = verify(a.root.resolve(), json.loads(a.manifest.read_text()))
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as e:
        p.error(str(e))
    print(json.dumps({'verified': not problems, 'problems': problems,
                      'limitation': 'Symbol presence cannot verify behavior; read the current implementation.'}, indent=2))
    raise SystemExit(bool(problems))


if __name__ == '__main__':
    main()
