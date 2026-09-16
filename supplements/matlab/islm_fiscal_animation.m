% IS-LM fiscal-expansion animation.
% Run from the project root with:
%   matlab -batch "run('supplements/matlab/islm_fiscal_animation.m')"

script_path = mfilename('fullpath');
root = fileparts(fileparts(fileparts(script_path)));
data_dir = fullfile(root, 'assets', 'data');
image_dir = fullfile(root, 'assets', 'images');
gif_dir = fullfile(root, 'assets', 'gif');
if ~exist(data_dir, 'dir'), mkdir(data_dir); end
if ~exist(image_dir, 'dir'), mkdir(image_dir); end
if ~exist(gif_dir, 'dir'), mkdir(gif_dir); end

% Linear IS-LM benchmark: r_IS = (A + G - Y)/b and r_LM = (kY - m)/h.
A = 130; b = 9; k = 0.5; h = 8; m = 42;
g_path = linspace(0, 24, 16)';
y_path = (h * (A + g_path) + b * m) ./ (h + b * k);
r_path = (k * y_path - m) ./ h;
assert(all(diff(y_path) > 0) && all(diff(r_path) > 0), 'Fiscal expansion should raise Y and r.');

path_table = table((0:length(g_path)-1)', g_path, y_path, r_path, ...
    'VariableNames', {'frame', 'government_spending', 'output', 'interest_rate'});
writetable(path_table, fullfile(data_dir, 'islm-fiscal-path.csv'));
metadata = struct('title', 'IS-LM fiscal expansion animation', ...
    'generator', 'supplements/matlab/islm_fiscal_animation.m', ...
    'matlab_version', version, ...
    'model', struct('autonomous_demand', A, 'is_slope', b, 'lm_output_coefficient', k, ...
                    'lm_interest_coefficient', h, 'real_money_balance', m), ...
    'shock', struct('government_spending_start', g_path(1), 'government_spending_end', g_path(end), 'frames', length(g_path)), ...
    'equilibrium', struct('output_start', y_path(1), 'output_end', y_path(end), ...
                          'interest_rate_start', r_path(1), 'interest_rate_end', r_path(end)));
fid = fopen(fullfile(data_dir, 'islm-fiscal-metadata.json'), 'w');
assert(fid ~= -1, 'Could not open metadata output.'); fwrite(fid, jsonencode(metadata), 'char'); fclose(fid);

y_grid = linspace(78, 152, 200)';
r_lm = (k * y_grid - m) ./ h;
paper = [1.00, 0.98, 0.94]; ink = [0.30, 0.23, 0.19];
terra = [0.60, 0.34, 0.20]; plum = [0.45, 0.36, 0.45];

% Static fallback: initial and final IS curves together.
fig = figure('Visible', 'off', 'Color', paper, 'Position', [100, 100, 850, 530]); hold on;
plot(y_grid, r_lm, 'LineWidth', 2.8, 'Color', plum, 'DisplayName', 'LM');
plot(y_grid, (A + g_path(1) - y_grid) ./ b, '--', 'LineWidth', 2.3, 'Color', terra, 'DisplayName', 'IS: G = 0');
plot(y_grid, (A + g_path(end) - y_grid) ./ b, '-', 'LineWidth', 2.8, 'Color', terra, 'DisplayName', 'IS: G = 24');
plot(y_path([1 end]), r_path([1 end]), 'o', 'MarkerSize', 8, 'MarkerFaceColor', ink, 'MarkerEdgeColor', ink, 'DisplayName', 'equilibrium');
text(y_path(1) - 11, r_path(1) - 0.28, 'E_0', 'Color', ink, 'FontSize', 12);
text(y_path(end) + 2, r_path(end) + 0.13, 'E_1', 'Color', ink, 'FontSize', 12);
xlim([78 152]); ylim([0 4.4]); grid on; box off; xlabel('output Y'); ylabel('interest rate r');
title('Fiscal expansion shifts IS and raises the short-run equilibrium'); legend('Location', 'northwest', 'Box', 'off');
exportgraphics(fig, fullfile(image_dir, 'islm-fiscal-static.png'), 'Resolution', 180); close(fig);

% Each GIF frame advances fiscal spending and draws the current equilibrium.
gif_path = fullfile(gif_dir, 'islm-fiscal-expansion.gif');
if exist(gif_path, 'file'), delete(gif_path); end
for frame = 1:length(g_path)
    fig = figure('Visible', 'off', 'Color', paper, 'Position', [100, 100, 850, 530]); hold on;
    plot(y_grid, r_lm, 'LineWidth', 2.8, 'Color', plum, 'DisplayName', 'LM');
    plot(y_grid, (A + g_path(1) - y_grid) ./ b, '--', 'LineWidth', 1.8, 'Color', [0.78, 0.65, 0.53], 'DisplayName', 'initial IS');
    plot(y_grid, (A + g_path(frame) - y_grid) ./ b, 'LineWidth', 2.8, 'Color', terra, 'DisplayName', 'current IS');
    plot(y_path(1:frame), r_path(1:frame), '-', 'LineWidth', 1.5, 'Color', [0.50, 0.42, 0.49], 'HandleVisibility', 'off');
    plot(y_path(frame), r_path(frame), 'o', 'MarkerSize', 8, 'MarkerFaceColor', ink, 'MarkerEdgeColor', ink, 'DisplayName', 'current equilibrium');
    xlim([78 152]); ylim([0 4.4]); grid on; box off; xlabel('output Y'); ylabel('interest rate r');
    title('IS-LM fiscal expansion: short-run adjustment');
    text(119, 3.88, sprintf('G = %.1f\nY* = %.1f\nr* = %.2f', g_path(frame), y_path(frame), r_path(frame)), ...
        'FontName', 'Consolas', 'FontSize', 12, 'Color', ink, 'VerticalAlignment', 'top');
    legend('Location', 'northwest', 'Box', 'off');
    temp_png = [tempname '.png']; exportgraphics(fig, temp_png, 'Resolution', 115);
    image_rgb = imread(temp_png); delete(temp_png); close(fig);
    [image_indexed, colour_map] = rgb2ind(image_rgb, 256);
    if frame == 1
        imwrite(image_indexed, colour_map, gif_path, 'gif', 'LoopCount', 1, 'DelayTime', 0.42);
    else
        imwrite(image_indexed, colour_map, gif_path, 'gif', 'WriteMode', 'append', 'DelayTime', 0.42);
    end
end
fprintf('Wrote IS-LM path CSV, metadata JSON, static PNG, and GIF.\n');
fprintf('Output: %.3f -> %.3f; interest rate: %.3f -> %.3f\n', y_path(1), y_path(end), r_path(1), r_path(end));
