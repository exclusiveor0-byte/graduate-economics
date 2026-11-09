# ols_geometry.jl
# =============================================================================
# OLS Geometry, Residual Orthogonality, and Fixed-X Sampling Distribution
# =============================================================================
#
# Model Setup:
#   y_i = \beta_0 + \beta_1 x_i + u_i,   \beta_0 = 1.00, \beta_1 = 1.40, \sigma = 0.80
#
# Geometry:
#   OLS solves the orthogonal projection of y onto \mathcal{C}(X).
#   Residual vector \hat{e} satisfies X' \hat{e} = 0 (orthogonality to column space).
#   Fixed-X Monte Carlo confirms Gauss–Markov sampling variance and BLUE property.
#
# Exports:
#   - assets/data/ols-geometry-baseline.csv
#   - assets/data/ols-geometry-metadata.json
# =============================================================================

using Random
using Statistics
using LinearAlgebra
using Printf

# -----------------------------------------------------------------------------
# 0. JSON Serializer (Stdlib / Zero-Dependency)
# -----------------------------------------------------------------------------
function to_json(val)
    if val === nothing
        return "null"
    elseif val isa Bool
        return val ? "true" : "false"
    elseif val isa Real
        if isnan(val) || isinf(val)
            error("Cannot serialize NaN or Inf to JSON")
        end
        return string(val)
    elseif val isa AbstractString
        escaped = replace(val, "\\" => "\\\\", "\"" => "\\\"", "\n" => "\\n", "\r" => "\\r", "\t" => "\\t")
        return "\"$escaped\""
    elseif val isa AbstractVector
        return "[" * join([to_json(x) for x in val], ",") * "]"
    elseif val isa AbstractDict || val isa NamedTuple
        entries = String[]
        for (k, v) in pairs(val)
            push!(entries, "\"$(string(k))\":" * to_json(v))
        end
        return "{" * join(entries, ",") * "}"
    else
        error("Unsupported JSON type: $(typeof(val))")
    end
end

# -----------------------------------------------------------------------------
# 1. Baseline Data-Generating Process & OLS Estimation
# -----------------------------------------------------------------------------
const seed = 20260916
const rng = MersenneTwister(seed)

const n = 40
const β_0 = 1.00
const β_1 = 1.40
const σ = 0.80
const replications = 1500

# Fixed regressor X with noise
x = collect(range(-2.0, 2.0, length=n)) .+ 0.15 .* randn(rng, n)
u = σ .* randn(rng, n)
y = β_0 .+ β_1 .* x .+ u
X = [ones(n) x]

# OLS Estimation via QR / Backslash
beta_hat = X \ y
y_hat = X * beta_hat
residual = y .- y_hat
sse = dot(residual, residual)
k_params = size(X, 2)
sigma_hat = sqrt(sse / (n - k_params))
vcov_hat = sigma_hat^2 * inv(X' * X)
se_beta_1 = sqrt(vcov_hat[2, 2])

# Verify exact residual orthogonality: X' e = 0
orthogonality_error = norm(X' * residual, Inf)
@assert orthogonality_error < 1e-10 "OLS residuals must be strictly orthogonal to X."

println(@sprintf("Baseline OLS Estimation (n = %d, k = %d):", n, k_params))
println(@sprintf("  beta_0_hat:          %.6f (true = %.2f)", beta_hat[1], β_0))
println(@sprintf("  beta_1_hat:          %.6f (true = %.2f)", beta_hat[2], β_1))
println(@sprintf("  se(beta_1):          %.6f", se_beta_1))
println(@sprintf("  SSE:                 %.6f, s = %.6f", sse, sigma_hat))
println(@sprintf("  Orthogonality error: %.3e (max |X'e|)", orthogonality_error))

# -----------------------------------------------------------------------------
# 2. Fixed-X Monte Carlo Simulation
# -----------------------------------------------------------------------------
println(@sprintf("Running Fixed-X Monte Carlo simulation (%d draws)...", replications))

beta_1_draws = Vector{Float64}(undef, replications)
for r in 1:replications
    y_draw = β_0 .+ β_1 .* x .+ σ .* randn(rng, n)
    beta_draw = X \ y_draw
    beta_1_draws[r] = beta_draw[2]
end

@assert all(isfinite, beta_1_draws) "Monte Carlo draws must be finite."

mean_b1 = mean(beta_1_draws)
sd_b1 = std(beta_1_draws)
theoretical_sd = σ * sqrt(inv(X' * X)[2, 2])

println(@sprintf("Monte Carlo Results:"))
println(@sprintf("  Empirical mean beta_1: %.6f (bias = %.4e)", mean_b1, mean_b1 - β_1))
println(@sprintf("  Empirical sd beta_1:   %.6f (theory = %.6f)", sd_b1, theoretical_sd))

# -----------------------------------------------------------------------------
# 3. Save Assets
# -----------------------------------------------------------------------------
root = dirname(dirname(@__DIR__))
data_dir = joinpath(root, "assets", "data")
mkpath(data_dir)

# Save Baseline CSV
baseline_csv = joinpath(data_dir, "ols-geometry-baseline.csv")
open(baseline_csv, "w") do f
    println(f, "x,y,y_hat,residual")
    for i in 1:n
        @printf(f, "%.6f,%.6f,%.6f,%.6f\n", x[i], y[i], y_hat[i], residual[i])
    end
end
println("Saved: $baseline_csv")

# Save Metadata JSON
metadata = (
    title = "OLS geometry and sampling explorer",
    generator = "supplements/julia/ols_geometry.jl",
    julia_version = "Julia $(VERSION)",
    seed = seed,
    sample_size = n,
    replications = replications,
    model = (
        beta_0 = β_0,
        beta_1 = β_1,
        sigma = σ
    ),
    baseline = (
        beta_0_hat = beta_hat[1],
        beta_1_hat = beta_hat[2],
        se_beta_1 = se_beta_1,
        sse = sse,
        orthogonality_error = orthogonality_error
    ),
    monte_carlo = (
        mean_beta_1_hat = mean_b1,
        sd_beta_1_hat = sd_b1
    )
)

metadata_json = joinpath(data_dir, "ols-geometry-metadata.json")
open(metadata_json, "w") do f
    write(f, to_json(metadata))
end
println("Saved: $metadata_json")

println("OLS geometry generation finished successfully.")
