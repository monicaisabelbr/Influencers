# Ejecutar desde la raiz: Rscript scripts/preparar.R
options(repos = c(CRAN = "https://cloud.r-project.org"), timeout = 300)
local_lib <- file.path(getwd(), ".Rlib")
dir.create(local_lib, showWarnings = FALSE)
.libPaths(c(local_lib, .libPaths()))
required <- c("charlatan", "bnlearn", "dplyr", "tidyr", "readr", "ggplot2",
              "plotly", "DT", "visNetwork", "flexdashboard", "rmarkdown",
              "knitr", "DiagrammeR")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) {
  install.packages(missing, lib = local_lib,
                  type = if (.Platform$OS.type == "windows") "binary" else "source")
}
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) stop("Faltan paquetes: ", paste(missing, collapse = ", "))
if (!rmarkdown::pandoc_available()) stop("Instale Pandoc o RStudio para renderizar HTML.")
message("Dependencias listas. Ejecute: Rscript run_all.R")
