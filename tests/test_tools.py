import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/rust-ui-performance/scripts'


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


compare = module('compare-runs')
anchors = module('verify-anchors')
capture = module('capture-environment')


class ComparisonTests(unittest.TestCase):
    def data(self, samples):
        return dict(metric='latency', unit='ms', workload='warm-A', samples=samples)

    def test_statistics_and_tail(self):
        result = compare.compare(self.data([1, 2, 3, 4, 100]), self.data([1, 2, 2, 3, 4]))
        self.assertEqual(result['before']['median'], 3)
        self.assertEqual(result['before']['mad'], 1)
        self.assertAlmostEqual(result['before']['p99'], 96.16)
        self.assertAlmostEqual(result['median_delta_percent'], -100 / 3)
        self.assertGreater(result['before']['p99'], result['after']['p99'])

    def test_zero_baseline(self):
        self.assertIsNone(compare.compare(self.data([0]), self.data([1]))['median_delta_percent'])

    def test_mismatched_population(self):
        for key in ('metric', 'unit', 'workload'):
            after = self.data([1]); after[key] = 'different'
            with self.assertRaises(ValueError):
                compare.compare(self.data([1]), after)

    def test_invalid_samples(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'samples.json'
            for values in ([], [True], [-1], [float('nan')], [float('inf')], ['10']):
                p.write_text(json.dumps(self.data(values)))
                with self.assertRaises(ValueError):
                    compare.load(p)

    def test_cli_preserves_failure(self):
        p = subprocess.run(['python3', str(SCRIPTS / 'compare-runs.py'), '/missing/a', '/missing/b'], capture_output=True)
        self.assertNotEqual(p.returncode, 0)


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Fixture')
        self.git('remote', 'add', 'origin', 'https://github.com/example/fixture.git')
        (self.root / 'owner.rs').write_text('struct RetainedNode;\n')
        (self.root / 'Cargo.lock').write_text('# fixture lock\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        self.manifest = dict(repository='https://github.com/example/fixture', commit=self.git('rev-parse', 'HEAD'), anchors=[dict(path='owner.rs', contains='RetainedNode')])

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def test_verified_snapshot(self):
        self.assertEqual(anchors.verify(self.root, self.manifest), [])

    def test_unknown_and_stale_revision(self):
        for revision in (None, 'a' * 40):
            manifest = dict(self.manifest, commit=revision)
            self.assertTrue(anchors.verify(self.root, manifest))

    def test_wrong_repository(self):
        self.assertTrue(anchors.verify(self.root, dict(self.manifest, repository='https://github.com/other/repo')))

    def test_dirty_missing_symbol_and_path(self):
        (self.root / 'owner.rs').write_text('struct Different;')
        errors = anchors.verify(self.root, self.manifest)
        self.assertTrue(any('dirty' in x for x in errors))
        self.assertTrue(any('missing literal' in x for x in errors))
        (self.root / 'owner.rs').unlink()
        self.assertTrue(any('missing path' in x for x in anchors.verify(self.root, self.manifest)))

    def test_escape_rejected(self):
        manifest = dict(self.manifest, anchors=[dict(path='../outside', contains='anything')])
        self.assertIn('anchor path escapes checkout', anchors.verify(self.root, manifest))

    def test_capture_hashes_missing_tools_and_secret_exclusion(self):
        with patch.dict(os.environ, {'SECRET_TOKEN': 'do-not-record'}, clear=True):
            result = capture.capture(self.root, 'release', None, None, 'warm-A', 'cargo bench')
        self.assertEqual(result['commit'], self.manifest['commit'])
        self.assertEqual(result['dirty_state'], '')
        self.assertEqual(len(result['file_sha256'][str(self.root / 'Cargo.lock')]), 64)
        self.assertNotIn('do-not-record', json.dumps(result))
        self.assertIsNone(result['rustc_verbose'])


if __name__ == '__main__':
    unittest.main()
