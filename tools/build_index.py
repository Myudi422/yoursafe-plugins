import hashlib
import json
import subprocess
import re
from pathlib import Path


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL)


def published_snapshot(root):
    """Compare with the last published bot snapshot, not an edited working index."""
    try:
        git(root, 'rev-parse', '--verify', 'HEAD')
    except subprocess.CalledProcessError:
        return {}
    try:
        ref = git(root, 'log', '-1', '--format=%H',
                  '--author=41898282+github-actions\\[bot\\]@users.noreply.github.com',
                  '--', 'index.json').decode().strip()
        if not ref:
            history = git(root, 'log', '--reverse', '--format=%H', '--', 'index.json').decode().splitlines()
            if not history:
                return {}
            ref = history[0]
        index = json.loads(git(root, 'show', f'{ref}:index.json'))
        result = {}
        for entry in index['plugins']:
            plugin = json.loads(git(root, 'show', f"{ref}:{entry['path']}"))
            assert plugin['id'] == entry['id']
            assert type(entry['version']) is int and entry['version'] > 0
            result[entry['id']] = (entry['version'], plugin)
        return result
    except subprocess.CalledProcessError:
        # A new, uncommitted repository has no published plugins yet.
        if not (root / '.git').exists():
            return {}
        raise


def content(plugin):
    return {key: value for key, value in plugin.items() if key != 'version'}


def build(root):
    previous = published_snapshot(root)
    entries, writes = [], []
    for path in sorted((root / 'plugins').glob('*/plugin.json')):
        raw = path.read_bytes()
        plugin = json.loads(raw)
        assert type(plugin['apiVersion']) is int and plugin['apiVersion'] == 1
        kind = plugin.get('type', 'video')
        assert kind == 'video'
        assert not any(key in plugin for key in ('script', 'scope', 'outbound', 'network', 'selectors', 'permissions'))
        assert plugin['id'] == path.parent.name
        assert re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', plugin['id'])
        assert isinstance(plugin['name'], str) and plugin['name'].strip()
        old = previous.get(plugin['id'])
        version = 1 if old is None else old[0] + (content(plugin) != content(old[1]))
        if type(plugin.get('version')) is not int or plugin['version'] != version:
            plugin['version'] = version
            raw = (json.dumps(plugin, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
            writes.append((path, raw))
        entries.append(dict(id=plugin['id'], name=plugin['name'], version=version,
                            path=path.relative_to(root).as_posix(), sha256=hashlib.sha256(raw).hexdigest(), type=kind, apiVersion=plugin['apiVersion']))
    # Validate every manifest before updating any file.
    for path, raw in writes:
        path.write_bytes(raw)
    (root / 'index.json').write_bytes((json.dumps(dict(apiVersion=1, plugins=entries), indent=2) + '\n').encode('utf-8'))
    print(f'Indexed {len(entries)} plugins; updated {len(writes)} automatic versions')


if __name__ == '__main__':
    build(Path(__file__).resolve().parents[1])
