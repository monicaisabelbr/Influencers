# Influencia360: análisis de redes sociales con redes bayesianas

## Publicación de la tarea

Sitio público en Netlify: **https://influencersbi2.netlify.app/**.

- [Reporte de datos](https://influencersbi2.netlify.app/dashboard_datos.html).
- [Reporte de resultados](https://influencersbi2.netlify.app/dashboard_resultados.html).
- [Informe de publicación y respuestas de la tarea](entrega/INFORME_PUBLICACION.md).
- [Informe en Word](entrega/INFORME_PUBLICACION.docx) y [PDF](entrega/INFORME_PUBLICACION.pdf).
- [Evidencia de verificación pública](entrega/evidencias/verificacion_publicacion.json).

Esta copia conserva el proyecto de [rubendcl/Influencers](https://github.com/rubendcl/Influencers).
La publicación se realizó manualmente con **Netlify Drop**, cargando `docs`.
Las actualizaciones de GitHub no se publican automáticamente con este método.
`netlify.toml` prepara la alternativa de conectar GitHub con Netlify: publicar `docs`
y dejar vacío el comando de construcción, porque R ya generó los HTML localmente.

Proyecto académico de Business Intelligence que genera una red social completamente ficticia con `charlatan`, explora perfiles, publicaciones, relaciones e interacciones, y emplea una red bayesiana discreta para identificar influenciadores y seguidores de valor.

## Ejecución rápida

Desde la raíz del proyecto:

```bash
Rscript run_all.R
```

La orden genera los CSV, entrena y evalúa el modelo y publica tres documentos en `docs/`:

- `index.html`: informe metodológico y ejecutivo.
- `dashboard_datos.html`: exploración interactiva de los datos iniciales.
- `dashboard_resultados.html`: ranking, red bayesiana y escenarios de inferencia.

Los resultados incluidos son reproducibles con la semilla `20260917`. Todos los nombres, organizaciones, perfiles y eventos son sintéticos; no representan personas reales.

## Estructura

```text
R/                    generación, preparación, modelado y utilidades
data/raw/             CSV simulados con charlatan
data/processed/       variables analíticas y rankings en CSV
models/               red ajustada (artefacto regenerable)
reports/              RMarkdown del informe y dashboards
docs/                 HTML listo para abrir o publicar
run_all.R              pipeline completo
```

## Dependencias principales

`charlatan`, `bnlearn`, `dplyr`, `tidyr`, `readr`, `ggplot2`, `plotly`, `DT`, `visNetwork`, `flexdashboard`, `rmarkdown`, `knitr` y `DiagrammeR`.

Si faltan paquetes, instálelos una vez con:

Para instalarlos en `.Rlib` dentro del proyecto, ejecute `Rscript scripts/preparar.R`.
En PowerShell, si la configuración regional produce errores con tildes, ejecute
`$env:LC_ALL = 'English_United States.utf8'` antes de `Rscript run_all.R`.

También se pueden instalar con el comando habitual de R:

```r
install.packages(c("charlatan", "bnlearn", "dplyr", "tidyr", "readr",
                   "ggplot2", "plotly", "DT", "visNetwork",
                   "flexdashboard", "rmarkdown", "knitr", "DiagrammeR"))
```

## Alcance analítico

La red bayesiana estima asociaciones probabilísticas condicionales. En este conjunto ficticio el proceso generador es conocido, pero el modelo aprendido de datos observacionales no demuestra causalidad. Sus probabilidades deben interpretarse como apoyo para priorización y no como una decisión automática sobre personas.

