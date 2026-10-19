"""Reconstruct the signed APK using official Godot binaries; verify exact SHA256."""
import base64,hashlib,io,json,os,pathlib,urllib.request,zipfile,zlib
ROOT=pathlib.Path(__file__).resolve().parent
recipe=json.loads((ROOT/'release.json').read_text())
local=os.environ.get('GODOT_TEMPLATE_APK')
if local: template=zipfile.ZipFile(local)
else:
 print('Downloading official Godot 4.3 templates',flush=True)
 archive=ROOT/'templates.tpz'
 urllib.request.urlretrieve('https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_export_templates.tpz',archive)
 with zipfile.ZipFile(archive) as package: template=zipfile.ZipFile(io.BytesIO(package.read('templates/android_debug.apk')))
output=bytearray()
for s in recipe['segments']:
 if 'literal' in s: output.extend(base64.b64decode(s['literal'],validate=True));continue
 raw=template.read(s['template_entry'])
 if s['method']==8:
  c=zlib.compressobj(6,zlib.DEFLATED,-15);raw=c.compress(raw)+c.flush()
 elif s['method']!=0: raise ValueError('Unsupported ZIP method')
 output.extend(raw)
assert len(output)==recipe['size'],'APK size mismatch'
assert hashlib.sha256(output).hexdigest()==recipe['sha256'],'APK SHA256 mismatch'
dist=pathlib.Path('dist');dist.mkdir(exist_ok=True)
(dist/'mina-profunda-v0.1.3-teste.apk').write_bytes(output)
for name in ['update.json','release-notes.md']: (dist/name).write_bytes((ROOT/name).read_bytes())
print('Verified signed APK:',recipe['sha256'],flush=True)
