"""Generate publication-grade animated GIFs for the OLS Projection Geometry supplement.

Outputs:
  - assets/gif/ols-projection-3d-geometry.gif
  - assets/gif/ols-frisch-waugh-lovell-geometry.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image

# Setup directories
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIF_DIR = os.path.join(ROOT, "assets", "gif")
os.makedirs(GIF_DIR, exist_ok=True)

# Styling parameters (Warm Editorial Theme matching the book)
BG_COLOR = "#fcf9f2"
INK_COLOR = "#2d251e"
MUTED_COLOR = "#75665b"
GRID_COLOR = "#e5ded3"
NAVY_COLOR = "#1f3b5c"       # y vector / main OLS fit
RED_COLOR = "#b83b26"        # Residual vector e_hat / condition explosion
TEAL_COLOR = "#087e8b"       # Subspace C(X) plane / fitted y_hat / prediction invariance
PLUM_COLOR = "#6b4c7a"       # Optimization trajectory / FWL residuals
GOLD_COLOR = "#d97706"       # Intercept vector 1 / Baseline
GREEN_COLOR = "#15803d"      # Orthogonal projections / Right angles

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Baseline numerical example (n=3, k=2)
# X = [1, -1; 1, 0; 1, 1], y = [2; 1; 4]
vec_1 = np.array([1.0, 1.0, 1.0])
vec_x = np.array([-1.0, 0.0, 1.0])
vec_y = np.array([2.0, 1.0, 4.0])

X_mat = np.column_stack([vec_1, vec_x])
XtX = X_mat.T @ X_mat
XtX_inv = np.linalg.inv(XtX)
beta_hat = XtX_inv @ (X_mat.T @ vec_y)  # [7/3, 1.0] = [2.333, 1.0]
y_hat = X_mat @ beta_hat                # [4/3, 7/3, 10/3] = [1.333, 2.333, 3.333]
e_hat = vec_y - y_hat                   # [2/3, -4/3, 2/3] = [0.667, -1.333, 0.667]


# ==============================================================================
# 1. GIF 1: 3D Observation Space Orthogonal Projection & Dual Parameter Space
# ==============================================================================
def generate_gif_projection_3d():
    print("Generating GIF 1: ols-projection-3d-geometry.gif ...")

    # Sequence of 17 frames:
    t_vals = np.linspace(0, 1, 10)
    t_hold = np.array([1.0] * 3)
    t_back = np.linspace(1, 0, 4)
    t_seq = np.concatenate([t_vals, t_hold, t_back])

    # Initial candidate in parameter space
    b0_init, b1_init = 0.8, -0.4
    b0_target, b1_target = 7.0 / 3.0, 1.0

    frames = []

    for idx, t in enumerate(t_seq):
        # Current candidate beta
        prog = 1.0 - (1.0 - t)**2
        b0_cur = b0_init + prog * (b0_target - b0_init)
        b1_cur = b1_init + prog * (b1_target - b1_init)
        beta_cur = np.array([b0_cur, b1_cur])
        y_cur = X_mat @ beta_cur
        rss_cur = np.sum((vec_y - y_cur)**2)
        grad_norm = 2.0 * np.linalg.norm(X_mat.T @ (vec_y - y_cur))

        # Camera azimuth rotation
        azim = -50.0 + 65.0 * np.sin(idx / len(t_seq) * np.pi)
        elev = 22.0

        fig = plt.figure(figsize=(10.5, 4.6), dpi=95)
        fig.patch.set_facecolor(BG_COLOR)

        # ----------------------------------------------------------------------
        # Left Panel: Parameter Space Contours S(beta)
        # ----------------------------------------------------------------------
        ax1 = fig.add_axes([0.06, 0.12, 0.40, 0.78])
        ax1.set_facecolor(BG_COLOR)
        for spine in ax1.spines.values():
            spine.set_color(GRID_COLOR)
        ax1.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

        # Grid for S(beta)
        b0_grid = np.linspace(0.0, 4.0, 100)
        b1_grid = np.linspace(-1.0, 2.5, 100)
        B0, B1 = np.meshgrid(b0_grid, b1_grid)
        # S(beta) = 8/3 + 3*(B0 - 7/3)^2 + 2*(B1 - 1)^2
        S_grid = 8.0 / 3.0 + 3.0 * (B0 - 7.0 / 3.0)**2 + 2.0 * (B1 - 1.0)**2

        levels = [2.7, 3.5, 5.0, 8.0, 13.0, 20.0, 30.0]
        cs = ax1.contour(B0, B1, S_grid, levels=levels, colors="#9c8c7c", alpha=0.6, linewidths=1.2)
        ax1.clabel(cs, inline=True, fontsize=7.5, fmt="%.1f")

        # Optimal point hat_beta
        ax1.scatter(b0_target, b1_target, color=TEAL_COLOR, s=90, marker="*",
                    edgecolor=INK_COLOR, lw=1.0, label=r"OLS 최적점 $\hat{\beta} = (7/3, 1)$", zorder=6)

        # Optimization trajectory
        t_track = np.linspace(0, t, 30)
        p_track = 1.0 - (1.0 - t_track)**2
        b0_tr = b0_init + p_track * (b0_target - b0_init)
        b1_tr = b1_init + p_track * (b1_target - b1_init)
        ax1.plot(b0_tr, b1_tr, "--", color=PLUM_COLOR, lw=1.8, label="경사하강 궤적", zorder=4)

        # Current candidate marker
        ax1.scatter(b0_cur, b1_cur, color=RED_COLOR, s=55, edgecolor="#ffffff",
                    lw=1.0, label=rf"현재 후보점 $\beta(t)$", zorder=5)

        ax1.set_xlim(0.0, 4.0)
        ax1.set_ylim(-1.0, 2.5)
        ax1.set_xlabel(r"절편 모수 $\beta_0$", fontsize=10.0, color=INK_COLOR)
        ax1.set_ylabel(r"기울기 모수 $\beta_1$", fontsize=10.0, color=INK_COLOR)
        ax1.set_title(r"모수공간 $\mathbb{R}^2$: 목적함수 $S(\beta)$ 최소화",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=8)
        ax1.legend(loc="upper left", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.0)

        # Badge left
        badge_left = (
            rf"$S(\beta) = {rss_cur:.3f}$  ($\min = {8.0/3.0:.3f}$)" "\n"
            rf"$\|\nabla S\| = {grad_norm:.2f}$" "\n"
            rf"$(\beta_0, \beta_1) = ({b0_cur:.2f}, {b1_cur:.2f})$"
        )
        ax1.text(0.96, 0.05, badge_left, transform=ax1.transAxes,
                 fontsize=8.5, va="bottom", ha="right",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#f3ede2", edgecolor="#d5c7b5", alpha=0.95))

        # ----------------------------------------------------------------------
        # Right Panel: 3D Observation Space Orthogonal Projection
        # ----------------------------------------------------------------------
        ax2 = fig.add_axes([0.50, 0.08, 0.47, 0.84], projection="3d")
        ax2.set_facecolor(BG_COLOR)
        ax2.view_init(elev=elev, azim=azim)

        # Transparent plane for C(X) = span(1, x)
        # grid of u in [0.5, 3.5], v in [-1.5, 1.5]
        u_p = np.linspace(0.2, 3.8, 10)
        v_p = np.linspace(-1.5, 1.5, 10)
        U_p, V_p = np.meshgrid(u_p, v_p)
        P_x1 = U_p * vec_1[0] + V_p * vec_x[0]
        P_x2 = U_p * vec_1[1] + V_p * vec_x[1]
        P_x3 = U_p * vec_1[2] + V_p * vec_x[2]
        ax2.plot_surface(P_x1, P_x2, P_x3, color="#087e8b", alpha=0.18, edgecolor="none", shade=False)

        # Draw origin
        ax2.scatter(0, 0, 0, color=INK_COLOR, s=20)

        # Basis vectors 1 and x
        ax2.quiver(0, 0, 0, vec_1[0], vec_1[1], vec_1[2], color=GOLD_COLOR, lw=1.6,
                   arrow_length_ratio=0.10, label=r"$\mathbf{1} = (1, 1, 1)'$")
        ax2.quiver(0, 0, 0, vec_x[0], vec_x[1], vec_x[2], color=MUTED_COLOR, lw=1.6,
                   arrow_length_ratio=0.10, label=r"$x = (-1, 0, 1)'$")

        # Dependent variable vector y
        ax2.quiver(0, 0, 0, vec_y[0], vec_y[1], vec_y[2], color=NAVY_COLOR, lw=2.4,
                   arrow_length_ratio=0.08, label=r"$y = (2, 1, 4)'$")

        # OLS projection y_hat
        ax2.quiver(0, 0, 0, y_hat[0], y_hat[1], y_hat[2], color=TEAL_COLOR, lw=2.2,
                   arrow_length_ratio=0.09, label=rf"$\hat{{y}} = P_X y$")

        # Residual vector e_hat: from y_hat to y
        ax2.quiver(y_hat[0], y_hat[1], y_hat[2], e_hat[0], e_hat[1], e_hat[2],
                   color=RED_COLOR, lw=2.2, arrow_length_ratio=0.12,
                   label=rf"$\hat{{e}} = M_X y$ (직교 잔차)")

        # Current point X*beta_cur and current residual line
        ax2.scatter(y_cur[0], y_cur[1], y_cur[2], color=PLUM_COLOR, s=40, zorder=6)
        ax2.plot([y_cur[0], vec_y[0]], [y_cur[1], vec_y[1]], [y_cur[2], vec_y[2]],
                 ":", color=RED_COLOR, lw=1.5, alpha=0.7)

        # Coordinate axes limits
        ax2.set_xlim(-0.5, 4.0)
        ax2.set_ylim(-0.5, 4.0)
        ax2.set_zlim(0.0, 5.0)
        ax2.set_xlabel(r"$y_1$", fontsize=9.0, color=INK_COLOR)
        ax2.set_ylabel(r"$y_2$", fontsize=9.0, color=INK_COLOR)
        ax2.set_zlabel(r"$y_3$", fontsize=9.0, color=INK_COLOR)
        ax2.set_title(rf"관측공간 $\mathbb{{R}}^3$: 직교사영 ($\hat{{e}} \perp \mathcal{{C}}(X)$)",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=10)
        ax2.legend(loc="upper left", framealpha=0.90, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=7.2)

        # Save frame to PIL
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    # Save animated GIF
    out_path = os.path.join(GIF_DIR, "ols-projection-3d-geometry.gif")
    durations = [280] * len(t_vals) + [650] * len(t_hold) + [280] * len(t_back)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(out_path) / 1024
    print(f"GIF 1 generated: {out_path} ({size_kb:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Frisch–Waugh–Lovell (FWL) Geometry and Multicollinearity Conditioning
# ==============================================================================
def generate_gif_frisch_waugh_lovell():
    print("Generating GIF 2: ols-frisch-waugh-lovell-geometry.gif ...")

    # Sequence of frames demonstrating:
    # Left: FWL 3-Stage Partial Orthogonal Projection:
    #       Stage 1: Raw vectors y, x, 1
    #       Stage 2: Orthogonalize by M_1 -> demeaned vectors M_1 y, M_1 x
    #       Stage 3: Univariate regression of M_1 y on M_1 x -> identical slope beta_1 = 1.0!
    # Right: Multicollinearity diagnostic:
    #        Sweep delta: 1.0 down to 0.005 -> Condition number & coefficient explosion vs prediction invariance!

    # 18 frames: delta sweep
    deltas_forward = [1.0, 0.60, 0.35, 0.20, 0.12, 0.07, 0.04, 0.02, 0.01, 0.005]
    deltas_hold = [0.005, 0.005, 0.005]
    deltas_back = [0.02, 0.08, 0.25, 0.60, 1.0]
    deltas = deltas_forward + deltas_hold + deltas_back

    # Setup for multicollinearity experiment (n=6, k=3)
    n6 = 6
    ones_6 = np.ones(n6)
    x1_6 = np.array([-2.0, -1.0, 0.0, 1.0, 2.0, 3.0])
    v_6 = np.array([1.0, -2.0, 1.0, 1.0, -2.0, 1.0])
    # Verify orthogonality: ones_6 @ v_6 == 0, x1_6 @ v_6 == 0
    norm_v = np.sqrt(np.sum(v_6**2))  # sqrt(12)

    # Precalculate curves across fine delta grid
    d_grid = np.logspace(-3, 0, 100)
    cond_grid = []
    beta_sens_grid = []
    pred_sens_grid = []

    for d in d_grid:
        x2_d = x1_6 + d * v_6
        X_d = np.column_stack([ones_6, x1_6, x2_d])
        cond_val = np.linalg.cond(X_d.T @ X_d)
        cond_grid.append(cond_val)
        # Theoretical sensitivity
        beta_sens_grid.append(1.0 / (np.sqrt(6.0) * d))
        pred_sens_grid.append(1.0)

    # FWL vectors for left panel (n=3)
    # y = [2, 1, 4]', 1 = [1, 1, 1]', x = [-1, 0, 1]'
    y_bar = 7.0 / 3.0
    x_bar = 0.0
    M1_y = vec_y - y_bar * vec_1  # [-1/3, -4/3, 5/3]
    M1_x = vec_x - x_bar * vec_1  # [-1, 0, 1]
    # Regression of M1_y on M1_x: slope = (M1_x' M1_y) / (M1_x' M1_x) = 2.0 / 2.0 = 1.0
    beta_fwl = np.dot(M1_x, M1_y) / np.dot(M1_x, M1_x)
    fwl_fit = beta_fwl * M1_x
    fwl_resid = M1_y - fwl_fit    # [2/3, -4/3, 2/3] == e_hat!

    frames = []

    for idx, d_cur in enumerate(deltas):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8), dpi=105)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, top=0.88, bottom=0.14, wspace=0.28)

        # ----------------------------------------------------------------------
        # Left Panel: FWL 2D Projection Subspace (Demeaned Observation Space)
        # ----------------------------------------------------------------------
        ax1.set_facecolor(BG_COLOR)
        for spine in ax1.spines.values():
            spine.set_color(GRID_COLOR)
        ax1.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

        # In the subspace orthogonal to 1, vectors live in a 2D plane.
        # We project M1_y and M1_x onto 2D coordinates for clear visualization:
        # Basis e1_sub = M1_x / ||M1_x|| = [-1, 0, 1] / sqrt(2)
        # Basis e2_sub = [1, -2, 1] / sqrt(6)  (orthogonal to 1 and M1_x)
        e1_sub = M1_x / np.sqrt(2.0)
        e2_sub = np.array([1.0, -2.0, 1.0]) / np.sqrt(6.0)

        # Coordinates in 2D plane:
        u_x = np.dot(M1_x, e1_sub)
        v_x = np.dot(M1_x, e2_sub)
        u_y = np.dot(M1_y, e1_sub)
        v_y = np.dot(M1_y, e2_sub)
        u_fit = np.dot(fwl_fit, e1_sub)
        v_fit = np.dot(fwl_fit, e2_sub)
        u_res = u_y - u_fit
        v_res = v_y - v_fit

        # Origin
        ax1.scatter(0, 0, color=INK_COLOR, s=25, zorder=5)

        # Partial regressor axis line: span of M1_x
        axis_span = np.linspace(-2.2, 2.2, 50)
        ax1.plot(axis_span, np.zeros_like(axis_span), "--", color=MUTED_COLOR, lw=1.2, alpha=0.6,
                 label=r"부분설명변수 축 $\mathcal{C}(M_1 x)$")

        # Vector M1_x
        ax1.annotate("", xy=(u_x, v_x), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=2.2))
        ax1.text(u_x + 0.08, v_x - 0.12, r"$M_1 x$", fontsize=10, color=GOLD_COLOR, fontweight="bold")

        # Vector M1_y
        ax1.annotate("", xy=(u_y, v_y), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="->", color=NAVY_COLOR, lw=2.4))
        ax1.text(u_y - 0.25, v_y + 0.10, r"$M_1 y$", fontsize=10, color=NAVY_COLOR, fontweight="bold")

        # Fitted partial projection
        ax1.annotate("", xy=(u_fit, v_fit), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=2.2))
        ax1.text(u_fit + 0.06, v_fit + 0.12, rf"$\hat{{\beta}}_1 M_1 x$ (${beta_fwl:.1f} M_1 x$)",
                 fontsize=9.5, color=TEAL_COLOR, fontweight="bold")

        # Orthogonal residual e_hat
        ax1.plot([u_fit, u_y], [v_fit, v_y], "-", color=RED_COLOR, lw=2.2,
                 label=r"직교 잔차 $\hat{e} = M_1 y - \hat{\beta}_1 M_1 x$")

        # Right angle marker
        ra_size = 0.12
        ax1.plot([u_fit, u_fit, u_fit - ra_size * 0.2],
                 [v_fit, v_fit + ra_size, v_fit + ra_size],
                 "-", color=RED_COLOR, lw=1.0)

        ax1.set_xlim(-1.8, 2.2)
        ax1.set_ylim(-1.0, 2.2)
        ax1.set_xlabel(r"직교기저 $e_1$ (방향 $M_1 x$)", fontsize=10.0, color=INK_COLOR)
        ax1.set_ylabel(r"직교기저 $e_2$ (여공간 방향)", fontsize=10.0, color=INK_COLOR)
        ax1.set_title(r"FWL 정리: $M_1 y$의 $M_1 x$ 직교사영 ($\hat{\beta}_1 = 1.0$ 일치)",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=8)
        ax1.legend(loc="upper left", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.0)

        # Info badge left
        badge_fwl = (
            rf"$\hat{{\beta}}_1 = \frac{{(M_1 x)'(M_1 y)}}{{(M_1 x)'(M_1 x)}} = \frac{{2.0}}{{2.0}} = {beta_fwl:.1f}$" "\n"
            rf"$\|M_1 y\|^2 = \|\hat{{\beta}}_1 M_1 x\|^2 + \|\hat{{e}}\|^2$" "\n"
            rf"$\frac{{14}}{{3}} = 2 + \frac{{8}}{{3}}$ (중심화 피타고라스)" "\n"
            r"$\hat{e}_{FWL} \equiv \hat{e}_{OLS}$ (잔차 완전 일치)"
        )
        ax1.text(0.96, 0.05, badge_fwl, transform=ax1.transAxes,
                 fontsize=8.5, va="bottom", ha="right",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#f3ede2", edgecolor="#d5c7b5", alpha=0.95))

        # ----------------------------------------------------------------------
        # Right Panel: Multicollinearity Conditioning & Invariance
        # ----------------------------------------------------------------------
        ax2.set_facecolor(BG_COLOR)
        for spine in ax2.spines.values():
            spine.set_color(GRID_COLOR)
        ax2.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

        # Plot curves
        ax2.plot(d_grid, cond_grid, "-", color=RED_COLOR, lw=2.2,
                 label=r"Gram 행렬 조건수 $\kappa(X_\delta' X_\delta) \sim \mathcal{O}(\delta^{-2})$")
        ax2.plot(d_grid, beta_sens_grid, "--", color=PLUM_COLOR, lw=2.0,
                 label=r"계수 추정 불안정성 $\|\Delta\hat{\beta}\| \sim \mathcal{O}(\delta^{-1})$")
        ax2.plot(d_grid, pred_sens_grid, "-", color=TEAL_COLOR, lw=2.8,
                 label=r"예측 변동 민감도 $\|\Delta\hat{y}\|/\|\Delta y\| \equiv 1.0$ (불변)")

        # Current delta markers
        cur_cond = np.linalg.cond((np.column_stack([ones_6, x1_6, x1_6 + d_cur * v_6])).T @ (np.column_stack([ones_6, x1_6, x1_6 + d_cur * v_6])))
        cur_beta_sens = 1.0 / (np.sqrt(6.0) * d_cur)

        ax2.scatter(d_cur, cur_cond, color=RED_COLOR, s=60, zorder=6)
        ax2.scatter(d_cur, cur_beta_sens, color=PLUM_COLOR, s=60, zorder=6)
        ax2.scatter(d_cur, 1.0, color=TEAL_COLOR, s=70, marker="s", zorder=6)
        ax2.axvline(d_cur, color=MUTED_COLOR, linestyle=":", lw=1.2, alpha=0.8)

        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.set_xlim(1e-3, 1.2)
        ax2.set_ylim(0.5, 2e7)
        ax2.set_xlabel(r"섭동 계수 $\delta$ (선형종속 접근: $\delta \rightarrow 0$)", fontsize=10.0, color=INK_COLOR)
        ax2.set_ylabel("민감도 및 조건수 (Log Scale)", fontsize=10.0, color=INK_COLOR)
        ax2.set_title(r"다중공선성의 기하: 부분공간 불변성 vs 좌표계 파탄",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=8)
        ax2.legend(loc="upper right", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=7.8)

        # Info badge right
        badge_right = (
            rf"현재 $\delta = {d_cur:.3f}$" "\n"
            rf"조건수 $\kappa(X'X) = {cur_cond:.1e}$" "\n"
            rf"계수 변동 노름: $\times {cur_beta_sens:.1f}$ 배" "\n"
            r"$\rightarrow$ 사영 $\hat{y}$는 불변, 계수 $\hat{\beta}$만 폭발"
        )
        ax2.text(0.04, 0.05, badge_right, transform=ax2.transAxes,
                 fontsize=8.5, va="bottom", ha="left",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#edf2f7", edgecolor="#cbd5e1", alpha=0.95))

        # Save frame to PIL
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    # Save animated GIF
    out_path = os.path.join(GIF_DIR, "ols-frisch-waugh-lovell-geometry.gif")
    durations = [280] * len(deltas_forward) + [650] * len(deltas_hold) + [280] * len(deltas_back)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(out_path) / 1024
    print(f"GIF 2 generated: {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_gif_projection_3d()
    generate_gif_frisch_waugh_lovell()
    print("All OLS projection geometry GIFs successfully generated!")
