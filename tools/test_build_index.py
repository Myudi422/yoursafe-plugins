import json
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path
from build_index import build


class AutomaticVersionsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run_git('init', '-b', 'main')
        self.run_git('config', 'user.name', 'Test author')
        self.run_git('config', 'user.email', 'test@example.com')
        self.path = self.root / 'plugins/example/plugin.json'
        self.path.parent.mkdir(parents=True)
        self.write(dict(apiVersion=1, id='example', name='Example', domains=['example.com']))
        build(self.root)
        self.commit()

    def run_git(self, *args):
        subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def write(self, plugin):
        self.path.write_text(json.dumps(plugin, indent=2) + '\n', encoding='utf-8')

    def read(self):
        return json.loads(self.path.read_bytes())

    def commit(self, bot=False):
        self.run_git('add', '.')
        args = ['commit', '-m', 'Publish']
        if bot:
            args += ['--author=github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>']
        self.run_git(*args)

    def test_new_plugin_starts_at_one_without_a_version_field(self):
        self.assertEqual(1, self.read()['version'])

    def test_executable_formats_are_rejected_without_modifying_catalog(self):
        before = (self.root / 'index.json').read_bytes()
        for api in (2, 3, 4):
            self.write(dict(apiVersion=api, type='shortlink', id='example', name='Unsupported', domains=['example.com']))
            with self.assertRaises(AssertionError):
                build(self.root)
            self.assertEqual(before, (self.root / 'index.json').read_bytes())
        self.write(dict(apiVersion=1, id='example', name='Unsupported', domains=['example.com'], script='function resolve(){return null;}'))
        with self.assertRaises(AssertionError):
            build(self.root)
        self.assertEqual(before, (self.root / 'index.json').read_bytes())

    def test_deleted_plugin_disappears_from_catalog(self):
        self.path.unlink()
        build(self.root)
        self.assertEqual([], json.loads((self.root / 'index.json').read_bytes())['plugins'])

    def test_content_edit_increments_once_even_when_run_repeatedly(self):
        plugin = self.read()
        plugin['domains'].append('another.example')
        self.write(plugin)
        # Simulate a GitHub editor commit, followed by an Actions commit.
        self.commit()
        build(self.root)
        self.assertEqual(2, self.read()['version'])
        build(self.root)
        self.assertEqual(2, self.read()['version'])
        self.commit(bot=True)
        build(self.root)
        self.assertEqual(2, self.read()['version'])
        plugin = self.read()
        plugin['description'] = 'Updated description'
        self.write(plugin)
        build(self.root)
        self.assertEqual(3, self.read()['version'])

    def test_formatting_and_manual_version_edits_do_not_bump(self):
        plugin = self.read()
        plugin['version'] = 999
        self.path.write_text(json.dumps(plugin), encoding='utf-8')
        build(self.root)
        self.assertEqual(1, self.read()['version'])

    def test_generated_checksum_covers_final_version_bytes(self):
        plugin = self.read()
        plugin['name'] = 'New name'
        self.write(plugin)
        build(self.root)
        entry = json.loads((self.root / 'index.json').read_bytes())['plugins'][0]
        self.assertEqual(2, entry['version'])
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(), entry['sha256'])

    def test_invalid_manifest_leaves_other_files_unmodified(self):
        before = self.path.read_bytes()
        index_before = (self.root / 'index.json').read_bytes()
        invalid = self.root / 'plugins/invalid/plugin.json'
        invalid.parent.mkdir()
        invalid.write_text('{broken', encoding='utf-8')
        with self.assertRaises(json.JSONDecodeError):
            build(self.root)
        self.assertEqual(before, self.path.read_bytes())
        self.assertEqual(index_before, (self.root / 'index.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
