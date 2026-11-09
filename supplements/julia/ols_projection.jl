# ols_projection.jl
# =============================================================================
# OLS Vector Space Geometry, Projection Operators, and FWL Subspace Decomposition
# =============================================================================
#
# Theoretical Foundation:
#   Observation space R^n, rank(X) = k
#   The Grand Equivalence:
#     \nabla_\beta S(\hat{\beta}) = 0   (Optimization in parameter space R^k)
#     \iff X' \hat{e} = 0               (Algebra: Normal equations)
#     \iff \hat{e} \perp \mathcal{C}(X)  (Geometry: Subspace orthogonality)
#     \iff \hat{y} = P_X y              (Projection operator P_X = X(X'X)^(-1)X')
#
# Exports:
#   - assets/data/ols-projection-metadata.json
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
# 1. Dual-Panel Geometry: n = 3, k = 2
# -----------------------------------------------------------------------------
println("Computing OLS projection geometry in R^3...")

ones3 = [1.0, 1.0, 1.0]
x_vec = [-1.0, 0.0, 1.0]
X = [ones3 x_vec]
y = [2.0, 1.0, 4.0]

# QR and backslash estimation
beta_hat = X \ y
y_hat = X * beta_hat
e_hat = y .- y_hat

# Verify orthogonality: X' e = 0
orthogonality_norm = norm(X' * e_hat, Inf)
@assert orthogonality_norm < 1e-12 "Normal equations X'e = 0 violated."

# Pythagorean decompositions
# Uncentered: ||y||^2 = ||y_hat||^2 + ||e_hat||^2
y_sq = dot(y, y)
y_hat_sq = dot(y_hat, y_hat)
e_hat_sq = dot(e_hat, e_hat)
@assert abs(y_sq - (y_hat_sq + e_hat_sq)) < 1e-12 "Uncentered Pythagorean identity violated."

# Centered: TSS = ESS + RSS
y_bar = sum(y) / length(y)
TSS = sum((y .- y_bar).^2)
ESS = sum((y_hat .- y_bar).^2)
RSS = sum(e_hat.^2)
@assert abs(TSS - (ESS + RSS)) < 1e-12 "Centered variance decomposition TSS = ESS + RSS violated."

R2 = ESS / TSS

println(@sprintf("Dual-Panel Model (n = 3, k = 2):"))
println(@sprintf("  beta_hat: [%.4f, %.4f] (exact: 7/3, 1)", beta_hat[1], beta_hat[2]))
println(@sprintf("  TSS: %.4f, ESS: %.4f, RSS: %.4f, R^2: %.4f (exact: 3/7)", TSS, ESS, RSS, R2))

# -----------------------------------------------------------------------------
# 2. Variable Addition & Nested Subspaces
# -----------------------------------------------------------------------------
# Intercept-only model X_0 = [1]
X0 = reshape(ones3, 3, 1)
beta_0 = X0 \ y
y_hat_0 = X0 * beta_0
e_hat_0 = y .- y_hat_0
RSS_0 = dot(e_hat_0, e_hat_0)
R2_0 = 0.0

# Model with slope X_1 = [1 x]
RSS_1 = RSS
R2_1 = R2
delta_RSS = RSS_0 - RSS_1
@assert abs(delta_RSS - ESS) < 1e-12 "Change in RSS must equal incremental ESS."

println(@sprintf("Nested Subspaces C(X_0) ⊂ C(X_1):"))
println(@sprintf("  X_0 (intercept only): RSS = %.4f (14/3), R^2 = %.4f", RSS_0, R2_0))
println(@sprintf("  X_1 (with slope):     RSS = %.4f (8/3),  R^2 = %.4f (3/7)", RSS_1, R2_1))
println(@sprintf("  RSS Reduction (ΔRSS): %.4f (= ESS)", delta_RSS))

# -----------------------------------------------------------------------------
# 3. Multicollinearity & Coordinate Stability Diagnostic
# -----------------------------------------------------------------------------
n_diag = 6
x1 = [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0]
v_dir = [1.0, -2.0, 1.0, 1.0, -2.0, 1.0]

delta_test = 0.01
x2_test = 2.0 .* x1 .+ delta_test .* v_dir
X_diag = [ones(n_diag) x1 x2_test]

kappa_X = cond(X_diag)
kappa_XX = cond(X_diag' * X_diag)

println(@sprintf("Multicollinearity Diagnostic (delta = %.4f):", delta_test))
println(@sprintf("  Condition number cond(X):   %.2f", kappa_X))
println(@sprintf("  Squared condition cond(X'X): %.2e", kappa_XX))

# -----------------------------------------------------------------------------
# 4. Save Metadata JSON
# -----------------------------------------------------------------------------
root = dirname(dirname(@__DIR__))
data_dir = joinpath(root, "assets", "data")
mkpath(data_dir)

metadata = (
    title = "OLS Vector Space Geometry, Normal Equations, and Projection Matrix",
    generator = "supplements/julia/ols_projection.jl",
    environment = (
        language = "Julia",
        version = string(VERSION)
    ),
    fig1_model = (
        n = 3,
        k = 2,
        X = [[1.0, -1.0], [1.0, 0.0], [1.0, 1.0]],
        y = [2.0, 1.0, 4.0],
        beta_hat = [beta_hat[1], beta_hat[2]],
        y_hat = [y_hat[1], y_hat[2], y_hat[3]],
        e_hat = [e_hat[1], e_hat[2], e_hat[3]],
        uncentered_decomposition = (
            y_sq = y_sq,
            y_hat_sq = y_hat_sq,
            e_hat_sq = e_hat_sq
        ),
        centered_decomposition = (
            TSS = TSS,
            ESS = ESS,
            RSS = RSS,
            R2 = R2
        )
    ),
    fig2_variable_addition = (
        X0_intercept_only = (
            RSS = RSS_0,
            R2 = R2_0
        ),
        X1_with_slope = (
            RSS = RSS_1,
            R2 = R2_1
        )
    ),
    fig3_multicollinearity = (
        n = n_diag,
        k = 3,
        x1 = x1,
        v = v_dir,
        delta_range = [0.0001, 1.0],
        perturbation_epsilon = 0.05
    )
)

out_json = joinpath(data_dir, "ols-projection-metadata.json")
open(out_json, "w") do f
    write(f, to_json(metadata))
end
println("Saved: $out_json")

println("OLS projection geometry generation finished successfully.")
