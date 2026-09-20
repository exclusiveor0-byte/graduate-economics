"""Generate publication-grade animated GIFs for the Correspondence Hemicontinuity supplement.

Outputs:
  - assets/gif/correspondence-uhc-vs-lhc.gif
  - assets/gif/correspondence-berge-maximum-theorem.gif
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
TEAL_COLOR = "#087e8b"       # UHC satisfied / Continuous / Safety tube
RED_COLOR = "#c0392b"        # LHC violation / Outer explosion / Breakdown
GOLD_COLOR = "#d97706"       # Target element / Optimal solution
PURPLE_COLOR = "#6b4c7a"     # Probe x / Reference fiber F(x0)
GREEN_COLOR = "#15803d"      # UHC safety inclusion

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# 1. GIF 1: UHC vs LHC Duality (Preset B: Inner Collapse vs Preset C: Outer Explosion)
# ==============================================================================
def generate_gif_uhc_lhc():
    print("Generating GIF 1: correspondence-uhc-vs-lhc.gif ...")

    # Sweep parameter x: from -0.8 to +0.8 through 0.0 with pauses at critical point 0.0
    x_in = np.linspace(-0.8, -0.06, 12)
    x_zero = np.zeros(6)
    x_out = np.linspace(0.06, 0.8, 12)
    x_back = np.linspace(0.8, 0.06, 10)
    x_zero2 = np.zeros(6)
    x_in2 = np.linspace(-0.06, -0.8, 8)
    x_vals = np.concatenate([x_in, x_zero, x_out, x_back, x_zero2, x_in2])

    frames = []

    for idx, x in enumerate(x_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.25)

        is_zero = abs(x) < 1e-4

        # -------------------------------------------------------------
        # Panel 1: Preset B (UHC Satisfied, LHC Violated - Inner Collapse)
        # F(0) = [0, 1], F(x) = {0} for x != 0
        # -------------------------------------------------------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(-1.1, 1.1)
        ax1.set_ylim(-0.35, 1.45)
        ax1.set_xlabel(r"모수 $x$ (Parameter Probe)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"선택지 $y \in F(x)$ (Fiber Space)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.set_title("프리셋 B: 내측 수축 (UHC 만족 / LHC 위반)", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Baseline graph of correspondence F
        # For x != 0: y = 0
        ax1.plot([-1.1, -0.01], [0, 0], color=MUTED_COLOR, linewidth=2.5)
        ax1.plot([0.01, 1.1], [0, 0], color=MUTED_COLOR, linewidth=2.5)
        # At x = 0: fiber [0, 1]
        ax1.plot([0, 0], [0, 1.0], color=PURPLE_COLOR, linewidth=4.0, zorder=5, label=r"기준 파이버 $F(0) = [0, 1]$")
        ax1.plot(0, 0, "o", color=PURPLE_COLOR, markersize=6, zorder=6)
        ax1.plot(0, 1.0, "o", color=PURPLE_COLOR, markersize=6, zorder=6)

        # UHC Neighborhood V around F(0): V = (-0.15, 1.15), U = (-0.6, 0.6)
        # Safe box U x V
        ax1.fill_between([-0.6, 0.6], -0.15, 1.15, color=GREEN_COLOR, alpha=0.12,
                         label=r"UHC 개근방 상자 $U \times V$ ($F(U) \subseteq V$)")
        ax1.plot([-0.6, 0.6, 0.6, -0.6, -0.6], [-0.15, -0.15, 1.15, 1.15, -0.15],
                 color=GREEN_COLOR, linestyle="--", linewidth=1.2)

        # Target test point y0 = 0.8 for LHC testing
        y0_target = 0.8
        ax1.plot(0, y0_target, "*", color=GOLD_COLOR, markersize=12, zorder=7,
                 label=r"LHC 검증 목표 $y_0 = 0.8 \in F(0)$")

        # Current probe x
        if is_zero:
            # At x = 0: fiber is [0, 1]
            ax1.plot([0, 0], [0, 1.0], color=TEAL_COLOR, linewidth=4.5, zorder=8)
            ax1.plot(0, y0_target, "o", color=TEAL_COLOR, markersize=8, zorder=9)
            ax1.annotate("x=0 도달!\n선택지 전체 [0, 1] 회복", xy=(0, y0_target), xytext=(0.15, 0.95),
                         fontweight="bold", color=TEAL_COLOR, fontsize=8.5,
                         arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.2))
        else:
            # At x != 0: fiber is only {0}
            ax1.plot(x, 0, "o", color=PURPLE_COLOR, markersize=8, zorder=8,
                     label=r"현재 파이버 $F(x) = \{0\}$")
            # Distance gap to y0 = 0.8
            ax1.plot([x, 0], [0, y0_target], linestyle=":", color=RED_COLOR, linewidth=1.8)
            ax1.annotate("", xy=(x, y0_target), xytext=(x, 0),
                         arrowprops=dict(arrowstyle="<->", color=RED_COLOR, lw=1.6))
            ax1.text(x + 0.04, 0.4, f"거리 $d={y0_target:.2f}$\n(접근 불가!)",
                     color=RED_COLOR, fontweight="bold", fontsize=8.2)

        # Status text for Panel 1
        uhc_b = "UHC: 만족 (외측 폭발 없음, $F(x) \\subset V$)"
        lhc_b = "LHC: 위반 (내측 소멸! $y_0=0.8$로 접근 불가)"
        ax1.text(-1.0, 1.30, uhc_b, color=GREEN_COLOR, fontsize=8.8, fontweight="bold")
        ax1.text(-1.0, 1.18, lhc_b, color=RED_COLOR, fontsize=8.8, fontweight="bold")
        ax1.legend(loc="lower right", fontsize=7.6, framealpha=0.92)

        # -------------------------------------------------------------
        # Panel 2: Preset C (LHC Satisfied, UHC Violated - Outer Explosion)
        # F(0) = {0}, F(x) = [0, 1] for x != 0
        # -------------------------------------------------------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(-1.1, 1.1)
        ax2.set_ylim(-0.35, 1.45)
        ax2.set_xlabel(r"모수 $x$ (Parameter Probe)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel(r"선택지 $y \in F(x)$ (Fiber Space)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("프리셋 C: 외측 폭발 (LHC 만족 / UHC 위반)", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Baseline graph of Preset C:
        # At x != 0, region is a slab [0, 1]
        ax2.fill_between([-1.1, -0.01], 0, 1.0, color="#dbeafe", alpha=0.35, label=r"대응 영역 $F(x) = [0, 1]$")
        ax2.fill_between([0.01, 1.1], 0, 1.0, color="#dbeafe", alpha=0.35)
        ax2.plot([-1.1, -0.01], [1.0, 1.0], color=TEAL_COLOR, linewidth=1.5, linestyle="--")
        ax2.plot([0.01, 1.1], [1.0, 1.0], color=TEAL_COLOR, linewidth=1.5, linestyle="--")
        ax2.plot([-1.1, -0.01], [0, 0], color=TEAL_COLOR, linewidth=1.5)
        ax2.plot([0.01, 1.1], [0, 0], color=TEAL_COLOR, linewidth=1.5)

        # At x = 0: fiber is single point {0}
        ax2.plot(0, 0, "o", color=PURPLE_COLOR, markersize=8, zorder=6, label=r"기준 파이버 $F(0) = \{0\}$")

        # Open neighborhood V around F(0) = {0}: V = (-0.2, 0.2)
        ax2.fill_between([-0.6, 0.6], -0.2, 0.2, color=RED_COLOR, alpha=0.12,
                         label=r"개근방 $V = (-0.2, 0.2)$ ($F(0) \subset V$)")
        ax2.plot([-0.6, 0.6, 0.6, -0.6, -0.6], [-0.2, -0.2, 0.2, 0.2, -0.2],
                 color=RED_COLOR, linestyle="--", linewidth=1.2)

        # Test point y0 = 0 in F(0)
        ax2.plot(0, 0, "*", color=GOLD_COLOR, markersize=12, zorder=7)

        # Current probe x
        if is_zero:
            ax2.plot(0, 0, "o", color=TEAL_COLOR, markersize=9, zorder=9)
            ax2.annotate("x=0: F(0)={0}\nV 안에 포함", xy=(0, 0), xytext=(0.15, -0.25),
                         fontweight="bold", color=TEAL_COLOR, fontsize=8.5,
                         arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.2))
        else:
            # At x != 0: fiber is [0, 1]
            ax2.plot([x, x], [0, 1.0], color=RED_COLOR, linewidth=3.5, zorder=8,
                     label=r"현재 파이버 $F(x) = [0, 1]$")
            # Highlight outer explosion outside V (from y = 0.2 to 1.0)
            ax2.plot([x, x], [0.2, 1.0], color=RED_COLOR, linewidth=5.0, zorder=9)
            ax2.annotate("외측 폭발!\n$F(x) \\not\\subseteq V$", xy=(x, 0.6),
                         xytext=(x + (0.15 if x > 0 else -0.55), 0.7),
                         fontweight="bold", color=RED_COLOR, fontsize=8.2,
                         arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.2))
            # But LHC: point 0 is in F(x), so distance is 0!
            ax2.plot(x, 0, "o", color=GREEN_COLOR, markersize=7, zorder=10)
            ax2.text(x + 0.04, -0.12, r"$y_k=0 \to 0$ ($\checkmark$)",
                     color=GREEN_COLOR, fontweight="bold", fontsize=8.2)

        # Status text for Panel 2
        uhc_c = "UHC: 위반 (외측 폭발! $F(x)=[0,1] \\not\\subseteq V$)"
        lhc_c = "LHC: 만족 (수열 $y_k=0 \\in F(x_k)$로 $y_0=0$ 접근 가능)"
        ax2.text(-1.0, 1.30, uhc_c, color=RED_COLOR, fontsize=8.8, fontweight="bold")
        ax2.text(-1.0, 1.18, lhc_c, color=GREEN_COLOR, fontsize=8.8, fontweight="bold")
        ax2.legend(loc="upper right", fontsize=7.6, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "correspondence-uhc-vs-lhc.gif")
    frames_to_save = frames + [frames[-1]] * 12
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Berge Maximum Theorem & Breakdown under LHC Violation
# ==============================================================================
def generate_gif_berge_theorem():
    print("Generating GIF 2: correspondence-berge-maximum-theorem.gif ...")

    # Objective function: f(x, y) = y
    # Panel 1: Constraint is Preset B (LHC fails) -> Value function v(x) jumps at x=0
    # Panel 2: Constraint is continuous Preset A: F(x) = [x/3, 1 - x/3] -> v(x) is continuous

    x_in = np.linspace(-0.8, -0.06, 12)
    x_zero = np.zeros(6)
    x_out = np.linspace(0.06, 0.8, 12)
    x_back = np.linspace(0.8, 0.06, 10)
    x_zero2 = np.zeros(6)
    x_in2 = np.linspace(-0.06, -0.8, 8)
    x_vals = np.concatenate([x_in, x_zero, x_out, x_back, x_zero2, x_in2])

    frames = []

    for idx, x in enumerate(x_vals):
        fig, axs = plt.subplots(2, 2, figsize=(11.5, 6.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.08, right=0.96, bottom=0.10, top=0.91, wspace=0.25, hspace=0.36)

        is_zero = abs(x) < 1e-4

        # =============================================================
        # Column 1: LHC Violation -> Value Function Discontinuity
        # (Top: Constraint Fiber F(x), Bottom: Value Function v(x))
        # =============================================================
        ax_c1_top = axs[0, 0]
        ax_c1_bot = axs[1, 0]

        # Top 1: Constraint Correspondence
        ax_c1_top.set_facecolor(BG_COLOR)
        ax_c1_top.set_xlim(-1.0, 1.0)
        ax_c1_top.set_ylim(-0.2, 1.3)
        ax_c1_top.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax_c1_top.set_title(r"LHC 위반 제약: $F(0)=[0,1], F(x)=\{0\}$", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_c1_top.set_ylabel(r"선택지 $y$", fontsize=9.5, color=INK_COLOR)

        # Baseline
        ax_c1_top.plot([-1.0, -0.01], [0, 0], color=MUTED_COLOR, linewidth=2.0)
        ax_c1_top.plot([0.01, 1.0], [0, 0], color=MUTED_COLOR, linewidth=2.0)
        ax_c1_top.plot([0, 0], [0, 1.0], color=PURPLE_COLOR, linewidth=3.5)

        # Current fiber and argmax
        if is_zero:
            ax_c1_top.plot([0, 0], [0, 1.0], color=RED_COLOR, linewidth=4.0)
            ax_c1_top.plot(0, 1.0, "*", color=GOLD_COLOR, markersize=13, zorder=8,
                           label=r"최적해 $y^*(0) = 1$")
        else:
            ax_c1_top.plot(x, 0, "o", color=RED_COLOR, markersize=8, zorder=8,
                           label=r"최적해 $y^*(x) = 0$")

        ax_c1_top.legend(loc="upper right", fontsize=7.8, framealpha=0.92)

        # Bottom 1: Value Function v(x) = max_{y in F(x)} y
        ax_c1_bot.set_facecolor(BG_COLOR)
        ax_c1_bot.set_xlim(-1.0, 1.0)
        ax_c1_bot.set_ylim(-0.2, 1.3)
        ax_c1_bot.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax_c1_bot.set_xlabel(r"모수 $x$", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax_c1_bot.set_ylabel(r"가치함수 $v(x)$", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax_c1_bot.set_title("가치함수 불연속 (Berge 최대정리 붕괴!)", fontsize=10.5, fontweight="bold", color=RED_COLOR)

        # v(x) is 0 for x != 0, and 1 at x = 0
        ax_c1_bot.plot([-1.0, -0.02], [0, 0], color=RED_COLOR, linewidth=2.5)
        ax_c1_bot.plot([0.02, 1.0], [0, 0], color=RED_COLOR, linewidth=2.5)
        ax_c1_bot.plot(0, 0, "o", markeredgecolor=RED_COLOR, markerfacecolor=BG_COLOR, markersize=7, markeredgewidth=1.5)
        ax_c1_bot.plot(0, 1.0, "o", color=RED_COLOR, markersize=8, zorder=6)

        # Current point on v(x)
        curr_v = 1.0 if is_zero else 0.0
        ax_c1_bot.plot(x, curr_v, "*", color=GOLD_COLOR, markersize=13, zorder=7)
        if is_zero:
            ax_c1_bot.annotate(r"$v(0)=1$ 로 상방 점프!" + "\n" + r"$\liminf_{x \to 0} v(x) = 0 < v(0)$",
                               xy=(0, 1.0), xytext=(0.15, 0.75),
                               fontweight="bold", color=RED_COLOR, fontsize=8.2,
                               arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.2))
        else:
            ax_c1_bot.text(x - 0.25, curr_v + 0.15, f"$v({x:.2f})=0$", color=RED_COLOR, fontsize=8.0, fontweight="bold")

        # =============================================================
        # Column 2: Continuous Constraint -> Continuous Value Function
        # (F(x) = [x/3, 1 - x/3], f(x, y) = y -> v(x) = 1 - x/3)
        # =============================================================
        ax_c2_top = axs[0, 1]
        ax_c2_bot = axs[1, 1]

        # Top 2: Continuous Constraint Correspondence
        ax_c2_top.set_facecolor(BG_COLOR)
        ax_c2_top.set_xlim(-1.0, 1.0)
        ax_c2_top.set_ylim(-0.4, 1.4)
        ax_c2_top.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax_c2_top.set_title(r"연속 제약: $F(x) = [x/3, 1 - x/3]$ (UHC + LHC)", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_c2_top.set_ylabel(r"선택지 $y$", fontsize=9.5, color=INK_COLOR)

        x_grid = np.linspace(-1.0, 1.0, 100)
        lower_b = x_grid / 3.0
        upper_b = 1.0 - x_grid / 3.0
        ax_c2_top.fill_between(x_grid, lower_b, upper_b, color="#cffafe", alpha=0.45, label=r"연속 대응 영역 $F(x)$")
        ax_c2_top.plot(x_grid, upper_b, color=TEAL_COLOR, linewidth=1.5, linestyle="--")
        ax_c2_top.plot(x_grid, lower_b, color=TEAL_COLOR, linewidth=1.5, linestyle="--")

        # Current fiber at x
        curr_low = x / 3.0
        curr_high = 1.0 - x / 3.0
        ax_c2_top.plot([x, x], [curr_low, curr_high], color=TEAL_COLOR, linewidth=4.0, zorder=6)
        ax_c2_top.plot(x, curr_high, "*", color=GOLD_COLOR, markersize=13, zorder=8,
                       label=f"최적해 $y^*(x) = {curr_high:.2f}$")

        ax_c2_top.legend(loc="lower left", fontsize=7.8, framealpha=0.92)

        # Bottom 2: Value Function v(x) = 1 - x/3 (Continuous!)
        ax_c2_bot.set_facecolor(BG_COLOR)
        ax_c2_bot.set_xlim(-1.0, 1.0)
        ax_c2_bot.set_ylim(-0.4, 1.4)
        ax_c2_bot.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax_c2_bot.set_xlabel(r"모수 $x$", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax_c2_bot.set_ylabel(r"가치함수 $v(x)$", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax_c2_bot.set_title("가치함수 연속 (Berge 최대정리 성립!)", fontsize=10.5, fontweight="bold", color=TEAL_COLOR)

        # Smooth curve v(x) = 1 - x/3
        ax_c2_bot.plot(x_grid, upper_b, color=TEAL_COLOR, linewidth=2.5, label=r"$v(x) = 1 - x/3$ (연속함수)")
        ax_c2_bot.plot(x, curr_high, "*", color=GOLD_COLOR, markersize=13, zorder=7)
        ax_c2_bot.annotate(f"v({x:.2f})={curr_high:.2f}\n(부드러운 연속 전이)",
                           xy=(x, curr_high), xytext=(x - 0.55 if x > 0.1 else x + 0.15, curr_high - 0.35),
                           fontweight="bold", color=TEAL_COLOR, fontsize=8.0,
                           arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.2))

        ax_c2_bot.legend(loc="upper right", fontsize=7.8, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "correspondence-berge-maximum-theorem.gif")
    frames_to_save = frames + [frames[-1]] * 12
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_uhc_lhc()
    generate_gif_berge_theorem()
    print("All Correspondence GIFs generated successfully!")
