% IV and weak instruments supplement.
% Run from the project root with:
%   matlab -batch "run('supplements/matlab/iv_weak_instruments.m')"

script_path = mfilename('fullpath');
root = fileparts(fileparts(fileparts(script_path)));
data_dir = fullfile(root, 'assets', 'data');
image_dir = fullfile(root, 'assets', 'images');
if ~exist(data_dir, 'dir'), mkdir(data_dir); end
if ~exist(image_dir, 'dir'), mkdir(image_dir); end

seed = 20260917;
rng(seed, 'twister');
n = 150;
beta = 1.00;
pi_strength = 0.70;
rho = 0.60;
replications = 2000;

% z is valid: it is independent of both v and e. Endogeneity arises because
% x contains v and u contains rho*v.
z = randn(n, 1);
v = randn(n, 1);
e = randn(n, 1);
u = rho * v + sqrt(1 - rho^2) * e;
x = pi_strength * z + v;
y = beta * x + u;

ols_hat = slope_with_intercept(x, y);
iv_hat = iv_slope(z, x, y);
first_stage = slope_with_intercept(z, x);
f_stat = first_stage_f(z, x);

ols_draws = zeros(replications, 1);
iv_draws = zeros(replications, 1);
for draw = 1:replications
    z_draw = randn(n, 1);
    v_draw = randn(n, 1);
    e_draw = randn(n, 1);
    u_draw = rho * v_draw + sqrt(1 - rho^2) * e_draw;
    x_draw = pi_strength * z_draw + v_draw;
    y_draw = beta * x_draw + u_draw;
    ols_draws(draw) = slope_with_intercept(x_draw, y_draw);
    iv_draws(draw) = iv_slope(z_draw, x_draw, y_draw);
end

assert(all(isfinite(ols_draws)), 'OLS draws must be finite.');
assert(all(isfinite(iv_draws)), '2SLS draws must be finite.');

baseline = table(z, x, y, u, ...
    'VariableNames', {'z', 'x', 'y', 'u'});
writetable(baseline, fullfile(data_dir, 'iv-weak-instruments-baseline.csv'));

metadata = struct( ...
    'title', 'IV and weak instruments explorer', ...
    'generator', 'supplements/matlab/iv_weak_instruments.m', ...
    'matlab_version', version, 'seed', seed, 'sample_size', n, ...
    'replications', replications, ...
    'model', struct('beta', beta, 'pi_strength', pi_strength, 'rho', rho), ...
    'baseline', struct('ols_beta_hat', ols_hat, 'iv_beta_hat', iv_hat, ...
                       'first_stage_pi_hat', first_stage, 'first_stage_f', f_stat), ...
    'monte_carlo', struct('mean_ols_hat', mean(ols_draws), ...
                          'mean_iv_hat', mean(iv_draws), ...
                          'sd_ols_hat', std(ols_draws), 'sd_iv_hat', std(iv_draws)) ...
);
fid = fopen(fullfile(data_dir, 'iv-weak-instruments-metadata.json'), 'w');
assert(fid ~= -1, 'Could not open metadata output.');
fwrite(fid, jsonencode(metadata), 'char');
fclose(fid);

fig = figure('Visible', 'off', 'Color', [1.00, 0.98, 0.94], ...
    'Position', [100, 100, 1150, 500]);
tiledlayout(1, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

nexttile;
scatter(z, x, 35, [0.60, 0.34, 0.20], 'filled'); hold on;
z_grid = linspace(min(z) - 0.15, max(z) + 0.15, 120)';
mean_x = mean(x); mean_z = mean(z);
plot(z_grid, mean_x + first_stage * (z_grid - mean_z), 'LineWidth', 2.5, 'Color', [0.30, 0.23, 0.19]);
grid on; box off; xlabel('instrument z_i'); ylabel('endogenous regressor x_i');
title(sprintf('First stage: pi hat = %.2f, F = %.1f', first_stage, f_stat));
legend({'sample', 'first-stage fit'}, 'Location', 'northwest', 'Box', 'off');

nexttile;
lower = min([quantile(ols_draws, 0.005), quantile(iv_draws, 0.005)]);
upper = max([quantile(ols_draws, 0.995), quantile(iv_draws, 0.995)]);
edges = linspace(lower, upper, 33);
histogram(ols_draws, edges, 'Normalization', 'pdf', 'FaceColor', [0.60, 0.34, 0.20], ...
    'FaceAlpha', 0.58, 'EdgeColor', 'none', 'DisplayName', 'OLS'); hold on;
histogram(iv_draws, edges, 'Normalization', 'pdf', 'FaceColor', [0.45, 0.36, 0.45], ...
    'FaceAlpha', 0.50, 'EdgeColor', 'none', 'DisplayName', '2SLS');
xline(beta, '--', 'LineWidth', 2, 'Color', [0.30, 0.23, 0.19], 'DisplayName', 'true beta');
grid on; box off; xlabel('slope estimate'); ylabel('density');
title(sprintf('Sampling distributions (%d replications)', replications));
legend('Location', 'northwest', 'Box', 'off');

exportgraphics(fig, fullfile(image_dir, 'iv-weak-instruments-static.png'), 'Resolution', 180);
close(fig);

fprintf('Wrote IV baseline CSV, metadata JSON, and static PNG.\n');
fprintf('OLS = %.6f, 2SLS = %.6f, first-stage F = %.3f\n', ols_hat, iv_hat, f_stat);

function b = slope_with_intercept(a, response)
    centered_a = a - mean(a);
    b = (centered_a' * (response - mean(response))) / (centered_a' * centered_a);
end

function b = iv_slope(instrument, regressor, response)
    centered_z = instrument - mean(instrument);
    b = (centered_z' * (response - mean(response))) / (centered_z' * (regressor - mean(regressor)));
end

function f = first_stage_f(instrument, regressor)
    b = slope_with_intercept(instrument, regressor);
    fitted = mean(regressor) + b * (instrument - mean(instrument));
    explained = sum((fitted - mean(regressor)).^2);
    residual = sum((regressor - fitted).^2);
    f = explained / (residual / (length(regressor) - 2));
end
