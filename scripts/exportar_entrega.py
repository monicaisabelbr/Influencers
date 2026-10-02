"""Exporta el informe de la tarea a Word, HTML autocontenido y PDF."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'entrega'
sys.path.insert(0, str(ROOT / '.herramientas'))
from playwright.sync_api import sync_playwright

source = 'INFORME_PUBLICACION.md'
subprocess.run(['pandoc', source, '--standalone', '-o', 'INFORME_PUBLICACION.docx'], cwd=OUT, check=True)
subprocess.run(['pandoc', source, '--standalone', '--embed-resources', '--css=estilos_informe.css',
                '-o', 'INFORME_PUBLICACION.html'], cwd=OUT, check=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1200, 'height': 1000})
    page.goto((OUT / 'INFORME_PUBLICACION.html').as_uri(), wait_until='networkidle')
    page.pdf(path=str(OUT / 'INFORME_PUBLICACION.pdf'), format='A4', print_background=True,
             prefer_css_page_size=True, display_header_footer=True,
             header_template='<span></span>',
             footer_template='<div style="font-size:9px;width:100%;text-align:center;color:#666">Influencia360 | <span class="pageNumber"></span> / <span class="totalPages"></span></div>')
    page.screenshot(path=str(OUT / 'evidencias' / 'vista_informe_entrega.png'))
    browser.close()
for ext in ['docx', 'html', 'pdf']:
    path = OUT / ('INFORME_PUBLICACION.' + ext)
    print(f'{path.name}: {path.stat().st_size} bytes')
