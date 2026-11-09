# islm_fiscal_shock.jl
# =============================================================================
# IS–LM Fiscal Expansion Dynamics & Equilibrium Path Generator
# =============================================================================
#
# Linear IS–LM model:
#   IS: r = (A + G - Y) / b
#   LM: r = (k Y - m) / h
#
# Equilibrium solution:
#   Y* = (h (A + G) + b m) / (h + b k)
#   r* = (k Y* - m) / h
#
# Exports:
#   - assets/data/islm-fiscal-path.csv
#   - assets/data/islm-fiscal-metadata.json
#   - assets/images/islm-fiscal-static.svg
# =============================================================================

using Printf
using DelimitedFiles

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
# 1. Model Parameters & Shock Path
# -----------------------------------------------------------------------------
const A = 130.0   # Autonomous expenditure
const b = 9.0     # Interest sensitivity of investment
const k = 0.5     # Income sensitivity of money demand
const h = 8.0     # Interest sensitivity of money demand
const m = 42.0    # Real money balances M/P

const n_frames = 16
const g_path = collect(range(0.0, 24.0, length=n_frames))

# Analytical equilibrium path
y_path = (h .* (A .+ g_path) .+ b * m) ./ (h + b * k)
r_path = (k .* y_path .- m) ./ h

@assert all(diff(y_path) .> 0) "Fiscal expansion must strictly increase output Y."
@assert all(diff(r_path) .> 0) "Fiscal expansion must strictly increase interest rate r."

# -----------------------------------------------------------------------------
# 2. Export CSV & Metadata JSON
# -----------------------------------------------------------------------------
root = dirname(dirname(@__DIR__))
data_dir = joinpath(root, "assets", "data")
image_dir = joinpath(root, "assets", "images")
mkpath(data_dir)
mkpath(image_dir)

# CSV Export
csv_path = joinpath(data_dir, "islm-fiscal-path.csv")
open(csv_path, "w") do f
    println(f, "frame,government_spending,output,interest_rate")
    for i in 1:n_frames
        @printf(f, "%d,%.6f,%.6f,%.6f\n", i - 1, g_path[i], y_path[i], r_path[i])
    end
end
println("Saved: $csv_path")

# Metadata JSON Export
metadata = (
    title = "IS-LM fiscal expansion animation",
    generator = "supplements/julia/islm_fiscal_shock.jl",
    julia_version = "Julia $(VERSION)",
    model = (
        autonomous_demand = A,
        is_slope = b,
        lm_output_coefficient = k,
        lm_interest_coefficient = h,
        real_money_balance = m
    ),
    shock = (
        government_spending_start = g_path[1],
        government_spending_end = g_path[end],
        frames = n_frames
    ),
    equilibrium = (
        output_start = round(y_path[1], digits=4),
        output_end = round(y_path[end], digits=4),
        interest_rate_start = round(r_path[1], digits=4),
        interest_rate_end = round(r_path[end], digits=4)
    )
)

metadata_path = joinpath(data_dir, "islm-fiscal-metadata.json")
open(metadata_path, "w") do f
    write(f, to_json(metadata))
end
println("Saved: $metadata_path")

