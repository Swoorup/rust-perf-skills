"""Offline structural/link/eval validation, not a behavioral eval."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/rust-ui-performance'


def validate():
    text = (SKILL / 'SKILL.md').read_text()
    name = re.search(r'^name: (.+)$', text, re.M).group(1)
    assert name == SKILL.name
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) and len(name) <= 64
    description = re.search(r'^description: (.+)$', text, re.M).group(1)
    assert 0 < len(description) <= 1024 and len(text.splitlines()) < 500
    manifest = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
    assert (ROOT / manifest['skills']).resolve() == SKILL.parent
    for file in ROOT.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)', file.read_text()):
            if not target.startswith(('https://', 'http://', '#')):
                assert (file.parent / target.split('#')[0]).exists(), (file, target)
    suite = json.loads((SKILL / 'evals/evals.json').read_text())
    assert suite['skill_name'] == name
    ids = [x['id'] for x in suite['evals']]
    assert len(ids) == len(set(ids)) and len(ids) >= 10
    for case in suite['evals']:
        assert case['prompt'] and case['expected_output'] and case['assertions']
        for file in case.get('files', []):
            assert (SKILL / file).is_file()
    print(f'Validated skill layout, plugin path, local Markdown links and {len(ids)} eval cases')


if __name__ == '__main__':
    validate()
