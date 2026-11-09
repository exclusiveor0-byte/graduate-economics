# iv_weak_instruments.jl
# =============================================================================
# Instrumental Variables (IV) & Weak Instruments Simulation Explorer
# =============================================================================
#
# Model Setup:
#   Structural:  y_i = \beta x_i + u_i,        \beta = 1.00
#   First-Stage: x_i = \pi z_i + v_i,          \pi = 0.70
#   Error:       u_i = \rho v_i + \sqrt{1 - \rho^2} e_i,  \rho = 0.60
#   Endogeneity arises because Cov(x_i, u_i) = \rho > 0.
#   Instrument z_i is strictly exogenous: Cov(z_i, u_i) = 0.
#
# Exports:
#   - assets/data/iv-weak-instruments-baseline.csv
#   - assets/data/iv-weak-instruments-metadata.json
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
# 1. Estimator Functions
# -----------------------------------------------------------------------------
function slope_with_intercept(a::Vector{Float64}, response::Vector{Float64})::Float64
    centered_a = a .- mean(a)
    return dot(centered_a, response .- mean(response)) / dot(centered_a, centered_a)
end

function iv_slope(instrument::Vector{Float64}, regressor::Vector{Float64}, response::Vector{Float64})::Float64
    centered_z = instrument .- mean(instrument)
    return dot(centered_z, response .- mean(response)) / dot(centered_z, regressor .- mean(regressor))
end

function first_stage_f(instrument::Vector{Float64}, regressor::Vector{Float64})::Float64
    b = slope_with_intercept(instrument, regressor)
    fitted = mean(regressor) .+ b .* (instrument .- mean(instrument))
    explained = sum((fitted .- mean(regressor)).^2)
    residual = sum((regressor .- fitted).^2)
    return explained / (residual / (length(regressor) - 2))
end

# -----------------------------------------------------------------------------
# 2. Baseline Sample Generation & Estimation
# -----------------------------------------------------------------------------
const seed = 20260917
const rng = MersenneTwister(seed)

const n = 150
const β = 1.00
const π_strength = 0.70
const ρ = 0.60
const replications = 2000

# Generate baseline sample
z = randn(rng, n)
v = randn(rng, n)
e = randn(rng, n)
u = ρ .* v .+ sqrt(1.0 - ρ^2) .* e
x = π_strength .* z .+ v
y = β .* x .+ u

ols_hat = slope_with_intercept(x, y)
iv_hat = iv_slope(z, x, y)
first_stage_pi = slope_with_intercept(z, x)
f_stat = first_stage_f(z, x)

println(@sprintf("Baseline Estimates (n = %d):", n))
println(@sprintf("  OLS beta_hat:       %.6f (Biased upward by rho = %.2f)", ols_hat, ρ))
println(@sprintf("  2SLS beta_hat:      %.6f (Consistent around beta = %.2f)", iv_hat, β))
println(@sprintf("  First-stage pi_hat: %.6f, F-stat: %.3f", first_stage_pi, f_stat))

# -----------------------------------------------------------------------------
# 3. Monte Carlo Simulation
# -----------------------------------------------------------------------------
println(@sprintf("Running Monte Carlo simulation (%d replications)...", replications))

ols_draws = Vector{Float64}(undef, replications)
iv_draws = Vector{Float64}(undef, replications)

for r in 1:replications
    z_draw = randn(rng, n)
    v_draw = randn(rng, n)
    e_draw = randn(rng, n)
    u_draw = ρ .* v_draw .+ sqrt(1.0 - ρ^2) .* e_draw
    x_draw = π_strength .* z_draw .+ v_draw
    y_draw = β .* x_draw .+ u_draw

    ols_draws[r] = slope_with_intercept(x_draw, y_draw)
    iv_draws[r] = iv_slope(z_draw, x_draw, y_draw)
end

@assert all(isfinite, ols_draws) "OLS draws must be finite."
@assert all(isfinite, iv_draws) "2SLS draws must be finite."

mean_ols = mean(ols_draws)
sd_ols = std(ols_draws)
mean_iv = mean(iv_draws)
sd_iv = std(iv_draws)

println(@sprintf("Monte Carlo Results:"))
println(@sprintf("  OLS:  mean = %.6f, sd = %.6f", mean_ols, sd_ols))
println(@sprintf("  2SLS: mean = %.6f, sd = %.6f", mean_iv, sd_iv))

# -----------------------------------------------------------------------------
# 4. Save Assets
# -----------------------------------------------------------------------------
root = dirname(dirname(@__DIR__))
data_dir = joinpath(root, "assets", "data")
mkpath(data_dir)

# Save Baseline CSV
baseline_csv = joinpath(data_dir, "iv-weak-instruments-baseline.csv")
open(baseline_csv, "w") do f
    println(f, "z,x,y,u")
    for i in 1:n
        @printf(f, "%.6f,%.6f,%.6f,%.6f\n", z[i], x[i], y[i], u[i])
    end
end
println("Saved: $baseline_csv")

# Save Metadata JSON
metadata = (
    title = "IV and weak instruments explorer",
    generator = "supplements/julia/iv_weak_instruments.jl",
    julia_version = "Julia $(VERSION)",
    seed = seed,
    sample_size = n,
    replications = replications,
    model = (
        beta = β,
        pi_strength = π_strength,
        rho = ρ
    ),
    baseline = (
        ols_beta_hat = ols_hat,
        iv_beta_hat = iv_hat,
        first_stage_pi_hat = first_stage_pi,
        first_stage_f = f_stat
    ),
    monte_carlo = (
        mean_ols_hat = mean_ols,
        mean_iv_hat = mean_iv,
        sd_ols_hat = sd_ols,
        sd_iv_hat = sd_iv
    )
)

metadata_json = joinpath(data_dir, "iv-weak-instruments-metadata.json")
open(metadata_json, "w") do f
    write(f, to_json(metadata))
end
println("Saved: $metadata_json")

println("IV and weak instruments generation finished successfully.")
