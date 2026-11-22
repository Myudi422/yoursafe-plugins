import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
plugins = []
for path in sorted((root / 'plugins').glob('*/plugin.json')):
    raw = path.read_bytes()
    plugin = json.loads(raw)
    assert plugin['apiVersion'] == 1
    assert plugin['id'] == path.parent.name
    assert isinstance(plugin['version'], int) and plugin['version'] > 0
    plugins.append(dict(id=plugin['id'], name=plugin['name'], version=plugin['version'],
                        path=path.relative_to(root).as_posix(), sha256=hashlib.sha256(raw).hexdigest()))
(root / 'index.json').write_text(json.dumps(dict(apiVersion=1, plugins=plugins), indent=2) + '\n', encoding='utf-8')
print(f'Indexed {len(plugins)} plugins')
