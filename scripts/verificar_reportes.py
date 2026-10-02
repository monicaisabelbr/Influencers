"""Verifica los HTML con Edge y guarda evidencia local o de la URL publicada."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import sys
import threading
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.herramientas'))
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', help='URL base de Netlify; sin argumento se comprueba docs local.')
args = parser.parse_args()
server = None
if args.url:
    base = args.url.rstrip('/') + '/'
    label = 'publicacion'
else:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'docs'))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}/'
    label = 'local'

out = ROOT / 'entrega' / 'evidencias'
out.mkdir(parents=True, exist_ok=True)
results = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        for name in ['index.html', 'dashboard_datos.html', 'dashboard_resultados.html']:
            errors.clear()
            response = page.goto(base + name, wait_until='networkidle', timeout=90000)
            assert response and response.status == 200, f'{name}: HTTP incorrecto'
            assert 'Influencia360' in page.title(), f'{name}: no muestra el reporte esperado'
            page.wait_for_function("document.querySelectorAll('.plotly.html-widget .main-svg').length > 0")
            tabs = page.locator('.navbar-nav a[data-toggle="tab"]')
            visited = []
            for i in range(tabs.count()):
                tab = tabs.nth(i)
                visited.append(tab.inner_text())
                tab.click()
                page.wait_for_timeout(250)
            table_count = page.evaluate("window.jQuery && jQuery.fn.dataTable ? jQuery.fn.dataTable.tables().length : 0")
            plot_count = page.locator('.plotly.html-widget .main-svg').count()
            if tabs.count():
                tabs.first.click()
            page.wait_for_timeout(400)
            page.screenshot(path=str(out / f'{label}_{Path(name).stem}.png'), full_page=False)
            assert not errors, f'{name}: errores JavaScript: {errors}'
            assert table_count > 0, f'{name}: faltan las tablas interactivas'
            # Verifica el filtro real de DataTables y restablece el contenido.
            table_test = page.evaluate("""() => {
                const node = jQuery.fn.dataTable.tables()[0];
                const table = jQuery(node).DataTable();
                const total = table.rows().count();
                table.search('CADENA_QUE_NO_EXISTE_360').draw();
                const filtered = table.rows({search:'applied'}).count();
                table.search('').draw();
                return {total, filtered};
            }""")
            assert table_test['total'] > 0 and table_test['filtered'] == 0
            results.append({'archivo': name, 'url': page.url, 'http': response.status,
                            'titulo': page.title(), 'pestanas': visited,
                            'graficos_svg': plot_count, 'tablas': table_count,
                            'filtro_verificado': True, 'errores_js': list(errors)})
        browser.close()
finally:
    if server:
        server.shutdown()

evidence = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'modo': label, 'resultados': results}
(out / f'verificacion_{label}.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(evidence, ensure_ascii=True, indent=2))
