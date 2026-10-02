"""Crea o reutiliza la copia de Influencers en la cuenta GitHub de esta entrega.

Usa Git Credential Manager; nunca escribe credenciales en archivos ni las imprime.
No modifica el repositorio original ni sobrescribe repositorios existentes.
"""
import json
import os
import subprocess
import urllib.error
import urllib.request

EXPECTED = 'monicaisabelbr'
UPSTREAM = 'rubendcl/Influencers'
env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='Never')
credential = subprocess.run(
    ['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\nusername=' + EXPECTED + '\n\n',
    text=True, capture_output=True, env=env, check=False,
)
if credential.returncode:
    raise SystemExit('No se pudo acceder a la sesion de GitHub guardada en Git Credential Manager.')
values = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
token = values.get('password')
if not token:
    raise SystemExit('No hay una credencial de GitHub disponible.')

def api(path, body=None):
    req = urllib.request.Request('https://api.github.com' + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'Influencia360-entrega', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)

user = api('/user')
if user['login'].lower() != EXPECTED.lower():
    raise SystemExit('La cuenta conectada no coincide con la cuenta de esta entrega.')
try:
    repo = api('/repos/' + EXPECTED + '/Influencers')
    if not repo.get('fork') or repo.get('source', {}).get('full_name', '').lower() != UPSTREAM.lower():
        raise SystemExit('Ya existe un repositorio diferente con ese nombre. No se modifico.')
    print('Copia existente: ' + repo['html_url'])
except urllib.error.HTTPError as exc:
    if exc.code != 404:
        raise SystemExit('GitHub devolvio HTTP ' + str(exc.code)) from None
    try:
        repo = api('/repos/' + UPSTREAM + '/forks', {'name': 'Influencers', 'default_branch_only': True})
    except urllib.error.HTTPError as err:
        raise SystemExit('No se pudo crear la copia: GitHub HTTP ' + str(err.code)) from None
    print('Copia creada: ' + repo['html_url'])
