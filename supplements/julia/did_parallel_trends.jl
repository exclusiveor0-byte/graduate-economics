# did_parallel_trends.jl
# =============================================================================
# Difference-in-Differences (DiD) & Parallel Trends Simulation Explorer
# =============================================================================
#
# Model Setup:
#   Panel with N = 1000 entities (500 treated D=1, 500 control D=0)
#   T = 10 periods (t = 1..10, treatment occurs at t* = 6, k = t - 6 in -5..4)
#   Two-Way Fixed Effects (TWFE) with entity fixed effects α_i and time effects λ_t
#   Autocorrelated errors: ε_{i,t} = ρ ε_{i,t-1} + sqrt(1 - ρ^2) η_{i,t} (ρ = 0.40)
#
# Scenarios:
#   1. Parallel Trends Holds (δ = 0.00):
#      E[Y_{it}(0)] has identical time trend for both groups.
#   2. Mild Differential Trend Violation (δ = 0.25):
#      Treated group experiences an unobserved differential linear drift.
#   3. Severe Violation (δ = 0.60):
#      Pre-trends visibly diverge, causing massive bias in simple DiD.
#
# Exports:
#   - assets/data/did-event-study-baseline.csv
#   - assets/data/did-parallel-trends-metadata.json
#   - assets/images/did-parallel-trends-static.svg
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
# 1. Chi-squared and Standard Normal Tail Probabilities (for P-values)
# -----------------------------------------------------------------------------
# Standard normal CDF approximation (Abramowitz & Stegun 26.2.17, error < 7.5e-8)
function norm_cdf(x::Float64)::Float64
    if x < -8.0
        return 0.0
    elseif x > 8.0
        return 1.0
    end
    t = 1.0 / (1.0 + 0.2316419 * abs(x))
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    pdf = (1.0 / sqrt(2.0 * pi)) * exp(-0.5 * x^2)
    cdf = 1.0 - pdf * poly
    return (x >= 0.0) ? cdf : (1.0 - cdf)
end

function norm_p_value(z::Float64)::Float64
    return 2.0 * (1.0 - norm_cdf(abs(z)))
end

# Incomplete gamma function approximation for Chi-squared p-values
function p_value_chisq(stat::Float64, df::Int)::Float64
    if stat <= 0.0
        return 1.0
    end
    # Wilson-Hilferty transformation approximation for chi-sq p-value
    s = stat / df
    z = (s^(1.0/3.0) - (1.0 - 2.0 / (9.0 * df))) / sqrt(2.0 / (9.0 * df))
    return max(0.0, min(1.0, 1.0 - norm_cdf(z)))
end

# -----------------------------------------------------------------------------
# 2. Panel DGP Generator
# -----------------------------------------------------------------------------
struct PanelDGP
    N::Int
    T::Int
    t_star::Int       # Treatment onset (e.g., 6)
    ref_k::Int        # Reference relative event time to omit (e.g., -1)
    tau_dynamic::Vector{Float64} # Dynamic effects for k >= 0 (length = T - t_star + 1)
    rho::Float64      # AR(1) coefficient for error
    seed::Int
end

function generate_panel_data(dgp::PanelDGP, delta::Float64; rng=MersenneTwister(dgp.seed))
    N, T, t_star = dgp.N, dgp.T, dgp.t_star
    N_t = div(N, 2)   # 500 treated, 500 control
    
    # Treatment indicator D_i: 1 for first N_t, 0 for rest
    D = zeros(Float64, N)
    D[1:N_t] .= 1.0
    
    # Entity fixed effects α_i ~ N(0, 1)
    alpha = randn(rng, N)
    
    # Common time effects λ_t (macro trend)
    lambda = [0.35 * t + 0.1 * sin(t) for t in 1:T]
    
    # Panel arrays (flattened by entity then time)
    total_obs = N * T
    y = zeros(Float64, total_obs)
    entity_id = zeros(Int, total_obs)
    time_id = zeros(Int, total_obs)
    d_vec = zeros(Float64, total_obs)
    post_vec = zeros(Float64, total_obs)
    event_time_vec = zeros(Int, total_obs)
    
    # Pre-generate autocorrelated errors
    idx = 1
    for i in 1:N
        eps = 0.0
        for t in 1:T
            eta = randn(rng)
            if t == 1
                eps = eta
            else
                eps = dgp.rho * eps + sqrt(1.0 - dgp.rho^2) * eta
            end
            
            k = t - t_star
            # Baseline counterfactual trend
            y_base = alpha[i] + lambda[t]
            
            # Differential trend violation (treated group only)
            diff_trend = (D[i] == 1.0) ? delta * (t - 1) : 0.0
            
            # Dynamic treatment effect (only for treated in post-period)
            treatment_effect = 0.0
            if D[i] == 1.0 && k >= 0
                lag_idx = k + 1
                treatment_effect = dgp.tau_dynamic[lag_idx]
            end
            
            y[idx] = y_base + diff_trend + treatment_effect + eps
            entity_id[idx] = i
            time_id[idx] = t
            d_vec[idx] = D[i]
            post_vec[idx] = (t >= t_star) ? 1.0 : 0.0
            event_time_vec[idx] = k
            idx += 1
        end
    end
    
    return (y=y, entity_id=entity_id, time_id=time_id, D=d_vec, Post=post_vec, k=event_time_vec, N=N, T=T)
