"""Generate publication-grade animated GIFs for the OLS Projection Geometry supplement.

Outputs:
  - assets/gif/ols-projection-3d-geometry.gif
  - assets/gif/ols-multicollinearity-geometry.gif
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
PURPLE_COLOR = "#6b4c7a"     # Parallelogram components / Coordinates
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
# 2. GIF 2: Multicollinearity Geometry: Parallelogram Collapse vs Prediction Invariance
# ==============================================================================
def generate_gif_multicollinearity_geometry():
    print("Generating GIF 2: ols-multicollinearity-geometry.gif ...")

    thetas_fwd = [65.0, 58.0, 50.0, 42.0, 35.0, 29.0, 24.0, 20.0, 16.0, 13.0, 10.5, 8.5]
    thetas_hold_low = [8.5, 8.5, 8.5]
    thetas_bwd = [11.0, 15.0, 22.0, 32.0, 46.0, 65.0]
    thetas_hold_high = [65.0, 65.0]

    thetas = thetas_fwd + thetas_hold_low + thetas_bwd + thetas_hold_high
    u, v = 2.0, 1.5

    frames = []

    for idx, theta_deg in enumerate(thetas):
        theta = np.radians(theta_deg)
        r_corr = np.cos(theta)
        vif = 1.0 / (np.sin(theta)**2)

        b2 = v / np.sin(theta)
        b1 = u - v * (np.cos(theta) / np.sin(theta))

        p_x1 = np.array([1.0, 0.0])
        p_x2 = np.array([np.cos(theta), np.sin(theta)])
        p_yhat = np.array([u, v])
        p_b1x1 = np.array([b1, 0.0])
        p_b2x2 = np.array([b2 * np.cos(theta), b2 * np.sin(theta)])

        fig, (ax_geo, ax_info) = plt.subplots(1, 2, figsize=(14.2, 7.2), dpi=100,
                                              gridspec_kw={'width_ratios': [1.25, 1.0]})
        fig.patch.set_facecolor(BG_COLOR)
        ax_geo.set_facecolor(BG_COLOR)
        ax_info.set_facecolor(BG_COLOR)

        # Left: Parallelogram Geometry
        ax_geo.set_xlim(-10.5, 13.5)
        ax_geo.set_ylim(-1.8, 6.0)
        ax_geo.set_xlabel("설명변수 평면 기저 X_1 방향 축", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax_geo.set_ylabel("직교 여차원 방향 축", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax_geo.set_title(f"■ [기하학적 실체] 다중공선성과 평행사변형 좌표계 붕괴 (θ = {theta_deg:.1f}°)",
                         fontsize=12, fontweight="bold", color=INK_COLOR, pad=10)
        ax_geo.grid(True, linestyle="--", alpha=0.4, color=GRID_COLOR)
        ax_geo.axhline(0, color=MUTED_COLOR, lw=0.8, linestyle="-", alpha=0.4)
        ax_geo.axvline(0, color=MUTED_COLOR, lw=0.8, linestyle="-", alpha=0.4)

        # Parallelogram dashed lines
        ax_geo.plot([p_b1x1[0], p_yhat[0]], [p_b1x1[1], p_yhat[1]], color=PURPLE_COLOR, linestyle="--", lw=1.5, alpha=0.7)
        ax_geo.plot([p_b2x2[0], p_yhat[0]], [p_b2x2[1], p_yhat[1]], color=RED_COLOR, linestyle="--", lw=1.5, alpha=0.7)

        # Shaded parallelogram polygon
        poly = plt.Polygon([[0, 0], p_b1x1, p_yhat, p_b2x2], facecolor="#e2e8f0", edgecolor="none", alpha=0.35)
        ax_geo.add_patch(poly)

        # Basis vectors x1, x2
        ax_geo.annotate("", xy=(p_x1[0], p_x1[1]), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=2.5, mutation_scale=15))
        ax_geo.text(1.1, -0.4, "기저 x_1", color=GOLD_COLOR, fontsize=10, fontweight="bold")

        ax_geo.annotate("", xy=(p_x2[0], p_x2[1]), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=2.5, mutation_scale=15))
        ax_geo.text(p_x2[0] + 0.1, p_x2[1] + 0.15, "기저 x_2", color=GOLD_COLOR, fontsize=10, fontweight="bold")

        # Component vectors b1*x1, b2*x2
        ax_geo.annotate("", xy=(p_b1x1[0], p_b1x1[1]), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=2.8, mutation_scale=18))
        ax_geo.annotate("", xy=(p_b2x2[0], p_b2x2[1]), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=PURPLE_COLOR, lw=2.8, mutation_scale=18))

        # Target vector y_hat
        ax_geo.annotate("", xy=(p_yhat[0], p_yhat[1]), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=3.8, mutation_scale=22))
        ax_geo.scatter([p_yhat[0]], [p_yhat[1]], color=TEAL_COLOR, s=120, zorder=6, edgecolor=INK_COLOR, lw=1.5)
        ax_geo.annotate(f"사영 벡터 y_hat = ({u:.1f}, {v:.1f})\n[예측치: 100% 불변 고정]",
                        xy=(p_yhat[0], p_yhat[1]), xytext=(p_yhat[0] + 0.4, p_yhat[1] + 0.9),
                        fontsize=9.5, fontweight="bold", color=TEAL_COLOR,
                        arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.5),
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffffff", edgecolor=TEAL_COLOR, alpha=0.95))

        # Labels for component vectors
        label_b1_x = p_b1x1[0] / 2.0 if abs(b1) > 2.0 else b1 - 0.8
        ax_geo.text(label_b1_x, -0.65, f"β_1 x_1 ({b1:+.2f})", color=RED_COLOR,
                    fontsize=9.5, fontweight="bold", ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor=RED_COLOR, alpha=0.85))

        label_b2_x = p_b2x2[0] / 2.0
        label_b2_y = p_b2x2[1] / 2.0 + 0.45
        ax_geo.text(label_b2_x, label_b2_y, f"β_2 x_2 ({b2:+.2f})", color=PURPLE_COLOR,
                    fontsize=9.5, fontweight="bold", ha="center",
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor=PURPLE_COLOR, alpha=0.85))

        # Right: Econometric Diagnostic Dashboard
        ax_info.axis("off")

        ax_info.text(0.04, 0.96, f"■ 실시간 다중공선성 진단 대시보드 (θ = {theta_deg:.1f}°)", fontsize=12, fontweight="bold", color=INK_COLOR)
        ax_info.axhline(0.92, xmin=0.04, xmax=0.96, color=MUTED_COLOR, lw=0.8, alpha=0.5)

        ax_info.text(0.06, 0.85, "1. 기하학적 각도 및 상관관계 지표", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_info.text(0.08, 0.78, f"• 두 설명변수 사이 각도 (θ):        {theta_deg:.1f}°", fontsize=9.5, color=INK_COLOR)
        ax_info.text(0.08, 0.72, f"• 설명변수 간 상관계수 (r = cos θ):    {r_corr:.4f}", fontsize=9.5, color=INK_COLOR)
        
        vif_c = GREEN_COLOR if vif < 5 else (GOLD_COLOR if vif < 10 else RED_COLOR)
        vif_status = "안전 (Normal)" if vif < 5 else ("주의 (Moderate)" if vif < 10 else "위험/폭발 (Severe Multicollinearity)")
        ax_info.text(0.08, 0.66, f"• 분산팽창지수 (VIF = 1 / sin²θ):    {vif:.2f}  [{vif_status}]", fontsize=9.5, fontweight="bold", color=vif_c)

        ax_info.text(0.06, 0.56, "2. 회귀계수 분해 vs 사영 예측치 불변성", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_info.text(0.08, 0.49, f"• 추정 계수 β_1 (x_1 방향 좌표):       {b1:+.2f}", fontsize=9.5, fontweight="bold", color=RED_COLOR)
        ax_info.text(0.08, 0.43, f"• 추정 계수 β_2 (x_2 방향 좌표):       {b2:+.2f}", fontsize=9.5, fontweight="bold", color=PURPLE_COLOR)
        ax_info.text(0.08, 0.37, f"• 사영 예측 벡터 합산:                  β_1 x_1 + β_2 x_2 ≡ ({u:.1f}, {v:.1f})", fontsize=9.5, fontweight="bold", color=TEAL_COLOR)
        ax_info.text(0.08, 0.31, f"• 예측치 노름 ||y_hat||:                {np.linalg.norm(p_yhat):.4f} (100% 불변)", fontsize=9.5, fontweight="bold", color=TEAL_COLOR)

        ax_info.text(0.06, 0.22, "3. 계량경제학적 핵심 결론 (Core Takeaway)", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        takeaway = (
            "• [예측(Prediction)은 안전]: 열공간 C(X) 평면 자체는 불변이므로\n"
            "  사영 벡터 y_hat(그림자)은 다중공선성에 전혀 영향을 받지 않는다.\n"
            "• [인과추론(Identification)은 파탄]: 두 기저축이 겹쳐지면서\n"
            "  평행사변형 좌표계가 붕괴하여 β_1은 음(-)으로, β_2는 양(+)으로\n"
            "  상쇄 폭발하므로 개별 변수의 한계효과 식별은 불가능해진다."
        )
        ax_info.text(0.06, 0.04, takeaway, fontsize=8.8, color=INK_COLOR, va="bottom",
                     bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5efe6", edgecolor="#dfd4c5", alpha=0.95))

        fig.suptitle("OLS 다중공선성의 기하학적 본질: 평행사변형 좌표계 붕괴 vs 사영 벡터 불변성",
                     fontsize=13.0, color=INK_COLOR, fontweight="bold", y=0.965)
        plt.subplots_adjust(left=0.06, right=0.96, top=0.88, bottom=0.10, wspace=0.25)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    # Save animated GIF
    out_path = os.path.join(GIF_DIR, "ols-multicollinearity-geometry.gif")
    durations = [280]*len(thetas_fwd) + [750]*len(thetas_hold_low) + [280]*len(thetas_bwd) + [750]*len(thetas_hold_high)
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
    generate_gif_multicollinearity_geometry()
    print("All OLS projection geometry GIFs successfully generated!")
