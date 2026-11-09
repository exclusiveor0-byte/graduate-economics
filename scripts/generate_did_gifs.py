"""Generate publication-grade animated GIFs for the Difference-in-Differences (DiD) supplement.

Outputs:
  - assets/gif/did-counterfactual-mechanism.gif
  - assets/gif/did-event-study-dynamics.gif
  - assets/gif/did-parallel-trends-violation.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
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
TEAL_COLOR = "#087e8b"       # Treated observed / ATT
AMBER_COLOR = "#b46f45"      # Policy shock / Intervention
RED_COLOR = "#c0392b"        # Violation / Bias / Rejection
GREEN_COLOR = "#15803d"      # Valid / Confidence bands
CARD_BG = "#f5f0e6"

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# 1. GIF 1: 2x2 DiD Mechanism & Counterfactual Construction
# ==============================================================================
def generate_gif_did_mechanism():
    print("Generating GIF 1: did-counterfactual-mechanism.gif ...")

    # Baseline coordinates
    # Control: Pre = 2.0, Post = 3.2 (Delta = +1.2)
    # Treated: Pre = 3.5, Post = 6.7 (Delta = +3.2)
    # Counterfactual = 3.5 + 1.2 = 4.7, ATT = 6.7 - 4.7 = 2.0
    y00 = 2.0
    y01 = 3.2
    y10 = 3.5
    y11 = 6.7
    y11_cf = y10 + (y01 - y00)  # 4.7
    att = y11 - y11_cf          # 2.0

    frames = []
    total_frames = 36

    for step in range(total_frames):
        fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)

        ax.set_xlim(-0.4, 1.4)
        ax.set_ylim(1.0, 7.8)
        ax.set_xticks([0.0, 1.0])
        ax.set_xticklabels(["사전 시점 (Post = 0)", "사후 시점 (Post = 1)"], fontsize=12, fontweight="bold", color=INK_COLOR)
        ax.set_ylabel("결과변수 $Y$", fontsize=12, fontweight="bold", color=INK_COLOR)
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color(INK_COLOR)

        # Title
        fig.suptitle("이중차분법(DiD)의 2×2 기하학과 반사실적(Counterfactual) 분해", fontsize=14, fontweight="bold", color=INK_COLOR, y=0.96)

        # Phase control
        # 0..10: Control trend appears
        # 11..20: Treated pre point appears, counterfactual projection formed
        # 21..30: Treated post observed appears, ATT vertical bracket highlighted
        # 31..35: Hold final state

        # 1. Control Group Line & Points
        p_ctrl = min(1.0, max(0.0, step / 10.0))
        cur_ctrl_y1 = y00 + p_ctrl * (y01 - y00)
        ax.plot([0.0, p_ctrl], [y00, cur_ctrl_y1], color=MUTED_COLOR, lw=3, label="통제집단 실제 궤적")
        ax.scatter([0.0], [y00], color=MUTED_COLOR, s=80, zorder=5)
        ax.text(-0.03, y00, "$E[Y_{00}]=2.0$", ha="right", va="center", color=MUTED_COLOR, fontweight="bold", fontsize=11)

        if p_ctrl > 0.8:
            ax.scatter([1.0], [y01], color=MUTED_COLOR, s=80, zorder=5)
            ax.text(1.03, y01, "$E[Y_{01}]=3.2$", ha="left", va="center", color=MUTED_COLOR, fontweight="bold", fontsize=11)
            ax.text(0.5, (y00 + y01) / 2 - 0.35, "자연적 시간 추세 ($\\Delta Y_0 = +1.2$)", ha="center", va="top", color=MUTED_COLOR, fontsize=10, style="italic")

        # 2. Treated Pre Point & Counterfactual Projection
        if step >= 10:
            p_cf = min(1.0, max(0.0, (step - 10) / 10.0))
            ax.scatter([0.0], [y10], color=TEAL_COLOR, s=90, zorder=5)
            ax.text(-0.03, y10, "$E[Y_{10}]=3.5$", ha="right", va="center", color=TEAL_COLOR, fontweight="bold", fontsize=11)

            cur_cf_y1 = y10 + p_cf * (y11_cf - y10)
            ax.plot([0.0, p_cf], [y10, cur_cf_y1], color=TEAL_COLOR, lw=2.5, ls="--", label="반사실적 가상 궤적 (평행추세)")

            if p_cf > 0.8:
                ax.scatter([1.0], [y11_cf], facecolor="white", edgecolor=TEAL_COLOR, lw=2.5, s=90, zorder=5)
                ax.text(1.03, y11_cf - 0.2, "$E[Y_{11}(0)] = 4.7$ (미처치 시)", ha="left", va="top", color=TEAL_COLOR, fontsize=10)

        # 3. Treated Post Observed & ATT
        if step >= 20:
            p_trt = min(1.0, max(0.0, (step - 20) / 10.0))
            cur_trt_y1 = y10 + p_trt * (y11 - y10)
            ax.plot([0.0, p_trt], [y10, cur_trt_y1], color=TEAL_COLOR, lw=3.5, label="처치집단 실제 궤적")
            if p_trt > 0.8:
                ax.scatter([1.0], [y11], color=TEAL_COLOR, s=100, zorder=5)
                ax.text(1.03, y11 + 0.15, "$E[Y_{11}]=6.7$ (실제 관측치)", ha="left", va="bottom", color=TEAL_COLOR, fontweight="bold", fontsize=11)

                # Vertical ATT Bracket
                ax.annotate(
                    "", xy=(1.0, y11), xytext=(1.0, y11_cf),
                    arrowprops=dict(arrowstyle="<->", color=RED_COLOR, lw=2.5, shrinkA=3, shrinkB=3)
                )
                badge_text = f"인과적 처치효과 (ATT)\nτ = 6.7 - 4.7 = +{att:.1f}"
                ax.text(0.88, (y11 + y11_cf) / 2, badge_text, ha="right", va="center",
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fcedec", edgecolor=RED_COLOR, lw=1.5),
                        color=RED_COLOR, fontweight="bold", fontsize=10)

        # Status annotation box
        if step < 11:
            msg = "1단계: 통제집단의 전후 자연적 변화량(\\Delta Y_0 = +1.2) 측정"
        elif step < 21:
            msg = "2단계: 평행추세 가정 하에 처치집단의 가상적 반사실적(Counterfactual) 점 도출"
        else:
            msg = "3단계: 실제 관측치와 반사실적 점의 격차로 순수 처치효과(ATT = +2.0) 식별"

        ax.text(0.02, 0.94, msg, transform=ax.transAxes, fontsize=11, fontweight="bold", color=INK_COLOR,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=CARD_BG, edgecolor=GRID_COLOR, lw=1))

        ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.86), frameon=True, facecolor="white", edgecolor=GRID_COLOR, fontsize=9)

        plt.subplots_adjust(left=0.10, right=0.92, top=0.90, bottom=0.12)
        fig.canvas.draw()
        img = Image.frombytes("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB")
        frames.append(img)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "did-counterfactual-mechanism.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=160, loop=0)
    print(f"[OK] Saved: {out_path}")


# ==============================================================================
# 2. GIF 2: Dynamic Event-Study Plot & Pre-trend Testing
# ==============================================================================
def generate_gif_event_study():
    print("Generating GIF 2: did-event-study-dynamics.gif ...")

    # Relative event times k in [-5, 4]
    k_vals = np.array([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4])
    # True dynamic coefficients
    gamma_true = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.5, 2.0, 2.3, 2.5])
    # Baseline sample estimates (matching Julia baseline output)
    gamma_est = np.array([0.08, -0.05, 0.04, -0.06, 0.0, 1.02, 1.48, 1.97, 2.32, 2.49])
    se_est = np.array([0.082, 0.078, 0.075, 0.072, 0.0, 0.073, 0.076, 0.079, 0.082, 0.085])

    frames = []
    total_frames = 28

    for step in range(total_frames):
        fig, ax = plt.subplots(figsize=(8.8, 5.0), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        ax.set_facecolor(BG_COLOR)

        ax.set_xlim(-5.8, 4.8)
        ax.set_ylim(-0.6, 3.2)
        ax.set_xticks(k_vals)
        ax.set_xticklabels([f"k={k}" if k != -1 else "k=-1\n(기준기)" for k in k_vals], fontsize=10, fontweight="bold", color=INK_COLOR)
        ax.set_ylabel("추정 처치 계수 $\\hat{\\gamma}_k$", fontsize=12, fontweight="bold", color=INK_COLOR)
        ax.set_xlabel("정책 개입 기준 상대 시점 $k = t - t^*$", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color(INK_COLOR)

        # Title
        fig.suptitle("다기간 동태적 이벤트 스터디(Event Study)와 사전 평행추세 검정", fontsize=14, fontweight="bold", color=INK_COLOR, y=0.96)

        # Shaded Pre / Post Regions
        ax.axvspan(-5.8, -0.5, color="#e8f4f8", alpha=0.5, label="사전 검정 구간 (Pre-trend: leads)")
        ax.axvspan(-0.5, 4.8, color="#fef6e9", alpha=0.5, label="사후 처치 구간 (Post-treatment: lags)")

        # Zero reference line
        ax.axhline(0.0, color=INK_COLOR, lw=1.5, ls="-", alpha=0.8)
        # Policy onset line
        ax.axvline(-0.5, color=AMBER_COLOR, lw=2, ls="--")
        ax.text(-0.4, 2.9, "정책 도입 ($t^*$)", color=AMBER_COLOR, fontweight="bold", fontsize=10)

        # Scanning reveal of coefficients
        n_reveal = min(len(k_vals), int(step * len(k_vals) / 18) + 1)

        # Plot revealed points & CIs
        for i in range(n_reveal):
            k = k_vals[i]
            coef = gamma_est[i]
            se = se_est[i]
            ci_l = coef - 1.96 * se
            ci_u = coef + 1.96 * se

            color = TEAL_COLOR if k >= 0 else (MUTED_COLOR if k == -1 else GREEN_COLOR)
            size = 60 if k != -1 else 40

            if k != -1:
                ax.plot([k, k], [ci_l, ci_u], color=color, lw=2.2, zorder=4)
                ax.plot([k - 0.12, k + 0.12], [ci_l, ci_l], color=color, lw=1.5, zorder=4)
                ax.plot([k - 0.12, k + 0.12], [ci_u, ci_u], color=color, lw=1.5, zorder=4)
            ax.scatter([k], [coef], color=color, s=size, zorder=5)

        # Connecting line for revealed points
        if n_reveal > 1:
            ax.plot(k_vals[:n_reveal], gamma_est[:n_reveal], color=TEAL_COLOR, lw=1.8, ls=":", alpha=0.7)

        # Current scanning line
        if n_reveal <= len(k_vals):
            scan_k = k_vals[min(n_reveal - 1, len(k_vals) - 1)]
            ax.axvline(scan_k, color=TEAL_COLOR, lw=1, ls=":", alpha=0.6)

        # Informative diagnosis box
        if n_reveal <= 5:
            diag_text = "사전 추세 검정: $k < -1$ 계수들이 0 주위에 밀집 (p = 0.28 > 0.05) → 평행추세 성립!"
            box_col = "#e8f4f8"
            border_col = TEAL_COLOR
        else:
            diag_text = f"사후 동학 추적: 정책 도입 후 처치효과가 누적 발현됨 (ATT_k: +{gamma_est[n_reveal-1]:.2f})"
            box_col = "#fcedec"
            border_col = RED_COLOR

        ax.text(0.03, 0.92, diag_text, transform=ax.transAxes, fontsize=10.5, fontweight="bold", color=INK_COLOR,
                bbox=dict(boxstyle="round,pad=0.4", facecolor=box_col, edgecolor=border_col, lw=1.5))

        ax.legend(loc="lower right", frameon=True, facecolor="white", edgecolor=GRID_COLOR, fontsize=9)

        plt.subplots_adjust(left=0.10, right=0.92, top=0.90, bottom=0.14)
        fig.canvas.draw()
        img = Image.frombytes("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB")
        frames.append(img)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "did-event-study-dynamics.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=180, loop=0)
    print(f"[OK] Saved: {out_path}")


# ==============================================================================
# 3. GIF 3: Parallel Trends Violation & Induced Estimator Bias
# ==============================================================================
def generate_gif_violation_bias():
    print("Generating GIF 3: did-parallel-trends-violation.gif ...")

    # Sweep delta from 0.0 up to 0.60 and back to 0.0
    delta_forward = np.linspace(0.0, 0.60, 20)
    delta_hold = np.array([0.60] * 6)
    delta_backward = np.linspace(0.60, 0.0, 14)
    delta_vals = np.concatenate([delta_forward, delta_hold, delta_backward])

    k_vals = np.array([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4])
    base_gamma = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.5, 2.0, 2.3, 2.5])
    se_fixed = 0.08

    frames = []

    for delta in delta_vals:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.8), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        for ax in (ax1, ax2):
            ax.set_facecolor(BG_COLOR)
            ax.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)
            for spine in ["top", "right"]:
                ax.spines[spine].set_visible(False)
            for spine in ["left", "bottom"]:
                ax.spines[spine].set_color(INK_COLOR)

        fig.suptitle(f"평행추세 위반 (차별적 추세 δ = {delta:.2f}) 시 발생하는 계량적 편향과 오경보",
                     fontsize=13, fontweight="bold", color=INK_COLOR, y=0.98)

        # -------------------------------------------------------------
        # Left Panel: Observed Trends & Counterfactual Divergence
        # -------------------------------------------------------------
        t_axis = np.linspace(1, 10, 50)
        t_star = 6.0
        # Control group trend
        y_ctrl = 1.5 + 0.35 * t_axis
        # Treated counterfactual (if parallel)
        y_treat_cf = 3.0 + 0.35 * t_axis
        # Treated latent differential trend
        y_treat_latent = 3.0 + (0.35 + delta) * t_axis
        # Observed treated: pre has latent trend, post has treatment effect (mean ~ 1.86) + latent trend
        post_mask = t_axis >= t_star
        y_treat_obs = y_treat_latent.copy()
        y_treat_obs[post_mask] += 1.86

        ax1.plot(t_axis, y_ctrl, color=MUTED_COLOR, lw=2.5, label="통제집단 관측치")
        ax1.plot(t_axis, y_treat_cf, color=TEAL_COLOR, lw=2, ls="--", label="참된 반사실적 (평행추세)")
        ax1.plot(t_axis, y_treat_obs, color=RED_COLOR if delta > 0.2 else TEAL_COLOR, lw=3, label="처치집단 실제 관측선")
        ax1.axvline(t_star, color=AMBER_COLOR, lw=1.5, ls=":")

        ax1.set_title("패널 시간 궤적과 반사실적 분기", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax1.set_xlabel("시점 $t$ (정책 개입: $t^*=6$)", fontsize=10, color=INK_COLOR)
        ax1.set_ylabel("결과변수 $Y$", fontsize=10, color=INK_COLOR)
        ax1.set_xlim(1.0, 10.0)
        ax1.set_ylim(1.5, 12.0)
        ax1.legend(loc="upper left", fontsize=8, facecolor="white", edgecolor=GRID_COLOR)

        # Bias calculation
        att_true = 1.86
        att_biased = att_true + delta * (t_star - 1.0)
        bias_str = f"편향(Bias): +{delta * (t_star - 1.0):.2f}\n추정 τ̂: {att_biased:.2f} (참값: {att_true:.2f})"
        ax1.text(0.95, 0.15, bias_str, transform=ax1.transAxes, ha="right", va="bottom",
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#fcedec" if delta > 0.1 else "#e8f4f8",
                           edgecolor=RED_COLOR if delta > 0.1 else TEAL_COLOR, lw=1.2),
                 fontsize=9, fontweight="bold", color=RED_COLOR if delta > 0.1 else TEAL_COLOR)

        # -------------------------------------------------------------
        # Right Panel: Event Study Plot with Diverging Pre-trend
        # -------------------------------------------------------------
        # In TWFE, differential linear trend delta manifests as delta * (k - ref_k)
        # ref_k = -1
        trend_shift = delta * (k_vals - (-1))
        gamma_distorted = base_gamma + trend_shift

        # Chi-sq test statistic on pre-treatment leads (k = -5, -4, -3, -2)
        pre_leads = gamma_distorted[:4]
        chi2_stat = np.sum((pre_leads / se_fixed)**2)
        p_val = 1.0 - (1.0 if chi2_stat > 30 else 0.5) # approximate
        is_rejected = chi2_stat > 9.49 # chi2 critical at df=4, 5%

        ax2.axhspan(-0.16, 0.16, color="#e5ded3", alpha=0.4, label="귀무가설 수용대 (±1.96 SE)")
        ax2.axhline(0.0, color=INK_COLOR, lw=1.2)
        ax2.axvline(-0.5, color=AMBER_COLOR, lw=1.5, ls=":")

        pt_color = RED_COLOR if is_rejected else TEAL_COLOR
        for i, k in enumerate(k_vals):
            val = gamma_distorted[i]
            if k != -1:
                ax2.plot([k, k], [val - 1.96 * se_fixed, val + 1.96 * se_fixed], color=pt_color, lw=2)
            ax2.scatter([k], [val], color=pt_color, s=50, zorder=5)

        ax2.plot(k_vals, gamma_distorted, color=pt_color, lw=1.5, ls=":", alpha=0.7)

        ax2.set_title("이벤트 스터디 추정치 왜곡", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax2.set_xlabel("상대 시점 $k = t - t^*$", fontsize=10, color=INK_COLOR)
        ax2.set_ylabel("추정치 $\\hat{\\gamma}_k$", fontsize=10, color=INK_COLOR)
        ax2.set_xlim(-5.5, 4.5)
        ax2.set_ylim(-3.5, 6.5)

        status_tag = "❌ 평행추세 기각! (오경보 경고)" if is_rejected else "✓ 평행추세 유효 (추론 신뢰)"
        tag_bg = "#fcedec" if is_rejected else "#e8f4f8"
        tag_col = RED_COLOR if is_rejected else GREEN_COLOR

        ax2.text(0.05, 0.90, f"사전 검정: {status_tag}\nχ² = {chi2_stat:.1f} (임계치 9.49)",
                 transform=ax2.transAxes, fontsize=9.5, fontweight="bold", color=tag_col,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor=tag_bg, edgecolor=tag_col, lw=1.2))

        ax2.legend(loc="lower right", fontsize=8, facecolor="white", edgecolor=GRID_COLOR)

        plt.subplots_adjust(left=0.08, right=0.94, top=0.88, bottom=0.14, wspace=0.28)
        fig.canvas.draw()
        img = Image.frombytes("RGBA", fig.canvas.get_width_height(), fig.canvas.buffer_rgba()).convert("RGB")
        frames.append(img)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "did-parallel-trends-violation.gif")
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=170, loop=0)
    print(f"[OK] Saved: {out_path}")


if __name__ == "__main__":
    generate_gif_did_mechanism()
    generate_gif_event_study()
    generate_gif_violation_bias()
    print("\nAll 3 DiD publication-grade GIFs generated successfully!")
