"""Generate publication-grade animated GIFs for the Classical Testing Trinity supplement.

Outputs:
  - assets/gif/classical-testing-likelihood-geometry.gif
  - assets/gif/classical-testing-contour-inequality.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from PIL import Image

# Setup directories
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIF_DIR = os.path.join(ROOT, "assets", "gif")
os.makedirs(GIF_DIR, exist_ok=True)

# Styling parameters (Warm Editorial Theme matching the site)
BG_COLOR = "#fcf9f2"
INK_COLOR = "#2d251e"
MUTED_COLOR = "#75665b"
GRID_COLOR = "#e5ded3"
TEAL_COLOR = "#087e8b"       # Likelihood Ratio (LR)
PLUM_COLOR = "#6b4c7a"       # Wald test (Horizontal distance)
RED_COLOR = "#c0392b"        # Lagrange Multiplier (LM / Score)
GOLD_COLOR = "#d97706"       # Critical threshold / True value
GREEN_COLOR = "#15803d"      # Consistency / Unbiased indicator

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# 1. GIF 1: 1D Log-Likelihood Geometry: Horizontal (W), Vertical (LR), Slope (LM)
# ==============================================================================
def generate_gif_likelihood_geometry():
    print("Generating GIF 1: classical-testing-likelihood-geometry.gif ...")

    # Sweep theta_hat from 0.40 up to 1.35 and back to show increasing distance from H0: theta = 0
    th_fwd = np.linspace(0.40, 1.35, 18)
    th_hold = np.array([1.35] * 4)
    th_bwd = np.linspace(1.35, 0.40, 12)
    th_vals = np.concatenate([th_fwd, th_hold, th_bwd])

    n_sample = 25  # moderate sample size
    th_0 = 0.0     # Null hypothesis H0: theta = 0
    crit_val = 3.841 # Chi-sq(1) at 5%

    frames = []

    for idx, th_hat in enumerate(th_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 5.6), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.95, bottom=0.13, top=0.88, wspace=0.28)

        # ----------------------------------------------------------------------
        # Left Panel: 1D Log-Likelihood Curve and 3 Geometric Measures
        # ----------------------------------------------------------------------
        ax1.set_facecolor(BG_COLOR)
        ax1.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        # Domain for theta
        th_grid = np.linspace(-0.6, 2.0, 300)
        # Log-likelihood parabola: ln L(th) = - (n/2)*(th - th_hat)^2
        ll_grid = -0.5 * n_sample * (th_grid - th_hat)**2
        ll_max = 0.0
        ll_0 = -0.5 * n_sample * (th_0 - th_hat)**2

        # Plot log-likelihood curve
        ax1.plot(th_grid, ll_grid, color=INK_COLOR, lw=2.2, label=r"로그우도함수 $\ln L(\theta)$")

        # Peak (Unrestricted MLE)
        ax1.scatter([th_hat], [ll_max], color=INK_COLOR, s=60, zorder=5)
        ax1.axvline(th_hat, color=MUTED_COLOR, linestyle=":", lw=1.2, alpha=0.7)
        ax1.text(th_hat, ll_max + 1.2, rf"$\hat{{\theta}}_{{MLE}} = {th_hat:.2f}$",
                 color=INK_COLOR, fontsize=9.5, fontweight="bold", ha="center")

        # Null hypothesis H0: theta = 0 (Restricted MLE)
        ax1.scatter([th_0], [ll_0], color=RED_COLOR, s=60, zorder=5)
        ax1.axvline(th_0, color=MUTED_COLOR, linestyle=":", lw=1.2, alpha=0.7)
        ax1.text(th_0, ll_0 - 3.5, r"$\theta_0 = 0$ ($H_0$)",
                 color=RED_COLOR, fontsize=9.5, fontweight="bold", ha="center")

        # Tangent line at theta_0 (LM Score)
        # Slope S(0) = n*(th_hat - 0)
        slope_0 = n_sample * th_hat
        tangent_x = np.array([th_0 - 0.35, th_0 + 0.35])
        tangent_y = ll_0 + slope_0 * (tangent_x - th_0)
        ax1.plot(tangent_x, tangent_y, color=RED_COLOR, lw=2.0, linestyle="-.",
                 label=rf"LM 접선 기울기 (Score $S(\theta_0) = {slope_0:.1f}$)")

        # 1. Wald: Horizontal Arrow on parameter axis
        y_wald_bar = -22.0
        ax1.annotate("", xy=(th_hat, y_wald_bar), xytext=(th_0, y_wald_bar),
                     arrowprops=dict(arrowstyle="<->", color=PLUM_COLOR, lw=2.0))
        ax1.text((th_0 + th_hat)/2, y_wald_bar + 1.2, r"Wald: 수평 거리 $(\hat{\theta} - \theta_0)$",
                 color=PLUM_COLOR, fontsize=9.0, fontweight="bold", ha="center")

        # 2. LR: Vertical Arrow of log-likelihood drop
        x_lr_bar = th_hat + 0.15
        ax1.annotate("", xy=(x_lr_bar, ll_max), xytext=(x_lr_bar, ll_0),
                     arrowprops=dict(arrowstyle="<->", color=TEAL_COLOR, lw=2.0))
        ax1.text(x_lr_bar + 0.06, (ll_max + ll_0)/2, r"LR: 수직 높이차" "\n" r"$2[\ln L(\hat{\theta}) - \ln L(\theta_0)]$",
                 color=TEAL_COLOR, fontsize=8.8, fontweight="bold", va="center")

        # Horizontal dashed line for LR height reference
        ax1.axhline(ll_0, color=TEAL_COLOR, linestyle="--", lw=1.0, alpha=0.5)

        ax1.set_xlim(-0.6, 2.0)
        ax1.set_ylim(-26.0, 4.0)
        ax1.set_xlabel(r"모수 $\theta$", fontsize=10.0, color=INK_COLOR)
        ax1.set_ylabel(r"로그우도 $\ln L(\theta)$", fontsize=10.0, color=INK_COLOR)
        ax1.set_title(r"로그우도 곡면 위의 3대 측정 기하 (수평·수직·접선)",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=10)
        ax1.legend(loc="upper right", framealpha=0.90, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.0)

        # Compute W, LR, LM statistics
        # In this Gaussian model:
        # SSR_U prop to 1, SSR_R / SSR_U = 1 + x where x = (th_hat - 0)^2
        x_stat = (th_hat - th_0)**2
        W_val = n_sample * x_stat
        LR_val = n_sample * np.log(1.0 + x_stat)
        LM_val = n_sample * (x_stat / (1.0 + x_stat))

        # ----------------------------------------------------------------------
        # Right Panel: Finite-Sample Inequality W >= LR >= LM & Conflict Zone
        # ----------------------------------------------------------------------
        ax2.set_facecolor(BG_COLOR)
        ax2.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        categories = ["LM (접선)", "LR (높이)", "Wald (수평)"]
        values = [LM_val, LR_val, W_val]
        colors = [RED_COLOR, TEAL_COLOR, PLUM_COLOR]

        y_pos = np.arange(len(categories))
        bars = ax2.barh(y_pos, values, height=0.52, color=colors, alpha=0.88, edgecolor=INK_COLOR, lw=1.2)

        # Critical threshold line (5% chi-square)
        ax2.axvline(crit_val, color=GOLD_COLOR, linestyle="--", lw=2.0, label=r"5% 임계치 ($\chi_1^2 = 3.841$)")

        # Add values inside or beside bars
        for bar, val in zip(bars, values):
            ax2.text(val + 0.6, bar.get_y() + bar.get_height()/2, f"{val:.2f}",
                     va="center", ha="left", fontsize=9.5, fontweight="bold", color=INK_COLOR)

        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(categories, fontsize=10.0, fontweight="bold", color=INK_COLOR)
        ax2.set_xlim(0, 48)
        ax2.set_xlabel("검정통계량 수치", fontsize=10.0, color=INK_COLOR)
        ax2.set_title(r"유한표본 부등식: $W \geq LR \geq LM$ 실시간 검증",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=10)
        ax2.legend(loc="lower right", framealpha=0.90, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.5)

        # Status annotation badge
        if LM_val > crit_val:
            status_text = "결론: 3대 검정 모두 기각 (합의 기각)"
            status_color = "#15803d"
        elif W_val > crit_val and LM_val <= crit_val:
            status_text = "주의: 검정 간 상충 구간! (Wald 기각, LM 채택)"
            status_color = "#b83b26"
        else:
            status_text = "결론: 3대 검정 모두 기각 실패 (채택)"
            status_color = "#0369a1"

        ineq_badge = (
            rf"부등식: $W ({W_val:.2f}) \geq LR ({LR_val:.2f}) \geq LM ({LM_val:.2f})$" "\n"
            rf"{status_text}"
        )
        ax2.text(0.50, 0.28, ineq_badge, transform=ax2.transAxes,
                 fontsize=9.0, va="center", ha="center",
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#f3ede2", edgecolor=status_color, lw=1.5, alpha=0.96))

        # Capture frame
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "classical-testing-likelihood-geometry.gif")
    durations = [140] * len(th_fwd) + [700] * len(th_hold) + [140] * len(th_bwd)
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
# 2. GIF 2: 2D Contour Geometry & Sample Size Size-Distortion Convergence
# ==============================================================================
def generate_gif_contour_inequality():
    print("Generating GIF 2: classical-testing-contour-inequality.gif ...")

    # Sweep sample size n from 20 to 250 to show convergence of size distortion
    n_fwd = np.round(np.geomspace(20, 260, 18)).astype(int)
    n_hold = np.array([260] * 4)
    n_bwd = np.round(np.geomspace(260, 20, 12)).astype(int)
    n_vals = np.concatenate([n_fwd, n_hold, n_bwd])

    frames = []

    # 2D Parameter contour setup
    # Parameters beta1, beta2
    b1_hat, b2_hat = 1.4, 1.4
    # Constraint line: beta1 + beta2 = 1.6  (so H0 is slightly displaced)
    # Restricted MLE on line: (0.8, 0.8)

    for idx, n_cur in enumerate(n_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.0, 5.6), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.95, bottom=0.13, top=0.88, wspace=0.28)

        # ----------------------------------------------------------------------
        # Left Panel: 2D Contour Ellipses & Tangency with Constraint Line
        # ----------------------------------------------------------------------
        ax1.set_facecolor(BG_COLOR)
        ax1.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        b1_grid = np.linspace(-0.2, 2.6, 150)
        b2_grid = np.linspace(-0.2, 2.6, 150)
        B1, B2 = np.meshgrid(b1_grid, b2_grid)

        # Quadratic surface (elliptical log-likelihood)
        # ln L = - 0.5 * [2*(b1 - b1_hat)^2 + 1*(b2 - b2_hat)^2 + 0.8*(b1 - b1_hat)*(b2 - b2_hat)]
        Q = 2.0 * (B1 - b1_hat)**2 + 1.2 * (B2 - b2_hat)**2 + 0.6 * (B1 - b1_hat) * (B2 - b2_hat)
        levels = [0.2, 0.6, 1.2, 2.2, 3.8, 6.0]

        cs = ax1.contour(B1, B2, Q, levels=levels, colors=MUTED_COLOR, alpha=0.6, linewidths=1.2)
        ax1.clabel(cs, inline=True, fontsize=7.5, fmt="%.1f")

        # Unrestricted MLE
        ax1.scatter([b1_hat], [b2_hat], color=INK_COLOR, s=65, zorder=6, label=r"비제약 정점 $\hat{\beta}$ (MLE)")

        # Constraint line: b1 + b2 = 1.6 => b2 = 1.6 - b1
        c_line_x = np.array([-0.2, 2.4])
        c_line_y = 1.6 - c_line_x
        ax1.plot(c_line_x, c_line_y, color=GOLD_COLOR, lw=2.2, linestyle="-",
                 label=r"제약선 $H_0: \beta_1 + \beta_2 = 1.6$")

        # Restricted MLE (tangency point)
        b1_tilde, b2_tilde = 0.72, 0.88
        ax1.scatter([b1_tilde], [b2_tilde], color=RED_COLOR, s=65, zorder=6,
                    label=r"제약 접점 $\tilde{\beta}$ (Restricted MLE)")

        # Normal/Gradient vector at restricted MLE: S(beta_tilde)
        grad_dx = 0.35
        grad_dy = 0.35
        ax1.annotate("", xy=(b1_tilde + grad_dx, b2_tilde + grad_dy), xytext=(b1_tilde, b2_tilde),
                     arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=2.2))
        ax1.text(b1_tilde + grad_dx + 0.05, b2_tilde + grad_dy + 0.05,
                 r"Score $S(\tilde{\beta}) = R'\tilde{\lambda}$" "\n(제약선 법선벡터)",
                 color=RED_COLOR, fontsize=8.5, fontweight="bold")

        # Wald vector: connecting beta_hat to beta_tilde
        ax1.annotate("", xy=(b1_tilde, b2_tilde), xytext=(b1_hat, b2_hat),
                     arrowprops=dict(arrowstyle="<->", color=PLUM_COLOR, lw=1.8, linestyle="--"))
        ax1.text((b1_hat + b1_tilde)/2 + 0.08, (b2_hat + b2_tilde)/2 - 0.12,
                 r"Wald 벡터 $(\hat{\beta} - \tilde{\beta})$", color=PLUM_COLOR, fontsize=8.5, fontweight="bold")

        ax1.set_xlim(-0.2, 2.4)
        ax1.set_ylim(-0.2, 2.4)
        ax1.set_xlabel(r"모수 $\beta_1$", fontsize=10.0, color=INK_COLOR)
        ax1.set_ylabel(r"모수 $\beta_2$", fontsize=10.0, color=INK_COLOR)
        ax1.set_title(r"2차원 모수공간 등고선과 제약선 외접 기하",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=10)
        ax1.legend(loc="upper right", framealpha=0.90, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=7.8)

        # ----------------------------------------------------------------------
        # Right Panel: Sample Size Dynamics & Type I Error Size Distortion
        # ----------------------------------------------------------------------
        ax2.set_facecolor(BG_COLOR)
        ax2.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        n_curve = np.linspace(15, 300, 100)
        # Analytical approximation of actual rejection rates under nominal 5% (q=2)
        # Wald over-rejects: 5% + C/n
        # LM under-rejects: 5% - C/n
        # LR is very close to 5%: 5% + 0.2*C/n
        c_distort = 120.0
        rej_wald = 5.0 + c_distort / n_curve
        rej_lm = np.maximum(0.5, 5.0 - c_distort / n_curve)
        rej_lr = 5.0 + 20.0 / n_curve

        ax2.plot(n_curve, rej_wald, color=PLUM_COLOR, lw=2.0, label="Wald 검정 (과대기각 / 왜곡)")
        ax2.plot(n_curve, rej_lr, color=TEAL_COLOR, lw=2.0, label="LR 검정 (중립적 / 안정)")
        ax2.plot(n_curve, rej_lm, color=RED_COLOR, lw=2.0, label="LM 검정 (과소기각 / 보수적)")

        ax2.axhline(5.0, color=GOLD_COLOR, linestyle="--", lw=1.5, label="공칭 5% 유의수준 (Nominal Size)")

        # Current n indicator vertical line
        ax2.axvline(n_cur, color=INK_COLOR, linestyle=":", lw=1.5)

        # Current values
        cur_w = 5.0 + c_distort / n_cur
        cur_lm = max(0.5, 5.0 - c_distort / n_cur)
        cur_lr = 5.0 + 20.0 / n_cur

        ax2.scatter([n_cur], [cur_w], color=PLUM_COLOR, s=50, zorder=5)
        ax2.scatter([n_cur], [cur_lr], color=TEAL_COLOR, s=50, zorder=5)
        ax2.scatter([n_cur], [cur_lm], color=RED_COLOR, s=50, zorder=5)

        ax2.set_xlim(15, 300)
        ax2.set_ylim(0, 16)
        ax2.set_xlabel("표본 크기 n", fontsize=10.0, color=INK_COLOR)
        ax2.set_ylabel("실제 기각률 (%) [제1종 오류]", fontsize=10.0, color=INK_COLOR)
        ax2.set_title(rf"표본 크기 $n = {n_cur}$에 따른 3대 검정 점근 수렴 동학",
                      fontsize=11.0, fontweight="bold", color=INK_COLOR, pad=10)
        ax2.legend(loc="upper right", framealpha=0.90, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.0)

        # Current status badge
        distort_badge = (
            rf"현재 $n = {n_cur}$ 실제 기각률:" "\n"
            rf"  - Wald : {cur_w:.1f}% (허위 발견 위험)" "\n"
            rf"  - LR   : {cur_lr:.1f}% (가장 안정)" "\n"
            rf"  - LM   : {cur_lm:.1f}% (보수적 검정)"
        )
        ax2.text(0.04, 0.08, distort_badge, transform=ax2.transAxes,
                 fontsize=8.5, va="bottom", ha="left",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#f3ede2", edgecolor=GRID_COLOR, alpha=0.95))

        # Capture frame
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "classical-testing-contour-inequality.gif")
    durations = [140] * len(n_fwd) + [700] * len(n_hold) + [140] * len(n_bwd)
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
    generate_gif_likelihood_geometry()
    generate_gif_contour_inequality()
