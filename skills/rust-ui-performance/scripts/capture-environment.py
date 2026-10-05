#!/usr/bin/env python3
"""Capture measurement provenance; never dump environment or config contents."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess


def run(args, cwd):
    try:
        p = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=30)
        return p.stdout.strip() if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def capture(root, profile, features, target, workload, command):
    files = {root / 'Cargo.lock', root / 'Cargo.toml', root / 'mise.toml', root / 'rust-toolchain', root / 'rust-toolchain.toml'}
    # Cargo also discovers configuration in ancestor directories and CARGO_HOME.
    for directory in [root, *root.parents]:
        files.update(directory / '.cargo' / name for name in ('config', 'config.toml'))
    cargo_home = Path(os.environ.get('CARGO_HOME', str(Path.home() / '.cargo')))
    files.update(cargo_home / name for name in ('config', 'config.toml'))
    identities = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p.is_file()}
    rust = run(['rustc', '-Vv'], root)
    return {'schema_version': 1, 'captured_at_utc': datetime.now(timezone.utc).isoformat(), 'commit': run(['git', 'rev-parse', 'HEAD'], root),
            'dirty_state': run(['git', 'status', '--porcelain=v1', '--untracked-files=all'], root),
            'rustc_verbose': rust, 'cargo_version': run(['cargo', '-V'], root),
            'target': target, 'host_target': next((x[6:] for x in (rust or '').splitlines() if x.startswith('host: ')), None),
            'os': platform.platform(), 'architecture': platform.machine(), 'cpu': platform.processor() or None,
            'cpu_model': run(['sysctl', '-n', 'machdep.cpu.brand_string'], root) if platform.system() == 'Darwin' else run(['lscpu'], root),
            'profile': profile, 'features': features, 'workload': workload, 'command': command,
            'compiler_flags': {k: os.environ.get(k) for k in ('RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'CARGO_BUILD_TARGET')},
            'profile_overrides': {k: v for k, v in os.environ.items() if k.startswith('CARGO_PROFILE_')},
            'file_sha256': identities,
            'limitations': 'Feature/profile values are declared, not resolved. Capture cargo metadata separately when needed; record GPU/backend, power/thermal state and dirty diff artifact manually. Missing tools are null.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    for key in ('profile', 'features', 'target', 'workload', 'command'):
        p.add_argument('--' + key, required=key in ('profile', 'workload', 'command'), default=None)
    a = p.parse_args()
    if not a.root.is_dir():
        p.error('root must be an existing checkout directory')
    print(json.dumps(capture(a.root.resolve(), a.profile, a.features, a.target, a.workload, a.command), indent=2))


if __name__ == '__main__':
    main()
