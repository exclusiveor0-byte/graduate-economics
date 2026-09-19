% Ramsey-Cass-Koopmans (RCK) Saddle-Path Dynamics & Numerical Shooting
% Generates:
%   1. assets/images/ramsey-phase-diagram-static.png (Publication-grade static multi-panel)
%   2. assets/gif/ramsey-saddle-path-convergence.gif (Core dynamic: saddle convergence)
%   3. assets/gif/ramsey-initial-consumption-divergence.gif (Saddle selection: c0 divergence)
%   4. assets/gif/ramsey-discount-rate-shock.gif (Comparative dynamics: vertical jump in c)
%   5. assets/gif/ramsey-shooting-algorithm.gif (Numerical shooting bisection)
%   6. assets/data/ramsey-saddle-path-metadata.json (Model parameters & steady-state values)

function ramsey_saddle_path()
    close all; clc;

    % Directory setup
    script_path = mfilename('fullpath');
    root = fileparts(fileparts(fileparts(script_path)));
    data_dir = fullfile(root, 'assets', 'data');
    image_dir = fullfile(root, 'assets', 'images');
    gif_dir = fullfile(root, 'assets', 'gif');

    if ~exist(data_dir, 'dir'), mkdir(data_dir); end
    if ~exist(image_dir, 'dir'), mkdir(image_dir); end
    if ~exist(gif_dir, 'dir'), mkdir(gif_dir); end

    fprintf('=== Ramsey-Cass-Koopmans Visualization Suite ===\n');

    % 1. Model Parameters
    params = struct();
    params.alpha = 0.33;       % Capital share in production Y = K^alpha (AL)^(1-alpha)
    params.theta = 2.00;       % Relative risk aversion (CRRA parameter)
    params.n     = 0.01;       % Population growth rate
    params.g     = 0.02;       % Technological progress rate
    params.delta = 0.05;       % Capital depreciation rate
    params.x     = params.n + params.g + params.delta; % Effective depreciation = 0.08
    params.rho0  = 0.04;       % Baseline rate of time preference
    params.rho1  = 0.02;       % Post-shock rate of time preference (patient households)

    % Steady states
    % Baseline (rho0)
    denom0 = params.rho0 + params.delta + params.theta * params.g; % 0.13
    k0_star = (params.alpha / denom0)^(1 / (1 - params.alpha));    % ~ 4.0164
    c0_star = k0_star^params.alpha - params.x * k0_star;           % ~ 1.2609
    y0_star = k0_star^params.alpha;                                 % ~ 1.5822

    % Post-shock (rho1)
    denom1 = params.rho1 + params.delta + params.theta * params.g; % 0.11
    k1_star = (params.alpha / denom1)^(1 / (1 - params.alpha));    % ~ 5.1537
    c1_star = k1_star^params.alpha - params.x * k1_star;           % ~ 1.3056
    y1_star = k1_star^params.alpha;                                 % ~ 1.7179

    % Golden Rule capital
    k_GR = (params.alpha / params.x)^(1 / (1 - params.alpha));     % ~ 8.2898
    c_GR = k_GR^params.alpha - params.x * k_GR;                    % ~ 1.3465

    % Jacobian and eigenvalues at baseline steady state
    J0 = [params.rho0 + (params.theta - 1)*params.g - params.n, -1; ...
          (c0_star / params.theta) * params.alpha * (params.alpha - 1) * k0_star^(params.alpha - 2), 0];
    [V0, D0] = eig(J0);
    [eig0_sorted, idx0] = sort(diag(D0));
    lambda0_stable = eig0_sorted(1);   % ~ -0.0946
    lambda0_unstable = eig0_sorted(2); % ~ +0.1446
    v0_stable = V0(:, idx0(1));
    if v0_stable(1) < 0, v0_stable = -v0_stable; end
    v0_unstable = V0(:, idx0(2));
    if v0_unstable(1) < 0, v0_unstable = -v0_unstable; end

    % Jacobian and eigenvalues at post-shock steady state
    J1 = [params.rho1 + (params.theta - 1)*params.g - params.n, -1; ...
          (c1_star / params.theta) * params.alpha * (params.alpha - 1) * k1_star^(params.alpha - 2), 0];
    [V1, D1] = eig(J1);
    [eig1_sorted, idx1] = sort(diag(D1));
    lambda1_stable = eig1_sorted(1);
    v1_stable = V1(:, idx1(1));
    if v1_stable(1) < 0, v1_stable = -v1_stable; end

    fprintf('Baseline E0*:   k0* = %.4f, c0* = %.4f (lambda = %.4f, %.4f)\n', ...
        k0_star, c0_star, lambda0_stable, lambda0_unstable);
    fprintf('Post-shock E1*: k1* = %.4f, c1* = %.4f (lambda = %.4f)\n', ...
        k1_star, c1_star, lambda1_stable);
    fprintf('Golden Rule:    k_GR = %.4f, c_GR = %.4f\n', k_GR, c_GR);

    % Global non-linear saddle paths via reverse-time integration
    [k_saddle0, c_saddle0] = compute_saddle_path(params.alpha, params.theta, params.x, ...
                                                 params.rho0, params.delta, params.g, ...
                                                 k0_star, c0_star, v0_stable);
    [k_saddle1, c_saddle1] = compute_saddle_path(params.alpha, params.theta, params.x, ...
                                                 params.rho1, params.delta, params.g, ...
                                                 k1_star, c1_star, v1_stable);

    % Consumption on post-shock saddle path at predetermined capital k0_star
    c_shock_jump = interp1(k_saddle1, c_saddle1, k0_star, 'pchip');
    fprintf('Post-shock jump at k0*: c drops from %.4f to %.4f (delta c = %.4f)\n', ...
        c0_star, c_shock_jump, c_shock_jump - c0_star);

    % Save JSON metadata
    save_metadata(data_dir, params, k0_star, c0_star, k1_star, c1_star, k_GR, c_GR, ...
                  lambda0_stable, lambda0_unstable, v0_stable, c_shock_jump);

    % Styling colors (Warm paper palette)
    colors = struct();
    colors.paper       = [0.985, 0.980, 0.970]; % Warm editorial paper
    colors.ink         = [0.180, 0.180, 0.220]; % Deep slate ink
    colors.kdot0       = [0.840, 0.360, 0.160]; % Warm coral / amber for k_dot = 0
    colors.cdot0       = [0.200, 0.440, 0.720]; % Indigo / steel blue for c_dot = 0
    colors.saddle      = [0.060, 0.540, 0.400]; % Emerald green for saddle path
    colors.saddle_post = [0.120, 0.350, 0.750]; % Royal blue for post-shock saddle
    colors.unstable    = [0.650, 0.650, 0.700]; % Light gray for unstable manifold
    colors.diverge_hi  = [0.850, 0.200, 0.200]; % Crimson for high c0 (capital exhausted)
    colors.diverge_lo  = [0.520, 0.220, 0.650]; % Purple for low c0 (TVC violation)
    colors.steady      = [0.920, 0.650, 0.100]; % Golden yellow for steady states
    colors.quiver      = [0.720, 0.760, 0.820]; % Faded blue for vector field arrows

    % Generate All Assets
    generate_static_figure(image_dir, params, colors, k0_star, c0_star, k1_star, c1_star, ...
                           k_GR, c_GR, k_saddle0, c_saddle0, k_saddle1, c_saddle1, c_shock_jump, ...
                           v0_unstable);

    generate_gif_1_convergence(gif_dir, params, colors, k0_star, c0_star, k_saddle0, c_saddle0);

    generate_gif_2_divergence(gif_dir, params, colors, k0_star, c0_star, k_saddle0, c_saddle0);

    generate_gif_3_discount_shock(gif_dir, params, colors, k0_star, c0_star, k1_star, c1_star, ...
                                 k_saddle0, c_saddle0, k_saddle1, c_saddle1, c_shock_jump);

    generate_gif_4_shooting(gif_dir, params, colors, k0_star, c0_star, k_saddle0, c_saddle0);

    fprintf('=== All Ramsey visualizations successfully generated! ===\n');
end

