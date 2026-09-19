% ols_projection_geometry.m
% =========================================================================
% OLS Vector Space Geometry, Normal Equations, and Projection Matrix
% =========================================================================
%
% This script produces publication-grade figures and metadata for the
% Graduate Economics supplement:
%   "OLS 직교사영과 정상방정식의 벡터 기하" (OLS Projection Geometry)
%
% Theoretical Foundation:
%   Observation Space R^n, rank(X) = k
%   Grand Equivalence:
%     \nabla_\beta S(\hat{\beta}) = 0 (Optimization in Parameter Space)
%     \iff X' \hat{e} = 0              (Algebra: Normal Equations)
%     \iff \hat{e} \perp C(X)          (Geometry: Subspace Orthogonality)
%     \iff \hat{y} = P_X y             (Projection Operator)
%
% Figures generated:
%   1. ols-projection-dual-panel.png:
%      Optimization (Parameter Space) <-> Projection (Observation Space R^3)
%   2. ols-projection-variable-addition.png:
%      Nested Spaces C(X_0) \subset C(X_1), RSS (14/3 -> 8/3), R^2 (0 -> 3/7)
%   3. ols-projection-multicollinearity.png:
%      Same Subspace, Bad Coordinates, Numerical Stability Diagnostic (n=6, k=3)
%
% Numerical Principles:
%   - Backslash X \ y for coordinates (avoids squaring condition number)
%   - Thin QR decomposition for orthogonal projections (Q * (Q' * y))
% =========================================================================

clear; close all; clc;

% -------------------------------------------------------------------------
% 0. Paths and Environment Setup
% -------------------------------------------------------------------------
isOctave = exist('OCTAVE_VERSION', 'builtin') ~= 0;

script_path = mfilename('fullpath');
if isempty(script_path)
    root_dir = pwd;
else
    root_dir = fileparts(fileparts(fileparts(script_path)));
end

img_dir = fullfile(root_dir, 'assets', 'images');
data_dir = fullfile(root_dir, 'assets', 'data');
if ~exist(img_dir, 'dir'), mkdir(img_dir); end
if ~exist(data_dir, 'dir'), mkdir(data_dir); end

% Consistent Color Palette
c_bg        = [0.99, 0.985, 0.97];  % Warm paper background
c_dark      = [0.15, 0.20, 0.28];  % Navy/charcoal text & main vectors
c_teal      = [0.10, 0.44, 0.40];  % Forest Teal (subspace & projections)
c_teal_lite = [0.82, 0.91, 0.89];  % Plane face tint
c_rust      = [0.72, 0.30, 0.18];  % Terracotta / Rust (residuals & errors)
c_gold      = [0.78, 0.55, 0.18];  % Amber gold (baseline intercept-only)
c_gray      = [0.50, 0.55, 0.60];  % Basis vectors / neutral lines

% Configure root graphics defaults for LaTeX
if ~isOctave
    set(groot, 'defaultTextInterpreter', 'latex');
    set(groot, 'defaultAxesTickLabelInterpreter', 'latex');
    set(groot, 'defaultLegendInterpreter', 'latex');
end

save_fig = @(fig, filename) save_figure_cross(fig, filename, isOctave);

% =========================================================================
% FIGURE 1: Dual-Panel Optimization <-> Observation Space Projection
% =========================================================================
fprintf('Generating Figure 1: Dual-Panel Projection Geometry...\n');

% Exact Setup: n = 3, k = 2
ones3 = [1; 1; 1];
x_vec = [-1; 0; 1];
X = [ones3, x_vec];
y = [2; 1; 4];

% Numerical solution via QR and backslash
[Q, ~] = qr(X, 0);
beta_hat = X \ y;           % [7/3; 1]
y_hat = Q * (Q' * y);       % [4/3; 7/3; 10/3]
e_hat = y - y_hat;          % [2/3; -4/3; 2/3]

XtX = X' * X;               % diag(3, 2)
err_norm_eq = norm(X' * e_hat);
y_norm_sq = norm(y)^2;
y_hat_norm_sq = norm(y_hat)^2;
e_hat_norm_sq = norm(e_hat)^2;

y_bar = mean(y);
TSS = norm(y - y_bar * ones3)^2;
ESS = norm(y_hat - y_bar * ones3)^2;
RSS = norm(e_hat)^2;

fig1 = figure('Position', [50, 50, 1300, 620], 'Color', c_bg, 'Visible', 'off');
tl1 = tiledlayout(fig1, 1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

% --- Left Panel: Parameter Space R^2 ---
ax1 = nexttile(tl1, 1); hold(ax1, 'on'); box(ax1, 'on');
b0_grid = linspace(0.5, 4.2, 300);
b1_grid = linspace(-0.5, 2.5, 300);
[B0, B1] = meshgrid(b0_grid, b1_grid);
S_grid = 8/3 + 3 * (B0 - 7/3).^2 + 2 * (B1 - 1).^2;

levels = [8/3 + 0.12, 3.2, 4.0, 5.5, 8.0, 12.0, 18.0, 26.0];
[C_mat, h_c] = contour(ax1, B0, B1, S_grid, levels, 'Color', [0.65, 0.72, 0.78], 'LineWidth', 1.2);
clabel(C_mat, h_c, 'Color', [0.40, 0.45, 0.50], 'FontSize', 8, 'LabelSpacing', 240);

% Candidate interpolation path: beta(t) = (1-t)*beta_start + t*beta_hat
beta_start = [1.0; 0.0];
t_vals = linspace(0, 1, 100);
path_beta = (1 - t_vals) .* beta_start + t_vals .* beta_hat;
plot(ax1, path_beta(1, :), path_beta(2, :), '--', 'Color', c_rust, 'LineWidth', 2.0);

% Quiver on path
arrow_t = 0.48;
arrow_pt = (1 - arrow_t) * beta_start + arrow_t * beta_hat;
arrow_dir = 0.35 * (beta_hat - beta_start) / norm(beta_hat - beta_start);
quiver(ax1, arrow_pt(1), arrow_pt(2), arrow_dir(1), arrow_dir(2), 0, ...
    'Color', c_rust, 'LineWidth', 2.2, 'MaxHeadSize', 0.6);

plot(ax1, beta_start(1), beta_start(2), 'o', 'MarkerSize', 8, ...
    'MarkerFaceColor', [0.85, 0.88, 0.90], 'MarkerEdgeColor', c_dark, 'LineWidth', 1.5);
text(ax1, beta_start(1) - 0.05, beta_start(2) - 0.18, '$\beta^{(0)} = (1, 0)^T$', ...
    'FontSize', 10, 'FontWeight', 'bold', 'Color', c_dark, 'Interpreter', 'latex');

plot(ax1, beta_hat(1), beta_hat(2), 'p', 'MarkerSize', 15, ...
    'MarkerFaceColor', c_teal, 'MarkerEdgeColor', c_dark, 'LineWidth', 1.5);
text(ax1, beta_hat(1) + 0.08, beta_hat(2) + 0.08, ...
    '$\hat{\beta} = (7/3, 1)^T, \quad S(\hat{\beta}) = 8/3 \approx 2.667$', ...
    'FontSize', 10.5, 'FontWeight', 'bold', 'Color', c_teal, 'Interpreter', 'latex');

xlabel(ax1, '$\beta_0$ (constant)', 'FontSize', 11, 'FontWeight', 'bold', 'Interpreter', 'latex');
ylabel(ax1, '$\beta_1$ (slope)', 'FontSize', 11, 'FontWeight', 'bold', 'Interpreter', 'latex');
title(ax1, 'Parameter Space: $S(\beta) = \frac{8}{3} + 3\left(\beta_0 - \frac{7}{3}\right)^2 + 2(\beta_1 - 1)^2$', ...
    'FontSize', 11, 'Color', c_dark, 'Interpreter', 'latex');
grid(ax1, 'on'); xlim(ax1, [0.6, 4.0]); ylim(ax1, [-0.4, 2.4]);

% --- Right Panel: Observation Space R^3 ---
ax2 = nexttile(tl1, 2); hold(ax2, 'on'); grid(ax2, 'on'); box(ax2, 'on');
view(ax2, -40, 22);

% Subspace Plane C(X): u*1 + v*x (broadened floor patch)
[u_pl, v_pl] = meshgrid(linspace(-0.6, 3.6, 35), linspace(-2.2, 2.2, 35));
pl_x = u_pl * ones3(1) + v_pl * x_vec(1);
pl_y = u_pl * ones3(2) + v_pl * x_vec(2);
pl_z = u_pl * ones3(3) + v_pl * x_vec(3);
surf(ax2, pl_x, pl_y, pl_z, 'FaceColor', c_teal_lite, 'FaceAlpha', 0.38, ...
    'EdgeColor', [0.70, 0.80, 0.78], 'EdgeAlpha', 0.4);

draw_vec3 = @(ax, o, v, col, w) quiver3(ax, o(1), o(2), o(3), v(1), v(2), v(3), 0, ...
    'Color', col, 'LineWidth', w, 'MaxHeadSize', 0.22);

O = [0; 0; 0];
draw_vec3(ax2, O, ones3, c_gray, 2.0);
text(ax2, ones3(1) + 0.15, ones3(2) + 0.05, ones3(3) - 0.15, ' $\mathbf{1} = (1,1,1)^T$', ...
    'FontSize', 9.5, 'Color', [0.35, 0.40, 0.45], 'Interpreter', 'latex');

draw_vec3(ax2, O, x_vec, c_gray, 2.0);
text(ax2, x_vec(1) - 0.25, x_vec(2) - 0.1, x_vec(3) + 0.15, ' $x = (-1,0,1)^T$', ...
    'FontSize', 9.5, 'Color', [0.35, 0.40, 0.45], 'Interpreter', 'latex');

draw_vec3(ax2, O, y, c_dark, 3.0);
text(ax2, y(1) + 0.15, y(2) + 0.05, y(3) + 0.25, ' $y = (2,1,4)^T$', ...
    'FontSize', 11, 'FontWeight', 'bold', 'Color', c_dark, 'Interpreter', 'latex');

draw_vec3(ax2, O, y_hat, c_teal, 3.0);
text(ax2, y_hat(1) - 0.15, y_hat(2) + 0.15, y_hat(3) + 0.1, ...
    ' $\hat{y} = P_X y = (4/3, 7/3, 10/3)^T$', ...
    'FontSize', 10.5, 'FontWeight', 'bold', 'Color', c_teal, 'Interpreter', 'latex', ...
    'HorizontalAlignment', 'right');

draw_vec3(ax2, y_hat, e_hat, c_rust, 3.0);
text(ax2, (y_hat(1)+y(1))/2 - 0.45, (y_hat(2)+y(2))/2 + 0.15, (y_hat(3)+y(3))/2 + 0.35, ...
    ' $\hat{e} \perp \mathcal{C}(X)$', 'FontSize', 11, 'FontWeight', 'bold', 'Color', c_rust, 'Interpreter', 'latex');

% 3D Right-Angle Square Marker at y_hat
s_sq = 0.35;
e_dir = e_hat / norm(e_hat);
yhat_dir = - y_hat / norm(y_hat);
q1 = y_hat + s_sq * yhat_dir;
q2 = q1 + s_sq * e_dir;
q3 = y_hat + s_sq * e_dir;
plot3(ax2, [q1(1), q2(1), q3(1)], [q1(2), q2(2), q3(2)], [q1(3), q2(3), q3(3)], ...
    'Color', c_rust, 'LineWidth', 1.8);

% Candidate point path on plane
z_start = X * beta_start;
path_z = X * path_beta;
plot3(ax2, path_z(1, :), path_z(2, :), path_z(3, :), '--', 'Color', c_rust, 'LineWidth', 1.6);
plot3(ax2, [z_start(1), y(1)], [z_start(2), y(2)], [z_start(3), y(3)], ':', ...
    'Color', [0.70, 0.50, 0.45], 'LineWidth', 1.2);
plot3(ax2, z_start(1), z_start(2), z_start(3), 'o', 'MarkerSize', 7, ...
    'MarkerFaceColor', [0.85, 0.88, 0.90], 'MarkerEdgeColor', c_dark);
text(ax2, z_start(1) + 0.12, z_start(2) - 0.15, z_start(3) - 0.2, '$X\beta^{(0)}$', ...
    'FontSize', 9.5, 'Color', c_dark, 'Interpreter', 'latex');

% Label Subspace plane nicely inside viewing bounds
text(ax2, -0.6, 2.2, 2.8, '$\mathcal{C}(X) = \mathrm{span}\{\mathbf{1}, x\}$', ...
    'FontSize', 11, 'FontWeight', 'bold', 'Color', c_teal, 'Interpreter', 'latex');

xlabel(ax2, 'Obs 1 ($y_1$)', 'FontSize', 10, 'Interpreter', 'latex');
ylabel(ax2, 'Obs 2 ($y_2$)', 'FontSize', 10, 'Interpreter', 'latex');
zlabel(ax2, 'Obs 3 ($y_3$)', 'FontSize', 10, 'Interpreter', 'latex');
xlim(ax2, [-1.5, 3.5]); ylim(ax2, [-1.0, 3.5]); zlim(ax2, [-0.5, 4.8]);
title(ax2, 'Observation Space: $X^T\hat{e} = 0 \iff \hat{e} \perp \mathcal{C}(X) \iff \hat{y} = P_X y$', ...
    'FontSize', 11, 'Color', c_dark, 'Interpreter', 'latex');

% Super title via tiledlayout
title(tl1, '\textbf{Grand Equivalence}: $\min_\beta \|y - X\beta\|^2 \iff X^T\hat{e} = 0 \iff \hat{e} \perp \mathcal{C}(X) \iff \hat{y} = P_X y$', ...
    'FontSize', 13.5, 'Color', c_dark, 'Interpreter', 'latex');

save_fig(fig1, fullfile(img_dir, 'ols-projection-dual-panel.png'));
close(fig1);


% =========================================================================
% FIGURE 2: Variable Addition and Nested Subspaces
% =========================================================================
fprintf('Generating Figure 2: Variable Addition and Nested Subspaces...\n');

% Intercept-only model: X0 = ones3
y_hat_0 = (ones3' * y / (ones3' * ones3)) * ones3; % [7/3; 7/3; 7/3]
e_hat_0 = y - y_hat_0;
RSS_0 = norm(e_hat_0)^2;   % 14/3
R2_0 = 0.0;

% Model with x added: X1 = [ones3, x_vec]
y_hat_1 = y_hat;           % [4/3; 7/3; 10/3]
e_hat_1 = e_hat;
RSS_1 = norm(e_hat_1)^2;   % 8/3
R2_1 = 1 - (RSS_1 / TSS);  % 3/7 approx 0.4286

fig2 = figure('Position', [100, 100, 1050, 720], 'Color', c_bg, 'Visible', 'off');
tl2 = tiledlayout(fig2, 1, 1, 'Padding', 'compact');
ax_f2 = nexttile(tl2, 1); hold(ax_f2, 'on'); grid(ax_f2, 'on'); box(ax_f2, 'on');
view(ax_f2, -40, 22);

% 1. Render Plane C(X_1) = span{1, x}
surf(ax_f2, pl_x, pl_y, pl_z, 'FaceColor', c_teal_lite, 'FaceAlpha', 0.38, ...
    'EdgeColor', [0.70, 0.80, 0.78], 'EdgeAlpha', 0.4);

% 2. Render 1D Subspace Line C(X_0) = span{1}
t_line = linspace(-0.5, 3.6, 60);
line_1d = t_line .* ones3;
plot3(ax_f2, line_1d(1, :), line_1d(2, :), line_1d(3, :), '-', ...
    'Color', c_gold, 'LineWidth', 3.5);
text(ax_f2, 0.5, 0.5, 0.7, '$\mathcal{C}(X_0) = \mathrm{span}\{\mathbf{1}\}$', ...
    'FontSize', 10.5, 'FontWeight', 'bold', 'Color', c_gold, 'Interpreter', 'latex');

% Vectors: y, y_hat_0, y_hat_1
draw_vec3(ax_f2, O, y, c_dark, 3.0);
text(ax_f2, y(1) + 0.15, y(2) + 0.05, y(3) + 0.25, ' $y = (2,1,4)^T$', ...
    'FontSize', 11, 'FontWeight', 'bold', 'Color', c_dark, 'Interpreter', 'latex');

draw_vec3(ax_f2, O, y_hat_0, c_gold, 3.0);
text(ax_f2, y_hat_0(1) + 0.2, y_hat_0(2) - 0.2, y_hat_0(3) - 0.35, ...
    ' $\hat{y}_0 = P_{\mathbf{1}}y = (\bar{y}, \bar{y}, \bar{y})^T$', ...
    'FontSize', 10.5, 'FontWeight', 'bold', 'Color', c_gold, 'Interpreter', 'latex');

draw_vec3(ax_f2, O, y_hat_1, c_teal, 3.0);
text(ax_f2, y_hat_1(1) - 0.15, y_hat_1(2) + 0.15, y_hat_1(3) + 0.1, ...
    ' $\hat{y}_1 = P_X y = (4/3, 7/3, 10/3)^T$', ...
    'FontSize', 10.5, 'FontWeight', 'bold', 'Color', c_teal, 'Interpreter', 'latex', ...
    'HorizontalAlignment', 'right');

% Hypotenuse e_hat_0
plot3(ax_f2, [y_hat_0(1), y(1)], [y_hat_0(2), y(2)], [y_hat_0(3), y(3)], '--', ...
    'Color', c_gold, 'LineWidth', 2.4);
text(ax_f2, (y_hat_0(1)+y(1))/2 + 0.22, (y_hat_0(2)+y(2))/2 - 0.15, (y_hat_0(3)+y(3))/2 - 0.15, ...
    ' $\|\hat{e}_0\|^2 = 14/3$', 'FontSize', 10.5, 'FontWeight', 'bold', 'Color', c_gold, 'Interpreter', 'latex');

% Leg 1: e_hat_1
draw_vec3(ax_f2, y_hat_1, e_hat_1, c_rust, 3.0);
text(ax_f2, (y_hat_1(1)+y(1))/2 - 0.45, (y_hat_1(2)+y(2))/2 + 0.15, (y_hat_1(3)+y(3))/2 + 0.35, ...
    ' $\|\hat{e}_1\|^2 = 8/3$', 'FontSize', 11, 'FontWeight', 'bold', 'Color', c_rust, 'Interpreter', 'latex');

% Leg 2: y_hat_1 - y_hat_0
draw_vec3(ax_f2, y_hat_0, y_hat_1 - y_hat_0, c_teal, 2.5);
text(ax_f2, (y_hat_0(1)+y_hat_1(1))/2 - 0.35, (y_hat_0(2)+y_hat_1(2))/2 + 0.15, (y_hat_0(3)+y_hat_1(3))/2 - 0.25, ...
    ' $\hat{y}_1 - \hat{y}_0$', 'FontSize', 10.5, 'FontWeight', 'bold', 'Color', c_teal, 'Interpreter', 'latex');

% Right-angle square marker at y_hat_1 between e_hat_1 and (y_hat_0 - y_hat_1)
s_sq2 = 0.30;
e1_dir = e_hat_1 / norm(e_hat_1);
dy_dir = (y_hat_0 - y_hat_1) / norm(y_hat_0 - y_hat_1);
m1 = y_hat_1 + s_sq2 * dy_dir;
m2 = m1 + s_sq2 * e1_dir;
m3 = y_hat_1 + s_sq2 * e1_dir;
plot3(ax_f2, [m1(1), m2(1), m3(1)], [m1(2), m2(2), m3(2)], [m1(3), m2(3), m3(3)], ...
    'Color', c_rust, 'LineWidth', 1.8);

text(ax_f2, -0.6, 2.2, 2.8, '$\mathcal{C}(X_1) = \mathrm{span}\{\mathbf{1}, x\}$', ...
    'FontSize', 11, 'FontWeight', 'bold', 'Color', c_teal, 'Interpreter', 'latex');

xlabel(ax_f2, 'Obs 1 ($y_1$)', 'FontSize', 10, 'Interpreter', 'latex');
ylabel(ax_f2, 'Obs 2 ($y_2$)', 'FontSize', 10, 'Interpreter', 'latex');
zlabel(ax_f2, 'Obs 3 ($y_3$)', 'FontSize', 10, 'Interpreter', 'latex');
xlim(ax_f2, [-1.5, 3.5]); ylim(ax_f2, [-1.0, 3.5]); zlim(ax_f2, [-0.5, 4.8]);

title(tl2, '\textbf{Variable Addition in OLS: Space Expansion from Line to Plane}', ...
    'FontSize', 13.5, 'Color', c_dark, 'Interpreter', 'latex');

% Beautiful 2D annotation panel at top-left
ann_str = { ...
    '$\mathcal{C}(X_0) \subset \mathcal{C}(X_1) \quad (\mathrm{Line} \subset \mathrm{Plane})$', ...
    '$X_0 = [\mathbf{1}]: \quad RSS_0 = 14/3, \quad R_0^2 = 0$', ...
    '$X_1 = [\mathbf{1}, x]: \quad RSS_1 = 8/3, \quad R_1^2 = 3/7$', ...
    'Pythagorean Theorem: $\|\hat{e}_0\|^2 = \|\hat{e}_1\|^2 + \|\hat{y}_1 - \hat{y}_0\|^2$', ...
    '$\frac{14}{3} = \frac{8}{3} + 2 \quad \iff \quad RSS_0 = RSS_1 + \Delta ESS$' ...
};

annotation(fig2, 'textbox', [0.06, 0.69, 0.38, 0.23], 'String', ann_str, ...
    'BackgroundColor', [1, 1, 1, 0.92], 'EdgeColor', [0.75, 0.78, 0.82], ...
    'FontSize', 9.5, 'Margin', 8, 'FitBoxToText', 'on', 'Interpreter', 'latex');

save_fig(fig2, fullfile(img_dir, 'ols-projection-variable-addition.png'));
close(fig2);


% =========================================================================
% FIGURE 3: Multicollinearity (Same Subspace, Ill-Conditioned Basis)
% =========================================================================
fprintf('Generating Figure 3: Multicollinearity Diagnostic...\n');

% Exact setup: n = 6, k = 3
ones6 = ones(6, 1);
x1_6 = [-2; -1; 0; 1; 2; 3];
v_6 = [1; -2; 1; 1; -2; 1];

assert(abs(ones6' * v_6) < 1e-12, '1''v must be 0');
assert(abs(x1_6' * v_6) < 1e-12, 'x1''v must be 0');
norm_v = sqrt(12);

deltas = logspace(0, -4, 60);
kappa_XtX = zeros(size(deltas));
amp_beta_emp = zeros(size(deltas));
amp_yhat_emp = zeros(size(deltas));

epsilon = 0.05;
delta_y = epsilon * (v_6 / norm_v); % in C(X_delta)

for idx = 1:length(deltas)
    d = deltas(idx);
    x2_d = x1_6 + d * v_6;
    X_d = [ones6, x1_6, x2_d];
    
    kappa_XtX(idx) = cond(X_d' * X_d);
    
    % Coordinate shift via backslash
    delta_beta = X_d \ delta_y;
    amp_beta_emp(idx) = norm(delta_beta) / norm(delta_y);
    
    % Projection shift via thin QR
    [Q_d, ~] = qr(X_d, 0);
    delta_yhat = Q_d * (Q_d' * delta_y);
    amp_yhat_emp(idx) = norm(delta_yhat) / norm(delta_y);
end

amp_beta_theory = 1 ./ (sqrt(6) * deltas);
amp_yhat_theory = ones(size(deltas));

fig3 = figure('Position', [60, 60, 1260, 480], 'Color', c_bg, 'Visible', 'off');
tl3 = tiledlayout(fig3, 1, 3, 'TileSpacing', 'compact', 'Padding', 'compact');

% Panel A: Condition Number kappa(X'*X)
ax31 = nexttile(tl3, 1);
loglog(ax31, deltas, kappa_XtX, '-', 'Color', c_rust, 'LineWidth', 2.4);
grid(ax31, 'on'); box(ax31, 'on');
set(ax31, 'XDir', 'reverse', 'XScale', 'log', 'YScale', 'log');
xlabel(ax31, '$\delta$ (collinearity parameter $\rightarrow 0$)', 'FontSize', 10, 'FontWeight', 'bold', 'Interpreter', 'latex');
ylabel(ax31, '$\kappa_2(X_\delta^T X_\delta)$', 'FontSize', 10, 'FontWeight', 'bold', 'Interpreter', 'latex');
title(ax31, {'[Panel A: Conditioning Explosion]', '$\kappa_2(X_\delta^T X_\delta) = O(\delta^{-2})$'}, ...
    'FontSize', 11, 'Color', c_dark, 'Interpreter', 'latex');

% Panel B: Coefficient Instability ||\Delta\beta|| / ||\Delta y||
ax32 = nexttile(tl3, 2); hold(ax32, 'on');
loglog(ax32, deltas, amp_beta_theory, '--', 'Color', c_dark, 'LineWidth', 2.0);
loglog(ax32, deltas(1:4:end), amp_beta_emp(1:4:end), 'o', 'Color', c_rust, ...
    'MarkerSize', 5.5, 'MarkerFaceColor', c_rust);
grid(ax32, 'on'); box(ax32, 'on');
set(ax32, 'XDir', 'reverse', 'XScale', 'log', 'YScale', 'log');
xlabel(ax32, '$\delta$ (collinearity parameter $\rightarrow 0$)', 'FontSize', 10, 'FontWeight', 'bold', 'Interpreter', 'latex');
ylabel(ax32, '$\|\Delta\hat{\beta}\|_2 / \|\Delta y\|_2$', 'FontSize', 10, 'FontWeight', 'bold', 'Interpreter', 'latex');
title(ax32, {'[Panel B: Coefficient Explosion]', '$\|\Delta\hat{\beta}\|_2 / \|\Delta y\|_2 = 1 / (\sqrt{6}\delta)$'}, ...
    'FontSize', 11, 'Color', c_dark, 'Interpreter', 'latex');
legend(ax32, {'Analytical: $1/(\sqrt{6} \delta)$', 'Numerical: $X_\delta \backslash \Delta y$'}, ...
    'Location', 'northwest', 'FontSize', 9, 'Interpreter', 'latex');

% Panel C: Prediction Stability ||\Delta y_hat|| / ||\Delta y||
ax33 = nexttile(tl3, 3); hold(ax33, 'on');
semilogx(ax33, deltas, amp_yhat_theory, '-', 'Color', c_teal, 'LineWidth', 2.4);
semilogx(ax33, deltas(1:4:end), amp_yhat_emp(1:4:end), 's', 'Color', c_teal, ...
    'MarkerSize', 5.5, 'MarkerFaceColor', c_teal);
grid(ax33, 'on'); box(ax33, 'on');
set(ax33, 'XDir', 'reverse', 'XScale', 'log');
ylim(ax33, [0.8, 1.2]);
xlabel(ax33, '$\delta$ (collinearity parameter $\rightarrow 0$)', 'FontSize', 10, 'FontWeight', 'bold', 'Interpreter', 'latex');
ylabel(ax33, '$\|\Delta\hat{y}\|_2 / \|\Delta y\|_2$', 'FontSize', 10, 'FontWeight', 'bold', 'Interpreter', 'latex');
title(ax33, {'[Panel C: Prediction Invariance]', '$\|\Delta\hat{y}\|_2 / \|\Delta y\|_2 \equiv 1$'}, ...
    'FontSize', 11, 'Color', c_dark, 'Interpreter', 'latex');
legend(ax33, {'Exact Bound ($P_{X_\delta} \equiv P_{\mathrm{span}\{\mathbf{1},x_1,v\}})$', 'Numerical (Thin QR)'}, ...
    'Location', 'southeast', 'FontSize', 8.5, 'Interpreter', 'latex');

% Global super title for Figure 3
title(tl3, 'Multicollinearity: Same Subspace $\mathcal{C}(X_\delta) = \mathrm{span}\{\mathbf{1}, x_1, v\}$, Increasingly Ill-Conditioned Basis ($n = 6, k = 3$)', ...
    'FontSize', 12.5, 'Color', c_dark, 'Interpreter', 'latex');

save_fig(fig3, fullfile(img_dir, 'ols-projection-multicollinearity.png'));
close(fig3);


% =========================================================================
% METADATA EXPORT
% =========================================================================
fprintf('Writing metadata JSON...\n');

meta = struct( ...
    'title', 'OLS Vector Space Geometry, Normal Equations, and Projection Matrix', ...
    'generator', 'supplements/matlab/ols_projection_geometry.m', ...
    'environment', struct('isOctave', isOctave, 'version', version), ...
    'fig1_model', struct( ...
        'n', 3, 'k', 2, ...
        'X', X, 'y', y, ...
        'beta_hat', beta_hat, ...
        'y_hat', y_hat, ...
        'e_hat', e_hat, ...
        'uncentered_decomposition', struct('y_sq', y_norm_sq, 'y_hat_sq', y_hat_norm_sq, 'e_hat_sq', e_hat_norm_sq), ...
        'centered_decomposition', struct('TSS', TSS, 'ESS', ESS, 'RSS', RSS, 'R2', R2_1) ...
    ), ...
    'fig2_variable_addition', struct( ...
        'X0_intercept_only', struct('RSS', RSS_0, 'R2', R2_0), ...
        'X1_with_slope', struct('RSS', RSS_1, 'R2', R2_1) ...
    ), ...
    'fig3_multicollinearity', struct( ...
        'n', 6, 'k', 3, ...
        'x1', x1_6, 'v', v_6, ...
        'delta_range', [min(deltas), max(deltas)], ...
        'perturbation_epsilon', epsilon ...
    ) ...
);

meta_file = fullfile(data_dir, 'ols-projection-metadata.json');
fid = fopen(meta_file, 'w');
if fid ~= -1
    fwrite(fid, jsonencode_compat(meta), 'char');
    fclose(fid);
end

fprintf('Completed successfully! All 3 figures and metadata generated.\n');


% =========================================================================
% LOCAL HELPER FUNCTIONS
% =========================================================================

function save_figure_cross(fig, filepath, isOctave)
    if isOctave
        print(fig, filepath, '-dpng', '-r300');
    else
        exportgraphics(fig, filepath, 'Resolution', 300);
    end
end

function str = jsonencode_compat(data)
    if exist('jsonencode', 'builtin') || exist('jsonencode', 'file')
        str = jsonencode(data);
    else
        str = '{ "title": "OLS Projection Geometry Metadata" }';
    end
end
