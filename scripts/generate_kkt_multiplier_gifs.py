"""Generate publication-grade animated GIFs for the KKT Inequality Optimization & Multipliers supplement.

Outputs:
  - assets/gif/kkt-multiplier-shadow-price.gif
  - assets/gif/kkt-corner-slackness-cone.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, Wedge
from PIL import Image

# Setup directories
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIF_DIR = os.path.join(ROOT, "assets", "gif")
os.makedirs(GIF_DIR, exist_ok=True)

# Editorial Styling
BG_COLOR = "#fcf9f2"
INK_COLOR = "#2d251e"
MUTED_COLOR = "#75665b"
GRID_COLOR = "#e5ded3"
TEAL_COLOR = "#087e8b"      # Component 2 / Inactive indicators
RED_COLOR = "#c0392b"       # Constraint 1 / Barrier Force / Multiplier
BLUE_COLOR = "#1d4ed8"      # Objective Gradient \nabla f
GOLD_COLOR = "#d97706"      # Normal Cone / Bliss point / Highlights
GREEN_COLOR = "#15803d"     # Feasible set / Value function

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# 1. GIF 1: Multiplier Dual Meaning: Barrier Force vs. Value Function Slope
# ==============================================================================
def generate_gif_multiplier_shadow_price():
    print("Generating GIF 1: kkt-multiplier-shadow-price.gif ...")

    # Parameter b sweeps from 3.2 to 10.4 and back
    b_fwd = np.linspace(3.4, 10.2, 22)
    b_hold1 = np.array([10.2] * 4)
    b_bwd = np.linspace(10.2, 3.4, 16)
    b_hold2 = np.array([3.4] * 3)
    b_vals = np.concatenate([b_fwd, b_hold1, b_bwd, b_hold2])

    frames = []

    # Grid for contour plot
    x1_grid = np.linspace(0, 7.5, 200)
    x2_grid = np.linspace(0, 7.5, 200)
    X1, X2 = np.meshgrid(x1_grid, x2_grid)
    # Objective: f(x1, x2) = -(x1-4)^2 - (x2-4)^2 + 32
    Z = -(X1 - 4.0)**2 - (X2 - 4.0)**2 + 32.0

    # Range of b for right panel value function
    b_curve = np.linspace(2.5, 11.0, 300)
    v_curve = np.where(b_curve < 8.0, -0.5 * (b_curve - 8.0)**2 + 32.0, 32.0)
    mu_curve = np.where(b_curve < 8.0, 8.0 - b_curve, 0.0)

    for idx, b in enumerate(b_vals):
        fig = plt.figure(figsize=(13.2, 6.0), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        # 3 subplots: Left (Decision space), Right-Top (Value function), Right-Bottom (Multiplier)
        gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1.0], height_ratios=[1.1, 0.9],
                              left=0.07, right=0.96, bottom=0.10, top=0.90, wspace=0.28, hspace=0.36)
        ax_dec = fig.add_subplot(gs[:, 0])
        ax_val = fig.add_subplot(gs[0, 1])
        ax_mu = fig.add_subplot(gs[1, 1])

        # ----------------------------------------------------------------------
        # 1. Left Panel: Decision Space (x1, x2)
        # ----------------------------------------------------------------------
        ax_dec.set_facecolor(BG_COLOR)
        ax_dec.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        # Contours of f
        cs = ax_dec.contour(X1, X2, Z, levels=[8, 16, 22, 26, 29, 31, 31.8],
                            colors=MUTED_COLOR, alpha=0.45, linewidths=1.0)
        ax_dec.clabel(cs, inline=True, fontsize=8, fmt="f=%1.0f")

        # Feasible polygon: x1, x2 >= 0 and x1 + x2 <= b
        if b <= 7.5:
            poly_pts = [[0, 0], [b, 0], [0, b]]
        else:
            poly_pts = [[0, 0], [7.5, 0], [7.5, max(0, b - 7.5)], [max(0, b - 7.5), 7.5], [0, 7.5]]
        feasible_poly = Polygon(poly_pts, closed=True, facecolor=GREEN_COLOR, alpha=0.12,
                                edgecolor=GREEN_COLOR, linestyle="--", lw=1.5, label=r"실행가능영역 $x_1+x_2 \leq b$")
        ax_dec.add_patch(feasible_poly)

        # Constraint line x1 + x2 = b
        lx = np.linspace(-0.5, 8.0, 100)
        ly = b - lx
        valid = (lx >= -0.2) & (ly >= -0.2) & (lx <= 7.5) & (ly <= 7.5)
        ax_dec.plot(lx[valid], ly[valid], color=RED_COLOR, lw=2.4, label=f"제약경계 $x_1+x_2 = {b:.1f}$")

        # Unconstrained Bliss point (4, 4)
        ax_dec.scatter([4.0], [4.0], color=GOLD_COLOR, s=110, marker="*", zorder=6, label="자유 최적점 $x^0=(4, 4)$")

        # Optimum determination
        is_binding = (b < 8.0)
        if is_binding:
            x_opt = np.array([b / 2.0, b / 2.0])
            mu_val = 8.0 - b
            v_val = -0.5 * (b - 8.0)**2 + 32.0
            grad_f = np.array([8.0 - b, 8.0 - b]) # [8 - 2x1, 8 - 2x2]
            status_text = f"바인딩 (Binding) · $\\mu^* = {mu_val:.2f} > 0$"
            status_color = RED_COLOR
        else:
            x_opt = np.array([4.0, 4.0])
            mu_val = 0.0
            v_val = 32.0
            grad_f = np.array([0.0, 0.0])
            status_text = f"비활성 (Slack) · $\\mu^* = 0.00$"
            status_color = TEAL_COLOR

        # Plot Optimum
        ax_dec.scatter([x_opt[0]], [x_opt[1]], color=status_color, s=120, zorder=7,
                       edgecolor=INK_COLOR, lw=1.8, label="KKT 최적해 $x^*(b)$")

        # Draw Vectors at x*
        scale = 0.38
        if is_binding:
            # 1. Gradient of objective: \nabla f pointing toward (4, 4)
            ax_dec.annotate("", xy=(x_opt[0] + grad_f[0] * scale, x_opt[1] + grad_f[1] * scale),
                            xytext=(x_opt[0], x_opt[1]),
                            arrowprops=dict(arrowstyle="-|>", color=BLUE_COLOR, lw=3.0, mutation_scale=18))
            ax_dec.text(x_opt[0] + grad_f[0] * scale * 0.5 + 0.15, x_opt[1] + grad_f[1] * scale * 0.5 - 0.25,
                        r"$\nabla f(x^*)$" + f"\n(크기 {np.linalg.norm(grad_f):.2f})",
                        color=BLUE_COLOR, fontsize=9.5, fontweight="bold")

            # 2. Constraint normal barrier force: \mu* \nabla g pointing inward (opposing \nabla f)
            norm_g = np.array([1.0, 1.0]) # normal pointing outward from constraint
            barrier_force = mu_val * norm_g
            ax_dec.annotate("", xy=(x_opt[0] - barrier_force[0] * scale, x_opt[1] - barrier_force[1] * scale),
                            xytext=(x_opt[0], x_opt[1]),
                            arrowprops=dict(arrowstyle="-|>", color=RED_COLOR, lw=3.0, linestyle="-", mutation_scale=18))
            ax_dec.text(x_opt[0] - barrier_force[0] * scale * 0.5 - 1.6, x_opt[1] - barrier_force[1] * scale * 0.5 + 0.15,
                        r"$-\mu^*\nabla g$" + f"\n(벽의 항력 $\\mu^*={mu_val:.2f}$)",
                        color=RED_COLOR, fontsize=9.5, fontweight="bold")

            # Equating text
            ax_dec.text(0.35, 6.7, r"$\mathbf{\nabla f(x^*) = \mu^* \nabla g(x^*)}$ (힘의 평형)",
                        color=INK_COLOR, fontsize=11, fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor=RED_COLOR, lw=1.2))
        else:
            ax_dec.text(0.35, 6.7, r"$\mathbf{\nabla f(x^*) = 0, \;\; \mu^* = 0}$ (자유 극대점)",
                        color=INK_COLOR, fontsize=11, fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor=TEAL_COLOR, lw=1.2))

        ax_dec.set_xlim(-0.2, 7.2)
        ax_dec.set_ylim(-0.2, 7.2)
        ax_dec.set_xlabel(r"선택변수 $x_1$", fontsize=10.5, color=INK_COLOR)
        ax_dec.set_ylabel(r"선택변수 $x_2$", fontsize=10.5, color=INK_COLOR)
        ax_dec.set_title(f"[선택 공간] 제약자원 $b = {b:.2f}$ | {status_text}", fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax_dec.legend(loc="lower left", fontsize=8.5, framealpha=0.92)

        # ----------------------------------------------------------------------
        # 2. Right-Top Subplot: Value Function v(b) and Tangent Line (Slope = \mu*)
        # ----------------------------------------------------------------------
        ax_val.set_facecolor(BG_COLOR)
        ax_val.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        ax_val.plot(b_curve, v_curve, color=GREEN_COLOR, lw=2.6, label=r"가치함수 $v(b) = \max f(x)$")
        ax_val.axvline(8.0, color=GOLD_COLOR, linestyle=":", lw=1.5, alpha=0.8, label="임계점 $b^* = 8$")

        # Current point on v(b)
        ax_val.scatter([b], [v_val], color=status_color, s=90, zorder=6, edgecolor=INK_COLOR, lw=1.5)

        # Tangent line: slope is mu_val
        b_tan = np.linspace(max(2.5, b - 1.8), min(11.0, b + 1.8), 50)
        v_tan = v_val + mu_val * (b_tan - b)
        ax_val.plot(b_tan, v_tan, color=RED_COLOR if is_binding else TEAL_COLOR, lw=2.0, linestyle="--",
                    label=f"접선 기울기 $dv/db = \\mu^* = {mu_val:.2f}$")

        ax_val.set_xlim(2.5, 11.0)
        ax_val.set_ylim(16.0, 35.0)
        ax_val.set_ylabel(r"최적가치 $v(b)$", fontsize=10, color=INK_COLOR)
        ax_val.set_title(r"[포락선 정리] $\frac{dv(b)}{db} = \mu^*(b)$ (자원의 그림자 가격)", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax_val.legend(loc="lower right", fontsize=8.0, framealpha=0.90)

        # ----------------------------------------------------------------------
        # 3. Right-Bottom Subplot: Multiplier \mu*(b) Function (Shadow Price Curve)
        # ----------------------------------------------------------------------
        ax_mu.set_facecolor(BG_COLOR)
        ax_mu.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        ax_mu.plot(b_curve, mu_curve, color=RED_COLOR, lw=2.4, label=r"승수 $\mu^*(b) = \max(8-b, 0)$")
        ax_mu.axvline(8.0, color=GOLD_COLOR, linestyle=":", lw=1.5, alpha=0.8)
        ax_mu.axhline(0.0, color=INK_COLOR, lw=1.0, alpha=0.5)

        # Current marker on \mu*
        ax_mu.scatter([b], [mu_val], color=status_color, s=90, zorder=6, edgecolor=INK_COLOR, lw=1.5)

        # Shading regions
        ax_mu.fill_between(b_curve[b_curve <= 8.0], mu_curve[b_curve <= 8.0], color=RED_COLOR, alpha=0.12, label="자원 희소 구간 (양의 그림자 가격)")
        ax_mu.fill_between(b_curve[b_curve >= 8.0], 0, 0.4, color=TEAL_COLOR, alpha=0.12, label="자원 잉여 구간 (승수 = 0)")

        ax_mu.set_xlim(2.5, 11.0)
        ax_mu.set_ylim(-0.4, 5.4)
        ax_mu.set_xlabel(r"제약 자원량 $b$", fontsize=10, color=INK_COLOR)
        ax_mu.set_ylabel(r"KKT 승수 $\mu^*(b)$", fontsize=10, color=INK_COLOR)
        ax_mu.set_title(r"[상보여유성 전이] 제약 결여($\mu^*>0$) $\to$ 잉여($\mu^*=0$)", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax_mu.legend(loc="upper right", fontsize=8.0, framealpha=0.90)

        # Render to frame
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    # Save GIF
    gif_path = os.path.join(GIF_DIR, "kkt-multiplier-shadow-price.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True)
    print(f"GIF 1 generated: {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Corner Solutions & Parallelogram Multiplier Decomposition
# ==============================================================================
def generate_gif_corner_slackness_cone():
    print("Generating GIF 2: kkt-corner-slackness-cone.gif ...")

    # Rotate the direction of objective gradient \nabla f from 15 deg to 75 deg and back
    angles_fwd = np.linspace(15.0, 75.0, 22)
    angles_hold = np.array([75.0] * 3)
    angles_bwd = np.linspace(75.0, 15.0, 16)
    angles_hold2 = np.array([15.0] * 3)
    angles = np.concatenate([angles_fwd, angles_hold, angles_bwd, angles_hold2])

    frames = []

    # Normal vectors for constraints:
    # Constraint 1: x1 + 2 x2 <= 6  => n1 = (1, 2)
    # Constraint 2: 2 x1 + x2 <= 6  => n2 = (2, 1)
    n1 = np.array([1.0, 2.0])
    n2 = np.array([2.0, 1.0])
    corner = np.array([2.0, 2.0]) # Intersection point

    # Angles of n2 and n1:
    # angle(n2) = arctan(1/2) = 26.565 deg
    # angle(n1) = arctan(2/1) = 63.435 deg
    ang_n2 = np.degrees(np.arctan2(1.0, 2.0))
    ang_n1 = np.degrees(np.arctan2(2.0, 1.0))

    # Gradient magnitude
    R = 3.2

    for idx, deg in enumerate(angles):
        rad = np.radians(deg)
        grad_f = R * np.array([np.cos(rad), np.sin(rad)])

        fig = plt.figure(figsize=(13.2, 6.0), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        gs = fig.add_gridspec(2, 2, width_ratios=[1.25, 1.0], height_ratios=[1.0, 1.0],
                              left=0.07, right=0.96, bottom=0.10, top=0.90, wspace=0.28, hspace=0.38)
        ax_cone = fig.add_subplot(gs[:, 0])
        ax_bar_mu = fig.add_subplot(gs[0, 1])
        ax_bar_slack = fig.add_subplot(gs[1, 1])

        # ----------------------------------------------------------------------
        # 1. Left Panel: Decision Space & Normal Cone at Corner (2, 2)
        # ----------------------------------------------------------------------
        ax_cone.set_facecolor(BG_COLOR)
        ax_cone.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        # Feasible polygon: (0,0), (3,0), (2,2), (0,3)
        feasible_poly = Polygon([[0, 0], [3, 0], [2, 2], [0, 3]], closed=True,
                                facecolor=GREEN_COLOR, alpha=0.15, edgecolor=INK_COLOR, lw=1.8,
                                label=r"실행가능영역 $\mathcal{F}$")
        ax_cone.add_patch(feasible_poly)

        # Plot constraint boundaries
        lx = np.linspace(-0.5, 4.5, 100)
        # C1: x2 = (6 - x1)/2
        ax_cone.plot(lx, (6.0 - lx) / 2.0, color=RED_COLOR, lw=2.2, label=r"제약 1: $x_1+2x_2=6$ ($\mathbf{n}_1=(1, 2)$)")
        # C2: x2 = 6 - 2*x1
        ax_cone.plot(lx, 6.0 - 2.0 * lx, color=TEAL_COLOR, lw=2.2, label=r"제약 2: $2x_1+x_2=6$ ($\mathbf{n}_2=(2, 1)$)")

        # Normal Cone at (2, 2)
        # Wedge from ang_n2 to ang_n1
        cone_wedge = Wedge(corner, 3.8, ang_n2, ang_n1, facecolor=GOLD_COLOR, alpha=0.22,
                           edgecolor=GOLD_COLOR, linestyle="--", lw=1.5, label="법선 원뿔 (Normal Cone)")
        ax_cone.add_patch(cone_wedge)

        # Plot Base Normals n1 and n2 from corner
        scale_n = 0.9
        ax_cone.annotate("", xy=(corner[0] + n1[0] * scale_n, corner[1] + n1[1] * scale_n), xytext=(corner[0], corner[1]),
                         arrowprops=dict(arrowstyle="-|>", color=RED_COLOR, lw=2.2, mutation_scale=15))
        ax_cone.text(corner[0] + n1[0] * scale_n + 0.05, corner[1] + n1[1] * scale_n + 0.1, r"$\mathbf{n}_1=(1,2)$",
                     color=RED_COLOR, fontsize=9.5, fontweight="bold")

        ax_cone.annotate("", xy=(corner[0] + n2[0] * scale_n, corner[1] + n2[1] * scale_n), xytext=(corner[0], corner[1]),
                         arrowprops=dict(arrowstyle="-|>", color=TEAL_COLOR, lw=2.2, mutation_scale=15))
        ax_cone.text(corner[0] + n2[0] * scale_n + 0.1, corner[1] + n2[1] * scale_n - 0.15, r"$\mathbf{n}_2=(2,1)$",
                     color=TEAL_COLOR, fontsize=9.5, fontweight="bold")

        # Determine Case based on angle
        # Inside Normal Cone: ang_n2 <= deg <= ang_n1
        in_cone = (ang_n2 <= deg <= ang_n1)
        if deg < ang_n2:
            case_name = "제약 2만 바인딩 (면 2 최적)"
            case_sub = f"$\\nabla f$ 방향각({deg:.1f}°) < $\\mathbf{{n}}_2$ 경사({ang_n2:.1f}°)"
            # At face 2: \mu1 = 0, \mu2 > 0
            # Optimum is shifted along face 2 towards (3, 0)
            opt_pt = np.array([2.0, 2.0]) # At corner threshold or on face
            mu1 = 0.0
            mu2 = R * np.cos(rad - np.radians(ang_n2)) / np.linalg.norm(n2)
            slack1 = 6.0 - (opt_pt[0] + 2 * opt_pt[1])
            slack2 = 0.0
            cone_status = "원뿔 외부 (Face 2)"
        elif deg > ang_n1:
            case_name = "제약 1만 바인딩 (면 1 최적)"
            case_sub = f"$\\nabla f$ 방향각({deg:.1f}°) > $\\mathbf{{n}}_1$ 경사({ang_n1:.1f}°)"
            opt_pt = np.array([2.0, 2.0])
            mu1 = R * np.cos(np.radians(ang_n1) - rad) / np.linalg.norm(n1)
            mu2 = 0.0
            slack1 = 0.0
            slack2 = 6.0 - (2 * opt_pt[0] + opt_pt[1])
            cone_status = "원뿔 외부 (Face 1)"
        else:
            case_name = "코너해 (Corner Solution): 두 제약 동시 바인딩"
            case_sub = f"$\\nabla f$가 법선 원뿔 내부 포섭 ({ang_n2:.1f}° $\\leq {deg:.1f}^\\circ \\leq$ {ang_n1:.1f}°)"
            opt_pt = np.array([2.0, 2.0])
            # Decompose grad_f = mu1 * n1 + mu2 * n2
            # [1 2; 2 1] [mu1; mu2] = [gx; gy]
            # mu1 = (2*gy - gx)/3, mu2 = (2*gx - gy)/3
            mu1 = (2.0 * grad_f[1] - grad_f[0]) / 3.0
            mu2 = (2.0 * grad_f[0] - grad_f[1]) / 3.0
            slack1 = 0.0
            slack2 = 0.0
            cone_status = "원뿔 내부 (Corner)"

        # Corner marker
        ax_cone.scatter([2.0], [2.0], color=GOLD_COLOR, s=130, zorder=8, edgecolor=INK_COLOR, lw=2.0)

        # Plot rotating gradient \nabla f
        scale_f = 0.85
        ax_cone.annotate("", xy=(corner[0] + grad_f[0] * scale_f, corner[1] + grad_f[1] * scale_f), xytext=(corner[0], corner[1]),
                         arrowprops=dict(arrowstyle="-|>", color=BLUE_COLOR, lw=3.2, mutation_scale=20))
        ax_cone.text(corner[0] + grad_f[0] * scale_f + 0.1, corner[1] + grad_f[1] * scale_f + 0.1,
                     r"$\nabla f$" + f" ({deg:.1f}°)", color=BLUE_COLOR, fontsize=10.5, fontweight="bold")

        # If inside normal cone, draw the parallelogram decomposition:
        if in_cone:
            vec1 = mu1 * n1 * scale_f
            vec2 = mu2 * n2 * scale_f
            # mu1 * n1 vector
            ax_cone.annotate("", xy=(corner[0] + vec1[0], corner[1] + vec1[1]), xytext=(corner[0], corner[1]),
                             arrowprops=dict(arrowstyle="-|>", color=RED_COLOR, lw=2.4, mutation_scale=14))
            # mu2 * n2 vector
            ax_cone.annotate("", xy=(corner[0] + vec2[0], corner[1] + vec2[1]), xytext=(corner[0], corner[1]),
                             arrowprops=dict(arrowstyle="-|>", color=TEAL_COLOR, lw=2.4, mutation_scale=14))
            # Dashed parallelogram lines
            ax_cone.plot([corner[0] + vec1[0], corner[0] + vec1[0] + vec2[0]],
                         [corner[1] + vec1[1], corner[1] + vec1[1] + vec2[1]],
                         color=MUTED_COLOR, linestyle=":", lw=1.5)
            ax_cone.plot([corner[0] + vec2[0], corner[0] + vec1[0] + vec2[0]],
                         [corner[1] + vec2[1], corner[1] + vec1[1] + vec2[1]],
                         color=MUTED_COLOR, linestyle=":", lw=1.5)

            # Text formula
            ax_cone.text(0.2, 5.0, r"$\mathbf{\nabla f = \mu_1^* \mathbf{n}_1 + \mu_2^* \mathbf{n}_2}$" + "\n" +
                         f"$\\mu_1^*={mu1:.2f}$ (제약 1 기여도)\n$\\mu_2^*={mu2:.2f}$ (제약 2 기여도)",
                         fontsize=9.5, fontweight="bold", color=INK_COLOR,
                         bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor=GOLD_COLOR, lw=1.4))

        ax_cone.set_xlim(-0.2, 5.2)
        ax_cone.set_ylim(-0.2, 5.4)
        ax_cone.set_xlabel(r"선택변수 $x_1$", fontsize=10, color=INK_COLOR)
        ax_cone.set_ylabel(r"선택변수 $x_2$", fontsize=10, color=INK_COLOR)
        ax_cone.set_title(f"[법선 원뿔과 벡터 분해] {case_name}", fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax_cone.legend(loc="lower left", fontsize=8.0, framealpha=0.92)

        # ----------------------------------------------------------------------
        # 2. Right-Top: Multipliers \mu_1* and \mu_2* Bar Chart (Dual Variables)
        # ----------------------------------------------------------------------
        ax_bar_mu.set_facecolor(BG_COLOR)
        ax_bar_mu.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR, axis="x")

        bars_mu = ax_bar_mu.barh([1, 0], [mu1, mu2], height=0.45, color=[RED_COLOR, TEAL_COLOR], alpha=0.88, edgecolor=INK_COLOR, lw=1.2)
        ax_bar_mu.set_yticks([1, 0])
        ax_bar_mu.set_yticklabels([r"제약 1 승수 $\mu_1^*$", r"제약 2 승수 $\mu_2^*$"], fontsize=9.5, fontweight="bold", color=INK_COLOR)
        ax_bar_mu.set_xlim(0, 2.5)
        ax_bar_mu.set_xlabel(r"승수 크기 (자원 한계가치 / 병목 강도)", fontsize=9.5, color=INK_COLOR)
        ax_bar_mu.set_title(f"[쌍대 변수: KKT 승수] {cone_status}", fontsize=11, fontweight="bold", color=INK_COLOR)

        # Value annotations on bars
        ax_bar_mu.text(mu1 + 0.08, 1, f"{mu1:.2f}", va="center", fontsize=9.5, fontweight="bold", color=RED_COLOR)
        ax_bar_mu.text(mu2 + 0.08, 0, f"{mu2:.2f}", va="center", fontsize=9.5, fontweight="bold", color=TEAL_COLOR)

        # ----------------------------------------------------------------------
        # 3. Right-Bottom: Slack Variables s1 and s2 (Primal Slackness)
        # ----------------------------------------------------------------------
        ax_bar_slack.set_facecolor(BG_COLOR)
        ax_bar_slack.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR, axis="x")

        bars_s = ax_bar_slack.barh([1, 0], [slack1, slack2], height=0.45, color=[RED_COLOR, TEAL_COLOR], alpha=0.35, edgecolor=INK_COLOR, lw=1.2)
        ax_bar_slack.set_yticks([1, 0])
        ax_bar_slack.set_yticklabels([r"제약 1 여유 $s_1$", r"제약 2 여유 $s_2$"], fontsize=9.5, fontweight="bold", color=INK_COLOR)
        ax_bar_slack.set_xlim(0, 2.5)
        ax_bar_slack.set_xlabel(r"제약 여유도 $s_j = b_j - g_j(x^*)$", fontsize=9.5, color=INK_COLOR)
        ax_bar_slack.set_title(r"[원시 변수: 여유도] 상보여유성 $\mu_j^* \cdot s_j = 0$ 검증", fontsize=11, fontweight="bold", color=INK_COLOR)

        # Annotations on slacks
        ax_bar_slack.text(slack1 + 0.08, 1, f"{slack1:.2f} ({'바인딩' if slack1 < 0.01 else '슬랙'})", va="center", fontsize=9, fontweight="bold", color=RED_COLOR)
        ax_bar_slack.text(slack2 + 0.08, 0, f"{slack2:.2f} ({'바인딩' if slack2 < 0.01 else '슬랙'})", va="center", fontsize=9, fontweight="bold", color=TEAL_COLOR)

        # Render to frame
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    # Save GIF
    gif_path = os.path.join(GIF_DIR, "kkt-corner-slackness-cone.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=True)
    print(f"GIF 2 generated: {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_multiplier_shadow_price()
    generate_gif_corner_slackness_cone()
    print("All KKT Multiplier GIFs generated successfully!")
