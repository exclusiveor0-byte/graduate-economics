"""Generate publication-grade animated GIFs for the Slutsky and Hicks Decomposition supplement.

Outputs:
  - assets/gif/slutsky-hicks-decomposition.gif
  - assets/gif/slutsky-demand-curves.gif
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
TEAL_COLOR = "#087e8b"      # Hicks substitution / Substitution effect
AMBER_COLOR = "#b46f45"     # Income effect
GOLD_COLOR = "#a16207"      # Indifference curves / Utility
PURPLE_COLOR = "#6b4c7a"    # Slutsky substitution
RED_COLOR = "#c0392b"       # Final price budget line

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ==============================================================================
# Model Baseline Parameters: Two-Good Cobb-Douglas
# u(x1, x2) = x1^0.5 * x2^0.5
# m = 100, p2 = 1.0
# p1_initial = 1.25 -> p1_new = 0.625 (Price drop)
# ==============================================================================
alpha = 0.5
m = 100.0
p2 = 1.0
p1_0 = 1.25
p1_1 = 0.625

# Initial bundle A
x1_0 = alpha * m / p1_0          # 40.0
x2_0 = (1.0 - alpha) * m / p2    # 50.0
u_0 = (x1_0 ** alpha) * (x2_0 ** (1.0 - alpha))  # sqrt(2000) ~ 44.7214

# Final bundle C
x1_1 = alpha * m / p1_1          # 80.0
x2_1 = (1.0 - alpha) * m / p2    # 50.0
u_1 = (x1_1 ** alpha) * (x2_1 ** (1.0 - alpha))  # sqrt(4000) ~ 63.2456

# Hicks compensation: mH = e(p1_1, p2, u_0)
# e(p, u) = (p1/alpha)^alpha * (p2/(1-alpha))^(1-alpha) * u = sqrt(p1_1 * 2 * 2) * u_0 = 2*sqrt(p1_1)*u_0
m_H = 2.0 * np.sqrt(p1_1 * p2) * u_0             # ~ 70.7107
x1_H = alpha * m_H / p1_1                         # ~ 56.5685
x2_H = (1.0 - alpha) * m_H / p2                   # ~ 35.3553

# Slutsky compensation: mS = p1_1 * x1_0 + p2 * x2_0
m_S = p1_1 * x1_0 + p2 * x2_0                     # 25 + 50 = 75.0
x1_S = alpha * m_S / p1_1                         # 60.0
x2_S = (1.0 - alpha) * m_S / p2                   # 37.5
u_S = (x1_S ** alpha) * (x2_S ** (1.0 - alpha))   # sqrt(2250) ~ 47.4342


# ==============================================================================
# 1. GIF 1: Hicks vs. Slutsky Decomposition Side-by-Side Animation
# ==============================================================================
def generate_gif_decomposition():
    print("Generating GIF 1: slutsky-hicks-decomposition.gif ...")
    n_frames = 36
    # 3 animation stages:
    # Phase 1: t in [0, 1]: Price drop and budget line rotation (0 to 11)
    # Phase 2: t in [1, 2]: Compensated budget lines appear and shift (12 to 23)
    # Phase 3: t in [2, 3]: Decomposition vectors and brackets expand (24 to 35)

    x1_grid = np.linspace(10.0, 130.0, 300)
    # Indifference curve equations: x2 = (u / x1^0.5)^2 = u^2 / x1
    curve_u0 = (u_0 ** 2) / x1_grid
    curve_uS = (u_S ** 2) / x1_grid
    curve_u1 = (u_1 ** 2) / x1_grid

    frames = []

    for i in range(n_frames):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.22)

        # Interpolation progress
        progress = i / (n_frames - 1)  # 0 to 1

        # Calculate dynamic elements
        # Budget line 0 (Initial): p1_0 * x1 + x2 = m -> x2 = m - p1_0 * x1
        x1_b0 = np.array([0, m / p1_0])
        x2_b0 = np.array([m, 0])

        # Budget line 1 (Final): p1_1 * x1 + x2 = m
        x1_b1 = np.array([0, m / p1_1])
        x2_b1 = np.array([m, 0])

        for ax, mode in [(ax1, "hicks"), (ax2, "slutsky")]:
            ax.set_facecolor(BG_COLOR)
            ax.set_xlim(0, 140)
            ax.set_ylim(0, 120)
            ax.set_xlabel(r"재화 1 ($x_1$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
            ax.set_ylabel(r"재화 2 ($x_2$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
            ax.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)

            # Always draw initial budget line and initial IC u0
            ax.plot(x1_b0, x2_b0, color=INK_COLOR, linewidth=1.8, label=r"초기 예산선 $L_0$ ($p_1=1.25$)")
            ax.plot(x1_grid, curve_u0, color=GOLD_COLOR, linestyle="--", linewidth=1.6, label=r"초기 무차별곡선 $u^0=44.7$")

            # Initial point A
            ax.plot(x1_0, x2_0, "o", color=INK_COLOR, markersize=7, zorder=6)
            ax.text(x1_0 - 7, x2_0 + 4, "A", fontsize=11, fontweight="bold", color=INK_COLOR)

        # ---------------- Panel 1: Hicks Decomposition ----------------
        ax1.set_title("Hicks 분해 (동일 효용 $u^0$ 기준 보상)", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        if progress > 0.15:
            # Draw final budget line L1 and point C
            p_final_prog = min(1.0, (progress - 0.15) / 0.35)
            curr_p1 = p1_0 + (p1_1 - p1_0) * p_final_prog
            ax1.plot([0, m / curr_p1], [m, 0], color=RED_COLOR, linewidth=1.8, alpha=0.9,
                     label=r"최종 예산선 $L_1$ ($p_1=0.625$)")
            if p_final_prog >= 0.99:
                ax1.plot(x1_grid, curve_u1, color=GOLD_COLOR, linestyle=":", linewidth=1.2, alpha=0.7)
                ax1.plot(x1_1, x2_1, "o", color=RED_COLOR, markersize=7, zorder=6)
                ax1.text(x1_1 + 3, x2_1 + 3, "C", fontsize=11, fontweight="bold", color=RED_COLOR)

        if progress > 0.45:
            # Hicks compensation line: p1_1 * x1 + x2 = m_H
            comp_prog = min(1.0, (progress - 0.45) / 0.35)
            curr_mH = m + (m_H - m) * comp_prog
            ax1.plot([0, curr_mH / p1_1], [curr_mH, 0], color=TEAL_COLOR, linestyle="-.", linewidth=2.0,
                     label=r"Hicks 보상선 $L_H$ ($m^H=70.7$)")

            if comp_prog >= 0.99:
                ax1.plot(x1_H, x2_H, "o", color=TEAL_COLOR, markersize=8, zorder=7)
                ax1.text(x1_H - 4, x2_H - 9, r"$B_H$", fontsize=11, fontweight="bold", color=TEAL_COLOR)

        if progress > 0.80:
            # Decomposition arrows: A -> B_H (Substitution) and B_H -> C (Income)
            ax1.annotate("", xy=(x1_H, x2_H), xytext=(x1_0, x2_0),
                         arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=2.0))
            ax1.annotate("", xy=(x1_1, x2_1), xytext=(x1_H, x2_H),
                         arrowprops=dict(arrowstyle="->", color=AMBER_COLOR, lw=2.0))

            # Bottom projections & brackets
            ax1.plot([x1_0, x1_0], [0, x2_0], ":", color=INK_COLOR, alpha=0.5)
            ax1.plot([x1_H, x1_H], [0, x2_H], ":", color=TEAL_COLOR, alpha=0.5)
            ax1.plot([x1_1, x1_1], [0, x2_1], ":", color=RED_COLOR, alpha=0.5)

            ax1.text((x1_0 + x1_H) / 2, 8, r"대체 (+16.6)", color=TEAL_COLOR, fontsize=8.5, ha="center", fontweight="bold")
            ax1.text((x1_H + x1_1) / 2, 8, r"소득 (+23.4)", color=AMBER_COLOR, fontsize=8.5, ha="center", fontweight="bold")
            ax1.text(x1_0, -6, r"$x_1^0=40$", color=INK_COLOR, fontsize=8, ha="center")
            ax1.text(x1_H, -6, r"$x_1^H=56.6$", color=TEAL_COLOR, fontsize=8, ha="center")
            ax1.text(x1_1, -6, r"$x_1^1=80$", color=RED_COLOR, fontsize=8, ha="center")

        ax1.legend(loc="upper right", fontsize=8.0, framealpha=0.9)

        # ---------------- Panel 2: Slutsky Decomposition ----------------
        ax2.set_title("Slutsky 분해 (초기 묶음 $A$ 구매력 유지 보상)", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        if progress > 0.15:
            # Draw final budget line L1 and point C
            p_final_prog = min(1.0, (progress - 0.15) / 0.35)
            curr_p1 = p1_0 + (p1_1 - p1_0) * p_final_prog
            ax2.plot([0, m / curr_p1], [m, 0], color=RED_COLOR, linewidth=1.8, alpha=0.9,
                     label=r"최종 예산선 $L_1$ ($p_1=0.625$)")
            if p_final_prog >= 0.99:
                ax2.plot(x1_grid, curve_u1, color=GOLD_COLOR, linestyle=":", linewidth=1.2, alpha=0.7)
                ax2.plot(x1_1, x2_1, "o", color=RED_COLOR, markersize=7, zorder=6)
                ax2.text(x1_1 + 3, x2_1 + 3, "C", fontsize=11, fontweight="bold", color=RED_COLOR)

        if progress > 0.45:
            # Slutsky compensation line: passes through A=(40, 50), slope -p1_1
            comp_prog = min(1.0, (progress - 0.45) / 0.35)
            curr_mS = m + (m_S - m) * comp_prog
            ax2.plot([0, curr_mS / p1_1], [curr_mS, 0], color=PURPLE_COLOR, linestyle="-.", linewidth=2.0,
                     label=r"Slutsky 보상선 $L_S$ ($m^S=75.0$)")

            if comp_prog >= 0.99:
                # Higher indifference curve uS
                ax2.plot(x1_grid, curve_uS, color=PURPLE_COLOR, linestyle=":", linewidth=1.4, alpha=0.8,
                         label=r"초과효용 $u^S=47.4 > u^0$")
                ax2.plot(x1_S, x2_S, "o", color=PURPLE_COLOR, markersize=8, zorder=7)
                ax2.text(x1_S - 4, x2_S - 9, r"$B_S$", fontsize=11, fontweight="bold", color=PURPLE_COLOR)

        if progress > 0.80:
            # Decomposition arrows: A -> B_S (Substitution) and B_S -> C (Income)
            ax2.annotate("", xy=(x1_S, x2_S), xytext=(x1_0, x2_0),
                         arrowprops=dict(arrowstyle="->", color=PURPLE_COLOR, lw=2.0))
            ax2.annotate("", xy=(x1_1, x2_1), xytext=(x1_S, x2_S),
                         arrowprops=dict(arrowstyle="->", color=AMBER_COLOR, lw=2.0))

            # Bottom projections & brackets
            ax2.plot([x1_0, x1_0], [0, x2_0], ":", color=INK_COLOR, alpha=0.5)
            ax2.plot([x1_S, x1_S], [0, x2_S], ":", color=PURPLE_COLOR, alpha=0.5)
            ax2.plot([x1_1, x1_1], [0, x2_1], ":", color=RED_COLOR, alpha=0.5)

            ax2.text((x1_0 + x1_S) / 2, 8, r"대체 (+20.0)", color=PURPLE_COLOR, fontsize=8.5, ha="center", fontweight="bold")
            ax2.text((x1_S + x1_1) / 2, 8, r"소득 (+20.0)", color=AMBER_COLOR, fontsize=8.5, ha="center", fontweight="bold")
            ax2.text(x1_0, -6, r"$x_1^0=40$", color=INK_COLOR, fontsize=8, ha="center")
            ax2.text(x1_S, -6, r"$x_1^S=60$", color=PURPLE_COLOR, fontsize=8, ha="center")
            ax2.text(x1_1, -6, r"$x_1^1=80$", color=RED_COLOR, fontsize=8, ha="center")

            # Highlight overcompensation
            ax2.annotate(r"과정보상! $m^S > m^H$" + "\n" + r"($u^S=47.4 > u^0=44.7$)",
                         xy=(x1_S, x2_S), xytext=(x1_S + 8, x2_S + 20),
                         fontweight="bold", color=PURPLE_COLOR, fontsize=8.5,
                         arrowprops=dict(arrowstyle="->", color=PURPLE_COLOR, lw=1.2))

        ax2.legend(loc="upper right", fontsize=8.0, framealpha=0.9)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "slutsky-hicks-decomposition.gif")
    frames_to_save = frames + [frames[-1]] * 8
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=130, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Marshallian vs. Hicksian Compensated Demand Curves
# ==============================================================================
def generate_gif_demand_curves():
    print("Generating GIF 2: slutsky-demand-curves.gif ...")
    n_frames = 36
    # Sweep p1 from 1.8 down to 0.6
    p1_vals = np.linspace(1.8, 0.6, n_frames)

    x1_grid = np.linspace(10.0, 130.0, 300)
    curve_u0 = (u_0 ** 2) / x1_grid

    # Dense price grid for demand curve background
    p1_dense = np.linspace(0.55, 1.9, 200)
    d1_marshall_dense = alpha * m / p1_dense
    h1_hicks_dense = np.sqrt(p2 / p1_dense) * u_0

    frames = []

    for idx, p1_curr in enumerate(p1_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.22)

        # Calculations at p1_curr
        # Marshallian choice C:
        x1_m_curr = alpha * m / p1_curr
        x2_m_curr = (1.0 - alpha) * m / p2
        u_m_curr = (x1_m_curr ** alpha) * (x2_m_curr ** (1.0 - alpha))

        # Hicksian choice B_H on u_0:
        m_H_curr = 2.0 * np.sqrt(p1_curr * p2) * u_0
        x1_h_curr = alpha * m_H_curr / p1_curr
        x2_h_curr = (1.0 - alpha) * m_H_curr / p2

        # ---------------- Panel 1: (x1, x2) Indifference Space ----------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(0, 130)
        ax1.set_ylim(0, 110)
        ax1.set_xlabel(r"재화 1 ($x_1$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"재화 2 ($x_2$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.set_title("무차별곡선 공간에서의 선택점 이동", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Baseline u0 curve and initial point A
        ax1.plot(x1_grid, curve_u0, color=GOLD_COLOR, linestyle="--", linewidth=1.6, label=r"기준 무차별곡선 $u^0=44.7$")
        ax1.plot(x1_0, x2_0, "o", color=INK_COLOR, markersize=6, zorder=5)
        ax1.text(x1_0 - 6, x2_0 + 4, "A", fontsize=10, fontweight="bold", color=INK_COLOR)

        # Actual Budget line at p1_curr
        ax1.plot([0, m / p1_curr], [m, 0], color=RED_COLOR, linewidth=1.8, label=f"실제 예산선 ($p_1={p1_curr:.2f}$)")

        # Hicks compensated budget line at p1_curr
        ax1.plot([0, m_H_curr / p1_curr], [m_H_curr, 0], color=TEAL_COLOR, linestyle="-.", linewidth=1.6,
                 label=r"Hicks 보상선 (접선)")

        # Current Indifference curve for Marshallian bundle if different
        if abs(p1_curr - p1_0) > 0.05:
            curve_u_curr = (u_m_curr ** 2) / x1_grid
            ax1.plot(x1_grid, curve_u_curr, color=RED_COLOR, linestyle=":", linewidth=1.2, alpha=0.6)

        # Plot moving points
        ax1.plot(x1_m_curr, x2_m_curr, "o", color=RED_COLOR, markersize=8, zorder=7)
        ax1.text(x1_m_curr + 2, x2_m_curr + 4, f"C ($x_1$={x1_m_curr:.1f})", color=RED_COLOR, fontsize=9, fontweight="bold")

        ax1.plot(x1_h_curr, x2_h_curr, "o", color=TEAL_COLOR, markersize=8, zorder=7)
        ax1.text(x1_h_curr + 2, x2_h_curr - 9, f"$B_H$ ($x_1$={x1_h_curr:.1f})", color=TEAL_COLOR, fontsize=9, fontweight="bold")

        # Horizontal PCC guide
        ax1.axhline(50.0, color=MUTED_COLOR, linestyle=":", linewidth=1.0, alpha=0.5)

        ax1.legend(loc="upper right", fontsize=8.0, framealpha=0.9)

        # ---------------- Panel 2: (p1, x1) Demand Space ----------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(20, 110)
        ax2.set_ylim(0.5, 1.9)
        ax2.set_xlabel(r"수요량 $x_1$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel(r"가격 $p_1$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("마샬 수요곡선 vs 힉스 보상수요곡선", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Full static demand curves
        ax2.plot(d1_marshall_dense, p1_dense, color=RED_COLOR, linewidth=2.0, label=r"Marshall 수요 $d_1(p_1)$ (완만함)")
        ax2.plot(h1_hicks_dense, p1_dense, color=TEAL_COLOR, linewidth=2.2, linestyle="--", label=r"Hicks 수요 $h_1(p_1, u^0)$ (가파름)")

        # Initial point marker
        ax2.plot(x1_0, p1_0, "o", color=INK_COLOR, markersize=7, zorder=6)
        ax2.annotate(r"초기점 ($p_1^0=1.25, x_1^0=40$)", xy=(x1_0, p1_0),
                     xytext=(x1_0 + 6, p1_0 + 0.12),
                     fontweight="bold", color=INK_COLOR, fontsize=8.5,
                     arrowprops=dict(arrowstyle="->", color=INK_COLOR, lw=1.2))

        # Current price horizontal reference line
        ax2.axhline(p1_curr, color=MUTED_COLOR, linestyle=":", linewidth=1.2, alpha=0.7)

        # Current points on demand curves
        ax2.plot(x1_m_curr, p1_curr, "o", color=RED_COLOR, markersize=8, zorder=8)
        ax2.plot(x1_h_curr, p1_curr, "o", color=TEAL_COLOR, markersize=8, zorder=8)

        # Bracket showing difference between Marshall and Hicks demand at current price
        if abs(x1_m_curr - x1_h_curr) > 3.0:
            color_diff = AMBER_COLOR
            ax2.annotate("", xy=(x1_m_curr, p1_curr), xytext=(x1_h_curr, p1_curr),
                         arrowprops=dict(arrowstyle="<->", color=color_diff, lw=1.8))
            mid_x = (x1_m_curr + x1_h_curr) / 2
            sign_str = "소득효과 > 0 (정상재)"
            ax2.text(mid_x, p1_curr - 0.08 if p1_curr > 0.8 else p1_curr + 0.05,
                     sign_str, color=color_diff, fontsize=8.5, ha="center", fontweight="bold")

        ax2.legend(loc="upper right", fontsize=8.0, framealpha=0.9)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "slutsky-demand-curves.gif")
    frames_to_save = frames + [frames[-1]] * 8
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=130, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_decomposition()
    generate_gif_demand_curves()
    print("All Slutsky GIFs generated successfully!")