% -------------------------------------------------------------------------
% Compute Global Saddle Path via Reverse-Time ODE Integration
% -------------------------------------------------------------------------
function [k_saddle, c_saddle] = compute_saddle_path(alpha, theta, x, rho, delta, g, k_star, c_star, v_stable)
    ode_rev = @(t, y) -[y(1)^alpha - y(2) - x*y(1); ...
                         (y(2)/theta) * (alpha * y(1)^(alpha - 1) - (rho + delta + theta*g))];
    opt = odeset('RelTol', 1e-6, 'AbsTol', 1e-8, 'Events', @event_reverse);

    % Using eps_init = 1e-2 ensures the trajectory cleanly spans from k=0.5 up to k=8.5
    eps_init = 1e-2;
    % Branch 1: Leftward (k < k_star)
    [~, yL] = ode45(ode_rev, [0, 80], [k_star; c_star] - eps_init * v_stable, opt);
    % Branch 2: Rightward (k > k_star)
    [~, yR] = ode45(ode_rev, [0, 80], [k_star; c_star] + eps_init * v_stable, opt);

    % Combine branches and sort by capital k
    k_all = [flipud(yL(:, 1)); k_star; yR(:, 1)];
    c_all = [flipud(yL(:, 2)); c_star; yR(:, 2)];

    [k_saddle, u_idx] = unique(k_all);
    c_saddle = c_all(u_idx);
end

function [value, isterminal, direction] = event_reverse(~, y)
    % Stop reverse integration if k drops below 0.20 or exceeds 9.5, or c drops below 0.05
    value = [y(1) - 0.20; y(2) - 0.05; 9.5 - y(1)];
    isterminal = [1; 1; 1];
    direction = [0; 0; 0];
end

% -------------------------------------------------------------------------
% Forward Integration Event Functions
% -------------------------------------------------------------------------
function [value, isterminal, direction] = event_forward(~, y)
    % Stop forward integration if k hits lower bound 0.08 or upper bound 8.5
    value = [y(1) - 0.08; y(2) - 0.03; 8.5 - y(1)];
    isterminal = [1; 1; 1];
    direction = [0; 0; 0];
end

