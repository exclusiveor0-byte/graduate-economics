# run_all.jl
# =============================================================================
# Run All Computational Supplements in Julia
# =============================================================================

println("="^70)
println("Running All 6 Graduate Economics Computational Supplements in Julia")
println("="^70)

scripts = [
    "solow_growth.jl",
    "islm_fiscal_shock.jl",
    "iv_weak_instruments.jl",
    "ols_geometry.jl",
    "ols_projection.jl",
    "ramsey_saddle_path.jl"
]

julia_dir = @__DIR__

for (idx, script) in enumerate(scripts)
    println("\n[$idx/$(length(scripts))] Running $script...")
    path = joinpath(julia_dir, script)
    include(path)
    println("✓ $script completed successfully.")
end

println("\n" * "="^70)
println("All 6 Julia computational supplements executed with 0 errors!")
println("="^70)
