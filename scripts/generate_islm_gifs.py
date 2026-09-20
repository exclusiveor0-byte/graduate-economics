"""Generate publication-grade animated GIFs for the IS-LM Fiscal Shock supplement.

Outputs:
  - assets/gif/islm-fiscal-expansion.gif
  - assets/gif/islm-policy-regimes.gif
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
TEAL_COLOR = "#087e8b"       # Output / Final equilibrium / Accommodative policy
RED_COLOR = "#c0392b"        # IS curve / Crowding out / Shock
GOLD_COLOR = "#d97706"       # Equilibrium marker / Highlights
PLUM_COLOR = "#6b4c7a"       # LM curve
GREEN_COLOR = "#15803d"      # Government spending expansion

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ==============================================================================
# Model Baseline Parameters: Linear IS-LM
# r_IS(Y; G) = (A + G - Y) / b
# r_LM(Y; m) = (k*Y - m) / h
# ==============================================================================
A = 130.0
b = 9.0
k = 0.5
h = 8.0
m_base = 42.0

# Multipliers
denom = h + b * k  # 8 + 4.5 = 12.5
mult_fiscal = h / denom        # 8 / 12.5 = 0.64
mult_interest = k / denom      # 0.5 / 12.5 = 0.04
mult_money = b / denom         # 9 / 12.5 = 0.72

def solve_equilibrium(G, m=m_base):
    Y = (h * (A + G) + b * m) / denom
    r = (k * Y - m) / h
    return Y, r

Y0, r0 = solve_equilibrium(0.0)  # 113.44, 1.84
Y_grid = np.linspace(75.0, 155.0, 300)


# ==============================================================================
# 1. GIF 1: Fiscal Expansion & Crowding-Out Decomposition
# ==============================================================================
def generate_gif_fiscal_expansion():
    print("Generating GIF 1: islm-fiscal-expansion.gif ...")

    # Sweep G: 0 -> 24 (forward) and hold
    g_forward = np.linspace(0.0, 24.0, 24)
    g_hold = np.array([24.0] * 12)
    g_vals = np.concatenate([g_forward, g_hold])

    # Precalculate baseline paths
    y_path = [solve_equilibrium(g)[0] for g in g_forward]
    r_path = [solve_equilibrium(g)[1] for g in g_forward]

    frames = []

    for idx, G in enumerate(g_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.25)

        Y_curr, r_curr = solve_equilibrium(G)
        dG = G
        dY = Y_curr - Y0
        dr = r_curr - r0
        dI = -b * dr
        Y_keynes = Y0 + dG  # Output if interest rate were fixed at r0

        # ---------------- Panel 1: IS-LM Plane ----------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(80.0, 152.0)
        ax1.set_ylim(0.2, 4.4)
        ax1.set_xlabel(r"산출량 $Y$ (Output)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"이자율 $r$ (Interest Rate, %)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.set_title("재정확대와 IS–LM 단기 균형 이동", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # LM Curve: r = (0.5*Y - 42) / 8
        r_LM = (k * Y_grid - m_base) / h
        ax1.plot(Y_grid, r_LM, color=PLUM_COLOR, linewidth=2.8, label=r"LM 곡선 ($M/P=42$)")

        # Initial IS Curve (G = 0)
        r_IS_0 = (A + 0.0 - Y_grid) / b
        ax1.plot(Y_grid, r_IS_0, color=MUTED_COLOR, linewidth=1.6, linestyle="--", label=r"초기 IS ($G=0$)")

        # Current IS Curve
        r_IS_curr = (A + G - Y_grid) / b
        ax1.plot(Y_grid, r_IS_curr, color=RED_COLOR, linewidth=2.6, label=f"현재 IS ($G={G:.1f}$)")

        # Initial Equilibrium E0
        ax1.plot(Y0, r0, "o", color=INK_COLOR, markersize=7, zorder=6)
        ax1.text(Y0 - 9.5, r0 - 0.28, r"$E_0(113.4, 1.84)$", color=INK_COLOR, fontsize=9.0, fontweight="bold")

        # Historical equilibrium path
        curr_step = min(idx + 1, len(y_path))
        ax1.plot(y_path[:curr_step], r_path[:curr_step], color=PLUM_COLOR, linewidth=2.0, linestyle=":", zorder=5)

        # Current Equilibrium E*
        ax1.plot(Y_curr, r_curr, "*", color=GOLD_COLOR, markersize=14, zorder=8,
                 label=f"현재 균형 $E^*({Y_curr:.1f}, {r_curr:.2f})$")

        # Keynesian Multiplier Shift at r0 (Horizontal dashed line & point)
        if dG > 1.0:
            # Horizontal line from E0 to Y_keynes at r0
            ax1.plot([Y0, Y_keynes], [r0, r0], color=GREEN_COLOR, linestyle=":", linewidth=1.5)
            ax1.plot(Y_keynes, r0, "s", color=GREEN_COLOR, markersize=6, zorder=6)
            ax1.text(Y_keynes - 2.0, r0 - 0.32, r"$E_{Keynes}$", color=GREEN_COLOR, fontsize=8.5, fontweight="bold")

            # Crowding out horizontal bracket/arrow from Y_keynes back to Y_curr
            ax1.annotate("", xy=(Y_curr, r0), xytext=(Y_keynes, r0),
                         arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.6))
            ax1.text((Y_curr + Y_keynes)/2 - 4.5, r0 + 0.12, f"구축효과\n${dI:.2f}$",
                     color=RED_COLOR, fontsize=8.0, fontweight="bold")

        # Final label when near full shock
        if G >= 23.5:
            ax1.text(Y_curr + 2.5, r_curr + 0.12, r"$E_1(128.8, 2.80)$",
                     color=RED_COLOR, fontsize=9.0, fontweight="bold")

        ax1.legend(loc="upper left", fontsize=8.0, framealpha=0.92)

        # ---------------- Panel 2: Multiplier & Crowding-Out Decomposition ----------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(-0.5, 2.5)
        ax2.set_ylim(-12.0, 28.0)
        ax2.set_xticks([0, 1, 2])
        ax2.set_xticklabels(["정부지출 확대\n($\\Delta G$)", "투자 구축손실\n($\\Delta I = -b\\Delta r$)", "순 산출 증가\n($\\Delta Y^*$)"],
                            fontsize=9.5, fontweight="bold", color=INK_COLOR)
        ax2.set_ylabel("변동액 (Units)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("총수요 구성요소 변동과 재정승수 분해", fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax2.axhline(0, color=INK_COLOR, linewidth=1.0)

        # Bars
        bars = ax2.bar([0, 1, 2], [dG, dI, dY], color=[GREEN_COLOR, RED_COLOR, TEAL_COLOR], width=0.55, alpha=0.85)

        # Annotations on bars
        ax2.text(0, max(dG + 1.0, 1.5), f"+{dG:.1f}", ha="center", va="bottom",
                 color=GREEN_COLOR, fontweight="bold", fontsize=9.5)
        ax2.text(1, min(dI - 1.5, -2.0) if abs(dI) > 0.3 else -2.0, f"{dI:.2f}", ha="center", va="top",
                 color=RED_COLOR, fontweight="bold", fontsize=9.5)
        ax2.text(2, max(dY + 1.0, 1.5), f"+{dY:.2f}", ha="center", va="bottom",
                 color=TEAL_COLOR, fontweight="bold", fontsize=9.5)

        # Summary Metrics Box
        status_box = (
            f"재정충격 $\\Delta G$: +{dG:.1f}\n"
            f"이자율 상승 $\\Delta r^*$: +{dr:.2f}%p\n"
            f"투자 구축손실 $\\Delta I$: {dI:.2f}\n"
            f"실제 산출 증가 $\\Delta Y^*$: +{dY:.2f}\n"
            f"실효 재정승수: {mult_fiscal:.2f}\n"
            f"구축률: {abs(dI)/dG * 100:.1f}%" if dG > 0 else "초기 기준 상태 (G=0)"
        )
        ax2.text(0.05, 0.95, status_box, transform=ax2.transAxes,
                 verticalalignment="top", fontsize=8.8, fontweight="bold",
                 color=INK_COLOR, bbox=dict(boxstyle="round,pad=0.5", facecolor="#fffbeb", edgecolor="#fde68a", alpha=0.95))

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "islm-fiscal-expansion.gif")
    frames_to_save = frames + [frames[-1]] * 12
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Policy Mix & Extreme Regimes (Liquidity Trap vs Classical Case)
# ==============================================================================
def generate_gif_policy_regimes():
    print("Generating GIF 2: islm-policy-regimes.gif ...")

    # Sweep G: 0 -> 24
    g_forward = np.linspace(0.0, 24.0, 24)
    g_hold = np.array([24.0] * 12)
    g_vals = np.concatenate([g_forward, g_hold])

    frames = []

    for idx, G in enumerate(g_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.25)

        # Baseline Pure Fiscal
        Y_pure, r_pure = solve_equilibrium(G)

        # Accommodative monetary policy: Central bank expands M to peg r at r0
        # r = (k*Y_keynes - m_accomm) / h = r0 => m_accomm = k*Y_keynes - h*r0
        Y_accomm = Y0 + G
        r_accomm = r0
        m_accomm = k * Y_accomm - h * r0

        # ---------------- Panel 1: Pure Fiscal vs Accommodative Policy ----------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(80.0, 152.0)
        ax1.set_ylim(0.2, 4.4)
        ax1.set_xlabel(r"산출량 $Y$ (Output)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"이자율 $r$ (Interest Rate, %)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.set_title("순수 재정확대 vs 통화정책 공조 (이자율 안정화)", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Original LM
        r_LM_base = (k * Y_grid - m_base) / h
        ax1.plot(Y_grid, r_LM_base, color=PLUM_COLOR, linewidth=2.2, label=r"기존 LM ($M/P=42$)")

        # Accommodated LM (shifts right as G increases)
        r_LM_acc = (k * Y_grid - m_accomm) / h
        ax1.plot(Y_grid, r_LM_acc, color=TEAL_COLOR, linewidth=2.2, linestyle="--",
                 label=f"공조 LM ($M/P={m_accomm:.1f}$)")

        # Current IS
        r_IS = (A + G - Y_grid) / b
        ax1.plot(Y_grid, r_IS, color=RED_COLOR, linewidth=2.5, label=f"확대 IS ($G={G:.1f}$)")

        # Equilibria points
        ax1.plot(Y0, r0, "o", color=INK_COLOR, markersize=7, zorder=6)
        ax1.plot(Y_pure, r_pure, "o", color=RED_COLOR, markersize=8, zorder=7,
                 label=f"순수 재정균형 ($Y^*={Y_pure:.1f}, r^*={r_pure:.2f}$)")
        ax1.plot(Y_accomm, r_accomm, "*", color=TEAL_COLOR, markersize=13, zorder=8,
                 label=f"통화공조 균형 ($Y^*={Y_accomm:.1f}, r^*={r_accomm:.2f}$)")

        # Arrow indicating output bonus from monetary accommodation
        if G > 2.0:
            ax1.annotate("", xy=(Y_accomm, r0), xytext=(Y_pure, r0),
                         arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.8))
            ax1.text((Y_pure + Y_accomm)/2 - 3.5, r0 - 0.35, "공조 보너스\n(구축 제거)",
                     color=TEAL_COLOR, fontsize=8.0, fontweight="bold")

        ax1.legend(loc="upper left", fontsize=7.6, framealpha=0.92)

        # ---------------- Panel 2: Extreme Regimes (Liquidity Trap vs Classical Case) ----------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(80.0, 152.0)
        ax2.set_ylim(0.2, 4.4)
        ax2.set_xlabel(r"산출량 $Y$ (Output)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel(r"이자율 $r$ (Interest Rate, %)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("극단적 레짐: 유동성 함정 ($h \\to \\infty$) vs 고전학파 ($h=0$)",
                      fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Horizontal LM (Liquidity Trap, r = 1.0)
        r_trap = 1.0
        ax2.axhline(r_trap, color=TEAL_COLOR, linewidth=2.6, label="유동성 함정 ($h \\to \\infty$, 수평 LM)")

        # Vertical LM (Classical Case, Y = 100.0)
        Y_class = 100.0
        ax2.axvline(Y_class, color=PLUM_COLOR, linewidth=2.6, linestyle="-.", label="고전학파 극단 ($h=0$, 수직 LM)")

        # Current IS
        ax2.plot(Y_grid, r_IS, color=RED_COLOR, linewidth=2.2, label=f"확대 IS ($G={G:.1f}$)")

        # Liquidity Trap equilibrium: IS intersects r_trap => Y = A + G - b*r_trap
        Y_trap_equil = A + G - b * r_trap
        ax2.plot(Y_trap_equil, r_trap, "*", color=TEAL_COLOR, markersize=12, zorder=7)

        # Classical equilibrium: IS intersects Y_class => r = (A + G - Y_class) / b
        r_class_equil = (A + G - Y_class) / b
        ax2.plot(Y_class, r_class_equil, "s", color=PLUM_COLOR, markersize=8, zorder=7)

        # Explanatory annotations
        ax2.annotate(f"유동성 함정: 구축효과 0%\n$\\Delta Y = \\Delta G = +{G:.1f}$ (완전 승수)",
                     xy=(Y_trap_equil, r_trap), xytext=(Y_trap_equil - 22.0 if Y_trap_equil > 130 else Y_trap_equil + 3.0, r_trap + 0.45),
                     fontweight="bold", color=TEAL_COLOR, fontsize=8.2,
                     arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.2))

        ax2.annotate(f"고전학파: 완전 구축 100%\n$\\Delta Y = 0$, 이자율만 급등",
                     xy=(Y_class, r_class_equil), xytext=(Y_class + 4.0, r_class_equil - 0.35),
                     fontweight="bold", color=PLUM_COLOR, fontsize=8.2,
                     arrowprops=dict(arrowstyle="->", color=PLUM_COLOR, lw=1.2))

        ax2.legend(loc="upper left", fontsize=7.6, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "islm-policy-regimes.gif")
    frames_to_save = frames + [frames[-1]] * 12
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_fiscal_expansion()
    generate_gif_policy_regimes()
    print("All IS-LM GIFs generated successfully!")
