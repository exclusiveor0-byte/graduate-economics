"""Generate publication-grade animated GIFs for the Core Competitive Convergence supplement.

Outputs:
  - assets/gif/core-shrinkage-edgeworth.gif
  - assets/gif/coalition-blocking-geometry.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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
NAVY_COLOR = "#1f3b5c"       # Contract curve / Walrasian price line
RED_COLOR = "#b83b26"        # Core segment / Blocked regions
CORAL_COLOR = "#d9534f"      # Core highlight
TEAL_COLOR = "#087e8b"       # Walrasian competitive equilibrium point / Invariance
PLUM_COLOR = "#6b4c7a"       # Coalition bundle / Alternative allocation
PURPLE_COLOR = "#6b4c7a"     # Consumer B indifference curve
GOLD_COLOR = "#d97706"       # Consumer A indifference curve / Endowment
GREEN_COLOR = "#15803d"      # Utility surplus / Improving vector

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# Model specifications:
# Total endowment: x_bar = 10, y_bar = 10
# u_A = x_A^0.6 * y_A^0.4
# u_B = x_B^0.4 * y_B^0.6
# e_A = (2, 8), e_B = (8, 2)
# Contract curve: y_A = 8*x_A / (18 - x_A)
# Walrasian equilibrium: p* = 1, x_A* = (6, 4), x_B* = (4, 6)

def uA(xA, yA):
    if xA <= 0 or yA <= 0: return 0.0
    return (xA**0.6) * (yA**0.4)

def uB(xB, yB):
    if xB <= 0 or yB <= 0: return 0.0
    return (xB**0.4) * (yB**0.6)

def contract_yA(xA):
    return 8.0 * xA / (18.0 - xA)

def compute_core_bounds(r):
    """Compute [xA_min, xA_max] for r-replica economy."""
    eA = np.array([2.0, 8.0])
    eB = np.array([8.0, 2.0])

    if r == 1:
        # Lower bound: uA(xA, yA) = uA(eA) = 2^1.8 ~ 3.4822
        # Upper bound: uB(10-xA, 10-yA) = uB(eB) = 2^1.8 ~ 3.4822
        xA_low, xA_high = 4.3162, 7.4766
        return xA_low, xA_high

    # Upper bound: B forms coalition of r of B and kA < r of A
    grid_high = np.linspace(6.0001, 7.4766, 1000)
    xA_high = 7.4766
    for xA in grid_high:
        yA = contract_yA(xA)
        x_alloc = np.array([xA, yA])
        xB_alloc = np.array([10.0 - xA, 10.0 - yA])
        uB_curr = uB(xB_alloc[0], xB_alloc[1])
        blocked = False
        for kA in range(1, r):
            lam = kA / r
            bundleB = eB + lam * (eA - x_alloc)
            if uB(bundleB[0], bundleB[1]) > uB_curr + 1e-6:
                blocked = True
                break
        if blocked:
            xA_high = xA
            break

    # Lower bound: A forms coalition of r of A and kB < r of B
    grid_low = np.linspace(5.9999, 4.3162, 1000)
    xA_low = 4.3162
    for xA in grid_low:
        yA = contract_yA(xA)
        x_alloc = np.array([xA, yA])
        uA_curr = uA(xA, yA)
        blocked = False
        for kB in range(1, r):
            lam = kB / r
            bundleA = eA + lam * (x_alloc - eA)
            if uA(bundleA[0], bundleA[1]) > uA_curr + 1e-6:
                blocked = True
                break
        if blocked:
            xA_low = xA
            break

    return xA_low, xA_high


# ==============================================================================
# 1. GIF 1: Core Shrinkage in Edgeworth Box (r = 1 -> inf)
# ==============================================================================
def generate_gif_core_shrinkage():
    print("Generating GIF 1: core-shrinkage-edgeworth.gif ...")

    r_fwd = [1, 2, 3, 4, 5, 7, 10, 15, 25, 50, 100]
    r_hold_high = [100, 100, 100, 100]
    r_bwd = [50, 25, 12, 6, 3, 2, 1]
    r_hold_low = [1, 1, 1]

    r_sequence = r_fwd + r_hold_high + r_bwd + r_hold_low

    # Precompute bounds
    bounds_dict = {}
    for r in set(r_sequence):
        bounds_dict[r] = compute_core_bounds(r)

    # Base Edgeworth elements
    xA_curve = np.linspace(0.01, 9.99, 300)
    yA_curve = contract_yA(xA_curve)

    # Indifference curve of A through omega=(2,8): uA=3.4822 => yA = (3.4822 / xA^0.6)^(1/0.4)
    xA_ind_A = np.linspace(1.2, 9.8, 200)
    yA_ind_A = (3.4822 / (xA_ind_A**0.6))**(1.0/0.4)

    # Indifference curve of B through omega=(2,8): xB=8, yB=2, uB=3.4822 => yB = (3.4822 / xB^0.4)^(1/0.6)
    xB_ind_B = np.linspace(1.2, 9.8, 200)
    yB_ind_B = (3.4822 / (xB_ind_B**0.4))**(1.0/0.6)
    # in A coords: xA = 10 - xB, yA = 10 - yB
    xA_ind_B = 10.0 - xB_ind_B
    yA_ind_B = 10.0 - yB_ind_B

    frames = []

    for idx, r in enumerate(r_sequence):
        xA_low, xA_high = bounds_dict[r]
        width_xA = xA_high - xA_low
        shrink_pct = (1.0 - (width_xA / 3.1604)) * 100.0

        fig, (ax_box, ax_info) = plt.subplots(1, 2, figsize=(14.4, 7.4), dpi=100,
                                              gridspec_kw={'width_ratios': [1.2, 1.0]})
        fig.patch.set_facecolor(BG_COLOR)
        ax_box.set_facecolor(BG_COLOR)
        ax_info.set_facecolor(BG_COLOR)

        # -------------------------------------------------------------
        # Left Panel: Edgeworth Box
        # -------------------------------------------------------------
        ax_box.set_xlim(-0.5, 10.5)
        ax_box.set_ylim(-0.5, 10.5)
        ax_box.set_xlabel(r"소비자 A의 $x$재 소비량 ($x_A$)", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_box.set_ylabel(r"소비자 A의 $y$재 소비량 ($y_A$)", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_box.set_title(f"■ [에지워스 상자] $r$-복제경제 코어 축소 (복제 수 $r = {r}$)",
                         fontsize=12, fontweight="bold", color=INK_COLOR, pad=12)

        # Draw Edgeworth boundary
        box_rect = patches.Rectangle((0, 0), 10, 10, fill=False, edgecolor=INK_COLOR, lw=1.8)
        ax_box.add_patch(box_rect)

        # Grid lines
        ax_box.grid(True, linestyle=":", alpha=0.4, color=GRID_COLOR)

        # Origin labels
        ax_box.text(-0.35, -0.35, r"$O_A(0,0)$", fontsize=10, fontweight="bold", color=INK_COLOR)
        ax_box.text(10.1, 10.15, r"$O_B(10,10)$", fontsize=10, fontweight="bold", color=INK_COLOR)

        # Top & Right axis labels for Consumer B
        ax_box.text(5.0, 10.25, r"$\leftarrow$ 소비자 B의 $x$재 소비량 ($x_B = 10 - x_A$)",
                    fontsize=9.5, color=MUTED_COLOR, ha="center")
        ax_box.text(10.35, 5.0, r"$\downarrow$ 소비자 B의 $y$재 소비량 ($y_B = 10 - y_A$)",
                    fontsize=9.5, color=MUTED_COLOR, va="center", rotation=-90)

        # Indifference curves through endowment
        valid_A = (yA_ind_A >= 0) & (yA_ind_A <= 10)
        ax_box.plot(xA_ind_A[valid_A], yA_ind_A[valid_A], color=GOLD_COLOR, lw=1.6, linestyle="--",
                    label=r"A의 초기 무차별곡선 $u_A(\omega)$")

        valid_B = (yA_ind_B >= 0) & (yA_ind_B <= 10)
        ax_box.plot(xA_ind_B[valid_B], yA_ind_B[valid_B], color=PURPLE_COLOR, lw=1.6, linestyle="--",
                    label=r"B의 초기 무차별곡선 $u_B(\omega)$")

        # Lens of mutual gains shading (r=1 core baseline)
        x_lens = np.linspace(4.3162, 7.4766, 100)
        y_lens_lower = contract_yA(x_lens)
        # Shading between ind curves
        # Use polygon for lens
        # For simplicity, shade along contract curve
        ax_box.plot(xA_curve, yA_curve, color=MUTED_COLOR, lw=1.4, linestyle=":",
                    label="계약곡선 (파레토 최적 궤적)")

        # Walrasian budget line: y = 10 - x (passes through omega=(2,8) and E*=(6,4))
        ax_box.plot([0, 10], [10, 0], color=TEAL_COLOR, lw=1.5, linestyle="-.", alpha=0.75,
                    label=r"경쟁균형 예산선 ($p^* = 1.0$)")

        # Initial endowment omega=(2,8)
        ax_box.scatter([2.0], [8.0], color=GOLD_COLOR, s=90, zorder=6, edgecolor=INK_COLOR, lw=1.2)
        ax_box.text(2.15, 8.25, r"초기부존 $\omega(2, 8)$", fontsize=9.5, fontweight="bold", color=INK_COLOR)

        # Blocked contract segments (outside current core)
        # Left blocked segment: [4.3162, xA_low]
        if xA_low > 4.3162:
            x_bl_left = np.linspace(4.3162, xA_low, 50)
            ax_box.plot(x_bl_left, contract_yA(x_bl_left), color=RED_COLOR, lw=2.2, linestyle=":", alpha=0.55)
        # Right blocked segment: [xA_high, 7.4766]
        if xA_high < 7.4766:
            x_bl_right = np.linspace(xA_high, 7.4766, 50)
            ax_box.plot(x_bl_right, contract_yA(x_bl_right), color=RED_COLOR, lw=2.2, linestyle=":", alpha=0.55)

        # Active Core Segment on contract curve
        x_core = np.linspace(xA_low, xA_high, 80)
        y_core = contract_yA(x_core)
        ax_box.plot(x_core, y_core, color=RED_COLOR, lw=4.5, zorder=7,
                    label=f"코어 $C^{{{r}}}(\\mathcal{{E}})$ (생존 배분)")

        # Core boundary dots
        ax_box.scatter([xA_low, xA_high], [contract_yA(xA_low), contract_yA(xA_high)],
                       color=RED_COLOR, s=65, zorder=8, edgecolor=INK_COLOR, lw=1.0)

        # Walrasian Competitive Equilibrium Point E*(6, 4)
        ax_box.scatter([6.0], [4.0], color=TEAL_COLOR, s=130, zorder=9, marker="*",
                       edgecolor=INK_COLOR, lw=1.2, label=r"왈라스 경쟁균형 $E^*(6, 4)$")
        ax_box.text(6.25, 3.65, r"$E^*(6, 4)$", fontsize=10, fontweight="bold", color=TEAL_COLOR)

        ax_box.legend(loc="upper left", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.0)

        # -------------------------------------------------------------
        # Right Panel: Convergence Dashboard
        # -------------------------------------------------------------
        ax_info.axis("off")

        title_r = f"r = {r}" if r < 100 else "r → ∞ (Debreu–Scarf 극한)"
        ax_info.text(0.04, 0.96, f"■ 복제경제 코어 수렴 진단 대시보드 ({title_r})",
                     fontsize=12, fontweight="bold", color=INK_COLOR)
        ax_info.axhline(0.925, xmin=0.04, xmax=0.96, color=MUTED_COLOR, lw=0.8, alpha=0.5)

        # 1. Population & Replication metrics
        pop_str = f"{2*r}명 (소비자 A {r}명 + B {r}명)" if r < 100 else "무한 집단 (Continuous Mass)"
        ax_info.text(0.06, 0.86, "1. 경제 규모 및 참가자 수", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_info.text(0.08, 0.80, f"• 복제 차수 (Replication Factor):   r = {r}", fontsize=9.5, color=INK_COLOR)
        ax_info.text(0.08, 0.74, f"• 경제 전체 인구 규모 (Population):     {pop_str}", fontsize=9.5, color=INK_COLOR)

        # 2. Core Interval & Width
        ax_info.text(0.06, 0.65, "2. 에지워스 상자 코어 배분 구간", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_info.text(0.08, 0.59, f"• x_A 생존 좌표 구간:   [{xA_low:.4f}, {xA_high:.4f}]",
                     fontsize=9.5, fontweight="bold", color=RED_COLOR)
        ax_info.text(0.08, 0.53, f"• 코어 구간 폭 (Δx_A):      {width_xA:.4f}  (초기 폭: 3.1604)",
                     fontsize=9.5, color=INK_COLOR)
        ax_info.text(0.08, 0.47, f"• 코어 수축률 (Shrinkage):  {shrink_pct:.1f}% 수렴 달성",
                     fontsize=9.5, fontweight="bold", color=TEAL_COLOR if shrink_pct > 80 else INK_COLOR)

        # Progress bar
        bar_bg = patches.Rectangle((0.08, 0.41), 0.82, 0.032, facecolor="#e2e8f0", edgecolor=MUTED_COLOR, lw=0.6)
        bar_fg = patches.Rectangle((0.08, 0.41), 0.82 * (shrink_pct / 100.0), 0.032,
                                   facecolor=TEAL_COLOR, edgecolor="none")
        ax_info.add_patch(bar_bg)
        ax_info.add_patch(bar_fg)
        ax_info.text(0.92, 0.426, f"{shrink_pct:.0f}%", fontsize=8.5, fontweight="bold",
                     color=TEAL_COLOR, va="center")

        # 3. Core Theoretical Takeaway
        ax_info.text(0.06, 0.33, "3. Debreu–Scarf 정리의 계량경제·미시적 결론", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        takeaway = (
            "• [가격 없는 자발적 연합]: 경매인이나 가격 기구가 전혀 없어도\n"
            "  자신들의 부존만으로 개선을 도모하는 연합(Coalition)의 블로킹을\n"
            "  통해 불공정한 배분들이 양 끝단에서 차례로 배제된다.\n"
            "• [보이지 않는 손의 극한적 정당화]: 경제가 복제되어 커질수록(r → ∞)\n"
            "  생존 배분 집합(Core)은 오직 '경쟁균형점 E*(6, 4)' 하나로 수렴한다.\n"
            "  즉, 완전경쟁시장의 가격 기구는 무수히 많은 참여자의 자발적\n"
            "  재협상과 연합 탈퇴가 낳은 필연적 균형점이다."
        )
        ax_info.text(0.06, 0.05, takeaway, fontsize=8.8, color=INK_COLOR, va="bottom",
                     bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5efe6", edgecolor="#dfd4c5", alpha=0.95))

        fig.suptitle("코어(Core)와 경쟁균형 수렴: 에지워스 상자에서 Debreu–Scarf 복제경제 동학",
                     fontsize=13.0, color=INK_COLOR, fontweight="bold", y=0.965)
        plt.subplots_adjust(left=0.06, right=0.96, top=0.88, bottom=0.09, wspace=0.22)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "core-shrinkage-edgeworth.gif")
    durations = [320] * len(r_fwd) + [850] * len(r_hold_high) + [320] * len(r_bwd) + [850] * len(r_hold_low)
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
# 2. GIF 2: Coalition Blocking Geometry (r=2 Unbalanced Coalition Mechanics)
# ==============================================================================
def generate_gif_coalition_blocking():
    print("Generating GIF 2: coalition-blocking-geometry.gif ...")

    # In r=2, consumers are {A1, A2, B1, B2}.
    # Endowment: eA = (2, 8), eB = (8, 2).
    # Consider a candidate allocation on contract curve: xA from 7.4 down to 6.1
    # At xA=7.4, B gets xB=(2.6, 4.38).
    # A coalition of 2 of B and 1 of A forms (ratio lam = 1/2).
    # Coalition endowment: 2*eB + 1*eA = (18, 12).
    # It gives A1 the candidate bundle xA = (xA, yA).
    # Remaining bundle for the 2 of B: (18 - xA, 12 - yA).
    # Per B consumer bundle: yB_coalition = (9 - 0.5*xA, 6 - 0.5*yA).
    # Compare uB(yB_coalition) with uB(10 - xA, 10 - yA).

    xA_vals_fwd = [7.40, 7.20, 7.00, 6.85, 6.76, 6.65, 6.50, 6.35, 6.20, 6.08, 6.00]
    xA_hold_low = [6.00, 6.00, 6.00]
    xA_vals_bwd = [6.15, 6.40, 6.70, 7.05, 7.40]
    xA_hold_high = [7.40, 7.40]

    xA_sequence = xA_vals_fwd + xA_hold_low + xA_vals_bwd + xA_hold_high

    frames = []

    for idx, xA in enumerate(xA_sequence):
        yA = contract_yA(xA)
        xB = 10.0 - xA
        yB = 10.0 - yA

        # Coalition of (kB=2, kA=1):
        # Per B consumer:
        coal_xB = 9.0 - 0.5 * xA
        coal_yB = 6.0 - 0.5 * yA

        uB_status_quo = uB(xB, yB)
        uB_coalition = uB(coal_xB, coal_yB)
        delta_uB = uB_coalition - uB_status_quo
        is_blocked = delta_uB > 1e-4

        fig, (ax_geo, ax_info) = plt.subplots(1, 2, figsize=(14.4, 7.4), dpi=100,
                                              gridspec_kw={'width_ratios': [1.2, 1.0]})
        fig.patch.set_facecolor(BG_COLOR)
        ax_geo.set_facecolor(BG_COLOR)
        ax_info.set_facecolor(BG_COLOR)

        # -------------------------------------------------------------
        # Left Panel: Consumer B's Consumption Space & Blocking Vector
        # -------------------------------------------------------------
        ax_geo.set_xlim(1.5, 7.5)
        ax_geo.set_ylim(2.5, 7.5)
        ax_geo.set_xlabel(r"소비자 B의 $x$재 소비량 ($x_B$)", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_geo.set_ylabel(r"소비자 B의 $y$재 소비량 ($y_B$)", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_geo.set_title(f"■ [B의 배분 평면] 불균등 연합(2 B + 1 A)의 블로킹 잉여 ($x_A = {xA:.2f}$)",
                         fontsize=12, fontweight="bold", color=INK_COLOR, pad=12)
        ax_geo.grid(True, linestyle=":", alpha=0.4, color=GRID_COLOR)

        # Indifference curves of B
        # 1. Status quo IC: uB = uB_status_quo => yB = (uB_status_quo / xB^0.4)^(1/0.6)
        xB_grid = np.linspace(1.8, 7.2, 150)
        yB_sq_curve = (uB_status_quo / (xB_grid**0.4))**(1.0/0.6)
        ax_geo.plot(xB_grid, yB_sq_curve, color=PURPLE_COLOR, lw=2.0, linestyle="--",
                    label=rf"현 배분 무차별곡선 ($u_B = {uB_status_quo:.3f}$)")

        # 2. Coalition IC: uB = uB_coalition
        yB_coal_curve = (uB_coalition / (xB_grid**0.4))**(1.0/0.6)
        ax_geo.plot(xB_grid, yB_coal_curve, color=GREEN_COLOR, lw=2.2, linestyle="-",
                    label=rf"연합 달성 무차별곡선 ($u_B = {uB_coalition:.3f}$)")

        # Status quo point
        ax_geo.scatter([xB], [yB], color=RED_COLOR, s=110, zorder=7, edgecolor=INK_COLOR, lw=1.2)
        ax_geo.annotate(f"현 배분 점 $x_B({xB:.2f}, {yB:.2f})$\n[에지워스 계약곡선 상]",
                        xy=(xB, yB), xytext=(xB - 0.7, yB + 0.5),
                        fontsize=9.0, fontweight="bold", color=RED_COLOR,
                        arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.3),
                        bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=RED_COLOR, alpha=0.9))

        # Coalition point
        ax_geo.scatter([coal_xB], [coal_yB], color=GREEN_COLOR, s=120, zorder=8, edgecolor=INK_COLOR, lw=1.2)
        ax_geo.annotate(f"연합 1인당 배분 $y_B({coal_xB:.2f}, {coal_yB:.2f})$\n[소비자 B의 효용 개선]",
                        xy=(coal_xB, coal_yB), xytext=(coal_xB + 0.3, coal_yB - 0.7),
                        fontsize=9.0, fontweight="bold", color=GREEN_COLOR,
                        arrowprops=dict(arrowstyle="->", color=GREEN_COLOR, lw=1.5),
                        bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=GREEN_COLOR, alpha=0.9))

        # Improvement arrow from status quo to coalition
        ax_geo.annotate("", xy=(coal_xB, coal_yB), xytext=(xB, yB),
                        arrowprops=dict(arrowstyle="->", color=GREEN_COLOR, lw=2.8, mutation_scale=18))

        # Walrasian competitive allocation for B: (4.0, 6.0)
        ax_geo.scatter([4.0], [6.0], color=TEAL_COLOR, s=130, zorder=9, marker="*",
                       edgecolor=INK_COLOR, lw=1.2, label=r"경쟁균형 배분 $x_B^*(4, 6)$")

        ax_geo.legend(loc="lower left", framealpha=0.92, facecolor=BG_COLOR, edgecolor=GRID_COLOR, fontsize=8.2)

        # -------------------------------------------------------------
        # Right Panel: Coalition Blocking Diagnostics & Surplus
        # -------------------------------------------------------------
        ax_info.axis("off")

        status_text = "■ 차단 성공 (Blocked by Coalition S)" if is_blocked else "■ 차단 불가 / 균형 안착 (Unblocked)"
        status_color = RED_COLOR if is_blocked else TEAL_COLOR
        ax_info.text(0.04, 0.96, f"{status_text}", fontsize=12, fontweight="bold", color=status_color)
        ax_info.axhline(0.925, xmin=0.04, xmax=0.96, color=MUTED_COLOR, lw=0.8, alpha=0.5)

        ax_info.text(0.06, 0.85, "1. 후보 배분 및 불균등 연합(Coalition) 구성", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_info.text(0.08, 0.79, f"• 검증 대상 계약곡선 배분:   x_A = ({xA:.2f}, {yA:.2f}),  x_B = ({xB:.2f}, {yB:.2f})", fontsize=9.2, color=INK_COLOR)
        ax_info.text(0.08, 0.73, f"• 차단 연합 S 구성원:        소비자 B 2명 + 소비자 A 1명 (총 3명)", fontsize=9.2, color=INK_COLOR)
        ax_info.text(0.08, 0.67, f"• 연합 총부존 e(S):           2·(8, 2) + 1·(2, 8) = (18, 12)", fontsize=9.2, color=INK_COLOR)

        ax_info.text(0.06, 0.57, "2. 자발적 재배분과 효용 잉여(Surplus)", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        ax_info.text(0.08, 0.51, f"• A 1명에게 보장하는 소비:  x_A = ({xA:.2f}, {yA:.2f})  [기존 효용 보존]", fontsize=9.2, color=INK_COLOR)
        ax_info.text(0.08, 0.45, f"• B 2명에게 남은 1인당 배분: y_B = ({coal_xB:.2f}, {coal_yB:.2f})", fontsize=9.2, fontweight="bold", color=GREEN_COLOR)
        ax_info.text(0.08, 0.39, f"• B의 기존 효용 u_B(x_B):       {uB_status_quo:.4f}", fontsize=9.2, color=PURPLE_COLOR)
        ax_info.text(0.08, 0.33, f"• B의 연합 효용 u_B(y_B):       {uB_coalition:.4f}  [효용 변화 Δu: {delta_uB:+.4f}]",
                     fontsize=9.2, fontweight="bold", color=GREEN_COLOR if is_blocked else MUTED_COLOR)

        # 3. Core Theoretical Conclusion
        ax_info.text(0.06, 0.23, "3. 불균등 연합이 창출하는 기하학적 함의", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        takeaway2 = (
            "• [2인 경제에서 차단 못 한 이유]: r=1에서는 1:1 교환뿐이므로\n"
            "  상대방에게 기존 효용을 주고 남는 잉여를 나눌 '동료'가 없었다.\n"
            "• [복제경제 불균등 연합의 힘]: B 2명이 A 1명을 '영입'하면\n"
            "  A의 1인당 과도한 지대를 희석시키고 B 구성원들이 잉여를 나누어 가질 수\n"
            "  있으므로, 경쟁균형보다 B에게 불리한 배분(xA > 6.76)은 모조리 차단된다.\n"
            "• [분리초평면 수렴]: r → ∞가 되면 연합 비율 kA/kB가 연속체로 확장되어\n"
            "  경쟁가격선 p*와 어긋나는 모든 비경쟁 배분의 차단이 완결된다."
        )
        ax_info.text(0.06, 0.04, takeaway2, fontsize=8.6, color=INK_COLOR, va="bottom",
                     bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5efe6", edgecolor="#dfd4c5", alpha=0.95))

        fig.suptitle("불균등 연합(Coalition)의 블로킹 기하학과 한계가격선 수렴",
                     fontsize=13.0, color=INK_COLOR, fontweight="bold", y=0.965)
        plt.subplots_adjust(left=0.06, right=0.96, top=0.88, bottom=0.09, wspace=0.22)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        img = Image.fromarray(rgba).convert("RGB")
        frames.append(img)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "coalition-blocking-geometry.gif")
    durations = [340] * len(xA_vals_fwd) + [850] * len(xA_hold_low) + [340] * len(xA_vals_bwd) + [850] * len(xA_hold_high)
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
    generate_gif_core_shrinkage()
    generate_gif_coalition_blocking()
    print("All Core convergence GIFs successfully generated!")
