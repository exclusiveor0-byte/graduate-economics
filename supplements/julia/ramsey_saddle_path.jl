# ramsey_saddle_path.jl
# =============================================================================
# Ramsey–Cass–Koopmans Model Saddle Path Dynamics & Shooting Algorithm
# =============================================================================
#
# Model Formulation (per effective worker):
#   Capital accumulation: \dot{k} = k^\alpha - c - x k,   where x = \delta + n + g
#   Euler equation:       \dot{c} = (c / \theta) [ \alpha k^{\alpha - 1} - (\rho + \delta + \theta g) ]
#
# Features:
#   1. Steady-state characterization (baseline E_0, post-shock E_1, Golden Rule E_GR)
#   2. Local linearization, Jacobian matrix, saddle eigenvalue decomposition (\lambda_1 < 0 < \lambda_2)
#   3. Global nonlinear saddle path via Reverse-Time RK4 integration (\tau = -t)
#   4. Jump in consumption c(0+) and vertical drop \Delta c following permanent drop in \rho
#
# Exports:
#   - assets/data/ramsey-saddle-path-metadata.json
# =============================================================================

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
# 1. Model Parameters
# -----------------------------------------------------------------------------
const α = 0.33
const θ = 2.0
const n = 0.01
const g = 0.02
const δ = 0.05
const x_deprec = δ + n + g     # Effective capital dilution x = 0.08
const ρ_base = 0.04           # Baseline rate of time preference
const ρ_shock = 0.02          # Post-shock discount rate (patient economy)

# -----------------------------------------------------------------------------
# 2. Steady-State Calculations
# -----------------------------------------------------------------------------
# Production and marginal product
f(k) = k^α
f_prime(k) = α * k^(α - 1.0)
f_double_prime(k) = α * (α - 1.0) * k^(α - 2.0)

# Golden Rule: f'(k_GR) = x = 0.08
const k_GR = (α / x_deprec)^(1.0 / (1.0 - α))
const c_GR = f(k_GR) - x_deprec * k_GR

# Baseline Steady State E_0: f'(k_0*) = rho_base + delta + theta * g = 0.13
const denom0 = ρ_base + δ + θ * g
const k0_star = (α / denom0)^(1.0 / (1.0 - α))
const c0_star = f(k0_star) - x_deprec * k0_star
const y0_star = f(k0_star)
const s0_star = x_deprec * k0_star / y0_star

# Post-Shock Steady State E_1: f'(k_1*) = rho_shock + delta + theta * g = 0.11
const denom1 = ρ_shock + δ + θ * g
const k1_star = (α / denom1)^(1.0 / (1.0 - α))
const c1_star = f(k1_star) - x_deprec * k1_star
const y1_star = f(k1_star)
const s1_star = x_deprec * k1_star / y1_star

# -----------------------------------------------------------------------------
# 3. Local Linearization & Saddle Eigendecomposition at E_0 & E_1
# -----------------------------------------------------------------------------
function get_jacobian_and_eigen(k_ss::Float64, c_ss::Float64, rho_val::Float64)
    j11 = rho_val + (θ - 1.0) * g - n
    j12 = -1.0
    j21 = (c_ss / θ) * α * (α - 1.0) * k_ss^(α - 2.0)
    j22 = 0.0

    J = [j11 j12; j21 j22]
    evals = eigen(J)

    idx = sortperm(real(evals.values))
    lam_stable = real(evals.values[idx[1]])
    lam_unstable = real(evals.values[idx[2]])

    v_st = real(evals.vectors[:, idx[1]])
    if v_st[1] < 0
        v_st .= -v_st
    end
    v_st ./= norm(v_st)

    return J, lam_stable, lam_unstable, v_st
end

J0, lambda0_stable, lambda0_unstable, v0_stable = get_jacobian_and_eigen(k0_star, c0_star, ρ_base)
J1, lambda1_stable, lambda1_unstable, v1_stable = get_jacobian_and_eigen(k1_star, c1_star, ρ_shock)

@assert lambda0_stable < 0.0 "Baseline stable eigenvalue must be negative."
@assert lambda0_unstable > 0.0 "Baseline unstable eigenvalue must be positive."

println("Ramsey–Cass–Koopmans Steady-State Analysis:")
println(@sprintf("  Golden Rule:  k_GR = %.4f, c_GR = %.4f", k_GR, c_GR))
println(@sprintf("  Baseline E0:  k* = %.6f, c* = %.6f, s* = %.4f", k0_star, c0_star, s0_star))
println(@sprintf("  Post-Shock E1: k* = %.6f, c* = %.6f, s* = %.4f", k1_star, c1_star, s1_star))
println(@sprintf("  Eigenvalues:  λ₁ = %.6f (stable), λ₂ = %.6f (unstable)", lambda0_stable, lambda0_unstable))
println(@sprintf("  Stable Eigenvector: [%.6f, %.6f]", v0_stable[1], v0_stable[2]))

# -----------------------------------------------------------------------------
# 4. Reverse-Time RK4 Integration for Global Saddle Path
# -----------------------------------------------------------------------------
# System: \dot{y} = F(y)
# In reverse time \tau = -t: dy/d\tau = -F(y)
function rk4_reverse_step(y::Vector{Float64}, dt::Float64, denom_val::Float64)
    # y = [k, c]
    function odefun(state)
        k, c = state[1], state[2]
        k_dot = k^α - c - x_deprec * k
        c_dot = (c / θ) * (α * k^(α - 1.0) - denom_val)
        return -[k_dot, c_dot]
    end

    k1 = odefun(y)
    k2 = odefun(y .+ 0.5 .* dt .* k1)
    k3 = odefun(y .+ 0.5 .* dt .* k2)
    k4 = odefun(y .+ dt .* k3)

    return y .+ (dt / 6.0) .* (k1 .+ 2.0 .* k2 .+ 2.0 .* k3 .+ k4)