# -----------------------------------------------------------------------------
# 3. Generate Standalone Vector SVG Figure
# -----------------------------------------------------------------------------
function generate_islm_svg(out_path::String)
    w, h_fig = 850, 520
    margin_left, margin_right = 75, 40
    margin_top, margin_bottom = 50, 60

    plot_w = w - margin_left - margin_right
    plot_h = h_fig - margin_top - margin_bottom

    y_min, y_max = 78.0, 152.0
    r_min, r_max = 0.0, 4.4

    xp(y) = margin_left + ((y - y_min) / (y_max - y_min)) * plot_w
    yp(r) = margin_top + plot_h - ((r - r_min) / (r_max - r_min)) * plot_h

    svg = IOBuffer()
    write(svg, """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 $w $h_fig" width="$w" height="$h_fig">
      <style>
        .axis { stroke: #68707a; stroke-width: 1.5; }
        .grid { stroke: #dfe3e8; stroke-width: 1; stroke-dasharray: 4,4; }
        .label { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; fill: #17191d; }
        .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 16px; font-weight: bold; fill: #17191d; }
        .legend { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; }
      </style>
      <rect width="100%" height="100%" fill="#fffcf7" />
    """)

    # Grid
    for y_val in 80:10:150
        x_coord = xp(Float64(y_val))
        write(svg, """  <line x1="$x_coord" y1="$margin_top" x2="$x_coord" y2="$(margin_top + plot_h)" class="grid" />
          <text x="$x_coord" y="$(margin_top + plot_h + 20)" class="label" text-anchor="middle">$y_val</text>\n""")
    end
    for r_val in 0.0:1.0:4.0
        y_coord = yp(r_val)
        write(svg, """  <line x1="$margin_left" y1="$y_coord" x2="$(margin_left + plot_w)" y2="$y_coord" class="grid" />
          <text x="$(margin_left - 10)" y="$(y_coord + 4)" class="label" text-anchor="end">$(round(r_val, digits=1))</text>\n""")
    end

    # Axes
    write(svg, """  <line x1="$margin_left" y1="$(margin_top + plot_h)" x2="$(margin_left + plot_w)" y2="$(margin_top + plot_h)" class="axis" />
      <line x1="$margin_left" y1="$margin_top" x2="$margin_left" y2="$(margin_top + plot_h)" class="axis" />
      <text x="$(margin_left + plot_w / 2)" y="$(h_fig - 15)" class="label" text-anchor="middle">Output Y</text>
      <text x="25" y="$(margin_top + plot_h / 2)" class="label" text-anchor="middle" transform="rotate(-90, 25, $(margin_top + plot_h / 2))">Interest Rate r</text>
      <text x="$(margin_left)" y="$(margin_top - 18)" class="title">Fiscal Expansion Shifts IS and Raises Short-Run Equilibrium</text>
    """)

    # Curves: LM Curve
    y_grid = range(y_min, y_max, length=100)
    lm_pts = [string(round(xp(y), digits=2), ",", round(yp((k * y - m) / h), digits=2)) for y in y_grid if (k*y-m)/h >= r_min && (k*y-m)/h <= r_max]
    write(svg, """  <polyline fill="none" stroke="#735c73" stroke-width="3" points="$(join(lm_pts, " "))" />\n""")

    # IS Curve (G = 0)
    is0_pts = [string(round(xp(y), digits=2), ",", round(yp((A - y) / b), digits=2)) for y in y_grid if (A-y)/b >= r_min && (A-y)/b <= r_max]
    write(svg, """  <polyline fill="none" stroke="#995733" stroke-width="2.5" stroke-dasharray="6,4" points="$(join(is0_pts, " "))" />\n""")

    # IS Curve (G = 24)
    is1_pts = [string(round(xp(y), digits=2), ",", round(yp((A + 24.0 - y) / b), digits=2)) for y in y_grid if (A+24.0-y)/b >= r_min && (A+24.0-y)/b <= r_max]
    write(svg, """  <polyline fill="none" stroke="#995733" stroke-width="3" points="$(join(is1_pts, " "))" />\n""")

    # Equilibrium transition trajectory
    path_pts = [string(round(xp(y), digits=2), ",", round(yp(r), digits=2)) for (y, r) in zip(y_path, r_path)]
    write(svg, """  <polyline fill="none" stroke="#4d3b30" stroke-width="2" stroke-dasharray="3,3" points="$(join(path_pts, " "))" />\n""")

    # Points E0 and E1
    x0, y0 = xp(y_path[1]), yp(r_path[1])
    x1, y1 = xp(y_path[end]), yp(r_path[end])
    write(svg, """  <circle cx="$x0" cy="$y0" r="6" fill="#4d3b30" />
      <text x="$(x0 - 10)" y="$(y0 - 12)" class="label" font-weight="bold" fill="#4d3b30">E₀ (G=0)</text>
      <circle cx="$x1" cy="$y1" r="6" fill="#4d3b30" />
      <text x="$(x1 + 10)" y="$(y1 - 10)" class="label" font-weight="bold" fill="#4d3b30">E₁ (G=24)</text>
    """)

    # Legend
    leg_x = margin_left + 20
    leg_y = margin_top + 20
    write(svg, """  <rect x="$leg_x" y="$leg_y" width="180" height="90" fill="#ffffff" stroke="#dfe3e8" rx="6" />
      <line x1="$(leg_x + 15)" y1="$(leg_y + 20)" x2="$(leg_x + 45)" y2="$(leg_y + 20)" stroke="#735c73" stroke-width="3" />
      <text x="$(leg_x + 55)" y="$(leg_y + 24)" class="legend" fill="#17191d">LM curve</text>
      <line x1="$(leg_x + 15)" y1="$(leg_y + 45)" x2="$(leg_x + 45)" y2="$(leg_y + 45)" stroke="#995733" stroke-width="2" stroke-dasharray="6,4" />
      <text x="$(leg_x + 55)" y="$(leg_y + 49)" class="legend" fill="#17191d">IS (G = 0)</text>
      <line x1="$(leg_x + 15)" y1="$(leg_y + 70)" x2="$(leg_x + 45)" y2="$(leg_y + 70)" stroke="#995733" stroke-width="3" />
      <text x="$(leg_x + 55)" y="$(leg_y + 74)" class="legend" fill="#17191d">IS (G = 24)</text>
    </svg>""")

    open(out_path, "w") do f
        write(f, String(take!(svg)))
    end
    println("Saved: $out_path")
end

svg_out = joinpath(image_dir, "islm-fiscal-static.svg")
generate_islm_svg(svg_out)

println(@sprintf("Equilibrium output: %.3f -> %.3f; interest rate: %.3f -> %.3f",
                 y_path[1], y_path[end], r_path[1], r_path[end]))
