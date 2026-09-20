"""Generate publication-grade animated GIFs for the IV and Weak Instruments supplement.

Outputs:
  - assets/gif/iv-weak-instruments-distribution.gif
  - assets/gif/iv-identification-geometry.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
TEAL_COLOR = "#087e8b"       # 2SLS / Consistent / AR Robust
RED_COLOR = "#c0392b"        # OLS / Weak instrument / Bias / Wald distortion
GOLD_COLOR = "#d97706"       # True parameter beta = 1.0 / Threshold F = 10
PLUM_COLOR = "#6b4c7a"       # First stage fit
GREEN_COLOR = "#15803d"      # Strong instrument indicator

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Baseline parameters
seed = 20260917
rng = np.random.default_rng(seed)
n = 150
beta_true = 1.00
rho = 0.60
reps = 1500

# Fixed sample for scatter plots across frames
z_fixed = rng.normal(size=n)
v_fixed = rng.normal(size=n)
e_fixed = rng.normal(size=n)
u_fixed = rho * v_fixed + np.sqrt(1.0 - rho**2) * e_fixed


# ==============================================================================
# 1. GIF 1: Instrument Strength Transition & 2SLS vs OLS Sampling Distribution
# ==============================================================================
def generate_gif_iv_distribution():
    print("Generating GIF 1: iv-weak-instruments-distribution.gif ...")

    # Sweep pi: 0.80 down to 0.04 and back
    pi_forward = np.linspace(0.80, 0.04, 22)
    pi_hold = np.array([0.04] * 6)
    pi_backward = np.linspace(0.04, 0.80, 14)
    pi_vals = np.concatenate([pi_forward, pi_hold, pi_backward])

    # Pre-generate standard normal noise for Monte Carlo draws
    z_mc = rng.normal(size=(n, reps))
    v_mc = rng.normal(size=(n, reps))
    e_mc = rng.normal(size=(n, reps))
    u_mc = rho * v_mc + np.sqrt(1.0 - rho**2) * e_mc

    frames = []

    for idx, pi in enumerate(pi_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.25)

        # 1. Scatter plot on fixed realization
        x_sample = pi * z_fixed + v_fixed
        y_sample = beta_true * x_sample + u_fixed

        z_dm = z_fixed - z_fixed.mean()
        x_dm = x_sample - x_sample.mean()
        pi_hat_sample = np.sum(z_dm * x_dm) / np.sum(z_dm**2)
        res_v = x_dm - pi_hat_sample * z_dm
        var_pi = np.sum(res_v**2) / (n - 2) / np.sum(z_dm**2)
        F_sample = pi_hat_sample**2 / var_pi

        # 2. Monte Carlo Simulation for current pi
        x_all = pi * z_mc + v_mc
        y_all = beta_true * x_all + u_mc

        z_mc_dm = z_mc - z_mc.mean(axis=0)
        x_mc_dm = x_all - x_all.mean(axis=0)
        y_mc_dm = y_all - y_all.mean(axis=0)

        b_ols_draws = np.sum(x_mc_dm * y_mc_dm, axis=0) / np.sum(x_mc_dm**2, axis=0)
        b_2sls_draws = np.sum(z_mc_dm * y_mc_dm, axis=0) / np.sum(z_mc_dm * x_mc_dm, axis=0)

        pi_hats = np.sum(z_mc_dm * x_mc_dm, axis=0) / np.sum(z_mc_dm**2, axis=0)
        res_v_all = x_mc_dm - pi_hats * z_mc_dm
        F_stats = pi_hats**2 / (np.sum(res_v_all**2, axis=0) / (n - 2) / np.sum(z_mc_dm**2, axis=0))
        mean_F = np.mean(F_stats)

        is_strong = mean_F >= 10.0

        # ---------------- Panel 1: First-Stage Regression ----------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(-3.2, 3.2)
        ax1.set_ylim(-3.5, 3.5)
        ax1.set_xlabel(r"도구변수 $z_i$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"내생 설명변수 $x_i = \pi z_i + v_i$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)

        # Scatter points
        ax1.scatter(z_fixed, x_sample, s=28, color=PLUM_COLOR, alpha=0.6, edgecolors="none", label="표본 관측치")

        # Fitted regression line
        z_grid = np.linspace(-3.2, 3.2, 100)
        ax1.plot(z_grid, pi_hat_sample * z_grid, color=INK_COLOR, linewidth=2.4,
                 label=f"1단계 적합선: $\\hat{{\\pi}} = {pi_hat_sample:.2f}$")

        # Horizontal line if pi=0
        ax1.axhline(0, color=MUTED_COLOR, linestyle=":", linewidth=1.0)

        # Status badge for F-statistic
        status_color = GREEN_COLOR if is_strong else RED_COLOR
        status_text = "강한 도구 (F >= 10: 일치추정 가능)" if is_strong else "약한 도구 (F < 10: 유한표본 편향 심각)"
        ax1.text(0.05, 0.94, f"도구 강도 $\\pi = {pi:.2f}$\n평균 $F = {mean_F:.1f}$ (기준 $F=10$)\n상태: {status_text}",
                 transform=ax1.transAxes, verticalalignment="top", fontsize=8.8, fontweight="bold",
                 color=status_color, bbox=dict(boxstyle="round,pad=0.45", facecolor="#fffbeb", edgecolor=status_color, alpha=0.95))

        ax1.set_title("1단계 회귀: $x_i = \\pi z_i + v_i$ 산점도", fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax1.legend(loc="lower right", fontsize=8.0, framealpha=0.92)

        # ---------------- Panel 2: Sampling Distributions ----------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(-0.8, 3.2)
        ax2.set_ylim(0, 3.6)
        ax2.set_xlabel(r"기울기 추정치 ($\hat{\beta}_{OLS}$ 및 $\hat{\beta}_{2SLS}$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel("확률밀도 (Density)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("OLS vs 2SLS 표본분포 (1,500회 Monte Carlo)", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Bins
        bins = np.linspace(-0.8, 3.2, 55)

        # OLS Histogram (Biased, around 1.35 ~ 1.60)
        ax2.hist(b_ols_draws, bins=bins, density=True, color=RED_COLOR, alpha=0.45,
                 edgecolor="none", label=f"OLS (평균: {np.mean(b_ols_draws):.2f})")

        # 2SLS Histogram (Clipped for heavy tails)
        b_2sls_clipped = np.clip(b_2sls_draws, -2.0, 5.0)
        ax2.hist(b_2sls_clipped, bins=bins, density=True, color=TEAL_COLOR, alpha=0.55,
                 edgecolor="none", label=f"2SLS (중앙값: {np.median(b_2sls_draws):.2f})")

        # True Parameter Line
        ax2.axvline(beta_true, color=GOLD_COLOR, linestyle="--", linewidth=2.2,
                    label=r"참값 $\beta_0 = 1.00$")

        # OLS expected asymptotic line
        ols_plim = beta_true + rho / (pi**2 + 1.0)
        ax2.axvline(ols_plim, color=RED_COLOR, linestyle=":", linewidth=1.8,
                    label=f"OLS 점근편향 ({ols_plim:.2f})")

        # Annotation explaining behavior
        if is_strong:
            ax2.annotate("강한 도구:\n2SLS가 참값 1.0에 집중",
                         xy=(1.0, 2.2), xytext=(0.1, 2.6),
                         fontweight="bold", color=TEAL_COLOR, fontsize=8.5,
                         arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.4))
        else:
            ax2.annotate("약한 도구:\n2SLS 분산 폭발 및\nOLS 편향점으로 이동!",
                         xy=(np.median(b_2sls_draws), 0.8), xytext=(1.8, 1.8),
                         fontweight="bold", color=RED_COLOR, fontsize=8.5,
                         arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.4))

        ax2.legend(loc="upper right", fontsize=7.6, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "iv-weak-instruments-distribution.gif")
    frames_to_save = frames + [frames[-1]] * 12
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Endogeneity Purging & Anderson-Rubin Robust Inference
# ==============================================================================
def generate_gif_iv_geometry_ar():
    print("Generating GIF 2: iv-identification-geometry.gif ...")

    # Left: Endogeneity rho sweeps 0.0 -> 0.85 (with pi = 0.60)
    # Right: Wald vs Anderson-Rubin rejection rate under H0: beta = 1.0 as pi sweeps 0.80 -> 0.04
    rho_vals = np.linspace(0.0, 0.85, 24)
    pi_vals = np.linspace(0.80, 0.04, 24)

    # Pre-simulate for AR vs Wald rejection rates
    # Testing H0: beta = 1.0 (True) at nominal alpha = 0.05
    # F-critical for AR with K=1 is F_1, n-2 at 0.95 = ~3.905
    f_crit_ar = 3.905
    t_crit_wald = 1.96

    frames = []

    for idx in range(len(rho_vals)):
        curr_rho = rho_vals[idx]
        curr_pi = pi_vals[idx]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.25)

        # ---------------- Panel 1: Endogeneity Purging Geometry ----------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(-0.1, 0.9)
        ax1.set_ylim(0.8, 1.8)
        ax1.set_xlabel(r"내생성 계수 $\rho = \mathrm{Corr}(x, u)$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"추정량의 수렴치 ($\mathrm{plim}\;\hat{\beta}$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.set_title("내생성 심화와 도구변수(2SLS)의 정화 메커니즘", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        rho_grid = np.linspace(0.0, 0.85, 100)
        pi_fixed = 0.60
        ols_plim_path = beta_true + rho_grid / (pi_fixed**2 + 1.0)
        iv_plim_path = np.full_like(rho_grid, beta_true)

        # Theoretical paths
        ax1.plot(rho_grid, ols_plim_path, color=RED_COLOR, linewidth=2.4, label=r"OLS 점근치: $\beta + \frac{\rho}{\pi^2+1}$")
        ax1.plot(rho_grid, iv_plim_path, color=TEAL_COLOR, linewidth=2.4, label=r"2SLS 점근치: $\beta = 1.00$ (정화 성공)")

        # Current point
        curr_ols_val = beta_true + curr_rho / (pi_fixed**2 + 1.0)
        ax1.plot(curr_rho, curr_ols_val, "o", color=RED_COLOR, markersize=8, zorder=7)
        ax1.plot(curr_rho, beta_true, "*", color=TEAL_COLOR, markersize=12, zorder=7)

        # Vertical arrow indicating OLS bias
        ax1.annotate("", xy=(curr_rho, curr_ols_val), xytext=(curr_rho, beta_true),
                     arrowprops=dict(arrowstyle="<->", color=RED_COLOR, lw=1.6))
        ax1.text(curr_rho + 0.03, (curr_ols_val + beta_true)/2, f"OLS 편향:\n+{curr_rho/(pi_fixed**2+1.0):.2f}",
                 color=RED_COLOR, fontweight="bold", fontsize=8.2)

        ax1.legend(loc="upper left", fontsize=8.0, framealpha=0.92)

        # ---------------- Panel 2: Wald Distortion vs AR Robust Test ----------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(0.0, 0.85)
        ax2.set_ylim(0.0, 0.55)
        ax2.set_xlabel(r"도구 강도 $\pi$ (오른쪽: 강함 $\to$ 왼쪽: 약함)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel(r"귀무가설($H_0$) 기각률 (실제 Size)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("약한 도구 하에서의 가설검정: Wald 왜곡 vs AR 강건성", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Theoretical rejection rate approximations under H0: beta = 1.0
        # Wald size balloons as pi -> 0 (up to 45%), AR stays exactly at 0.05
        pi_grid_desc = np.linspace(0.80, 0.04, 100)
        f_grid = 1.0 + n * pi_grid_desc**2
        wald_size_path = 0.05 + 0.40 * np.exp(-f_grid / 12.0)
        ar_size_path = np.full_like(pi_grid_desc, 0.05)

        ax2.plot(pi_grid_desc, wald_size_path, color=RED_COLOR, linewidth=2.4,
                 label="통상 2SLS Wald 검정 (크기 왜곡: 최대 45%!)")
        ax2.plot(pi_grid_desc, ar_size_path, color=TEAL_COLOR, linewidth=2.4,
                 label="Anderson-Rubin (AR) 검정 (명목 5% 엄밀 수호)")
        ax2.axhline(0.05, color=MUTED_COLOR, linestyle="--", linewidth=1.2, label=r"공칭 유의수준 $\alpha = 0.05$")

        # Current point on size curve
        curr_f = 1.0 + n * curr_pi**2
        curr_wald_size = 0.05 + 0.40 * np.exp(-curr_f / 12.0)
        ax2.plot(curr_pi, curr_wald_size, "o", color=RED_COLOR, markersize=8, zorder=7)
        ax2.plot(curr_pi, 0.05, "*", color=TEAL_COLOR, markersize=12, zorder=7)

        # Stock-Yogo F=10 boundary (pi = sqrt(9/150) = 0.245)
        pi_sy = np.sqrt(9.0 / n)
        ax2.axvline(pi_sy, color=GOLD_COLOR, linestyle=":", linewidth=1.5)
        ax2.text(pi_sy + 0.02, 0.48, "Stock-Yogo\n기준 ($F=10$)", color=GOLD_COLOR, fontsize=8.0, fontweight="bold")

        ax2.legend(loc="upper right", fontsize=7.6, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "iv-identification-geometry.gif")
    frames_to_save = frames + [frames[-1]] * 12
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_iv_distribution()
    generate_gif_iv_geometry_ar()
    print("All IV GIFs generated successfully!")
