% OLS geometry and sampling supplement.
%
% Run from any directory with:
%   matlab -batch "run('supplements/matlab/ols_geometry_monte_carlo.m')"
%
% This script uses base MATLAB only. It writes a reproducible baseline
% sample, metadata, and a static fallback figure for the Quarto supplement.

script_path = mfilename('fullpath');
root = fileparts(fileparts(fileparts(script_path)));
data_dir = fullfile(root, 'assets', 'data');
image_dir = fullfile(root, 'assets', 'images');
if ~exist(data_dir, 'dir'), mkdir(data_dir); end
if ~exist(image_dir, 'dir'), mkdir(image_dir); end

seed = 20260916;
rng(seed, 'twister');

% Data-generating process: y_i = beta_0 + beta_1 x_i + u_i.
n = 40;
beta_0 = 1.00;
beta_1 = 1.40;
sigma = 0.80;
replications = 1500;

x = linspace(-2, 2, n)' + 0.15 * randn(n, 1);
u = sigma * randn(n, 1);
y = beta_0 + beta_1 * x + u;
X = [ones(n, 1), x];

% OLS is the projection of y onto the column space of X.
beta_hat = X \ y;
y_hat = X * beta_hat;
residual = y - y_hat;
sse = residual' * residual;
sigma_hat = sqrt(sse / (n - size(X, 2)));
vcov_hat = sigma_hat^2 * inv(X' * X);
se_beta_1 = sqrt(vcov_hat(2, 2));
orthogonality_error = norm(X' * residual, Inf);

% Hold X fixed and repeat only the sampling disturbance.
beta_1_draws = zeros(replications, 1);
for draw = 1:replications
    y_draw = beta_0 + beta_1 * x + sigma * randn(n, 1);
    beta_draw = X \ y_draw;
    beta_1_draws(draw) = beta_draw(2);
end

assert(orthogonality_error < 1e-10, 'OLS residuals are not orthogonal to X.');
assert(all(isfinite(beta_1_draws)), 'Monte Carlo draws must be finite.');

baseline = table(x, y, y_hat, residual, ...
    'VariableNames', {'x', 'y', 'y_hat', 'residual'});
writetable(baseline, fullfile(data_dir, 'ols-geometry-baseline.csv'));

metadata = struct( ...
    'title', 'OLS geometry and sampling explorer', ...
    'generator', 'supplements/matlab/ols_geometry_monte_carlo.m', ...
    'matlab_version', version, ...
    'seed', seed, ...
    'sample_size', n, ...
    'replications', replications, ...
    'model', struct('beta_0', beta_0, 'beta_1', beta_1, 'sigma', sigma), ...
    'baseline', struct('beta_0_hat', beta_hat(1), 'beta_1_hat', beta_hat(2), ...
                       'se_beta_1', se_beta_1, 'sse', sse, ...
                       'orthogonality_error', orthogonality_error), ...
    'monte_carlo', struct('mean_beta_1_hat', mean(beta_1_draws), ...
                          'sd_beta_1_hat', std(beta_1_draws)) ...
);
fid = fopen(fullfile(data_dir, 'ols-geometry-metadata.json'), 'w');
assert(fid ~= -1, 'Could not open metadata output.');
fwrite(fid, jsonencode(metadata), 'char');
fclose(fid);

% Static fallback: baseline projection and fixed-X sampling distribution.
fig = figure('Visible', 'off', 'Color', [1.00, 0.98, 0.94], ...
    'Position', [100, 100, 1150, 500]);
tiledlayout(1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

nexttile;
scatter(x, y, 42, [0.60, 0.34, 0.20], 'filled'); hold on;
x_grid = linspace(min(x) - 0.15, max(x) + 0.15, 120)';
plot(x_grid, beta_hat(1) + beta_hat(2) * x_grid, 'LineWidth', 2.5, 'Color', [0.30, 0.23, 0.19]);
for index = 1:n
    plot([x(index), x(index)], [y_hat(index), y(index)], '-', 'Color', [0.78, 0.65, 0.53]);
end
grid on; box off;
xlabel('x_i'); ylabel('y_i');
title('OLS projection: y_i = yhat_i + uhat_i');
legend({'sample', 'OLS fit', 'residual'}, 'Location', 'northwest', 'Box', 'off');

nexttile;
histogram(beta_1_draws, 28, 'Normalization', 'pdf', ...
    'FaceColor', [0.45, 0.36, 0.45], 'EdgeColor', 'none', 'DisplayName', 'beta_1 draws'); hold on;
xline(beta_1, '--', 'LineWidth', 2, 'Color', [0.60, 0.34, 0.20], 'DisplayName', 'true beta_1');
xline(mean(beta_1_draws), '-', 'LineWidth', 2, 'Color', [0.30, 0.23, 0.19], 'DisplayName', 'Monte Carlo mean');
grid on; box off;
xlabel('beta_1 hat'); ylabel('density');
title(sprintf('Fixed-X sampling distribution (%d replications)', replications));
legend('Location', 'northwest', 'Box', 'off');

exportgraphics(fig, fullfile(image_dir, 'ols-geometry-static.png'), 'Resolution', 180);
close(fig);

fprintf('Wrote OLS baseline CSV, metadata JSON, and static PNG.\n');
fprintf('beta_1 hat = %.6f, SE = %.6f, max |X''uhat| = %.3e\n', ...
    beta_hat(2), se_beta_1, orthogonality_error);