end

# -----------------------------------------------------------------------------
# 3. Two-Way Fixed Effects (TWFE) Event-Study Estimator
# -----------------------------------------------------------------------------
function estimate_event_study(data, ref_k::Int)
    y = data.y
    N, T = data.N, data.T
    total_obs = length(y)
    
    # Unique relative event times
    all_k = sort(unique(data.k))
    est_k = filter(k -> k != ref_k, all_k)
    K = length(est_k)
    
    # Regressors: Z_{it}^k = D_i * 1(k_t == k)
    Z = zeros(Float64, total_obs, K)
    for j in 1:K
        target_k = est_k[j]
        for obs in 1:total_obs
            if data.D[obs] == 1.0 && data.k[obs] == target_k
                Z[obs, j] = 1.0
            end
        end
    end
    
    # Within-transformation (absorb entity and time fixed effects)
    # ỹ_{it} = y_{it} - ȳ_i. - ȳ_.t + ȳ_..
    # Z̃_{it} = Z_{it} - Z̄_i. - Z̄_.t + Z̄_..
    y_entity_mean = zeros(Float64, N)
    y_time_mean = zeros(Float64, T)
    for obs in 1:total_obs
        i = data.entity_id[obs]
        t = data.time_id[obs]
        y_entity_mean[i] += y[obs] / T
        y_time_mean[t] += y[obs] / N
    end
    y_grand_mean = mean(y)
    
    Z_entity_mean = zeros(Float64, N, K)
    Z_time_mean = zeros(Float64, T, K)
    for obs in 1:total_obs
        i = data.entity_id[obs]
        t = data.time_id[obs]
        for j in 1:K
            Z_entity_mean[i, j] += Z[obs, j] / T
            Z_time_mean[t, j] += Z[obs, j] / N
        end
    end
    Z_grand_mean = [mean(Z[:, j]) for j in 1:K]
    
    y_tilde = zeros(Float64, total_obs)
    Z_tilde = zeros(Float64, total_obs, K)
    for obs in 1:total_obs
        i = data.entity_id[obs]
        t = data.time_id[obs]
        y_tilde[obs] = y[obs] - y_entity_mean[i] - y_time_mean[t] + y_grand_mean
        for j in 1:K
            Z_tilde[obs, j] = Z[obs, j] - Z_entity_mean[i, j] - Z_time_mean[t, j] + Z_grand_mean[j]
        end
    end
    
    # OLS coefficient vector: gamma_hat = (Z̃' Z̃)^{-1} Z̃' ỹ
    ZtZ = Z_tilde' * Z_tilde
    Zty = Z_tilde' * y_tilde
    gamma_hat = ZtZ \ Zty
    residuals = y_tilde - Z_tilde * gamma_hat
    
    # Clustered covariance matrix at entity level
    # V = (Z̃' Z̃)^{-1} [ \sum_{i=1}^N (Z̃_i' e_i) (Z̃_i' e_i)' ] (Z̃' Z̃)^{-1}
    meat = zeros(Float64, K, K)
    for i in 1:N
        row_range = ((i - 1) * T + 1):(i * T)
        Z_i = Z_tilde[row_range, :]
        e_i = residuals[row_range]
        score_i = Z_i' * e_i
        meat += score_i * score_i'
    end
    # Small-sample adjustment factor (N / (N - 1)) * ((NT - 1) / (NT - N - T - K + 1))
    dof_factor = (N / (N - 1))
    meat *= dof_factor
    
    inv_ZtZ = inv(ZtZ)
    vcov = inv_ZtZ * meat * inv_ZtZ
    se = sqrt.(max.(0.0, diag(vcov)))
    
    # Joint Chi-squared test for Pre-trends (k < -1)
    pre_indices = [j for j in 1:K if est_k[j] < ref_k]
    pre_stat = 0.0
    pre_pval = 1.0
    if !isempty(pre_indices)
        gamma_pre = gamma_hat[pre_indices]
        vcov_pre = vcov[pre_indices, pre_indices]
        pre_stat = dot(gamma_pre, vcov_pre \ gamma_pre)
        pre_pval = p_value_chisq(pre_stat, length(pre_indices))
    end
    
    return (est_k=est_k, gamma=gamma_hat, se=se, vcov=vcov, pre_stat=pre_stat, pre_pval=pre_pval)
