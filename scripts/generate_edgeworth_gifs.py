"""Generate publication-grade animated GIFs for the Edgeworth Box and Welfare Theorems supplement.

Outputs:
  - assets/gif/edgeworth-competitive-equilibrium.gif
  - assets/gif/edgeworth-second-welfare-theorem.gif
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
TEAL_COLOR = "#087e8b"      # Contract curve / Pareto efficiency
AMBER_COLOR = "#c0392b"     # Consumer B / Indifference curve B (clear contrast)
GOLD_COLOR = "#d97706"      # Consumer A / Indifference curve A
PURPLE_COLOR = "#6b4c7a"    # Equilibrium / Supporting price
RED_COLOR = "#dc2626"       # Budget lines / Disequilibrium

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ==============================================================================
# Model Baseline Parameters: 2-Consumer, 2-Good Pure Exchange Economy
# Box size: X_bar = 10, Y_bar = 10
# Preferences: u_A = x_A^0.6 * y_A^0.4, u_B = x_B^0.4 * y_B^0.6
# Initial Endowment: omega_A = (2, 8) => omega_B = (8, 2)
# ==============================================================================
X_bar = 10.0
Y_bar = 10.0
alpha_A = 0.6
alpha_B = 0.4
e_A1 = 2.0
e_A2 = 8.0
e_B1 = X_bar - e_A1  # 8.0
e_B2 = Y_bar - e_A2  # 2.0

# Contract curve: MRS_A = MRS_B => y_A(x_A) = 8*x_A / (18 - x_A)
def contract_curve_y(x):
    return (8.0 * x) / (18.0 - x)

# Utility functions
def util_A(x, y):
    return (x ** alpha_A) * (y ** (1.0 - alpha_A))

def util_B(xB, yB):
    return (xB ** alpha_B) * (yB ** (1.0 - alpha_B))

# Exact Indifference curve formulations in (xA, yA) space
# For A: u_A = x_A^0.6 * y_A^0.4 => y_A = (u_A / x_A^0.6)^(1/0.4) = u_A^2.5 / x_A^1.5
def ic_A_y(x, u):
    return (u ** (1.0 / (1.0 - alpha_A))) / (x ** (alpha_A / (1.0 - alpha_A)))

# For B: u_B = x_B^0.4 * y_B^0.6 => y_B = (u_B / x_B^0.4)^(1/0.6) = u_B^(5/3) / x_B^(2/3)
# where x_B = X_bar - x, and y_A = Y_bar - y_B
def ic_B_y(x, u):
    xB = X_bar - x
    with np.errstate(invalid="ignore"):
        yB = (u ** (1.0 / (1.0 - alpha_B))) / (xB ** (alpha_B / (1.0 - alpha_B)))
        return Y_bar - yB

# Initial utilities at endowment omega
uA_omega = util_A(e_A1, e_A2)  # ~ 3.4822
uB_omega = util_B(e_B1, e_B2)  # ~ 3.4822

# Competitive equilibrium values: p* = 1.0, x_A* = (6, 4), x_B* = (4, 6)
p_star = 1.0
xA_star = 6.0
yA_star = 4.0
uA_star = util_A(xA_star, yA_star)  # ~ 5.1017
uB_star = util_B(X_bar - xA_star, Y_bar - yA_star)  # ~ 5.1017


# ==============================================================================
# 1. GIF 1: Competitive Equilibrium & First Welfare Theorem (Tâtonnement Dynamics)
# ==============================================================================
def generate_gif_equilibrium():
    print("Generating GIF 1: edgeworth-competitive-equilibrium.gif ...")
    # Price sweep: starts high (1.75) -> drops to low (0.62) -> converges to p* = 1.0
    # Both consumers' demands remain comfortably inside the box [0, 10] x [0, 10] throughout
    p_phase1 = np.linspace(1.75, 0.62, 22)
    p_phase2 = np.linspace(0.62, 1.0, 14)
    p_vals = np.concatenate([p_phase1, p_phase2])

    xA_grid = np.linspace(0.01, 9.99, 400)
    cc_y = contract_curve_y(xA_grid)

    frames = []

    # Dense price grid for excess demand curve in Panel 2
    p_dense = np.linspace(0.50, 2.0, 200)
    zx_dense = 5.6 / p_dense - 5.6

    for idx, p in enumerate(p_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.25)

        # Demands at price p
        mA = p * e_A1 + e_A2
        xA_dem = alpha_A * mA / p
        yA_dem = (1.0 - alpha_A) * mA

        mB = p * e_B1 + e_B2
        xB_dem = alpha_B * mB / p
        yB_dem = (1.0 - alpha_B) * mB
        # Coordinates of B's demand in A's frame
        xB_dem_inA = X_bar - xB_dem
        yB_dem_inA = Y_bar - yB_dem

        zx = xA_dem + xB_dem - X_bar
        is_equil = abs(p - 1.0) < 0.02 and idx > 26

        # Current utility levels at demand points
        uA_curr = util_A(xA_dem, yA_dem)
        uB_curr = util_B(xB_dem, yB_dem)

        # ---------------- Panel 1: Edgeworth Box ----------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(0, X_bar)
        ax1.set_ylim(0, Y_bar)
        ax1.set_xlabel(r"소비자 A의 재화 1 ($x_A$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"소비자 A의 재화 2 ($y_A$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)

        # Box border & Origins
        ax1.plot([0, X_bar, X_bar, 0, 0], [0, 0, Y_bar, Y_bar, 0], color=INK_COLOR, linewidth=1.8)
        ax1.text(-0.4, -0.4, r"$O_A$", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax1.text(X_bar + 0.1, Y_bar + 0.1, r"$O_B$", fontsize=11, fontweight="bold", color=AMBER_COLOR)

        # Contract Curve
        ax1.plot(xA_grid, cc_y, color=TEAL_COLOR, linewidth=2.4, label="계약곡선 (Pareto Efficient)")

        # Initial endowment omega = (2, 8)
        ax1.plot(e_A1, e_A2, "o", color=INK_COLOR, markersize=8, zorder=6)
        ax1.annotate(r"초기부존 $\omega(2,8)$", xy=(e_A1, e_A2), xytext=(e_A1 + 0.3, e_A2 + 0.4),
                     fontweight="bold", color=INK_COLOR, fontsize=9.5)

        # Budget line passing through omega: y = e_A2 - p*(x - e_A1)
        x_bl = np.array([0, X_bar])
        y_bl = e_A2 - p * (x_bl - e_A1)
        bl_color = PURPLE_COLOR if is_equil else RED_COLOR
        ax1.plot(x_bl, y_bl, color=bl_color, linewidth=2.0, linestyle="--",
                 label=f"예산선 (기울기 $-p={-p:.2f}$)")

        if not is_equil:
            # Disequilibrium: Plot both indifference curves passing through dA and dB
            uA_vals = ic_A_y(xA_grid, uA_curr)
            maskA = (uA_vals >= 0) & (uA_vals <= Y_bar)
            ax1.plot(xA_grid[maskA], uA_vals[maskA], color=GOLD_COLOR, linewidth=1.5, alpha=0.6,
                     label=r"$u_A$ 무차별곡선 ($d_A$에서 접함)")

            uB_vals = ic_B_y(xA_grid, uB_curr)
            maskB = (uB_vals >= 0) & (uB_vals <= Y_bar)
            ax1.plot(xA_grid[maskB], uB_vals[maskB], color=AMBER_COLOR, linewidth=1.5, alpha=0.6,
                     label=r"$u_B$ 무차별곡선 ($d_B$에서 접함)")

            # A's optimal bundle
            ax1.plot(xA_dem, yA_dem, "o", color=GOLD_COLOR, markersize=8, zorder=7)
            ax1.text(xA_dem + 0.2, yA_dem + 0.25, r"$d_A$", fontsize=9.5, fontweight="bold", color=GOLD_COLOR)

            # B's optimal bundle in box
            ax1.plot(xB_dem_inA, yB_dem_inA, "s", color=AMBER_COLOR, markersize=8, zorder=7)
            ax1.text(xB_dem_inA - 0.9, yB_dem_inA - 0.75, r"$d_B$", fontsize=9.5, fontweight="bold", color=AMBER_COLOR)

            # Arrow indicating disequilibrium mismatch
            ax1.annotate("", xy=(xB_dem_inA, yB_dem_inA), xytext=(xA_dem, yA_dem),
                         arrowprops=dict(arrowstyle="<->", color=RED_COLOR, lw=1.6, ls=":"))
        else:
            # Equilibrium coincidence at (6, 4)!
            # Plot the tangent indifference curves
            uA_vals = ic_A_y(xA_grid, uA_star)
            maskA = (uA_vals >= 0) & (uA_vals <= Y_bar)
            ax1.plot(xA_grid[maskA], uA_vals[maskA], color=GOLD_COLOR, linewidth=2.3, zorder=7,
                     label=r"$u_A^*$ 무차별곡선")

            uB_vals = ic_B_y(xA_grid, uB_star)
            maskB = (uB_vals >= 0) & (uB_vals <= Y_bar)
            ax1.plot(xA_grid[maskB], uB_vals[maskB], color=AMBER_COLOR, linewidth=2.3, zorder=7,
                     label=r"$u_B^*$ 무차별곡선")

            # Equilibrium star marker
            ax1.plot(xA_star, yA_star, "*", color=GOLD_COLOR, markersize=15, zorder=9,
                     label=r"경쟁균형 $x^*(6,4)$")

            ax1.annotate(r"제1후생정리: 두 무차별곡선 상호 외접!" + "\n" + r"$x^* \in$ 계약곡선 ($MRS_A=MRS_B=p^*=1$)",
                         xy=(xA_star, yA_star), xytext=(xA_star - 5.2, yA_star - 2.5),
                         fontweight="bold", color=PURPLE_COLOR, fontsize=9.5,
                         arrowprops=dict(arrowstyle="->", color=PURPLE_COLOR, lw=1.6))

        status_str = "시장청산 경쟁균형 도달! (p*=1.0)" if is_equil else f"가격 모색 중: p={p:.2f}"
        ax1.set_title(f"Edgeworth 상자 ({status_str})", fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax1.legend(loc="lower left", fontsize=8.0, framealpha=0.92)

        # ---------------- Panel 2: Walrasian Excess Demand ----------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(-4.0, 6.0)
        ax2.set_ylim(0.45, 2.1)
        ax2.set_xlabel(r"재화 1 초과수요 $z_x(p) = d_A^x + d_B^x - \bar{x}$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel(r"상대가격 $p = p_x / p_y$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("왈라스 시장청산과 가격 조정 동학", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Excess demand curve
        ax2.plot(zx_dense, p_dense, color=TEAL_COLOR, linewidth=2.2, label=r"총초과수요곡선 $z_x(p) = \frac{5.6}{p} - 5.6$")
        ax2.axvline(0, color=INK_COLOR, linestyle="-", linewidth=1.2)
        ax2.axhline(p_star, color=PURPLE_COLOR, linestyle="--", linewidth=1.2, label=r"균형가격 $p^* = 1.0$")

        # Shading excess demand vs excess supply
        ax2.axvspan(0, 6.0, color="#fef3c7", alpha=0.4, label=r"초과수요 ($z_x > 0 \to \dot{p} > 0$)")
        ax2.axvspan(-4.0, 0, color="#e0f2fe", alpha=0.4, label=r"초과공급 ($z_x < 0 \to \dot{p} < 0$)")

        # Current point on excess demand
        curr_pt_color = PURPLE_COLOR if is_equil else RED_COLOR
        ax2.plot(zx, p, "o", color=curr_pt_color, markersize=8, zorder=6)
        txt_pos = (zx + 0.3, p + 0.08) if zx < 2.5 else (zx - 2.8, p + 0.08)
        ax2.annotate(f"p={p:.2f}\n$z_x$={zx:+.2f}", xy=(zx, p), xytext=txt_pos,
                     fontweight="bold", color=curr_pt_color, fontsize=8.5)

        ax2.legend(loc="upper right", fontsize=8.0, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "edgeworth-competitive-equilibrium.gif")
    # Hold equilibrium frame for 16 frames (~2.2 seconds)
    frames_to_save = frames + [frames[-1]] * 16
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Second Welfare Theorem (Supporting Price & UPF Redistribution)
# ==============================================================================
def generate_gif_second_welfare():
    print("Generating GIF 2: edgeworth-second-welfare-theorem.gif ...")
    n_frames = 36
    # Target allocation xA sweeps along the contract curve from 2.0 to 8.0
    xA_targets = np.linspace(2.0, 8.0, n_frames)

    xA_grid = np.linspace(0.01, 9.99, 400)
    cc_y = contract_curve_y(xA_grid)

    # Precalculate Utility Possibility Frontier (UPF)
    # Along contract curve: uA(xA, cc_y(xA)), uB(10-xA, 10-cc_y(xA))
    uA_upf = np.array([util_A(x, contract_curve_y(x)) for x in xA_grid])
    uB_upf = np.array([util_B(X_bar - x, Y_bar - contract_curve_y(x)) for x in xA_grid])

    frames = []

    for idx, xA_tgt in enumerate(xA_targets):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.25)

        yA_tgt = contract_curve_y(xA_tgt)
        xB_tgt = X_bar - xA_tgt
        yB_tgt = Y_bar - yA_tgt

        # Supporting price at x_tgt: p_sup = MRS_A(x_tgt) = (alpha_A/(1-alpha_A)) * (yA/xA) = 1.5 * (yA/xA)
        p_sup = (alpha_A / (1.0 - alpha_A)) * (yA_tgt / xA_tgt)

        # Current utilities at target
        uA_tgt = util_A(xA_tgt, yA_tgt)
        uB_tgt = util_B(xB_tgt, yB_tgt)

        # ---------------- Panel 1: Edgeworth Box & Supporting Price Line ----------------
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(0, X_bar)
        ax1.set_ylim(0, Y_bar)
        ax1.set_xlabel(r"소비자 A의 재화 1 ($x_A$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"소비자 A의 재화 2 ($y_A$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.set_title("계약곡선 위의 목표 배분과 지지가격선", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # Box border & Origins
        ax1.plot([0, X_bar, X_bar, 0, 0], [0, 0, Y_bar, Y_bar, 0], color=INK_COLOR, linewidth=1.8)
        ax1.text(-0.4, -0.4, r"$O_A$", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax1.text(X_bar + 0.1, Y_bar + 0.1, r"$O_B$", fontsize=11, fontweight="bold", color=AMBER_COLOR)

        # Contract curve
        ax1.plot(xA_grid, cc_y, color=TEAL_COLOR, linewidth=2.4, label="계약곡선 (Pareto Optimal)")

        # Initial endowment omega = (2, 8)
        ax1.plot(e_A1, e_A2, "o", color=MUTED_COLOR, markersize=7, zorder=5)
        ax1.text(e_A1 + 0.2, e_A2 + 0.3, r"초기 $\omega(2,8)$", color=MUTED_COLOR, fontsize=8.5)

        # Supporting budget line passing through x_tgt: y - yA_tgt = -p_sup * (x - xA_tgt)
        x_bl = np.array([0, X_bar])
        y_bl = yA_tgt - p_sup * (x_bl - xA_tgt)
        ax1.plot(x_bl, y_bl, color=PURPLE_COLOR, linewidth=2.0, linestyle="--",
                 label=f"지지가격선 (기울기 $-p={-p_sup:.2f}$)")

        # Both tangent indifference curves at target point x_tgt!
        uA_vals = ic_A_y(xA_grid, uA_tgt)
        maskA = (uA_vals >= 0) & (uA_vals <= Y_bar)
        ax1.plot(xA_grid[maskA], uA_vals[maskA], color=GOLD_COLOR, linewidth=1.8, alpha=0.85,
                 label=r"$u_A$ 무차별곡선")

        uB_vals = ic_B_y(xA_grid, uB_tgt)
        maskB = (uB_vals >= 0) & (uB_vals <= Y_bar)
        ax1.plot(xA_grid[maskB], uB_vals[maskB], color=AMBER_COLOR, linewidth=1.8, alpha=0.85,
                 label=r"$u_B$ 무차별곡선")

        # Target point on contract curve
        ax1.plot(xA_tgt, yA_tgt, "*", color=GOLD_COLOR, markersize=13, zorder=8,
                 label=f"목표 배분 $x^*({xA_tgt:.1f}, {yA_tgt:.1f})$")

        # Transfer vector: Arrow from initial endowment to target budget line
        ax1.annotate("", xy=(xA_tgt, yA_tgt), xytext=(e_A1, e_A2),
                     arrowprops=dict(arrowstyle="->", color=MUTED_COLOR, lw=1.6, ls="-."))
        ax1.text((e_A1 + xA_tgt) / 2 - 0.5, (e_A2 + yA_tgt) / 2 + 0.3,
                 "일괄이전 (Lump-sum)", color=MUTED_COLOR, fontsize=8.5, fontweight="bold")

        ax1.legend(loc="lower right", fontsize=7.8, framealpha=0.92)

        # ---------------- Panel 2: Utility Possibility Frontier (UPF) ----------------
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(0, 10.5)
        ax2.set_ylim(0, 10.5)
        ax2.set_xlabel(r"소비자 A의 효용 $u_A$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel(r"소비자 B의 효용 $u_B$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.set_title("효용가능경계 (UPF)와 제2후생정리의 분권화", fontsize=11.5, fontweight="bold", color=INK_COLOR)

        # UPF Curve
        ax2.plot(uA_upf, uB_upf, color=TEAL_COLOR, linewidth=2.4, label="효용가능경계 (UPF)")

        # Initial endowment utility point (Inside UPF, Pareto inefficient)
        ax2.plot(uA_omega, uB_omega, "o", color=MUTED_COLOR, markersize=7, zorder=6)
        ax2.annotate(f"초기 효용\n$U(\\omega)=({uA_omega:.2f}, {uB_omega:.2f})$\n(비효율 내부점)",
                     xy=(uA_omega, uB_omega), xytext=(uA_omega + 0.5, uB_omega - 1.5),
                     fontweight="bold", color=MUTED_COLOR, fontsize=8.5,
                     arrowprops=dict(arrowstyle="->", color=MUTED_COLOR, lw=1.2))

        # Current target utility on UPF
        ax2.plot(uA_tgt, uB_tgt, "*", color=GOLD_COLOR, markersize=13, zorder=8,
                 label=f"목표 효용 $U^*({uA_tgt:.2f}, {uB_tgt:.2f})$")

        # Arrow showing welfare improvement via market decentralization
        ax2.annotate("", xy=(uA_tgt, uB_tgt), xytext=(uA_omega, uB_omega),
                     arrowprops=dict(arrowstyle="->", color=PURPLE_COLOR, lw=2.0))

        ax2.annotate(r"제2후생정리:" + "\n" + r"재분배 후 시장기구로" + "\n" + r"임의의 UPF 달성 가능!",
                     xy=(uA_tgt, uB_tgt),
                     xytext=(uA_tgt - 2.5 if uA_tgt > 6.0 else uA_tgt + 0.8,
                             uB_tgt - 2.0 if uB_tgt > 5.0 else uB_tgt + 0.8),
                     fontweight="bold", color=PURPLE_COLOR, fontsize=9.0)

        ax2.legend(loc="lower left", fontsize=8.0, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "edgeworth-second-welfare-theorem.gif")
    frames_to_save = frames + [frames[-1]] * 12
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=140, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_equilibrium()
    generate_gif_second_welfare()
    print("All Edgeworth GIFs generated successfully!")