% -------------------------------------------------------------------------
% Figure 0: Publication-Grade Static Multi-Panel Figure
% -------------------------------------------------------------------------
function generate_static_figure(image_dir, params, colors, k0_star, c0_star, k1_star, c1_star, ...
                                k_GR, c_GR, k_saddle0, c_saddle0, k_saddle1, c_saddle1, c_shock_jump, ...
                                v0_unstable)
    fprintf('Generating Static Multi-Panel Figure...\n');
    fig = figure('Visible', 'off', 'Color', colors.paper, 'Position', [80, 80, 1280, 720]);

    denom0 = params.rho0 + params.delta + params.theta * params.g;
    denom1 = params.rho1 + params.delta + params.theta * params.g;

    % Subplot 1: Comprehensive Phase Portrait (Left, spanning full height)
    ax1 = subplot('Position', [0.06, 0.10, 0.52, 0.83]);
    hold(ax1, 'on'); ax1.Color = colors.paper;

    % Grid for nullclines
    k_grid = linspace(0.1, 7.5, 300);
    c_kdot0 = k_grid.^params.alpha - params.x * k_grid;

    % Vector field
    [K_mesh, C_mesh] = meshgrid(linspace(0.6, 7.2, 16), linspace(0.3, 2.1, 14));
    K_dot = K_mesh.^params.alpha - C_mesh - params.x * K_mesh;
    C_dot = (C_mesh ./ params.theta) .* (params.alpha .* K_mesh.^(params.alpha - 1) - denom0);
    norm_factor = sqrt(K_dot.^2 + C_dot.^2);
    norm_factor(norm_factor < 1e-6) = 1e-6;
    K_dot_u = K_dot ./ norm_factor;
    C_dot_u = C_dot ./ norm_factor;
    quiver(ax1, K_mesh, C_mesh, K_dot_u, C_dot_u, 0.38, 'Color', colors.quiver, ...
           'LineWidth', 1.0, 'MaxHeadSize', 0.8, 'DisplayName', 'Vector field (\partial k, \partial c)');

    % Nullclines
    plot(ax1, k_grid, c_kdot0, '-', 'LineWidth', 2.8, 'Color', colors.kdot0, ...
         'DisplayName', '$\dot{k} = 0 \quad (c = f(k) - xk)$');
    plot(ax1, [k0_star, k0_star], [0, 2.4], '--', 'LineWidth', 2.8, 'Color', colors.cdot0, ...
         'DisplayName', '$\dot{c} = 0 \quad (k = k^*)$');

    % Golden Rule line
    plot(ax1, [k_GR, k_GR], [0, 2.4], ':', 'LineWidth', 1.8, 'Color', [0.55, 0.45, 0.25], ...
         'DisplayName', '$k_{GR} \quad (\mathrm{Golden\ Rule})$');

    % Unstable manifold (linear tangent near E0)
    unstable_span = linspace(-1.8, 1.8, 50);
    plot(ax1, k0_star + unstable_span * v0_unstable(1), c0_star + unstable_span * v0_unstable(2), ...
         ':', 'LineWidth', 1.8, 'Color', colors.unstable, 'DisplayName', '$\mathrm{Unstable\ Manifold}\ (\lambda_2 > 0)$');

    % Saddle path (stable manifold)
    plot(ax1, k_saddle0, c_saddle0, '-', 'LineWidth', 3.2, 'Color', colors.saddle, ...
         'DisplayName', '$\mathrm{Saddle\ Path\ /\ Stable\ Manifold}\ (\lambda_1 < 0)$');

    % Steady state marker
    plot(ax1, k0_star, c0_star, 'o', 'MarkerSize', 10, 'MarkerFaceColor', colors.steady, ...
         'MarkerEdgeColor', colors.ink, 'LineWidth', 1.5, 'DisplayName', '$\mathrm{Steady\ State}\ E_0^*$');

    % Quadrant directional annotations
    text(ax1, 1.4, 0.55, '$\begin{array}{c}\dot{k} > 0 \\ \dot{c} > 0\end{array}$', ...
         'Interpreter', 'latex', 'FontSize', 12, 'Color', colors.ink);
    text(ax1, 1.4, 1.70, '$\begin{array}{c}\dot{k} < 0 \\ \dot{c} > 0\end{array}$', ...
         'Interpreter', 'latex', 'FontSize', 12, 'Color', colors.ink);
    text(ax1, 5.6, 1.70, '$\begin{array}{c}\dot{k} < 0 \\ \dot{c} < 0\end{array}$', ...
         'Interpreter', 'latex', 'FontSize', 12, 'Color', colors.ink);
    text(ax1, 5.6, 0.55, '$\begin{array}{c}\dot{k} > 0 \\ \dot{c} < 0\end{array}$', ...
         'Interpreter', 'latex', 'FontSize', 12, 'Color', colors.ink);

    % Text label for E0
    text(ax1, k0_star + 0.15, c0_star - 0.08, ...
         sprintf('E_0^* (k*=%.2f, c*=%.2f)', k0_star, c0_star), ...
         'FontWeight', 'bold', 'FontSize', 11, 'Color', colors.ink);

    xlim(ax1, [0.3, 7.5]); ylim(ax1, [0.2, 2.3]);
    grid(ax1, 'on'); box(ax1, 'off');
    xlabel(ax1, 'Capital per Effective Worker k', 'FontSize', 12, 'FontWeight', 'bold', 'Color', colors.ink);
    ylabel(ax1, 'Consumption per Effective Worker c', 'FontSize', 12, 'FontWeight', 'bold', 'Color', colors.ink);
    title(ax1, 'A. Ramsey-Cass-Koopmans Phase Portrait & Saddle-Point Stability', ...
          'FontSize', 13, 'FontWeight', 'bold', 'Color', colors.ink);
    legend(ax1, 'Location', 'northwest', 'Box', 'off', 'FontSize', 9, 'Interpreter', 'latex');

    % Subplot 2: Initial Consumption Divergence & Saddle Selection (Top Right)
    ax2 = subplot('Position', [0.65, 0.56, 0.32, 0.37]);
    hold(ax2, 'on'); ax2.Color = colors.paper;

    k0_val = 2.0;
    c0_saddle_val = interp1(k_saddle0, c_saddle0, k0_val, 'pchip');
    c0_high_val = c0_saddle_val + 0.18;
    c0_low_val  = c0_saddle_val - 0.18;

    ode_fwd0 = @(t, y) [y(1)^params.alpha - y(2) - params.x * y(1); ...
                        (y(2)/params.theta) * (params.alpha * y(1)^(params.alpha - 1) - denom0)];
    opt_fwd = odeset('RelTol', 1e-6, 'AbsTol', 1e-8, 'Events', @event_forward);

    [~, y_saddle] = ode45(ode_fwd0, [0, 50], [k0_val; c0_saddle_val], opt_fwd);
    [~, y_high]   = ode45(ode_fwd0, [0, 30], [k0_val; c0_high_val], opt_fwd);
    [~, y_low]    = ode45(ode_fwd0, [0, 30], [k0_val; c0_low_val], opt_fwd);

    % Background curves (HandleVisibility = off)
    plot(ax2, k_grid, c_kdot0, '--', 'LineWidth', 1.5, 'Color', colors.kdot0, 'HandleVisibility', 'off');
    plot(ax2, [k0_star, k0_star], [0, 2.4], '--', 'LineWidth', 1.5, 'Color', colors.cdot0, 'HandleVisibility', 'off');
    plot(ax2, k_saddle0, c_saddle0, ':', 'LineWidth', 1.8, 'Color', [0.70, 0.85, 0.78], 'HandleVisibility', 'off');

    % Trajectories
    plot(ax2, y_high(:, 1), y_high(:, 2), '-', 'LineWidth', 2.4, 'Color', colors.diverge_hi, ...
         'DisplayName', '$c_0 > c_0^* \quad (\mathrm{Capital\ Exhaustion}\ k \to 0)$');
    plot(ax2, y_saddle(:, 1), y_saddle(:, 2), '-', 'LineWidth', 2.8, 'Color', colors.saddle, ...
         'DisplayName', '$c_0 = c_0^* \quad (\mathrm{Optimal\ Saddle\ Path}\ \to E_0^*)$');
    plot(ax2, y_low(:, 1), y_low(:, 2), '-', 'LineWidth', 2.4, 'Color', colors.diverge_lo, ...
         'DisplayName', '$c_0 < c_0^* \quad (\mathrm{TVC\ Violation\ /\ Overaccum.})$');

    % Initial dots (HandleVisibility = off)
    plot(ax2, k0_val, c0_high_val, 's', 'MarkerSize', 7, 'MarkerFaceColor', colors.diverge_hi, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    plot(ax2, k0_val, c0_saddle_val, 'o', 'MarkerSize', 8, 'MarkerFaceColor', colors.saddle, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    plot(ax2, k0_val, c0_low_val, 'd', 'MarkerSize', 7, 'MarkerFaceColor', colors.diverge_lo, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    plot(ax2, k0_star, c0_star, 'p', 'MarkerSize', 10, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    xlim(ax2, [0.3, 6.8]); ylim(ax2, [0.4, 2.1]);
    grid(ax2, 'on'); box(ax2, 'off');
    xlabel(ax2, 'Capital k', 'FontSize', 10, 'FontWeight', 'bold', 'Color', colors.ink);
    ylabel(ax2, 'Consumption c', 'FontSize', 10, 'FontWeight', 'bold', 'Color', colors.ink);
    title(ax2, 'B. Saddle-Path Selection: Unique Convergence', 'FontSize', 11, 'FontWeight', 'bold', 'Color', colors.ink);
    legend(ax2, 'Location', 'northwest', 'Box', 'off', 'FontSize', 8, 'Interpreter', 'latex');

    % Subplot 3: Comparative Dynamics: Permanent Shock \rho \downarrow (Bottom Right)
    ax3 = subplot('Position', [0.65, 0.10, 0.32, 0.37]);
    hold(ax3, 'on'); ax3.Color = colors.paper;

    % Background curves for post-shock (HandleVisibility = off)
    plot(ax3, k_grid, c_kdot0, '--', 'LineWidth', 1.5, 'Color', colors.kdot0, 'HandleVisibility', 'off');
    plot(ax3, [k0_star, k0_star], [0, 2.4], ':', 'LineWidth', 1.4, 'Color', [0.65, 0.70, 0.78], 'HandleVisibility', 'off');
    plot(ax3, [k1_star, k1_star], [0, 2.4], '--', 'LineWidth', 1.8, 'Color', colors.saddle_post, 'HandleVisibility', 'off');

    plot(ax3, k_saddle0, c_saddle0, ':', 'LineWidth', 1.8, 'Color', [0.65, 0.78, 0.70], ...
         'DisplayName', '$\mathrm{Old\ Saddle\ Path}\ (\rho = 0.04)$');
    plot(ax3, k_saddle1, c_saddle1, '-', 'LineWidth', 2.8, 'Color', colors.saddle_post, ...
         'DisplayName', '$\mathrm{New\ Saddle\ Path}\ (\rho = 0.02)$');

    % Transition trajectory from (k0_star, c_shock_jump)
    ode_fwd1 = @(t, y) [y(1)^params.alpha - y(2) - params.x * y(1); ...
                        (y(2)/params.theta) * (params.alpha * y(1)^(params.alpha - 1) - denom1)];
    [~, y_trans] = ode45(ode_fwd1, [0, 50], [k0_star; c_shock_jump], opt_fwd);
    plot(ax3, y_trans(:, 1), y_trans(:, 2), '-', 'LineWidth', 3.0, 'Color', [0.90, 0.40, 0.10], ...
         'DisplayName', '$\mathrm{Dynamic\ Transition\ to}\ E_1^*$');

    % Vertical jump line
    plot(ax3, [k0_star, k0_star], [c0_star, c_shock_jump], 'r--', 'LineWidth', 2.2, ...
         'DisplayName', '$\mathrm{Vertical\ Jump:}\ c(t_0^+) \downarrow$');

    % Steady state points (HandleVisibility = off)
    plot(ax3, k0_star, c0_star, 'o', 'MarkerSize', 8, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    plot(ax3, k0_star, c_shock_jump, 'v', 'MarkerSize', 8, 'MarkerFaceColor', [0.90, 0.25, 0.25], 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    plot(ax3, k1_star, c1_star, 'p', 'MarkerSize', 11, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    text(ax3, k0_star - 0.55, (c0_star + c_shock_jump)/2, '\Delta c < 0', ...
         'Color', [0.85, 0.15, 0.15], 'FontWeight', 'bold', 'FontSize', 9);
    text(ax3, k0_star - 0.70, c0_star + 0.08, 'E_0^*', 'FontWeight', 'bold', 'FontSize', 10, 'Color', colors.ink);
    text(ax3, k1_star + 0.15, c1_star - 0.05, 'E_1^*', 'FontWeight', 'bold', 'FontSize', 10, 'Color', colors.ink);

    xlim(ax3, [2.5, 6.8]); ylim(ax3, [0.8, 1.8]);
    grid(ax3, 'on'); box(ax3, 'off');
    xlabel(ax3, 'Capital k', 'FontSize', 10, 'FontWeight', 'bold', 'Color', colors.ink);
    ylabel(ax3, 'Consumption c', 'FontSize', 10, 'FontWeight', 'bold', 'Color', colors.ink);
    title(ax3, 'C. Comparative Dynamics: Patient Households (\rho \downarrow)', ...
          'FontSize', 11, 'FontWeight', 'bold', 'Color', colors.ink);
    legend(ax3, 'Location', 'northwest', 'Box', 'off', 'FontSize', 8, 'Interpreter', 'latex');

    out_file = fullfile(image_dir, 'ramsey-phase-diagram-static.png');
    exportgraphics(fig, out_file, 'Resolution', 220);
    close(fig);
    fprintf('Saved: %s\n', out_file);
end

% -------------------------------------------------------------------------
% GIF 1: Core Dynamic: Saddle-Path Convergence (Phase Portrait + Time Series)
% -------------------------------------------------------------------------
function generate_gif_1_convergence(gif_dir, params, colors, k0_star, c0_star, k_saddle0, c_saddle0)
    fprintf('Generating GIF 1: Saddle-Path Convergence...\n');
    gif_file = fullfile(gif_dir, 'ramsey-saddle-path-convergence.gif');
    if exist(gif_file, 'file'), delete(gif_file); end

    % Simulate convergence trajectory along the saddle path from k0 = 1.8
    k_init = 1.8;
    c_init = interp1(k_saddle0, c_saddle0, k_init, 'pchip');

    denom0 = params.rho0 + params.delta + params.theta * params.g;
    ode_fwd = @(t, y) [y(1)^params.alpha - y(2) - params.x * y(1); ...
                       (y(2)/params.theta) * (params.alpha * y(1)^(params.alpha - 1) - denom0)];
    opt = odeset('RelTol', 1e-6, 'AbsTol', 1e-8);
    T_end = 36;
    [t_sim, y_sim] = ode45(ode_fwd, [0, T_end], [k_init; c_init], opt);

    % Resample to N_frames uniformly in time
    N_frames = 32;
    t_frames = linspace(0, T_end, N_frames);
    k_frames = interp1(t_sim, y_sim(:, 1), t_frames, 'pchip');
    c_frames = interp1(t_sim, y_sim(:, 2), t_frames, 'pchip');

    % Setup Figure
    fig = figure('Visible', 'off', 'Color', colors.paper, 'Position', [100, 100, 960, 500]);

    % Left Subplot: Phase Portrait
    ax1 = subplot('Position', [0.07, 0.12, 0.44, 0.78]);
    hold(ax1, 'on'); ax1.Color = colors.paper;

    k_grid = linspace(0.2, 6.5, 200);
    c_kdot0 = k_grid.^params.alpha - params.x * k_grid;

    % Quiver (HandleVisibility = off)
    [Km, Cm] = meshgrid(linspace(0.8, 6.0, 14), linspace(0.4, 2.0, 12));
    Kd = Km.^params.alpha - Cm - params.x * Km;
    Cd = (Cm ./ params.theta) .* (params.alpha .* Km.^(params.alpha - 1) - denom0);
    nrm = sqrt(Kd.^2 + Cd.^2); nrm(nrm < 1e-6) = 1e-6;
    quiver(ax1, Km, Cm, Kd./nrm, Cd./nrm, 0.35, 'Color', colors.quiver, 'LineWidth', 0.9, ...
           'MaxHeadSize', 0.8, 'HandleVisibility', 'off');

    % Fixed curves
    plot(ax1, k_grid, c_kdot0, '-', 'LineWidth', 2.4, 'Color', colors.kdot0, 'DisplayName', 'dk/dt = 0');
    plot(ax1, [k0_star, k0_star], [0, 2.4], '--', 'LineWidth', 2.4, 'Color', colors.cdot0, 'DisplayName', 'dc/dt = 0');
    plot(ax1, k_saddle0, c_saddle0, '-', 'LineWidth', 3.0, 'Color', [0.70, 0.85, 0.78], 'DisplayName', 'Saddle path');
    plot(ax1, k0_star, c0_star, 'o', 'MarkerSize', 9, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'DisplayName', 'E^*');

    % Dynamic objects
    h_trail1 = plot(ax1, nan, nan, '-', 'LineWidth', 3.0, 'Color', colors.saddle, 'DisplayName', 'Economy trajectory');
    h_dot1   = plot(ax1, nan, nan, 'o', 'MarkerSize', 10, 'MarkerFaceColor', colors.saddle, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    h_info1  = text(ax1, 0.05, 0.22, '', 'Units', 'normalized', 'FontName', 'Consolas', 'FontSize', 9.5, ...
                    'Color', colors.ink, 'BackgroundColor', [1, 1, 1, 0.85], 'EdgeColor', [0.8, 0.8, 0.8]);

    xlim(ax1, [0.4, 6.2]); ylim(ax1, [0.3, 2.2]);
    grid(ax1, 'on'); box(ax1, 'off');
    xlabel(ax1, 'Capital per effective worker k', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax1, 'Consumption per effective worker c', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax1, 'Phase Diagram Dynamics', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax1, 'Location', 'northwest', 'Box', 'off', 'FontSize', 8);

    % Right Subplot: Time Series
    ax2 = subplot('Position', [0.58, 0.12, 0.38, 0.78]);
    hold(ax2, 'on'); ax2.Color = colors.paper;

    % Target dashed lines
    plot(ax2, [0, T_end], [k0_star, k0_star], '--', 'LineWidth', 1.8, 'Color', colors.cdot0, 'DisplayName', 'k^* = 4.02');
    plot(ax2, [0, T_end], [c0_star, c0_star], '--', 'LineWidth', 1.8, 'Color', colors.kdot0, 'DisplayName', 'c^* = 1.26');

    % Dynamic lines
    h_line_k = plot(ax2, nan, nan, '-', 'LineWidth', 2.8, 'Color', colors.cdot0, 'DisplayName', 'k(t) [Capital]');
    h_line_c = plot(ax2, nan, nan, '-', 'LineWidth', 2.8, 'Color', colors.kdot0, 'DisplayName', 'c(t) [Consumption]');
    h_dot_k  = plot(ax2, nan, nan, 'o', 'MarkerSize', 8, 'MarkerFaceColor', colors.cdot0, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    h_dot_c  = plot(ax2, nan, nan, 'o', 'MarkerSize', 8, 'MarkerFaceColor', colors.kdot0, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    xlim(ax2, [0, T_end]); ylim(ax2, [0.8, 4.4]);
    grid(ax2, 'on'); box(ax2, 'off');
    xlabel(ax2, 'Time t', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax2, 'Levels (k, c)', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax2, 'Dynamic Transition Paths', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax2, 'Location', 'east', 'Box', 'off', 'FontSize', 9);

    % Render Frames
    for f = 1:N_frames
        curr_k = k_frames(1:f);
        curr_c = c_frames(1:f);
        curr_t = t_frames(1:f);

        % Update Left
        h_trail1.XData = curr_k;
        h_trail1.YData = curr_c;
        h_dot1.XData = curr_k(end);
        h_dot1.YData = curr_c(end);
        y_val = curr_k(end)^params.alpha;
        s_val = (y_val - curr_c(end)) / y_val;
        h_info1.String = sprintf('t = %4.1f\nk(t) = %5.3f  (k* = %5.3f)\nc(t) = %5.3f  (c* = %5.3f)\nSaving rate s = %4.1f%%', ...
                                 t_frames(f), curr_k(end), k0_star, curr_c(end), c0_star, s_val * 100);

        % Update Right
        h_line_k.XData = curr_t;
        h_line_k.YData = curr_k;
        h_line_c.XData = curr_t;
        h_line_c.YData = curr_c;
        h_dot_k.XData = curr_t(end);
        h_dot_k.YData = curr_k(end);
        h_dot_c.XData = curr_t(end);
        h_dot_c.YData = curr_c(end);

        % Frame Capture
        temp_png = [tempname '.png'];
        exportgraphics(fig, temp_png, 'Resolution', 120);
        img = imread(temp_png);
        delete(temp_png);
        [img_ind, cmap] = rgb2ind(img, 256);

        delay = 0.08;
        if f == N_frames, delay = 1.20; end % Pause at final steady state

        if f == 1
            imwrite(img_ind, cmap, gif_file, 'gif', 'LoopCount', Inf, 'DelayTime', delay);
        else
            imwrite(img_ind, cmap, gif_file, 'gif', 'WriteMode', 'append', 'DelayTime', delay);
        end
    end
    close(fig);
    fprintf('Saved: %s\n', gif_file);
end

% -------------------------------------------------------------------------
% GIF 2: Saddle Selection: Divergence from Non-Optimal Initial Consumption
% -------------------------------------------------------------------------
function generate_gif_2_divergence(gif_dir, params, colors, k0_star, c0_star, k_saddle0, c_saddle0)
    fprintf('Generating GIF 2: Initial Consumption Divergence...\n');
    gif_file = fullfile(gif_dir, 'ramsey-initial-consumption-divergence.gif');
    if exist(gif_file, 'file'), delete(gif_file); end

    k0_val = 2.0;
    c0_saddle = interp1(k_saddle0, c_saddle0, k0_val, 'pchip');
    c0_hi = c0_saddle + 0.20;
    c0_lo = c0_saddle - 0.20;

    denom0 = params.rho0 + params.delta + params.theta * params.g;
    ode_fwd = @(t, y) [y(1)^params.alpha - y(2) - params.x * y(1); ...
                       (y(2)/params.theta) * (params.alpha * y(1)^(params.alpha - 1) - denom0)];
    opt = odeset('RelTol', 1e-6, 'AbsTol', 1e-8, 'Events', @event_forward);

    [t_s, y_s] = ode45(ode_fwd, [0, 40], [k0_val; c0_saddle], opt);
    [t_h, y_h] = ode45(ode_fwd, [0, 40], [k0_val; c0_hi], opt);
    [t_l, y_l] = ode45(ode_fwd, [0, 40], [k0_val; c0_lo], opt);

    % Common time grid up to max duration
    N_frames = 34;
    T_max = 18; % By t=18, path H has collapsed and path L has overaccumulated
    t_frames = linspace(0, T_max, N_frames);

    fig = figure('Visible', 'off', 'Color', colors.paper, 'Position', [100, 100, 960, 500]);

    % Left Subplot: Phase Portrait
    ax1 = subplot('Position', [0.07, 0.12, 0.44, 0.78]);
    hold(ax1, 'on'); ax1.Color = colors.paper;

    k_grid = linspace(0.1, 7.5, 200);
    c_kdot0 = k_grid.^params.alpha - params.x * k_grid;

    plot(ax1, k_grid, c_kdot0, '-', 'LineWidth', 2.2, 'Color', colors.kdot0, 'DisplayName', 'dk/dt = 0');
    plot(ax1, [k0_star, k0_star], [0, 2.4], '--', 'LineWidth', 2.2, 'Color', colors.cdot0, 'DisplayName', 'dc/dt = 0');
    plot(ax1, k_saddle0, c_saddle0, ':', 'LineWidth', 1.8, 'Color', [0.70, 0.85, 0.78], 'DisplayName', 'Saddle path');
    plot(ax1, k0_star, c0_star, 'p', 'MarkerSize', 10, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    % Dynamic paths
    h_trail_h = plot(ax1, nan, nan, '-', 'LineWidth', 2.6, 'Color', colors.diverge_hi, 'DisplayName', 'Path H (c_0 > c_0^*)');
    h_trail_s = plot(ax1, nan, nan, '-', 'LineWidth', 2.8, 'Color', colors.saddle, 'DisplayName', 'Path S (c_0 = c_0^*)');
    h_trail_l = plot(ax1, nan, nan, '-', 'LineWidth', 2.6, 'Color', colors.diverge_lo, 'DisplayName', 'Path L (c_0 < c_0^*)');

    h_dot_h = plot(ax1, nan, nan, 's', 'MarkerSize', 8, 'MarkerFaceColor', colors.diverge_hi, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    h_dot_s = plot(ax1, nan, nan, 'o', 'MarkerSize', 9, 'MarkerFaceColor', colors.saddle, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    h_dot_l = plot(ax1, nan, nan, 'd', 'MarkerSize', 8, 'MarkerFaceColor', colors.diverge_lo, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    xlim(ax1, [0.1, 7.2]); ylim(ax1, [0.2, 2.2]);
    grid(ax1, 'on'); box(ax1, 'off');
    xlabel(ax1, 'Capital k', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax1, 'Consumption c', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax1, 'Phase Plane: 3 Candidate Trajectories', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax1, 'Location', 'northwest', 'Box', 'off', 'FontSize', 8);

    % Right Subplot: Capital Stock Evolution k(t)
    ax2 = subplot('Position', [0.58, 0.12, 0.38, 0.78]);
    hold(ax2, 'on'); ax2.Color = colors.paper;

    plot(ax2, [0, T_max], [k0_star, k0_star], '--', 'LineWidth', 1.8, 'Color', colors.steady, 'DisplayName', 'k^* steady state');
    plot(ax2, [0, T_max], [0, 0], 'k-', 'LineWidth', 1.2, 'HandleVisibility', 'off');

    h_kt_h = plot(ax2, nan, nan, '-', 'LineWidth', 2.6, 'Color', colors.diverge_hi, 'DisplayName', 'k_H(t): Capital Exhaustion');
    h_kt_s = plot(ax2, nan, nan, '-', 'LineWidth', 2.8, 'Color', colors.saddle, 'DisplayName', 'k_S(t): Converges to k^*');
    h_kt_l = plot(ax2, nan, nan, '-', 'LineWidth', 2.6, 'Color', colors.diverge_lo, 'DisplayName', 'k_L(t): TVC Violated');

    % Status alert text (Normalized coordinates, bottom-right)
    h_status = text(ax2, 0.05, 0.85, '', 'Units', 'normalized', 'FontName', 'Consolas', 'FontSize', 9.0, ...
                    'Color', colors.ink, 'BackgroundColor', [1, 1, 1, 0.85], 'EdgeColor', [0.8, 0.8, 0.8]);

    xlim(ax2, [0, T_max]); ylim(ax2, [0, 8.0]);
    grid(ax2, 'on'); box(ax2, 'off');
    xlabel(ax2, 'Time t', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax2, 'Capital Stock k(t)', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax2, 'Capital Accumulation over Time', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax2, 'Location', 'southeast', 'Box', 'off', 'FontSize', 8.5);

    % Render Frames
    for f = 1:N_frames
        t_curr = t_frames(f);

        % Path H
        idx_h = find(t_h <= t_curr);
        if isempty(idx_h), idx_h = 1; end
        h_trail_h.XData = y_h(idx_h, 1);
        h_trail_h.YData = y_h(idx_h, 2);
        h_dot_h.XData = y_h(idx_h(end), 1);
        h_dot_h.YData = y_h(idx_h(end), 2);
        h_kt_h.XData = t_h(idx_h);
        h_kt_h.YData = y_h(idx_h, 1);

        % Path S
        idx_s = find(t_s <= t_curr);
        if isempty(idx_s), idx_s = 1; end
        h_trail_s.XData = y_s(idx_s, 1);
        h_trail_s.YData = y_s(idx_s, 2);
        h_dot_s.XData = y_s(idx_s(end), 1);
        h_dot_s.YData = y_s(idx_s(end), 2);
        h_kt_s.XData = t_s(idx_s);
        h_kt_s.YData = y_s(idx_s, 1);

        % Path L
        idx_l = find(t_l <= t_curr);
        if isempty(idx_l), idx_l = 1; end
        h_trail_l.XData = y_l(idx_l, 1);
        h_trail_l.YData = y_l(idx_l, 2);
        h_dot_l.XData = y_l(idx_l(end), 1);
        h_dot_l.YData = y_l(idx_l(end), 2);
        h_kt_l.XData = t_l(idx_l);
        h_kt_l.YData = y_l(idx_l, 1);

        % Diagnosis status text
        msg_h = 'c0 too high -> k depleting';
        if y_h(idx_h(end), 1) <= 0.15, msg_h = 'CRASH: k -> 0 (Exhausted!)'; end
        msg_s = sprintf('c0 optimal -> k -> %.2f (Stable)', k0_star);
        msg_l = 'c0 too low -> overaccumulating';
        if y_l(idx_l(end), 1) >= 6.0, msg_l = 'INEFFICIENT: TVC Violated!'; end

        h_status.String = sprintf('[t = %4.1f]\nRed:    %s\nGreen:  %s\nPurple: %s', ...
                                  t_curr, msg_h, msg_s, msg_l);

        % Frame Capture
        temp_png = [tempname '.png'];
        exportgraphics(fig, temp_png, 'Resolution', 120);
        img = imread(temp_png);
        delete(temp_png);
        [img_ind, cmap] = rgb2ind(img, 256);

        delay = 0.08;
        if f == N_frames, delay = 1.30; end

        if f == 1
            imwrite(img_ind, cmap, gif_file, 'gif', 'LoopCount', Inf, 'DelayTime', delay);
        else
            imwrite(img_ind, cmap, gif_file, 'gif', 'WriteMode', 'append', 'DelayTime', delay);
        end
    end
    close(fig);
    fprintf('Saved: %s\n', gif_file);
end

% -------------------------------------------------------------------------
% GIF 3: Comparative Dynamics: Permanent Shock \rho \downarrow (Vertical Jump)
% -------------------------------------------------------------------------
function generate_gif_3_discount_shock(gif_dir, params, colors, k0_star, c0_star, k1_star, c1_star, ...
                                      k_saddle0, c_saddle0, k_saddle1, c_saddle1, c_shock_jump)
    fprintf('Generating GIF 3: Discount Rate Shock & Jump Dynamics...\n');
    gif_file = fullfile(gif_dir, 'ramsey-discount-rate-shock.gif');
    if exist(gif_file, 'file'), delete(gif_file); end

    denom1 = params.rho1 + params.delta + params.theta * params.g;
    ode_fwd1 = @(t, y) [y(1)^params.alpha - y(2) - params.x * y(1); ...
                        (y(2)/params.theta) * (params.alpha * y(1)^(params.alpha - 1) - denom1)];
    opt = odeset('RelTol', 1e-6, 'AbsTol', 1e-8);
    [t_trans, y_trans] = ode45(ode_fwd1, [0, 40], [k0_star; c_shock_jump], opt);

    N_pre = 6;
    N_jump = 4;
    N_trans = 26;

    fig = figure('Visible', 'off', 'Color', colors.paper, 'Position', [100, 100, 960, 500]);

    % Left Subplot: Phase Plane
    ax1 = subplot('Position', [0.07, 0.12, 0.44, 0.78]);
    hold(ax1, 'on'); ax1.Color = colors.paper;

    k_grid = linspace(2.0, 7.0, 200);
    c_kdot0 = k_grid.^params.alpha - params.x * k_grid;

    % Fixed curves
    plot(ax1, k_grid, c_kdot0, '-', 'LineWidth', 2.2, 'Color', colors.kdot0, 'DisplayName', 'dk/dt = 0');
    plot(ax1, [k0_star, k0_star], [0, 2.4], ':', 'LineWidth', 2.0, 'Color', [0.65, 0.70, 0.78], 'DisplayName', 'Old dc/dt = 0');
    plot(ax1, [k1_star, k1_star], [0, 2.4], '--', 'LineWidth', 2.4, 'Color', colors.cdot0, 'DisplayName', 'New dc/dt = 0');

    plot(ax1, k_saddle0, c_saddle0, ':', 'LineWidth', 1.8, 'Color', [0.70, 0.85, 0.75], 'DisplayName', 'Old saddle (\rho=0.04)');
    plot(ax1, k_saddle1, c_saddle1, '-', 'LineWidth', 2.6, 'Color', [0.60, 0.75, 0.95], 'DisplayName', 'New saddle (\rho=0.02)');

    % Steady states (HandleVisibility = off)
    plot(ax1, k0_star, c0_star, 'o', 'MarkerSize', 8, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    plot(ax1, k1_star, c1_star, 'p', 'MarkerSize', 10, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    text(ax1, k0_star - 0.45, c0_star + 0.08, 'E_0^*', 'FontWeight', 'bold', 'FontSize', 10, 'Color', colors.ink);
    text(ax1, k1_star + 0.15, c1_star - 0.05, 'E_1^*', 'FontWeight', 'bold', 'FontSize', 10, 'Color', colors.ink);

    % Dynamic objects
    h_jump_line = plot(ax1, nan, nan, 'r--', 'LineWidth', 2.2, 'DisplayName', 'Vertical Jump \Delta c');
    h_trans_line = plot(ax1, nan, nan, '-', 'LineWidth', 3.0, 'Color', colors.saddle_post, 'DisplayName', 'Transition to E_1^*');
    h_moving_dot = plot(ax1, nan, nan, 'o', 'MarkerSize', 9, 'MarkerFaceColor', [0.90, 0.20, 0.20], ...
                        'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    xlim(ax1, [2.5, 6.5]); ylim(ax1, [0.8, 1.8]);
    grid(ax1, 'on'); box(ax1, 'off');
    xlabel(ax1, 'Capital k', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax1, 'Consumption c', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax1, 'Phase Plane: Vertical Jump & Transition', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax1, 'Location', 'northwest', 'Box', 'off', 'FontSize', 8);

    % Right Subplot: Time Series
    ax2 = subplot('Position', [0.58, 0.12, 0.38, 0.78]);
    hold(ax2, 'on'); ax2.Color = colors.paper;

    % Target lines
    plot(ax2, [-6, 40], [k1_star, k1_star], '--', 'LineWidth', 1.5, 'Color', colors.cdot0, 'DisplayName', 'New k_1^*');
    plot(ax2, [-6, 40], [c1_star, c1_star], '--', 'LineWidth', 1.5, 'Color', colors.kdot0, 'DisplayName', 'New c_1^*');

    h_ts_k = plot(ax2, nan, nan, '-', 'LineWidth', 2.8, 'Color', colors.cdot0, 'DisplayName', 'k(t) [Capital]');
    h_ts_c = plot(ax2, nan, nan, '-', 'LineWidth', 2.8, 'Color', colors.kdot0, 'DisplayName', 'c(t) [Consumption]');
    h_ts_dot_k = plot(ax2, nan, nan, 'o', 'MarkerSize', 7, 'MarkerFaceColor', colors.cdot0, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    h_ts_dot_c = plot(ax2, nan, nan, 'o', 'MarkerSize', 7, 'MarkerFaceColor', colors.kdot0, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    % Information box (Normalized coordinates, top-left)
    h_ts_info = text(ax2, 0.05, 0.85, '', 'Units', 'normalized', 'FontName', 'Consolas', 'FontSize', 9.0, ...
                     'Color', colors.ink, 'BackgroundColor', [1, 1, 1, 0.85], 'EdgeColor', [0.8, 0.8, 0.8]);

    xlim(ax2, [-6, 40]); ylim(ax2, [0.8, 5.8]);
    grid(ax2, 'on'); box(ax2, 'off');
    xlabel(ax2, 'Time t (Shock at t = 0)', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax2, 'Levels (k, c)', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax2, 'Time Series: Discontinuous Jump in c', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax2, 'Location', 'southeast', 'Box', 'off', 'FontSize', 8.5);

    % Simulation time arrays
    t_pre_vals = linspace(-6, 0, N_pre);
    t_trans_grid = linspace(0, 40, N_trans);
    k_trans_grid = interp1(t_trans, y_trans(:, 1), t_trans_grid, 'pchip');
    c_trans_grid = interp1(t_trans, y_trans(:, 2), t_trans_grid, 'pchip');

    total_frames = N_pre + N_jump + N_trans;
    for f = 1:total_frames
        if f <= N_pre
            % Pre-shock steady state
            curr_k = k0_star; curr_c = c0_star;
            curr_t = t_pre_vals(f);
            h_moving_dot.XData = curr_k; h_moving_dot.YData = curr_c;
            h_moving_dot.MarkerFaceColor = colors.steady;

            h_jump_line.XData = nan; h_jump_line.YData = nan;
            h_trans_line.XData = nan; h_trans_line.YData = nan;

            h_ts_k.XData = t_pre_vals(1:f); h_ts_k.YData = repmat(k0_star, 1, f);
            h_ts_c.XData = t_pre_vals(1:f); h_ts_c.YData = repmat(c0_star, 1, f);
            h_ts_dot_k.XData = curr_t; h_ts_dot_k.YData = curr_k;
            h_ts_dot_c.XData = curr_t; h_ts_dot_c.YData = curr_c;

            h_ts_info.String = sprintf('[t = %4.1f] Steady State E0*\nrho = 0.04 (Normal)\nk = %.3f, c = %.3f', ...
                                      curr_t, curr_k, curr_c);
        elseif f <= N_pre + N_jump
            % Vertical Jump at t = 0
            jf = f - N_pre;
            alpha_jump = jf / N_jump;
            curr_k = k0_star; % Capital is predetermined!
            curr_c = (1 - alpha_jump) * c0_star + alpha_jump * c_shock_jump;
            curr_t = 0;

            h_moving_dot.XData = curr_k; h_moving_dot.YData = curr_c;
            h_moving_dot.MarkerFaceColor = [0.90, 0.20, 0.20];

            h_jump_line.XData = [k0_star, k0_star];
            h_jump_line.YData = [c0_star, curr_c];

            h_ts_k.XData = [t_pre_vals, 0]; h_ts_k.YData = [repmat(k0_star, 1, N_pre), k0_star];
            h_ts_c.XData = [t_pre_vals, 0]; h_ts_c.YData = [repmat(c0_star, 1, N_pre), curr_c];
            h_ts_dot_k.XData = 0; h_ts_dot_k.YData = curr_k;
            h_ts_dot_c.XData = 0; h_ts_dot_c.YData = curr_c;

            h_ts_info.String = sprintf('[t = 0.0] SHOCK: rho -> 0.02!\nk(0) = %.3f (NO horizontal jump)\nc(0+) = %.3f (VERTICAL JUMP DOWN)\nDelta c = %.3f (Save more!)', ...
                                      curr_k, curr_c, curr_c - c0_star);
        else
            % Transition along new saddle path
            tf = f - (N_pre + N_jump);
            curr_k = k_trans_grid(tf);
            curr_c = c_trans_grid(tf);
            curr_t = t_trans_grid(tf);

            h_moving_dot.XData = curr_k; h_moving_dot.YData = curr_c;
            h_moving_dot.MarkerFaceColor = colors.saddle_post;

            h_jump_line.XData = [k0_star, k0_star];
            h_jump_line.YData = [c0_star, c_shock_jump];

            h_trans_line.XData = k_trans_grid(1:tf);
            h_trans_line.YData = c_trans_grid(1:tf);

            all_t = [t_pre_vals, 0, t_trans_grid(1:tf)];
            all_k = [repmat(k0_star, 1, N_pre), k0_star, k_trans_grid(1:tf)];
            all_c = [repmat(c0_star, 1, N_pre), c_shock_jump, c_trans_grid(1:tf)];

            h_ts_k.XData = all_t; h_ts_k.YData = all_k;
            h_ts_c.XData = all_t; h_ts_c.YData = all_c;
            h_ts_dot_k.XData = curr_t; h_ts_dot_k.YData = curr_k;
            h_ts_dot_c.XData = curr_t; h_ts_dot_c.YData = curr_c;

            h_ts_info.String = sprintf('[t = %4.1f] Transition to E1*\nk(t) = %5.3f -> %5.3f\nc(t) = %5.3f -> %5.3f\nCapital accumulating (k_dot > 0)', ...
                                      curr_t, curr_k, k1_star, curr_c, c1_star);
        end

        % Frame Capture
        temp_png = [tempname '.png'];
        exportgraphics(fig, temp_png, 'Resolution', 120);
        img = imread(temp_png);
        delete(temp_png);
        [img_ind, cmap] = rgb2ind(img, 256);

        delay = 0.08;
        if f == total_frames, delay = 1.30; end

        if f == 1
            imwrite(img_ind, cmap, gif_file, 'gif', 'LoopCount', Inf, 'DelayTime', delay);
        else
            imwrite(img_ind, cmap, gif_file, 'gif', 'WriteMode', 'append', 'DelayTime', delay);
        end
    end
    close(fig);
    fprintf('Saved: %s\n', gif_file);
end

% -------------------------------------------------------------------------
% GIF 4: Numerical Shooting Algorithm (Bisection Search for Saddle Path)
% -------------------------------------------------------------------------
function generate_gif_4_shooting(gif_dir, params, colors, k0_star, c0_star, k_saddle0, c_saddle0)
    fprintf('Generating GIF 4: Numerical Shooting Algorithm...\n');
    gif_file = fullfile(gif_dir, 'ramsey-shooting-algorithm.gif');
    if exist(gif_file, 'file'), delete(gif_file); end

    k0_val = 2.0;
    c0_true = interp1(k_saddle0, c_saddle0, k0_val, 'pchip');

    denom0 = params.rho0 + params.delta + params.theta * params.g;
    ode_fwd = @(t, y) [y(1)^params.alpha - y(2) - params.x * y(1); ...
                       (y(2)/params.theta) * (params.alpha * y(1)^(params.alpha - 1) - denom0)];
    opt = odeset('RelTol', 1e-6, 'AbsTol', 1e-8, 'Events', @event_forward);

    % Run 6 iterations of bisection
    c_low = 0.40;
    c_high = 1.40;
    N_iters = 6;
    shoot_data = cell(N_iters, 1);

    for j = 1:N_iters
        c_guess = (c_low + c_high) / 2;
        [t_sim, y_sim, te, ye, ie] = ode45(ode_fwd, [0, 45], [k0_val; c_guess], opt);

        % Determine overshoot or undershoot
        if ~isempty(ie) && any(ie == 1)
            type = 'Overshoot (Capital Exhausted)';
            is_over = true;
            c_high = c_guess;
        elseif ~isempty(ie) && any(ie == 3)
            type = 'Undershoot (TVC Violation)';
            is_over = false;
            c_low = c_guess;
        else
            if y_sim(end, 1) < k0_star
                type = 'Overshoot'; is_over = true; c_high = c_guess;
            else
                type = 'Undershoot'; is_over = false; c_low = c_guess;
            end
        end

        s = struct();
        s.iter = j;
        s.c_guess = c_guess;
        s.type = type;
        s.is_over = is_over;
        s.t = t_sim;
        s.y = y_sim;
        s.c_low = c_low;
        s.c_high = c_high;
        shoot_data{j} = s;
    end

    fig = figure('Visible', 'off', 'Color', colors.paper, 'Position', [100, 100, 960, 500]);

    % Left Subplot: Phase Plane Shooting
    ax1 = subplot('Position', [0.07, 0.12, 0.44, 0.78]);
    hold(ax1, 'on'); ax1.Color = colors.paper;

    k_grid = linspace(0.1, 7.5, 200);
    c_kdot0 = k_grid.^params.alpha - params.x * k_grid;

    plot(ax1, k_grid, c_kdot0, '-', 'LineWidth', 2.0, 'Color', colors.kdot0, 'DisplayName', 'dk/dt = 0');
    plot(ax1, [k0_star, k0_star], [0, 2.4], '--', 'LineWidth', 2.0, 'Color', colors.cdot0, 'DisplayName', 'dc/dt = 0');
    plot(ax1, k_saddle0, c_saddle0, ':', 'LineWidth', 1.8, 'Color', [0.70, 0.85, 0.78], 'DisplayName', 'True saddle path');

    % Target E0* bullseye (HandleVisibility = off)
    plot(ax1, k0_star, c0_star, 'o', 'MarkerSize', 16, 'MarkerFaceColor', 'none', 'MarkerEdgeColor', [0.90, 0.25, 0.15], ...
         'LineWidth', 1.8, 'HandleVisibility', 'off');
    plot(ax1, k0_star, c0_star, 'o', 'MarkerSize', 8, 'MarkerFaceColor', colors.steady, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');
    text(ax1, k0_star + 0.20, c0_star, 'Target E^*', 'FontWeight', 'bold', 'FontSize', 10, 'Color', colors.ink);

    % Handle arrays for iterations
    h_hist_lines = gobjects(N_iters, 1);
    for j = 1:N_iters
        h_hist_lines(j) = plot(ax1, nan, nan, '-', 'LineWidth', 1.5, 'Color', [0.75, 0.75, 0.75], 'HandleVisibility', 'off');
    end
    h_active_line = plot(ax1, nan, nan, '-', 'LineWidth', 3.0, 'Color', colors.saddle, 'DisplayName', 'Current Shoot Trajectory');
    h_active_dot  = plot(ax1, nan, nan, 'o', 'MarkerSize', 9, 'MarkerFaceColor', colors.saddle, 'MarkerEdgeColor', colors.ink, 'HandleVisibility', 'off');

    xlim(ax1, [0.1, 7.2]); ylim(ax1, [0.2, 2.2]);
    grid(ax1, 'on'); box(ax1, 'off');
    xlabel(ax1, 'Capital k', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax1, 'Consumption c', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax1, 'Phase Plane: Bisection Shooting', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax1, 'Location', 'northwest', 'Box', 'off', 'FontSize', 8);

    % Right Subplot: Bisection Search Interval [c_low, c_high]
    ax2 = subplot('Position', [0.58, 0.12, 0.38, 0.78]);
    hold(ax2, 'on'); ax2.Color = colors.paper;

    % Target true c0
    plot(ax2, [0, N_iters + 1], [c0_true, c0_true], '--', 'LineWidth', 2.0, 'Color', colors.saddle, ...
         'DisplayName', sprintf('True c_0^* = %.4f', c0_true));

    h_bar_low  = plot(ax2, nan, nan, 'v-', 'LineWidth', 1.8, 'Color', colors.diverge_lo, 'DisplayName', 'Lower Bound c_{low}');
    h_bar_high = plot(ax2, nan, nan, '^-', 'LineWidth', 1.8, 'Color', colors.diverge_hi, 'DisplayName', 'Upper Bound c_{high}');
    h_guess    = plot(ax2, nan, nan, 'o-', 'LineWidth', 2.2, 'Color', colors.ink, 'DisplayName', 'Midpoint Guess c_0^{(j)}');

    % Information box (Normalized coordinates, top-left)
    h_shoot_info = text(ax2, 0.05, 0.85, '', 'Units', 'normalized', 'FontName', 'Consolas', 'FontSize', 9.0, ...
                        'Color', colors.ink, 'BackgroundColor', [1, 1, 1, 0.85], 'EdgeColor', [0.8, 0.8, 0.8]);

    xlim(ax2, [0.5, N_iters + 0.5]); ylim(ax2, [0.35, 1.45]);
    grid(ax2, 'on'); box(ax2, 'off');
    xlabel(ax2, 'Iteration j', 'FontSize', 11, 'FontWeight', 'bold');
    ylabel(ax2, 'Initial Guess c_0', 'FontSize', 11, 'FontWeight', 'bold');
    title(ax2, 'Exponential Convergence of Bounds', 'FontSize', 12, 'FontWeight', 'bold');
    legend(ax2, 'Location', 'southeast', 'Box', 'off', 'FontSize', 8.5);

    % Render frame sequence
    frames_per_iter = 5;
    hist_low = []; hist_high = []; hist_guess = [];

    frame_count = 0;
    for j = 1:N_iters
        s = shoot_data{j};
        t_sim = s.t; y_sim = s.y;
        n_pts = length(t_sim);

        % Color for active line
        if s.is_over
            cur_col = colors.diverge_hi;
        else
            cur_col = colors.diverge_lo;
        end
        if j == N_iters, cur_col = colors.saddle; end
        h_active_line.Color = cur_col;
        h_active_dot.MarkerFaceColor = cur_col;

        hist_guess = [hist_guess, s.c_guess];
        hist_low   = [hist_low, s.c_low];
        hist_high  = [hist_high, s.c_high];

        for step = 1:frames_per_iter
            frame_count = frame_count + 1;
            pt_idx = round((step / frames_per_iter) * n_pts);
            if pt_idx < 1, pt_idx = 1; end

            % Animate current trajectory
            h_active_line.XData = y_sim(1:pt_idx, 1);
            h_active_line.YData = y_sim(1:pt_idx, 2);
            h_active_dot.XData = y_sim(pt_idx, 1);
            h_active_dot.YData = y_sim(pt_idx, 2);

            % Update Right panel
            h_guess.XData = 1:j; h_guess.YData = hist_guess;
            h_bar_low.XData = 1:j; h_bar_low.YData = hist_low;
            h_bar_high.XData = 1:j; h_bar_high.YData = hist_high;

            err = abs(s.c_guess - c0_true);
            h_shoot_info.String = sprintf('[Iter %d / %d]\nGuess c0  = %7.5f\nError |e| = %7.5f\nOutcome:  %s', ...
                                          j, N_iters, s.c_guess, err, s.type);

            % Capture frame
            temp_png = [tempname '.png'];
            exportgraphics(fig, temp_png, 'Resolution', 120);
            img = imread(temp_png);
            delete(temp_png);
            [img_ind, cmap] = rgb2ind(img, 256);

            delay = 0.09;
            if step == frames_per_iter && j < N_iters, delay = 0.35; end
            if j == N_iters && step == frames_per_iter, delay = 1.40; end

            if frame_count == 1
                imwrite(img_ind, cmap, gif_file, 'gif', 'LoopCount', Inf, 'DelayTime', delay);
            else
                imwrite(img_ind, cmap, gif_file, 'gif', 'WriteMode', 'append', 'DelayTime', delay);
            end
        end

        % Archive trajectory into faint background history
        h_hist_lines(j).XData = y_sim(:, 1);
        h_hist_lines(j).YData = y_sim(:, 2);
        h_hist_lines(j).Color = [cur_col, 0.45]; % Semi-transparent
    end
    close(fig);
    fprintf('Saved: %s\n', gif_file);
end

% -------------------------------------------------------------------------
% Save JSON Metadata
% -------------------------------------------------------------------------
function save_metadata(data_dir, params, k0_star, c0_star, k1_star, c1_star, k_GR, c_GR, ...
                       lambda0_stable, lambda0_unstable, v0_stable, c_shock_jump)
    meta = struct();
    meta.title = 'Ramsey-Cass-Koopmans Model Saddle Path Dynamics & Shooting Algorithm';
    meta.generator = 'supplements/matlab/ramsey_saddle_path.m';
    meta.matlab_version = version;
    meta.timestamp = char(datetime('now', 'Format', 'yyyy-MM-dd HH:mm:ss'));

    meta.parameters = struct('alpha', params.alpha, ...
                             'theta', params.theta, ...
                             'n', params.n, ...
                             'g', params.g, ...
                             'delta', params.delta, ...
                             'effective_depreciation_x', params.x, ...
                             'rho_baseline', params.rho0, ...
                             'rho_shock', params.rho1);

    meta.steady_states = struct(...
        'baseline', struct('k_star', k0_star, 'c_star', c0_star, ...
                           'output_y', k0_star^params.alpha, ...
                           'saving_rate', (k0_star^params.alpha - c0_star) / (k0_star^params.alpha), ...
                           'stable_eigenvalue', lambda0_stable, ...
                           'unstable_eigenvalue', lambda0_unstable, ...
                           'stable_eigenvector', v0_stable), ...
        'post_shock', struct('k_star', k1_star, 'c_star', c1_star, ...
                             'output_y', k1_star^params.alpha, ...
                             'saving_rate', (k1_star^params.alpha - c1_star) / (k1_star^params.alpha)), ...
        'golden_rule', struct('k_GR', k_GR, 'c_GR', c_GR));

    meta.comparative_dynamics = struct(...
        'shock_type', 'Permanent drop in discount rate rho from 0.04 to 0.02', ...
        'predetermined_capital_k0', k0_star, ...
        'pre_shock_consumption', c0_star, ...
        'jump_consumption_c_t0_plus', c_shock_jump, ...
        'vertical_jump_delta_c', c_shock_jump - c0_star, ...
        'long_run_capital_change', k1_star - k0_star, ...
        'long_run_consumption_change', c1_star - c0_star);

    json_path = fullfile(data_dir, 'ramsey-saddle-path-metadata.json');
    fid = fopen(json_path, 'w', 'n', 'UTF-8');
    assert(fid ~= -1, 'Could not create JSON file');
    fwrite(fid, jsonencode(meta, 'PrettyPrint', true), 'char');
    fclose(fid);
    fprintf('Saved metadata: %s\n', json_path);
end
