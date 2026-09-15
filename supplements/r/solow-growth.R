# Solow growth supplement: generate browser data and a static fallback.
#
# Run from any directory with:
#   Rscript supplements/r/solow-growth.R
#
# This script uses base R only. It writes the scenario grid consumed by the
# browser tool and an SVG fallback for environments without JavaScript.

script_path <- sub("^--file=", "", commandArgs(trailingOnly = FALSE)[grep("^--file=", commandArgs(trailingOnly = FALSE))])
if (length(script_path) != 1L) stop("Run this file with Rscript.")
root <- normalizePath(file.path(dirname(script_path), "..", ".."), mustWork = TRUE)
data_dir <- file.path(root, "assets", "data")
image_dir <- file.path(root, "assets", "images")
dir.create(data_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(image_dir, recursive = TRUE, showWarnings = FALSE)

# All variables are per effective worker. The law of motion is
# k_{t+1} = ((1-delta) k_t + s k_t^alpha) / ((1+n)(1+g)).
alpha <- 0.33
n <- 0.01
g <- 0.02
horizon <- 40L
s_values <- c(0.18, 0.22, 0.26, 0.30)
delta_values <- c(0.04, 0.06, 0.08)
k0_values <- c(0.50, 1.00, 2.00)
defaults <- list(s = 0.22, delta = 0.06, k0 = 0.50)

fmt_number <- function(x) {
  value <- formatC(as.numeric(x), format = "f", digits = 6, drop0trailing = FALSE)
  sub("\\.?0+$", "", value)
}
json_number <- function(x) {
  if (!is.finite(x)) stop("JSON output cannot contain non-finite values.")
  fmt_number(x)
}
json_string <- function(x) {
  escaped <- gsub("\\\\", "\\\\\\\\", x)
  escaped <- gsub('"', '\\\\"', escaped, fixed = TRUE)
  paste0('"', escaped, '"')
}
json_object <- function(fields) paste0("{", paste(fields, collapse = ","), "}")
json_array <- function(items) paste0("[", paste(items, collapse = ","), "]")
json_field <- function(name, value) paste0(json_string(name), ":", value)

scenario <- function(s, delta, k0) {
  dilution <- (1 + n) * (1 + g) - (1 - delta)
  k_star <- (s / dilution)^(1 / (1 - alpha))
  periods <- 0:horizon
  k <- numeric(length(periods))
  y <- numeric(length(periods))
  c <- numeric(length(periods))
  i <- numeric(length(periods))
  k[1] <- k0
  for (index in seq_along(periods)) {
    y[index] <- k[index]^alpha
    i[index] <- s * y[index]
    c[index] <- (1 - s) * y[index]
    if (index < length(periods)) {
      k[index + 1] <- ((1 - delta) * k[index] + i[index]) / ((1 + n) * (1 + g))
    }
  }
  list(
    id = paste0("s", sprintf("%.2f", s), "-d", sprintf("%.2f", delta), "-k", sprintf("%.2f", k0)),
    parameters = list(s = s, delta = delta, k0 = k0),
    steady_state = list(k = k_star, y = k_star^alpha, c = (1 - s) * k_star^alpha),
    path = data.frame(t = periods, k = k, y = y, c = c, i = i)
  )
}

scenario_json <- function(item) {
  points <- vapply(seq_len(nrow(item$path)), function(index) {
    row <- item$path[index, ]
    json_object(c(
      json_field("t", json_number(row$t)),
      json_field("k", json_number(row$k)),
      json_field("y", json_number(row$y)),
      json_field("c", json_number(row$c)),
      json_field("i", json_number(row$i))
    ))
  }, character(1))
  json_object(c(
    json_field("id", json_string(item$id)),
    json_field("parameters", json_object(c(
      json_field("s", json_number(item$parameters$s)),
      json_field("delta", json_number(item$parameters$delta)),
      json_field("k0", json_number(item$parameters$k0))
    ))),
    json_field("steady_state", json_object(c(
      json_field("k", json_number(item$steady_state$k)),
      json_field("y", json_number(item$steady_state$y)),
      json_field("c", json_number(item$steady_state$c))
    ))),
    json_field("path", json_array(points))
  ))
}

scenario_grid <- expand.grid(s = s_values, delta = delta_values, k0 = k0_values)
scenarios <- lapply(seq_len(nrow(scenario_grid)), function(index) {
  scenario(scenario_grid$s[index], scenario_grid$delta[index], scenario_grid$k0[index])
})

baseline <- scenario(defaults$s, defaults$delta, defaults$k0)
expected_next <- ((1 - defaults$delta) * defaults$k0 + defaults$s * defaults$k0^alpha) / ((1 + n) * (1 + g))
stopifnot(
  nrow(baseline$path) == horizon + 1L,
  all(is.finite(as.matrix(baseline$path))),
  all(baseline$path$k > 0),
  abs(baseline$path$k[2] - expected_next) < 1e-12
)

payload <- json_object(c(
  json_field("title", json_string("Solow growth transition explorer")),
  json_field("model", json_object(c(
    json_field("alpha", json_number(alpha)),
    json_field("n", json_number(n)),
    json_field("g", json_number(g)),
    json_field("horizon", json_number(horizon)),
    json_field("law_of_motion", json_string("k_next = ((1-delta)*k + s*k^alpha) / ((1+n)*(1+g))"))
  ))),
  json_field("defaults", json_object(c(
    json_field("s", json_number(defaults$s)),
    json_field("delta", json_number(defaults$delta)),
    json_field("k0", json_number(defaults$k0))
  ))),
  json_field("values", json_object(c(
    json_field("s", json_array(vapply(s_values, json_number, character(1)))),
    json_field("delta", json_array(vapply(delta_values, json_number, character(1)))),
    json_field("k0", json_array(vapply(k0_values, json_number, character(1))))
  ))),
  json_field("scenarios", json_array(vapply(scenarios, scenario_json, character(1))))
))
writeLines(payload, file.path(data_dir, "solow-growth-scenarios.json"), useBytes = TRUE)

metadata <- json_object(c(
  json_field("title", json_string("Solow growth transition explorer")),
  json_field("generator", json_string("supplements/r/solow-growth.R")),
  json_field("runtime", json_string(paste("R", getRversion()))),
  json_field("units", json_string("per effective worker")),
  json_field("assumptions", json_object(c(
    json_field("production", json_string("y = k^alpha")),
    json_field("population_growth", json_number(n)),
    json_field("technology_growth", json_number(g)),
    json_field("alpha", json_number(alpha))
  ))),
  json_field("scenario_count", json_number(length(scenarios)))
))
writeLines(metadata, file.path(data_dir, "solow-growth-metadata.json"), useBytes = TRUE)

svg(file.path(image_dir, "solow-growth-static.svg"), width = 8, height = 4.7, pointsize = 11)
par(mar = c(4.2, 4.2, 2.4, 1.0), family = "sans")
plot(baseline$path$t, baseline$path$k, type = "l", lwd = 3, col = "#087e8b",
     xlab = "period", ylab = "capital per effective worker", main = "Solow transition: baseline")
abline(h = baseline$steady_state$k, lty = 2, lwd = 2, col = "#a16207")
legend("bottomright", legend = c("k_t", "steady state k*"), col = c("#087e8b", "#a16207"),
       lty = c(1, 2), lwd = c(3, 2), bty = "n")
dev.off()

message("Wrote ", length(scenarios), " scenarios, metadata, and static SVG.")
