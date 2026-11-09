# solow_growth.jl
# =============================================================================
# Solow–Swan Growth Transition Scenario Generator
# =============================================================================
#
# Generates discrete-time transition paths for 36 parameter scenarios of the
# Solow–Swan neoclassical growth model per unit of effective labor:
#   k_{t+1} = ((1 - \delta) k_t + s k_t^\alpha) / ((1 + n)(1 + g))
#
# Exports:
#   - assets/data/solow-growth-scenarios.json
#   - assets/data/solow-growth-metadata.json
#   - assets/images/solow-growth-static.svg
# =============================================================================

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
# 1. Model Setup and Parameters
# -----------------------------------------------------------------------------
const α = 0.33
const n = 0.01
const g = 0.02
const horizon = 40

const s_values = [0.18, 0.22, 0.26, 0.30]
const δ_values = [0.04, 0.06, 0.08]
const k0_values = [0.50, 1.00, 2.00]

const default_s = 0.22
const default_δ = 0.06
const default_k0 = 0.50

# -----------------------------------------------------------------------------
# 2. Simulation Logic
# -----------------------------------------------------------------------------
struct SolowScenario
    id::String
    parameters::NamedTuple
    steady_state::NamedTuple
    path::Vector{NamedTuple}
end

function simulate_scenario(s::Float64, δ::Float64, k0::Float64)::SolowScenario
    dilution = (1.0 + n) * (1.0 + g) - (1.0 - δ)
    k_star = (s / dilution)^(1.0 / (1.0 - α))
    y_star = k_star^α
    c_star = (1.0 - s) * y_star

    path = Vector{NamedTuple}(undef, horizon + 1)
    k_curr = k0

    for t in 0:horizon
        y_curr = k_curr^α
        i_curr = s * y_curr
        c_curr = (1.0 - s) * y_curr
        path[t + 1] = (t = t, k = round(k_curr, digits=6), y = round(y_curr, digits=6),
                       c = round(c_curr, digits=6), i = round(i_curr, digits=6))
        if t < horizon
            k_curr = ((1.0 - δ) * k_curr + i_curr) / ((1.0 + n) * (1.0 + g))
        end
    end

    id = @sprintf("s%.2f-d%.2f-k%.2f", s, δ, k0)
    params = (s = s, delta = δ, k0 = k0)
    ss = (k = round(k_star, digits=6), y = round(y_star, digits=6), c = round(c_star, digits=6))

    return SolowScenario(id, params, ss, path)
end

# -----------------------------------------------------------------------------
# 3. Execution & Validation
# -----------------------------------------------------------------------------
println("Simulating Solow–Swan scenarios in Julia...")

scenarios = SolowScenario[]
for k0 in k0_values
    for δ in δ_values
        for s in s_values
            push!(scenarios, simulate_scenario(s, δ, k0))
        end
    end
end

# Baseline assertion
baseline = simulate_scenario(default_s, default_δ, default_k0)
expected_next = ((1.0 - default_δ) * default_k0 + default_s * default_k0^α) / ((1.0 + n) * (1.0 + g))
@assert length(baseline.path) == horizon + 1
@assert abs(baseline.path[2].k - round(expected_next, digits=6)) < 1e-5
@assert length(scenarios) == 36

println("Generated $(length(scenarios)) scenarios successfully.")

# -----------------------------------------------------------------------------
# 4. Save JSON Assets
# -----------------------------------------------------------------------------
root = dirname(dirname(@__DIR__))
data_dir = joinpath(root, "assets", "data")
image_dir = joinpath(root, "assets", "images")
mkpath(data_dir)
mkpath(image_dir)

# Construct scenarios JSON payload
scenario_entries = [
    (
        id = sc.id,
        parameters = sc.parameters,
        steady_state = sc.steady_state,
        path = sc.path
    )
    for sc in scenarios
]

payload = (
    title = "Solow growth transition explorer",
    model = (
        alpha = α,
        n = n,
        g = g,
        horizon = horizon,
        law_of_motion = "k_next = ((1-delta)*k + s*k^alpha) / ((1+n)*(1+g))"
    ),
    defaults = (
        s = default_s,
        delta = default_δ,
        k0 = default_k0
    ),
    values = (
        s = s_values,
        delta = δ_values,
        k0 = k0_values
    ),
    scenarios = scenario_entries
)

scenarios_json_path = joinpath(data_dir, "solow-growth-scenarios.json")
open(scenarios_json_path, "w") do f
    write(f, to_json(payload))
end
println("Saved: $scenarios_json_path")

# Construct metadata JSON
metadata = (
    title = "Solow growth transition explorer",
    generator = "supplements/julia/solow_growth.jl",
    runtime = "Julia $(VERSION)",
    units = "per effective worker",
    assumptions = (
        production = "y = k^alpha",
        population_growth = n,
        technology_growth = g,
        alpha = α
    ),
    scenario_count = length(scenarios)
)