end

# Simple 2x2 DiD estimator
function estimate_did_2x2(data)
    y = data.y
    D = data.D
    Post = data.Post
    total = length(y)
    
    # Means across 4 cells
    y11 = mean(y[(D .== 1.0) .& (Post .== 1.0)])
    y10 = mean(y[(D .== 1.0) .& (Post .== 0.0)])
    y01 = mean(y[(D .== 0.0) .& (Post .== 1.0)])
    y00 = mean(y[(D .== 0.0) .& (Post .== 0.0)])
    
    tau_did = (y11 - y10) - (y01 - y00)
    counterfactual = y10 + (y01 - y00)
    
    return (y11=y11, y10=y10, y01=y01, y00=y00, tau=tau_did, counterfactual=counterfactual)
end

# -----------------------------------------------------------------------------
# 4. Main Execution & Monte Carlo Simulation
# -----------------------------------------------------------------------------
const seed = 20261109
println("="^70)
println("Running DiD & Parallel Trends Simulation Suite (Seed: $seed)")
println("="^70)

# True parameter profile
# k = -5, -4, -3, -2, -1 (ref), 0, 1, 2, 3, 4
tau_dynamic = [1.00, 1.50, 2.00, 2.30, 2.50] # Dynamic lag effects for k >= 0
dgp = PanelDGP(1000, 10, 6, -1, tau_dynamic, 0.40, seed)

scenarios = [
    (id="parallel_valid", label="Parallel Trends Holds (δ = 0.00)", delta=0.00),
    (id="violation_mild", label="Mild Violation (δ = 0.25)", delta=0.25),
    (id="violation_severe", label="Severe Violation (δ = 0.60)", delta=0.60)
]

# Baseline Single-Sample Estimation
baseline_rows = String[]
push!(baseline_rows, "scenario_id,scenario_label,event_time,coef,se,ci_lower,ci_upper,p_value,is_pre,true_param")

meta_scenarios = Dict{String, Any}()

for sc in scenarios
    data = generate_panel_data(dgp, sc.delta; rng=MersenneTwister(seed))
    es = estimate_event_study(data, dgp.ref_k)
    did = estimate_did_2x2(data)
    
    println("\n[Scenario: $(sc.label)]")
    @printf("  2x2 DiD Estimate τ̂: %.4f (Counterfactual: %.4f)\n", did.tau, did.counterfactual)
    @printf("  Pre-trend Joint Test: χ² = %.3f, p-value = %.4f %s\n", 
            es.pre_stat, es.pre_pval, (es.pre_pval < 0.05 ? "❌ REJECT (Violation Detected)" : "✓ FAIL TO REJECT (Parallel Holds)"))
    
    # Store reference period k = -1 as normalized 0
    all_k = sort([es.est_k; dgp.ref_k])
    
    k_data = []
    for k in all_k
        if k == dgp.ref_k
            coef = 0.0
            se_k = 0.0
            ci_l = 0.0
            ci_u = 0.0
            pval = 1.0
            is_pre = true
            true_p = 0.0
        else
            idx = findfirst(==(k), es.est_k)
            coef = es.gamma[idx]
            se_k = es.se[idx]
            ci_l = coef - 1.96 * se_k
            ci_u = coef + 1.96 * se_k
            z_stat = coef / (se_k > 0 ? se_k : 1e-6)
            pval = norm_p_value(z_stat)
            is_pre = (k < dgp.ref_k)
            
            # True parameter: 0 for k < 0, dynamic for k >= 0, plus delta*(k - ref_k)
            # Note: with TWFE, differential linear trend delta appears as delta*(k - ref_k)
            base_effect = (k >= 0) ? dgp.tau_dynamic[k + 1] : 0.0
            trend_effect = sc.delta * (k - dgp.ref_k)
            true_p = base_effect + trend_effect
        end
        
        push!(baseline_rows, @sprintf("%s,\"%s\",%d,%.5f,%.5f,%.5f,%.5f,%.5f,%s,%.5f",
              sc.id, sc.label, k, coef, se_k, ci_l, ci_u, pval, is_pre ? "true" : "false", true_p))
        
        push!(k_data, (k=k, coef=round(coef, digits=4), se=round(se_k, digits=4), 
                       ci_lower=round(ci_l, digits=4), ci_upper=round(ci_u, digits=4), 
                       p_value=round(pval, digits=4), is_pre=is_pre))
    end
    
    meta_scenarios[sc.id] = (
        label=sc.label,
        delta=sc.delta,
        did_2x2=(
            y11=round(did.y11, digits=4),
            y10=round(did.y10, digits=4),
            y01=round(did.y01, digits=4),
            y00=round(did.y00, digits=4),
            tau_estimate=round(did.tau, digits=4),
            counterfactual=round(did.counterfactual, digits=4)
        ),
        pre_trend_test=(
            chi2_stat=round(es.pre_stat, digits=3),
            df=length(filter(<(dgp.ref_k), es.est_k)),
            p_value=round(es.pre_pval, digits=4),
            rejected_at_5pct=(es.pre_pval < 0.05)
        ),
        event_study=k_data
    )
