"""Generate publication-grade animated GIFs for the OLS Geometry and Sampling Variation supplement.

Outputs:
  - assets/gif/ols-sample-size-sampling-distribution.gif
  - assets/gif/ols-parameter-confidence-ellipse.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
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
NAVY_COLOR = "#1f3b5c"       # OLS fit / OLS ellipse / Blueprint
RED_COLOR = "#b83b26"        # Sample data / True parameter / Terracotta
TEAL_COLOR = "#087e8b"       # Theoretical density / Consistent / AR
PLUM_COLOR = "#6b4c7a"       # Monte Carlo histogram
GOLD_COLOR = "#d97706"       # True population line / 95% CI marker
GREEN_COLOR = "#15803d"      # BLUE indicator / Minimum variance

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Baseline parameters
seed = 20260920
rng = np.random.default_rng(seed)
beta_0_true = 1.00
beta_1_true = 1.40
sigma_true = 0.80
reps = 1500

# Fixed large pool of x and standard normal errors for deterministic subsamples
N_MAX = 250
x_pool = np.linspace(-2.0, 2.0, N_MAX) + 0.12 * rng.normal(size=N_MAX)
# Ensure x is centered around ~0.20 to maintain a slight non-zero mean for ellipse tilt
x_pool = x_pool - np.mean(x_pool) + 0.20
u_pool = sigma_true * rng.normal(size=N_MAX)


# ==============================================================================
# 1. GIF 1: Sample Size Transition & OLS Sampling Variation Contraction
# ==============================================================================
def generate_gif_sample_size():
    print("Generating GIF 1: ols-sample-size-sampling-distribution.gif ...")

    # Sequence of sample sizes: 16 to 220
    n_forward = [16, 20, 25, 32, 42, 55, 72, 95, 125, 165, 220]
    n_hold = [220, 220, 220]
    n_backward = [165, 110, 65, 36, 22]
    n_sequence = n_forward + n_hold + n_backward

    frames = []

    for idx, n in enumerate(n_sequence):
        # Current sample
        x_n = x_pool[:n]
        u_n = u_pool[:n]
        y_n = beta_0_true + beta_1_true * x_n + u_n

        # OLS estimation
        x_bar = np.mean(x_n)
        y_bar = np.mean(y_n)
        s_xx = np.sum((x_n - x_bar)**2)
        s_xy = np.sum((x_n - x_bar) * (y_n - y_bar))
        b1_hat = s_xy / s_xx
        b0_hat = y_bar - b1_hat * x_bar

        y_hat = b0_hat + b1_hat * x_n
        residuals = y_n - y_hat
        sse = np.sum(residuals**2)
        s2 = sse / (n - 2)
        s_res = np.sqrt(s2)
        se_b1 = np.sqrt(s2 / s_xx)
        sst = np.sum((y_n - y_bar)**2)
        r2 = 1.0 - (sse / sst) if sst > 1e-12 else 0.0
        ortho_err = np.max([np.abs(np.sum(residuals)), np.abs(np.sum(x_n * residuals))])

        # Fixed-X Monte Carlo simulation (reps draws)
        # Using vectorized matrix operations for high performance
        # y_draws: shape (n, reps)
        mc_rng = np.random.default_rng(seed + n * 101)
        mc_u = sigma_true * mc_rng.normal(size=(n, reps))
        mc_y = (beta_0_true + beta_1_true * x_n)[:, None] + mc_u
        mc_y_bar = np.mean(mc_y, axis=0) # shape (reps,)
        mc_s_xy = np.sum((x_n - x_bar)[:, None] * (mc_y - mc_y_bar[None, :]), axis=0)
        mc_b1 = mc_s_xy / s_xx

        # Theoretical standard error: sigma / sqrt(S_xx)
        theo_se_b1 = sigma_true / np.sqrt(s_xx)

        # Plot setup
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.0), dpi=120)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, top=0.88, bottom=0.14, wspace=0.26)

        # ----------------------------------------------------------------------
        # Left Panel: Sample Scatter, Fitted Line, and Residual Stems
        # ----------------------------------------------------------------------
        ax1.set_facecolor(BG_COLOR)
        for spine in ax1.spines.values():
            spine.set_color(GRID_COLOR)
        ax1.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

        # True regression line
        x_line = np.linspace(-2.4, 2.4, 100)
        ax1.plot(x_line, beta_0_true + beta_1_true * x_line, "--", color=MUTED_COLOR,
                 lw=1.8, label=r"모집단 회귀선: $y = 1.0 + 1.4x$", zorder=2)

        # Residual stems
        for xi, yi, yhi in zip(x_n, y_n, y_hat):
            ax1.plot([xi, xi], [yhi, yi], "-", color="#caa892", lw=0.9, alpha=0.7, zorder=3)

        # Fitted OLS line
        ax1.plot(x_line, b0_hat + b1_hat * x_line, "-", color=NAVY_COLOR,
                 lw=2.5, label=rf"OLS 적합선: $\hat{{y}} = {b0_hat:.2f} + {b1_hat:.2f}x$", zorder=4)

        # Sample scatter
        ax1.scatter(x_n, y_n, color=RED_COLOR, s=36, edgecolor="#ffffff",
                    linewidth=0.6, alpha=0.85, label=rf"표본 관측치 ($n={n}$)", zorder=5)

        ax1.set_xlim(-2.4, 2.4)
        ax1.set_ylim(-3.2, 5.2)
        ax1.set_xlabel(r"설명변수 $x_i$", fontsize=10.5, color=INK_COLOR)
        ax1.set_ylabel(r"종속변수 $y_i$", fontsize=10.5, color=INK_COLOR)
        ax1.set_title(rf"OLS 표본 적합과 직교 사영 ($n = {n}$)", fontsize=11.5, fontweight="bold", color=INK_COLOR, pad=8)
        ax1.legend(loc="upper left", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.5)

        # Summary badge on left panel
        info_text_left = (
            rf"$\hat{{\beta}}_1 = {b1_hat:.3f}$  ($SE = {se_b1:.3f}$)" "\n"
            rf"$s = {s_res:.3f}$  ($\sigma = {sigma_true:.2f}$)" "\n"
            rf"$R^2 = {r2:.3f}$" "\n"
            rf"$\max |X'\hat{{e}}| = {ortho_err:.1e}$"
        )
        ax1.text(0.96, 0.05, info_text_left, transform=ax1.transAxes,
                 fontsize=8.5, va="bottom", ha="right",
                 bbox=dict(boxstyle="round,pad=0.45", facecolor="#f3ede2", edgecolor="#d5c7b5", alpha=0.95))

        # ----------------------------------------------------------------------
        # Right Panel: Fixed-X Monte Carlo Sampling Distribution of b1
        # ----------------------------------------------------------------------
        ax2.set_facecolor(BG_COLOR)
        for spine in ax2.spines.values():
            spine.set_color(GRID_COLOR)
        ax2.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

        # Histogram of Monte Carlo draws
        bins = np.linspace(0.80, 2.00, 36)
        counts, _, _ = ax2.hist(mc_b1, bins=bins, density=True, color=PLUM_COLOR,
                                alpha=0.45, edgecolor="#ffffff", linewidth=0.5,
                                label=rf"MC 표본분포 ($B={reps:,}$)")

        # Theoretical Gaussian density curve: N(beta_1, theo_se_b1^2)
        b_grid = np.linspace(0.80, 2.00, 300)
        theo_pdf = (1.0 / (np.sqrt(2.0 * np.pi) * theo_se_b1)) * np.exp(-0.5 * ((b_grid - beta_1_true) / theo_se_b1)**2)
        ax2.plot(b_grid, theo_pdf, "-", color=TEAL_COLOR, lw=2.4,
                 label=rf"이론적 정규밀도 $\mathcal{{N}}(\beta_1, \sigma^2/S_{{xx}})$")

        # True beta_1 line
        ax2.axvline(beta_1_true, color=GOLD_COLOR, linestyle="--", lw=2.0,
                    label=rf"참 모수 $\beta_1 = {beta_1_true:.2f}$")

        # 95% Confidence Interval band on distribution
        ci_low = beta_1_true - 1.96 * theo_se_b1
        ci_high = beta_1_true + 1.96 * theo_se_b1
        ax2.axvspan(ci_low, ci_high, color=TEAL_COLOR, alpha=0.10,
                    label=r"이론적 95% 신뢰구간 ($\pm 1.96 SE$)")

        ax2.set_xlim(0.80, 2.00)
        ax2.set_ylim(0, max(7.5, np.max(theo_pdf) * 1.15))
        ax2.set_xlabel(r"기울기 추정량 $\hat{\beta}_1$", fontsize=10.5, color=INK_COLOR)
        ax2.set_ylabel("확률밀도 (Density)", fontsize=10.5, color=INK_COLOR)
        ax2.set_title(r"고정 $X$ 표본분포 수축: $SE(\hat{\beta}_1) \propto 1/\sqrt{n}$",
                      fontsize=11.5, fontweight="bold", color=INK_COLOR, pad=8)
        ax2.legend(loc="upper right", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.2)

        # Summary badge on right panel
        mc_mean_b1 = np.mean(mc_b1)
        mc_sd_b1 = np.std(mc_b1)
        info_text_right = (
            rf"표본 크기 $n = {n}$" "\n"
            rf"이론적 $SE(\hat{{\beta}}_1) = {theo_se_b1:.3f}$" "\n"
            rf"MC 평균: {mc_mean_b1:.3f} | 표준편차: {mc_sd_b1:.3f}" "\n"
            rf"95% 구간폭: $\Delta = {ci_high - ci_low:.3f}$"
        )
        ax2.text(0.04, 0.95, info_text_right, transform=ax2.transAxes,
                 fontsize=8.5, va="top", ha="left",
                 bbox=dict(boxstyle="round,pad=0.45", facecolor="#edf2f7", edgecolor="#cbd5e1", alpha=0.95))

        # Save frame to PIL
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    # Save animated GIF
    out_path = os.path.join(GIF_DIR, "ols-sample-size-sampling-distribution.gif")
    durations = [280] * len(n_forward) + [650, 650, 650] + [280] * len(n_backward)
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
# 2. GIF 2: Joint Confidence Ellipse and Gauss–Markov BLUE Geometry
# ==============================================================================
def generate_gif_parameter_confidence_ellipse():
    print("Generating GIF 2: ols-parameter-confidence-ellipse.gif ...")

    # Sequence of frames demonstrating:
    # Left: Joint 95% Confidence Ellipse in (beta_0, beta_1) plane contracting as n expands
    # Right: Gauss-Markov Theorem: Loewner ordering of covariance matrix
    #        Var(tilde_beta) = Var(hat_beta) + D D' >= Var(hat_beta)
    #        demonstrating that OLS achieves the innermost dispersion ellipse!

    n_vals = [18, 22, 28, 36, 48, 64, 85, 115, 160, 220]
    n_hold = [220, 220, 220]
    n_back = [160, 100, 55, 30]
    n_seq = n_vals + n_hold + n_back

    # F critical values (2, n-2) at alpha=0.05
    # For moderate to large n, F_{2, n-2}(0.05) ~ 3.10 to 3.55
    def f_crit_05(df2):
        # Good numerical approximation for F(2, df2, 0.05)
        # Exact: 2 * ( (1/0.05)^(2/df2) - 1 ) / ... wait, for numerator df1=2:
        # P(F <= c) = 1 - (1 + 2c/df2)^(-df2/2) = 0.95 => 1 + 2c/df2 = 0.05^(-2/df2)
        # c = (df2 / 2) * (0.05^(-2/df2) - 1)
        return (df2 / 2.0) * (0.05**(-2.0 / df2) - 1.0)

    # Student-t critical values at alpha=0.05 two-tailed
    def t_crit_05(df):
        # Hill's approximation / standard formula
        return 1.96 + 2.37 / df + 2.82 / (df**2)

    frames = []

    for idx, n in enumerate(n_seq):
        x_n = x_pool[:n]
        u_n = u_pool[:n]
        y_n = beta_0_true + beta_1_true * x_n + u_n

        # Regressors
        X_mat = np.column_stack([np.ones(n), x_n])
        XtX = X_mat.T @ X_mat
        XtX_inv = np.linalg.inv(XtX)
        beta_hat = XtX_inv @ (X_mat.T @ y_n)
        b0_h, b1_h = beta_hat[0], beta_hat[1]

        resid = y_n - X_mat @ beta_hat
        df_e = n - 2
        s2 = np.sum(resid**2) / df_e
        cov_hat = s2 * XtX_inv
        se_b0 = np.sqrt(cov_hat[0, 0])
        se_b1 = np.sqrt(cov_hat[1, 1])
        corr_b0_b1 = cov_hat[0, 1] / (se_b0 * se_b1)

        f_val = f_crit_05(df_e)
        t_val = t_crit_05(df_e)

        # Plot setup
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8), dpi=105)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, top=0.88, bottom=0.14, wspace=0.26)

        # ----------------------------------------------------------------------
        # Left Panel: Joint Confidence Ellipse vs Marginal Confidence Intervals
        # ----------------------------------------------------------------------
        ax1.set_facecolor(BG_COLOR)
        for spine in ax1.spines.values():
            spine.set_color(GRID_COLOR)
        ax1.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

        # Generate ellipse points: (beta - b_hat)' (XtX / s2) (beta - b_hat) <= 2 * F_crit
        # Using eigendecomposition of cov_hat = s2 * XtX_inv
        eigvals, eigvecs = np.linalg.eigh(cov_hat)
        # Scaled semi-axes lengths for 95% joint confidence ellipse: sqrt(2 * F * lambda_i)
        scale_95 = np.sqrt(2.0 * f_val)
        semi_a = scale_95 * np.sqrt(eigvals[1])
        semi_b = scale_95 * np.sqrt(eigvals[0])
        angle_deg = np.degrees(np.arctan2(eigvecs[1, 1], eigvecs[0, 1]))

        # Confidence Ellipse 95%
        ellipse_95 = Ellipse(xy=(b0_h, b1_h), width=2 * semi_a, height=2 * semi_b,
                             angle=angle_deg, edgecolor=NAVY_COLOR, facecolor="#1f3b5c",
                             alpha=0.18, lw=2.2, label=r"결합 95% 신뢰타원 ($F$-검정)", zorder=3)
        ax1.add_patch(ellipse_95)

        # 90% Confidence Ellipse (subtle inner)
        f_val_90 = (df_e / 2.0) * (0.10**(-2.0 / df_e) - 1.0)
        semi_a_90 = np.sqrt(2.0 * f_val_90) * np.sqrt(eigvals[1])
        semi_b_90 = np.sqrt(2.0 * f_val_90) * np.sqrt(eigvals[0])
        ellipse_90 = Ellipse(xy=(b0_h, b1_h), width=2 * semi_a_90, height=2 * semi_b_90,
                             angle=angle_deg, edgecolor="#087e8b", facecolor="none",
                             linestyle=":", lw=1.5, label=r"결합 90% 신뢰타원", zorder=3)
        ax1.add_patch(ellipse_90)

        # Marginal 95% Confidence Rectangle (Bonferroni / individual t-tests)
        rect_x0 = b0_h - t_val * se_b0
        rect_x1 = b0_h + t_val * se_b0
        rect_y0 = b1_h - t_val * se_b1
        rect_y1 = b1_h + t_val * se_b1
        ax1.plot([rect_x0, rect_x1, rect_x1, rect_x0, rect_x0],
                 [rect_y0, rect_y0, rect_y1, rect_y1, rect_y0],
                 "--", color=RED_COLOR, lw=1.5, alpha=0.75,
                 label=r"개별 95% 신뢰구간 직사각형 ($t$-검정)", zorder=4)

        # True Parameter Point
        ax1.scatter(beta_0_true, beta_1_true, marker="*", s=160, color=GOLD_COLOR,
                    edgecolor=INK_COLOR, lw=1.2, label=rf"참 모수 $(\beta_0^*, \beta_1^*) = ({beta_0_true:.1f}, {beta_1_true:.1f})$", zorder=6)

        # OLS Point Estimate
        ax1.scatter(b0_h, b1_h, marker="o", s=50, color=NAVY_COLOR,
                    edgecolor="#ffffff", lw=1.0, label=rf"OLS 추정치 $(\hat{{\beta}}_0, \hat{{\beta}}_1)$", zorder=7)

        ax1.set_xlim(0.4, 1.6)
        ax1.set_ylim(0.8, 2.0)
        ax1.set_xlabel(r"절편 모수 $\beta_0$", fontsize=10.5, color=INK_COLOR)
        ax1.set_ylabel(r"기울기 모수 $\beta_1$", fontsize=10.5, color=INK_COLOR)
        ax1.set_title(rf"모수공간 결합 신뢰타원 수축 동학 ($n={n}$)",
                      fontsize=11.5, fontweight="bold", color=INK_COLOR, pad=8)
        ax1.legend(loc="upper right", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.0)

        # Badge left panel
        info_badge_left = (
            rf"공분산: $\mathrm{{Cov}}(\hat{{\beta}}_0, \hat{{\beta}}_1) = {cov_hat[0, 1]:.3f}$" "\n"
            rf"상관계수: $\rho = {corr_b0_b1:.2f}$ (음의 기울기 회전)" "\n"
            rf"$SE(\hat{{\beta}}_0) = {se_b0:.3f}$,  $SE(\hat{{\beta}}_1) = {se_b1:.3f}$"
        )
        ax1.text(0.04, 0.05, info_badge_left, transform=ax1.transAxes,
                 fontsize=8.5, va="bottom", ha="left",
                 bbox=dict(boxstyle="round,pad=0.45", facecolor="#f3ede2", edgecolor="#d5c7b5", alpha=0.95))

        # ----------------------------------------------------------------------
        # Right Panel: Gauss–Markov Theorem & Dispersion Ellipses (BLUE Geometry)
        # ----------------------------------------------------------------------
        ax2.set_facecolor(BG_COLOR)
        for spine in ax2.spines.values():
            spine.set_color(GRID_COLOR)
        ax2.grid(True, linestyle="--", alpha=0.6, color=GRID_COLOR)

        # Baseline theoretical OLS covariance at reference n=50
        ref_n = 50
        ref_X = np.column_stack([np.ones(ref_n), x_pool[:ref_n]])
        Sigma_OLS = (sigma_true**2) * np.linalg.inv(ref_X.T @ ref_X)

        # Inefficiency matrix Delta = D D' >= 0
        Delta = np.array([[0.016, -0.005],
                          [-0.005, 0.024]])

        # Progressively animate alternative estimator variance: Sigma_ALT(gamma)
        # As frames proceed, gamma shifts or shows multiple nested ellipses
        gamma_current = 0.2 + 0.9 * (np.sin(idx / len(n_seq) * np.pi))

        # Function to plot dispersion ellipse for a given covariance matrix
        def plot_dispersion_ellipse(cov, ax, color, label, lw=2.0, ls="-", fill=False, alpha=0.15):
            evals, evecs = np.linalg.eigh(cov)
            # 1-sigma dispersion ellipse contour: (b - b*)' cov^{-1} (b - b*) = 1
            # axes lengths: sqrt(evals)
            w = 2.0 * np.sqrt(evals[1])
            h = 2.0 * np.sqrt(evals[0])
            ang = np.degrees(np.arctan2(evecs[1, 1], evecs[0, 1]))
            el = Ellipse(xy=(beta_0_true, beta_1_true), width=w, height=h,
                         angle=ang, edgecolor=color, facecolor=color if fill else "none",
                         linestyle=ls, lw=lw, alpha=alpha, label=label, zorder=4)
            ax.add_patch(el)

        # 1. Plot reference alternative estimators (static contours)
        plot_dispersion_ellipse(Sigma_OLS + 1.2 * Delta, ax2, "#9e2a2b",
                                r"비효율 선형추정량 $\tilde{\beta}_3$ ($\Sigma + 1.2 \Delta$)", lw=1.4, ls=":", fill=False)
        plot_dispersion_ellipse(Sigma_OLS + 0.6 * Delta, ax2, "#c05621",
                                r"비효율 선형추정량 $\tilde{\beta}_2$ ($\Sigma + 0.6 \Delta$)", lw=1.5, ls="--", fill=False)

        # 2. Plot dynamically highlighted alternative estimator
        Sigma_dyn = Sigma_OLS + gamma_current * Delta
        plot_dispersion_ellipse(Sigma_dyn, ax2, RED_COLOR,
                                rf"임의의 선형불편추정량 $\tilde{{\beta}}$ ($\gamma = {gamma_current:.2f}$)",
                                lw=2.2, ls="-", fill=True, alpha=0.12)

        # 3. Plot OLS dispersion ellipse (Innermost, BLUE)
        plot_dispersion_ellipse(Sigma_OLS, ax2, GREEN_COLOR,
                                r"OLS 최량선형불편추정량 (BLUE: $\Sigma_{\mathrm{OLS}}$)",
                                lw=2.8, ls="-", fill=True, alpha=0.25)

        # Mark true parameter at the center
        ax2.scatter(beta_0_true, beta_1_true, marker="*", s=160, color=GOLD_COLOR,
                    edgecolor=INK_COLOR, lw=1.2, label=r"참 모수 벡터 $\beta^* = (\beta_0^*, \beta_1^*)$", zorder=6)

        # Draw a line along arbitrary linear combination vector c
        theta_c = np.radians(35)
        c_vec = np.array([np.cos(theta_c), np.sin(theta_c)])
        r_line = 0.35
        ax2.plot([beta_0_true - r_line * c_vec[0], beta_0_true + r_line * c_vec[0]],
                 [beta_1_true - r_line * c_vec[1], beta_1_true + r_line * c_vec[1]],
                 "-.", color=MUTED_COLOR, lw=1.5, label=r"임의의 선형결합 방향 $c'\beta$", zorder=5)

        ax2.set_xlim(beta_0_true - 0.40, beta_0_true + 0.40)
        ax2.set_ylim(beta_1_true - 0.38, beta_1_true + 0.38)
        ax2.set_xlabel(r"$\beta_0$ 모수축", fontsize=10.5, color=INK_COLOR)
        ax2.set_ylabel(r"$\beta_1$ 모수축", fontsize=10.5, color=INK_COLOR)
        ax2.set_title(r"Gauss–Markov 정리의 기하학: 최소 분산 타원 (BLUE)",
                      fontsize=11.5, fontweight="bold", color=INK_COLOR, pad=8)
        ax2.legend(loc="upper left", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=7.8)

        # Badge right panel
        var_c_ols = c_vec @ Sigma_OLS @ c_vec
        var_c_alt = c_vec @ Sigma_dyn @ c_vec
        info_badge_right = (
            r"$\mathrm{Var}(\tilde{\beta}|X) = \Sigma_{\mathrm{OLS}} + \sigma^2 DD' \geq \Sigma_{\mathrm{OLS}}$" "\n"
            rf"방향 $c'\beta$ 분산: $\mathrm{{Var}}(c'\hat{{\beta}}) = {var_c_ols:.4f}$ (최소)" "\n"
            rf"대안 추정량 분산: $\mathrm{{Var}}(c'\tilde{{\beta}}) = {var_c_alt:.4f}$" "\n"
            r"$\rightarrow$ OLS 분산 타원이 항상 내부 포함 (BLUE)"
        )
        ax2.text(0.96, 0.05, info_badge_right, transform=ax2.transAxes,
                 fontsize=8.5, va="bottom", ha="right",
                 bbox=dict(boxstyle="round,pad=0.45", facecolor="#e6f4ea", edgecolor="#a8dab5", alpha=0.95))

        # Save frame to PIL
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    # Save animated GIF
    out_path = os.path.join(GIF_DIR, "ols-parameter-confidence-ellipse.gif")
    durations = [280] * len(n_vals) + [650, 650, 650] + [280] * len(n_back)
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
    generate_gif_sample_size()
    generate_gif_parameter_confidence_ellipse()
    print("All OLS geometry GIFs successfully generated!")