metadata_json_path = joinpath(data_dir, "solow-growth-metadata.json")
open(metadata_json_path, "w") do f
    write(f, to_json(metadata))
end
println("Saved: $metadata_json_path")

# -----------------------------------------------------------------------------
# 5. Generate Standalone SVG Plot
# -----------------------------------------------------------------------------
function generate_static_svg(sc::SolowScenario, out_path::String)
    w, h = 800, 470
    margin_left, margin_right = 80, 50
    margin_top, margin_bottom = 50, 60

    plot_w = w - margin_left - margin_right
    plot_h = h - margin_top - margin_bottom

    t_max = Float64(horizon)
    k_max = max(sc.steady_state.k * 1.15, maximum(p.k for p in sc.path) * 1.1)

    x_pixel(t) = margin_left + (t / t_max) * plot_w
    y_pixel(k) = margin_top + plot_h - (k / k_max) * plot_h

    # SVG header
    svg = IOBuffer()
    write(svg, """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 $w $h" width="$w" height="$h">
      <style>
        .axis { stroke: #68707a; stroke-width: 1.5; }
        .grid { stroke: #dfe3e8; stroke-width: 1; stroke-dasharray: 4,4; }
        .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; fill: #17191d; }
        .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; fill: #17191d; }
        .legend { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
      </style>
      <rect width="100%" height="100%" fill="#ffffff" />
    """)

    # Grid & Axes
    for t_step in 0:10:horizon
        xp = x_pixel(t_step)
        write(svg, """  <line x1="$xp" y1="$margin_top" x2="$xp" y2="$(margin_top + plot_h)" class="grid" />
          <text x="$xp" y="$(margin_top + plot_h + 20)" class="label" text-anchor="middle">$t_step</text>\n""")
    end

    k_step_size = round(k_max / 5, digits=1)
    for kv in 0:k_step_size:k_max
        yp = y_pixel(kv)
        write(svg, """  <line x1="$margin_left" y1="$yp" x2="$(margin_left + plot_w)" y2="$yp" class="grid" />
          <text x="$(margin_left - 12)" y="$(yp + 4)" class="label" text-anchor="end">$(round(kv, digits=1))</text>\n""")
    end

    # Axes
    write(svg, """  <line x1="$margin_left" y1="$(margin_top + plot_h)" x2="$(margin_left + plot_w)" y2="$(margin_top + plot_h)" class="axis" />
      <line x1="$margin_left" y1="$margin_top" x2="$margin_left" y2="$(margin_top + plot_h)" class="axis" />
      <text x="$(margin_left + plot_w / 2)" y="$(h - 15)" class="label" text-anchor="middle">Period (t)</text>
      <text x="25" y="$(margin_top + plot_h / 2)" class="label" text-anchor="middle" transform="rotate(-90, 25, $(margin_top + plot_h / 2))">Capital per effective worker (k)</text>
      <text x="$(margin_left)" y="$(margin_top - 18)" class="title">Solow Transition: Baseline (s = $(default_s), δ = $(default_δ), k₀ = $(default_k0))</text>
    """)

    # Steady-state reference line
    yss = y_pixel(sc.steady_state.k)
    write(svg, """  <line x1="$margin_left" y1="$yss" x2="$(margin_left + plot_w)" y2="$yss" stroke="#a16207" stroke-width="2.5" stroke-dasharray="6,4" />\n""")

    # Trajectory path line
    points = [string(round(x_pixel(p.t), digits=2), ",", round(y_pixel(p.k), digits=2)) for p in sc.path]
    polyline_str = join(points, " ")
    write(svg, """  <polyline fill="none" stroke="#087e8b" stroke-width="3.5" points="$polyline_str" />\n""")

    # Legend
    leg_x = margin_left + plot_w - 200
    leg_y = margin_top + plot_h - 60
    write(svg, """  <rect x="$leg_x" y="$leg_y" width="190" height="52" fill="#ffffff" stroke="#dfe3e8" rx="6" />
      <line x1="$(leg_x + 15)" y1="$(leg_y + 18)" x2="$(leg_x + 45)" y2="$(leg_y + 18)" stroke="#087e8b" stroke-width="3" />
      <text x="$(leg_x + 55)" y="$(leg_y + 22)" class="legend" fill="#17191d">k_t (trajectory)</text>
      <line x1="$(leg_x + 15)" y1="$(leg_y + 36)" x2="$(leg_x + 45)" y2="$(leg_y + 36)" stroke="#a16207" stroke-width="2.5" stroke-dasharray="6,4" />
      <text x="$(leg_x + 55)" y="$(leg_y + 40)" class="legend" fill="#17191d">k* = $(round(sc.steady_state.k, digits=3)) (SS)</text>
    </svg>""")

    open(out_path, "w") do f
        write(f, String(take!(svg)))
    end
    println("Saved: $out_path")
end

svg_path = joinpath(image_dir, "solow-growth-static.svg")
generate_static_svg(baseline, svg_path)

println("Solow growth generation finished successfully.")