end

# -----------------------------------------------------------------------------
# 5. Monte Carlo Simulation (1,000 replications)
# -----------------------------------------------------------------------------
const mc_reps = 1000
println("\nRunning Monte Carlo ($mc_reps replications per scenario)...")

mc_summary = Dict{String, Any}()

for sc in scenarios
    tau_samples = zeros(Float64, mc_reps)
    pre_rejections = 0
    ci_coverage_true = 0
    
    # We evaluate against average post-treatment effect = mean(tau_dynamic) = 1.86
    true_avg_att = mean(dgp.tau_dynamic)
    
    rng_mc = MersenneTwister(seed + 100)
    for rep in 1:mc_reps
        data = generate_panel_data(dgp, sc.delta; rng=rng_mc)
        did = estimate_did_2x2(data)
        es = estimate_event_study(data, dgp.ref_k)
        
        tau_samples[rep] = did.tau
        if es.pre_pval < 0.05
            pre_rejections += 1
        end
    end
    
    mean_tau = mean(tau_samples)
    std_tau = std(tau_samples)
    bias = mean_tau - true_avg_att
    rmse = sqrt(mean((tau_samples .- true_avg_att).^2))
    rejection_rate = pre_rejections / mc_reps
    
    @printf("  [%s]\n", sc.id)
    @printf("    Mean τ̂: %.4f (True ATT: %.4f, Bias: %+.4f)\n", mean_tau, true_avg_att, bias)
    @printf("    Std Dev: %.4f, RMSE: %.4f\n", std_tau, rmse)
    @printf("    Pre-trend Rejection Rate (α = 0.05): %.1f%%\n", rejection_rate * 100.0)
    
    mc_summary[sc.id] = (
        mean_tau=round(mean_tau, digits=4),
        true_att=round(true_avg_att, digits=4),
        bias=round(bias, digits=4),
        std_tau=round(std_tau, digits=4),
        rmse=round(rmse, digits=4),
        pre_test_rejection_rate=round(rejection_rate, digits=4)
    )
end

# -----------------------------------------------------------------------------
# 6. Save Data Files
# -----------------------------------------------------------------------------
root_dir = dirname(dirname(@__DIR__))
assets_data = joinpath(root_dir, "assets", "data")
assets_img = joinpath(root_dir, "assets", "images")
mkpath(assets_data)
mkpath(assets_img)

# 1. CSV Export
csv_path = joinpath(assets_data, "did-event-study-baseline.csv")
write(csv_path, join(baseline_rows, "\n") * "\n")
println("\n✓ Saved CSV: $csv_path")

