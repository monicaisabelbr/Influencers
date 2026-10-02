"""Captura el espacio que ocupan las tablas del dashboard de resultados."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.herramientas'))
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--etapa', default='antes', choices=['antes', 'despues', 'publicado'])
parser.add_argument('--url')
args = parser.parse_args()
out = ROOT / 'entrega' / 'evidencias' / 'diseno_resultados'
out.mkdir(parents=True, exist_ok=True)
server = None
if args.url:
    base = args.url.rstrip('/')
else:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'docs'))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'

results = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(base + '/dashboard_resultados.html', wait_until='networkidle')
        sizes = [(1440, 1000)] if args.etapa == 'antes' else [(1440, 1000), (1366, 768), (390, 844)]
        for width, height in sizes:
          if width < 600:
            # flexdashboard recarga al cruzar el umbral movil; abrir una pagina
            # nueva evita competir con esa navegacion durante la comprobacion.
            page.close()
            page = browser.new_page(viewport={'width': width, 'height': height})
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(base + '/dashboard_resultados.html', wait_until='networkidle')
          else:
            page.set_viewport_size({'width': width, 'height': height})
          for title in ['Influenciadores', 'Seguidores', 'Evaluación']:
            link = page.get_by_role('link', name=title, exact=True)
            if not link.is_visible():
                page.locator('.navbar-toggle').click()
            link.click()
            if width < 600 and page.locator('.navbar-collapse.in').count():
                page.locator('.navbar-toggle').click()
            page.wait_for_timeout(600)
            page.evaluate('window.scrollTo(0, 0)')
            page.screenshot(path=str(out / f'{args.etapa}_{width}_{title}.png'))
            boxes = page.evaluate("""() => {
                const selectors = ['.dashboard-page-wrapper.active', '.dashboard-page-wrapper.active .dashboard-row',
                    '.dashboard-page-wrapper.active .chart-wrapper', '.dashboard-page-wrapper.active .chart-stage',
                    '.dashboard-page-wrapper.active .html-widget', '.dashboard-page-wrapper.active .dataTables_wrapper',
                    '.dashboard-page-wrapper.active .dataTables_scrollBody', '.dashboard-page-wrapper.active table'];
                return selectors.flatMap(s => [...document.querySelectorAll(s)].map(e => {
                    const r=e.getBoundingClientRect();
                    const st=getComputedStyle(e);
                    return {selector:s, x:r.x, y:r.y, width:r.width, height:r.height,
                      style:e.getAttribute('style'), overflow:st.overflow,
                      columns:[...e.querySelectorAll('thead tr:first-child th')].map(h=>h.getBoundingClientRect().width)};
                }));
            }""")
            if args.etapa != 'antes':
                panel = page.locator('.dashboard-page-wrapper.active')
                widget = panel.locator('.datatables.html-widget')
                counts = widget.evaluate("""e => {
                    const table = jQuery(e).data('datatable');
                    return {total: table.rows().count(), current: table.rows({page:'current'}).count(),
                            user: table.row(0).data()[2]};
                }""")
                chart_box = panel.locator('.chart-wrapper').first.bounding_box()
                assert chart_box['width'] >= width - 30, 'No aprovecha el ancho disponible'
                dimensions = page.evaluate('({content:document.documentElement.scrollWidth, viewport:innerWidth})')
                assert dimensions['content'] <= dimensions['viewport'] + 1, (title, width, dimensions)
                if title != 'Evaluación':
                    assert counts['total'] == 650 and counts['current'] == 25, counts
                    if width > 600:
                        assert chart_box['height'] >= height - 100, 'Ranking demasiado bajo'
                        assert chart_box['y'] + chart_box['height'] <= height + 1
                    search = panel.locator('.dataTables_filter input')
                    search.fill(counts['user'])
                    page.wait_for_function("""() => {
                        const e = document.querySelector('.dashboard-page-wrapper.active .datatables');
                        return jQuery(e).data('datatable').rows({search:'applied'}).count() === 1;
                    }""")
                    search.fill('')
                    page.wait_for_function("""() => {
                        const e = document.querySelector('.dashboard-page-wrapper.active .datatables');
                        return jQuery(e).data('datatable').rows({search:'applied'}).count() === 650;
                    }""")
                    panel.locator('.paginate_button.next').click()
                    assert widget.evaluate("e => jQuery(e).data('datatable').page.info().page") == 1
                    panel.locator('.paginate_button.previous').click()
                    scroll = panel.locator('.dataTables_scrollBody')
                    scroll.evaluate('e => { e.scrollLeft = e.scrollWidth; }')
                    page.wait_for_timeout(100)
                    reachable = scroll.evaluate("""e => {
                        const last = e.querySelector('tbody tr td:last-child').getBoundingClientRect();
                        const viewport = e.getBoundingClientRect();
                        return last.right <= viewport.right + 1 && last.left >= viewport.left;
                    }""")
                    assert reachable, 'La ultima columna no se puede consultar'
                    scroll.evaluate('e => { e.scrollLeft = 0; }')
                else:
                    assert counts['total'] == 2 and counts['current'] == 2
                    assert panel.locator('.dataTables_scrollBody').evaluate('e => e.scrollHeight <= e.clientHeight + 1'), 'Evaluacion recortada'
                    explanation = panel.locator('.chart-wrapper').nth(1).bounding_box()
                    assert explanation['y'] >= chart_box['y'] + chart_box['height']
                    assert explanation['y'] - (chart_box['y'] + chart_box['height']) < 30
            results.append({'pestana': title, 'ventana': [width, height], 'elementos': boxes})
        assert not errors, errors
        browser.close()
finally:
    if server:
        server.shutdown()
(out / f'{args.etapa}.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps([{'pestana': r['pestana'], 'ventana': r['ventana'], 'paneles': [
    {k: e[k] for k in ['width', 'height', 'y']} for e in r['elementos']
    if e['selector'].endswith('.chart-wrapper')]} for r in results], ensure_ascii=True, indent=2))