end

function compute_saddle_path(k_ss::Float64, c_ss::Float64, denom_val::Float64, v_st::Vector{Float64})
    eps_init = 1e-2
    dt = 0.01
    max_steps = 8000

    # Branch 1: Leftward (k < k_ss)
    yL = [[k_ss - eps_init * v_st[1], c_ss - eps_init * v_st[2]]]
    for _ in 1:max_steps
        y_next = rk4_reverse_step(yL[end], dt, denom_val)
        # Event: stop if k < 0.20 or c < 0.05 or k > 9.5
        if y_next[1] < 0.20 || y_next[2] < 0.05 || y_next[1] > 9.5
            break
        end
        push!(yL, y_next)
    end

    # Branch 2: Rightward (k > k_ss)
    yR = [[k_ss + eps_init * v_st[1], c_ss + eps_init * v_st[2]]]
    for _ in 1:max_steps
        y_next = rk4_reverse_step(yR[end], dt, denom_val)
        if y_next[1] < 0.20 || y_next[2] < 0.05 || y_next[1] > 9.5
            break
        end
        push!(yR, y_next)
    end

    # Combine branches sorted by capital k
    k_all = Float64[]
    c_all = Float64[]
    for pt in reverse(yL)
        push!(k_all, pt[1])
        push!(c_all, pt[2])
    end
    push!(k_all, k_ss)
    push!(c_all, c_ss)
    for pt in yR
        push!(k_all, pt[1])
        push!(c_all, pt[2])
    end

    return k_all, c_all
end

# Linear interpolation helper
function interpolate_saddle(k_grid::Vector{Float64}, c_grid::Vector{Float64}, k_target::Float64)::Float64
    idx = searchsortedlast(k_grid, k_target)
    if idx == 0
        return c_grid[1]
    elseif idx >= length(k_grid)
        return c_grid[end]
    end
    k_low, k_high = k_grid[idx], k_grid[idx + 1]
    c_low, c_high = c_grid[idx], c_grid[idx + 1]
    weight = (k_target - k_low) / (k_high - k_low)
    return c_low + weight * (c_high - c_low)
end

k_saddle0, c_saddle0 = compute_saddle_path(k0_star, c0_star, denom0, v0_stable)
k_saddle1, c_saddle1 = compute_saddle_path(k1_star, c1_star, denom1, v1_stable)

# Consumption jump upon discount rate shock (predetermined k0_star)
c_shock_jump = interpolate_saddle(k_saddle1, c_saddle1, k0_star)
delta_c = c_shock_jump - c0_star

println(@sprintf("Comparative Dynamics (rho: 0.04 -> 0.02):"))
println(@sprintf("  Predetermined k(0):     %.6f", k0_star))
println(@sprintf("  Pre-shock c(0-):        %.6f", c0_star))
println(@sprintf("  Jump consumption c(0+): %.6f", c_shock_jump))
println(@sprintf("  Vertical Jump Δc:       %.6f (Drop ~ %.2f%% to save more)", delta_c, abs(delta_c) / c0_star * 100))

# -----------------------------------------------------------------------------
# 5. Save Metadata JSON
# -----------------------------------------------------------------------------
root = dirname(dirname(@__DIR__))
data_dir = joinpath(root, "assets", "data")
mkpath(data_dir)

metadata = (
    title = "Ramsey-Cass-Koopmans Model Saddle Path Dynamics & Shooting Algorithm",
    generator = "supplements/julia/ramsey_saddle_path.jl",
    julia_version = "Julia $(VERSION)",
    parameters = (
        alpha = α,
        theta = θ,
        n = n,
        g = g,
        delta = δ,
        effective_depreciation_x = x_deprec,
        rho_baseline = ρ_base,
        rho_shock = ρ_shock
    ),
    steady_states = (
        baseline = (
            k_star = k0_star,
            c_star = c0_star,
            output_y = y0_star,
            saving_rate = s0_star,
            stable_eigenvalue = lambda0_stable,
            unstable_eigenvalue = lambda0_unstable,
            stable_eigenvector = [v0_stable[1], v0_stable[2]]
        ),
        post_shock = (
            k_star = k1_star,
            c_star = c1_star,
            output_y = y1_star,
            saving_rate = s1_star
        ),
        golden_rule = (
            k_GR = k_GR,
            c_GR = c_GR
        )
    ),
    comparative_dynamics = (
        shock_type = "Permanent drop in discount rate rho from 0.04 to 0.02",
        predetermined_capital_k0 = k0_star,
        pre_shock_consumption = c0_star,
        jump_consumption_c_t0_plus = c_shock_jump,
        vertical_jump_delta_c = delta_c,
        long_run_capital_change = k1_star - k0_star,
        long_run_consumption_change = c1_star - c0_star
    )
)

out_json = joinpath(data_dir, "ramsey-saddle-path-metadata.json")
open(out_json, "w") do f
    write(f, to_json(metadata))
end
println("Saved: $out_json")

println("Ramsey saddle path generation finished successfully.")