# 2. Metadata JSON Export
meta_path = joinpath(assets_data, "did-parallel-trends-metadata.json")
metadata = (
    title="Difference-in-Differences and Parallel Trends Simulation",
    generated_at="2026-11-09",
    seed=seed,
    dgp=(
        N=dgp.N,
        T=dgp.T,
        t_star=dgp.t_star,
        ref_k=dgp.ref_k,
        rho=dgp.rho,
        tau_dynamic=dgp.tau_dynamic,
        true_att_mean=round(mean(dgp.tau_dynamic), digits=4)
    ),
    scenarios=meta_scenarios,
    monte_carlo_1000=mc_summary
)
write(meta_path, to_json(metadata))
println("✓ Saved JSON Metadata: $meta_path")

# -----------------------------------------------------------------------------
# 7. Generate Static High-Resolution SVG Diagram
# -----------------------------------------------------------------------------
svg_path = joinpath(assets_img, "did-parallel-trends-static.svg")

# Clean editorial SVG showing 2x2 DiD geometry and counterfactual
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" width="100%" height="100%">
  <defs>
    <style>
      .bg { fill: #fcf9f2; }
      .grid { stroke: #e5ded3; stroke-width: 1; stroke-dasharray: 4,4; }
      .axis { stroke: #2d251e; stroke-width: 2; }
      .text-title { font-family: 'Pretendard', 'Segoe UI', sans-serif; font-size: 18px; font-weight: 700; fill: #2d251e; }
      .text-sub { font-family: 'Pretendard', 'Segoe UI', sans-serif; font-size: 13px; fill: #75665b; }
      .text-axis { font-family: 'Pretendard', 'Segoe UI', sans-serif; font-size: 14px; font-weight: 600; fill: #2d251e; }
      .text-label { font-family: 'Pretendard', 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600; }
      .line-treat { stroke: #087e8b; stroke-width: 3.5; fill: none; }
      .line-control { stroke: #75665b; stroke-width: 3.5; fill: none; }
      .line-counter { stroke: #087e8b; stroke-width: 2.5; stroke-dasharray: 6,6; fill: none; }
      .line-diff { stroke: #c0392b; stroke-width: 2; marker-start: url(#arrow-up); marker-end: url(#arrow-down); }
      .pt-treat { fill: #087e8b; stroke: #fcf9f2; stroke-width: 2; }
      .pt-control { fill: #75665b; stroke: #fcf9f2; stroke-width: 2; }
      .pt-counter { fill: #ffffff; stroke: #087e8b; stroke-width: 2.5; }
      .box-att { fill: #fcedec; stroke: #c0392b; stroke-width: 1.5; rx: 6; }
    </style>
    <marker id="arrow-down" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#c0392b"/>
    </marker>
    <marker id="arrow-up" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 10 0 L 0 5 L 10 10 z" fill="#c0392b"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="900" height="520" class="bg"/>

  <!-- Title & Subtitle -->
  <text x="50" y="45" class="text-title">이중차분법(DiD)의 기하학: 반사실적(Counterfactual) 궤적과 ATT 식별</text>
  <text x="50" y="70" class="text-sub">평행추세 가정이 성립할 때 통제집단의 전후 변화를 이용해 처치집단의 가상적 미처치 궤적을 복원한다</text>

  <!-- Axes -->
  <line x1="120" y1="440" x2="820" y2="440" class="axis"/>
  <line x1="120" y1="100" x2="120" y2="440" class="axis"/>

  <!-- Grid lines -->
  <line x1="280" y1="100" x2="280" y2="440" class="grid"/>
  <line x1="660" y1="100" x2="660" y2="440" class="grid"/>
  <line x1="120" y1="360" x2="820" y2="360" class="grid"/>
  <line x1="120" y1="280" x2="820" y2="280" class="grid"/>
  <line x1="120" y1="200" x2="820" y2="200" class="grid"/>
  <line x1="120" y1="130" x2="820" y2="130" class="grid"/>

  <!-- Axis Labels -->
  <text x="280" y="470" text-anchor="middle" class="text-axis">사전 시점 (Post = 0)</text>
  <text x="660" y="470" text-anchor="middle" class="text-axis">사후 시점 (Post = 1)</text>
  <text x="470" y="500" text-anchor="middle" class="text-sub">시점 t (정책 개입 발생: t*)</text>
  <text x="70" y="270" text-anchor="middle" transform="rotate(-90 70 270)" class="text-axis">결과변수 Y</text>

  <!-- Intervention Line -->
  <line x1="470" y1="100" x2="470" y2="440" stroke="#b46f45" stroke-width="2" stroke-dasharray="5,5"/>
  <text x="475" y="120" fill="#b46f45" font-family="'Pretendard', sans-serif" font-size="12px" font-weight="700">정책 개입 시점 (t*)</text>

  <!-- Coordinates:
       Treated: Pre(280, 260) -> Post(660, 130)
       Control: Pre(280, 380) -> Post(660, 300)
       Counterfactual for Treated: Pre(280, 260) -> Post(660, 180)  [dy = -80, same as control]
  -->
  
  <!-- Trend Lines -->
  <!-- Control Group Line -->
  <line x1="280" y1="380" x2="660" y2="300" class="line-control"/>
  <!-- Counterfactual Line (Parallel) -->
  <line x1="280" y1="260" x2="660" y2="180" class="line-counter"/>
  <!-- Treated Group Observed Line -->
  <line x1="280" y1="260" x2="660" y2="130" class="line-treat"/>

  <!-- Vertical Brackets / ATT Indicator -->
  <line x1="660" y1="135" x2="660" y2="175" class="line-diff"/>

  <!-- Data Points -->
  <!-- Control Points -->
  <circle cx="280" cy="380" r="6" class="pt-control"/>
  <circle cx="660" cy="300" r="6" class="pt-control"/>

  <!-- Treated Points -->
  <circle cx="280" cy="260" r="6" class="pt-treat"/>
  <circle cx="660" cy="130" r="6" class="pt-treat"/>

  <!-- Counterfactual Point -->
  <circle cx="660" cy="180" r="6" class="pt-counter"/>

  <!-- Point Annotations -->
  <text x="265" y="385" text-anchor="end" class="text-label" fill="#75665b">E[Y₀₀]</text>
  <text x="680" y="305" text-anchor="start" class="text-label" fill="#75665b">E[Y₀₁] (통제 관측치)</text>

  <text x="265" y="265" text-anchor="end" class="text-label" fill="#087e8b">E[Y₁₀]</text>
  <text x="680" y="130" text-anchor="start" class="text-label" fill="#087e8b">E[Y₁₁] (처치 관측치)</text>

  <text x="680" y="185" text-anchor="start" class="text-label" fill="#087e8b">E[Y₁₁(0)] = E[Y₁₀] + ΔY₀ (반사실적)</text>

  <!-- ATT Callout Box -->
  <g transform="translate(690, 140)">
    <rect width="170" height="50" class="box-att"/>
    <text x="85" y="22" text-anchor="middle" fill="#c0392b" font-family="'Pretendard', sans-serif" font-size="12px" font-weight="700">처치 효과 (ATT: τ)</text>
    <text x="85" y="38" text-anchor="middle" fill="#c0392b" font-family="'Pretendard', sans-serif" font-size="11px">E[Y₁₁] - E[Y₁₁(0)]</text>
  </g>

  <!-- Parallel slope explanation -->
  <g transform="translate(340, 310)">
    <text x="0" y="0" fill="#75665b" font-family="'Pretendard', sans-serif" font-size="12px" font-style="italic">자연적 시간 추세 (ΔY₀ = E[Y₀₁] - E[Y₀₀])</text>
    <path d="M 20 10 L 80 -8" stroke="#75665b" stroke-width="1" fill="none" marker-end="url(#arrow-down)"/>
  </g>

  <!-- Legend Box -->
  <g transform="translate(140, 120)">
    <rect width="210" height="90" fill="#ffffff" stroke="#e5ded3" stroke-width="1.5" rx="4"/>
    <line x1="15" y1="22" x2="45" y2="22" class="line-treat"/>
    <circle cx="30" cy="22" r="4" class="pt-treat"/>
    <text x="55" y="26" class="text-sub" font-weight="600">처치집단 실제 관측선</text>

    <line x1="15" y1="47" x2="45" y2="47" class="line-counter"/>
    <circle cx="30" cy="47" r="4" class="pt-counter"/>
    <text x="55" y="51" class="text-sub" font-weight="600">반사실적 잠재 추세선</text>

    <line x1="15" y1="72" x2="45" y2="72" class="line-control"/>
    <circle cx="30" cy="72" r="4" class="pt-control"/>
    <text x="55" y="76" class="text-sub" font-weight="600">통제집단 실제 관측선</text>
  </g>
</svg>
"""

write(svg_path, svg_content)
println("✓ Saved SVG: $svg_path")

println("\n" * "="^70)
println("DiD & Parallel Trends Suite execution complete!")
println("="^70)
