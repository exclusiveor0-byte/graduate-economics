"""Generate publication-grade 3D animated GIFs for the KKT Inequality Optimization & Multipliers supplement.

Outputs:
  - assets/gif/kkt-multiplier-shadow-price.gif (3D Mountain Surface, Vertical Barrier Wall, and Cross-Section Shadow Price)
  - assets/gif/kkt-corner-slackness-cone.gif (3D Intersecting Walls at Corner, Summit Rotation, and Multiplier Decomposition)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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
RED_COLOR = "#c0392b"       # Wall 1 / Barrier Force / Multiplier 1
TEAL_COLOR = "#087e8b"      # Wall 2 / Multiplier 2
GOLD_COLOR = "#d97706"      # Summit / Corner Highlight
GREEN_COLOR = "#15803d"     # Feasible Surface / Mountain Profile
BLUE_COLOR = "#1d4ed8"      # Uphill Gradient Vector / Tangent Slope

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# 1. GIF 1: 3D Mountain Surface & Vertical Barrier Wall (Uphill Slope = Multiplier)
# ==============================================================================
def generate_gif_multiplier_shadow_price():
    print("Generating 3D GIF 1: kkt-multiplier-shadow-price.gif ...")

    # Sweep parameter b from 3.4 to 9.8 and back
    b_fwd = np.linspace(3.4, 9.6, 16)
    b_hold1 = np.array([9.6] * 3)
    b_bwd = np.linspace(9.6, 3.4, 12)
    b_hold2 = np.array([3.4] * 2)
    b_vals = np.concatenate([b_fwd, b_hold1, b_bwd, b_hold2])

    # Surface mesh
    x1 = np.linspace(0, 6.2, 50)
    x2 = np.linspace(0, 6.2, 50)
    X1, X2 = np.meshgrid(x1, x2)
    # Hill peak at (4, 4), max height 32
    Z = -(X1 - 4.0)**2 - (X2 - 4.0)**2 + 32.0

    frames = []

    for idx, b in enumerate(b_vals):
        fig = plt.figure(figsize=(14.5, 6.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        # ----------------------------------------------------------------------
        # Left Panel: 3D Mountain Surface & Moving Vertical Barrier Wall
        # ----------------------------------------------------------------------
        ax1 = fig.add_subplot(1, 2, 1, projection='3d')
        ax1.set_facecolor(BG_COLOR)

        # Feasible surface (colored) vs Infeasible surface (faded wireframe)
        mask_feas = (X1 + X2 <= b)
        Z_feas = np.where(mask_feas, Z, np.nan)
        Z_infeas = np.where(~mask_feas, Z, np.nan)

        ax1.plot_surface(X1, X2, Z_feas, cmap="viridis", alpha=0.82, edgecolor='none', zorder=2)
        ax1.plot_wireframe(X1, X2, Z_infeas, color="#a8a29e", alpha=0.22, lw=0.6, zorder=1)

        # Vertical barrier wall at x1 + x2 = b
        s_min = max(0.0, b - 6.0)
        s_max = min(6.0, b)
        if s_max > s_min:
            s = np.linspace(s_min, s_max, 30)
            w_x1 = s
            w_x2 = b - s
            w_z_top = -(w_x1 - 4.0)**2 - (w_x2 - 4.0)**2 + 32.0
            w_z_bot = np.zeros_like(s)

            wall_verts = []
            for i in range(len(s) - 1):
                poly = [
                    [w_x1[i], w_x2[i], w_z_bot[i]],
                    [w_x1[i+1], w_x2[i+1], w_z_bot[i+1]],
                    [w_x1[i+1], w_x2[i+1], w_z_top[i+1]],
                    [w_x1[i], w_x2[i], w_z_top[i]]
                ]
                wall_verts.append(poly)

            wall_coll = Poly3DCollection(wall_verts, facecolors=RED_COLOR, alpha=0.45,
                                         edgecolors='#962d22', linewidths=0.5, zorder=4)
            ax1.add_collection3d(wall_coll)
            ax1.plot(w_x1, w_x2, w_z_top, color=RED_COLOR, lw=3.0, zorder=5)

        # Optimum calculation
        is_binding = (b < 8.0)
        if is_binding:
            opt_x = b / 2.0
            opt_y = b / 2.0
            opt_z = -2.0 * (b/2.0 - 4.0)**2 + 32.0
            mu = 8.0 - b
            status_str = f"바인딩 (제약벽 위 최고점) · 승수 μ* = {mu:.2f}"
            opt_color = RED_COLOR
        else:
            opt_x = 4.0
            opt_y = 4.0
            opt_z = 32.0
            mu = 0.0
            status_str = "자유 최적점 (산 정상 도달) · 승수 μ* = 0.00"
            opt_color = GOLD_COLOR

        # Marker for optimum
        ax1.scatter([opt_x], [opt_y], [opt_z], color=opt_color, s=130, edgecolor='black', lw=1.6, zorder=10)

        # Summit star
        ax1.scatter([4.0], [4.0], [32.0], color=GOLD_COLOR, s=150, marker='*', edgecolor='black', lw=1.6, zorder=9)

        # Arrow pointing uphill towards summit
        if is_binding:
            scale_arrow = 0.4
            ax1.quiver(opt_x, opt_y, opt_z,
                       (4.0 - opt_x) * scale_arrow, (4.0 - opt_y) * scale_arrow, (32.0 - opt_z) * scale_arrow * 0.4,
                       color=BLUE_COLOR, lw=3.2, arrow_length_ratio=0.25, zorder=11)

        ax1.set_xlim(0, 6.0)
        ax1.set_ylim(0, 6.0)
        ax1.set_zlim(0, 35.0)
        ax1.set_xlabel(r'$x_1$', fontsize=9.5)
        ax1.set_ylabel(r'$x_2$', fontsize=9.5)
        ax1.set_zlabel('효용/가치 $f(x)$', fontsize=9.5)
        ax1.view_init(elev=28, azim=-55)
        ax1.set_title(f"[3D 효용 곡면과 제약벽] 자원 $b = {b:.1f}$\n{status_str}", fontsize=11, fontweight='bold', color=INK_COLOR)

        # ----------------------------------------------------------------------
        # Right Panel: 2D Vertical Cross-Section Profile & Tangent Slope
        # ----------------------------------------------------------------------
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.set_facecolor(BG_COLOR)
        ax2.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR)

        r_grid = np.linspace(0, 6.0, 200)
        Z_r = -2.0 * (r_grid - 4.0)**2 + 32.0

        ax2.plot(r_grid, Z_r, color=GREEN_COLOR, lw=2.6, label="산의 수직 단면 프로파일 $f(r, r)$")

        r_wall = b / 2.0
        # Shading feasible area
        ax2.fill_between(r_grid[r_grid <= r_wall], Z_r[r_grid <= r_wall], -5, color=GREEN_COLOR, alpha=0.15,
                         label=rf"실행가능 영역 (벽 안쪽 $r \leq {r_wall:.2f}$)")
        # Wall line
        ax2.axvline(r_wall, color=RED_COLOR, lw=3.0, linestyle="-", label=f"수직 제약벽 ($x_1+x_2 = {b:.1f}$)")

        # Tangent slope line at optimum
        if is_binding:
            z_wall = -2.0 * (r_wall - 4.0)**2 + 32.0
            slope_r = -4.0 * (r_wall - 4.0) # dz/dr = 2*(8 - b) = 2*mu
            r_tan = np.linspace(max(0.0, r_wall - 0.7), min(6.0, r_wall + 1.2), 50)
            z_tan = z_wall + slope_r * (r_tan - r_wall)
            ax2.plot(r_tan, z_tan, color=BLUE_COLOR, lw=2.5, linestyle="--",
                     label=rf"벽에서의 오르막 경사 (승수 $\mu^* = {mu:.2f}$)")
            ax2.scatter([r_wall], [z_wall], color=RED_COLOR, s=120, zorder=6, edgecolor="black", label=f"벽 위의 최고점 ($z={z_wall:.1f}$)")
        else:
            ax2.scatter([4.0], [32.0], color=GOLD_COLOR, s=150, marker="*", zorder=7, edgecolor="black", label="산 정상 도달 ($z=32.0, \mu^*=0$)")
            # Flat tangent at summit
            r_tan = np.linspace(3.0, 5.0, 50)
            ax2.plot(r_tan, [32.0]*50, color=GOLD_COLOR, lw=2.5, linestyle="--", label=r"정상에서의 경사 ($\mu^* = 0.00$)")

        ax2.scatter([4.0], [32.0], color=GOLD_COLOR, s=130, marker="*", zorder=5, edgecolor="black")

        # Inset formula box
        if is_binding:
            msg = (
                f"★ 승수(μ*)의 3D 물리적 의미:\n"
                f"· 벽 너머 산 정상을 향한 오르막 경사의 가파름\n"
                f"· 벽을 1단위 밀어냈을 때 더 올라갈 수 있는 고도\n"
                f"  → dz/db = μ* = {mu:.2f} (자원의 그림자 가격)"
            )
            box_color = RED_COLOR
        else:
            msg = (
                "★ 상보여유성 (Complementary Slackness):\n"
                "· 산 정상이 이미 제약벽 안쪽에 있으므로,\n"
                "· 벽을 더 밀어도 고도가 오르지 않음 (μ* = 0)"
            )
            box_color = GREEN_COLOR

        ax2.text(0.04, 0.70, msg, transform=ax2.transAxes, fontsize=9.5, fontweight="bold", color=INK_COLOR,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor=box_color, lw=1.5))

        ax2.set_xlim(0, 6.0)
        ax2.set_ylim(0, 36.0)
        ax2.set_xlabel(r"대각선 이동 거리 $r$ ($x_1 = x_2 = r$)", fontsize=10, color=INK_COLOR)
        ax2.set_ylabel(r"고도 / 목적함수값 $z = f(x)$", fontsize=10, color=INK_COLOR)
        ax2.set_title(r"[2D 단면 투영] $\mu^* = \frac{dz}{db}$ : 산의 오르막 경사 (그림자 가격)",
                      fontsize=11.5, fontweight='bold', color=INK_COLOR)
        ax2.legend(loc="lower right", fontsize=8.0, framealpha=0.92)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    gif_path = os.path.join(GIF_DIR, "kkt-multiplier-shadow-price.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=130, loop=0, optimize=True)
    print(f"3D GIF 1 generated: {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: 3D Corner Solution (Two Intersecting Walls at a Vertex & Dual Multipliers)
# ==============================================================================
def generate_gif_corner_slackness_cone():
    print("Generating 3D GIF 2: kkt-corner-slackness-cone.gif ...")

    # Rotate the summit of the hill outside the corner from 15 deg to 75 deg and back
    angles_fwd = np.linspace(16.0, 74.0, 16)
    angles_hold = np.array([74.0] * 3)
    angles_bwd = np.linspace(74.0, 16.0, 12)
    angles_hold2 = np.array([16.0] * 2)
    angles = np.concatenate([angles_fwd, angles_hold, angles_bwd, angles_hold2])

    frames = []

    # Grid
    x1 = np.linspace(0, 4.5, 45)
    x2 = np.linspace(0, 4.5, 45)
    X1, X2 = np.meshgrid(x1, x2)

    # Corner is at (2, 2)
    # Wall 1 normal is (1, 2) => angle is arctan(2/1) = 63.435 deg
    # Wall 2 normal is (2, 1) => angle is arctan(1/2) = 26.565 deg
    ang_w2 = np.degrees(np.arctan2(1.0, 2.0))
    ang_w1 = np.degrees(np.arctan2(2.0, 1.0))

    R_summit = 2.4

    for idx, deg in enumerate(angles):
        rad = np.radians(deg)
        x0 = 2.0 + R_summit * np.cos(rad)
        y0 = 2.0 + R_summit * np.sin(rad)
        Z = -(X1 - x0)**2 - (X2 - y0)**2 + 25.0

        fig = plt.figure(figsize=(14.5, 6.5), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        # ----------------------------------------------------------------------
        # Left Panel: 3D Corner Walls Meeting at (2, 2)
        # ----------------------------------------------------------------------
        ax1 = fig.add_subplot(1, 2, 1, projection='3d')
        ax1.set_facecolor(BG_COLOR)

        # Feasible mask: X1 + 2*X2 <= 6 and 2*X1 + X2 <= 6
        mask_feas = (X1 + 2.0*X2 <= 6.0) & (2.0*X1 + X2 <= 6.0)
        Z_feas = np.where(mask_feas, Z, np.nan)
        Z_infeas = np.where(~mask_feas, Z, np.nan)

        ax1.plot_surface(X1, X2, Z_feas, cmap="viridis", alpha=0.82, edgecolor='none', zorder=2)
        ax1.plot_wireframe(X1, X2, Z_infeas, color="#a8a29e", alpha=0.22, lw=0.6, zorder=1)

        # Wall 1: X1 + 2*X2 = 6 from (0, 3) to (2, 2)
        w1_x = np.linspace(0, 2, 20)
        w1_y = (6.0 - w1_x) / 2.0
        w1_z_top = -(w1_x - x0)**2 - (w1_y - y0)**2 + 25.0
        w1_z_bot = np.zeros_like(w1_x)

        wall1_verts = []
        for i in range(len(w1_x) - 1):
            poly = [
                [w1_x[i], w1_y[i], w1_z_bot[i]],
                [w1_x[i+1], w1_y[i+1], w1_z_bot[i+1]],
                [w1_x[i+1], w1_y[i+1], w1_z_top[i+1]],
                [w1_x[i], w1_y[i], w1_z_top[i]]
            ]
            wall1_verts.append(poly)
        wall1_coll = Poly3DCollection(wall1_verts, facecolors=RED_COLOR, alpha=0.45, edgecolors='#962d22', lw=0.5, zorder=4)
        ax1.add_collection3d(wall1_coll)
        ax1.plot(w1_x, w1_y, w1_z_top, color=RED_COLOR, lw=2.8, zorder=5)

        # Wall 2: 2*X1 + X2 = 6 from (2, 2) to (3, 0)
        w2_x = np.linspace(2, 3, 20)
        w2_y = 6.0 - 2.0 * w2_x
        w2_z_top = -(w2_x - x0)**2 - (w2_y - y0)**2 + 25.0
        w2_z_bot = np.zeros_like(w2_x)

        wall2_verts = []
        for i in range(len(w2_x) - 1):
            poly = [
                [w2_x[i], w2_y[i], w2_z_bot[i]],
                [w2_x[i+1], w2_y[i+1], w2_z_bot[i+1]],
                [w2_x[i+1], w2_y[i+1], w2_z_top[i+1]],
                [w2_x[i], w2_y[i], w2_z_top[i]]
            ]
            wall2_verts.append(poly)
        wall2_coll = Poly3DCollection(wall2_verts, facecolors=TEAL_COLOR, alpha=0.45, edgecolors='#065f69', lw=0.5, zorder=4)
        ax1.add_collection3d(wall2_coll)
        ax1.plot(w2_x, w2_y, w2_z_top, color=TEAL_COLOR, lw=2.8, zorder=5)

        # Optimum determination
        # When deg < ang_w2: face 2 is optimal
        # When deg > ang_w1: face 1 is optimal
        # When ang_w2 <= deg <= ang_w1: corner (2, 2) is optimal
        if deg < ang_w2:
            # Face 2: 2*x1 + x2 = 6
            # Maximize -(x1 - x0)^2 - (6 - 2*x1 - y0)^2
            # Derivative: -2(x1 - x0) + 4(6 - 2*x1 - y0) = 0 => -10*x1 + 2*x0 + 24 - 4*y0 = 0
            opt_x1 = np.clip((2.0 * x0 - 4.0 * y0 + 24.0) / 10.0, 2.0, 3.0)
            opt_x2 = 6.0 - 2.0 * opt_x1
            mu1 = 0.0
            # multiplier on wall 2: \nabla f = mu2 * (2, 1)
            grad_x = 2.0 * (x0 - opt_x1)
            mu2 = grad_x / 2.0
            slack1 = 6.0 - (opt_x1 + 2.0 * opt_x2)
            slack2 = 0.0
            state_title = "제약벽 2면 최적 (벽 1 슬랙)"
        elif deg > ang_w1:
            # Face 1: x1 + 2*x2 = 6
            # Maximize -(6 - 2*x2 - x0)^2 - (x2 - y0)^2
            # Derivative: 4(6 - 2*x2 - x0) - 2(x2 - y0) = 0 => -10*x2 + 24 - 4*x0 + 2*y0 = 0
            opt_x2 = np.clip((24.0 - 4.0 * x0 + 2.0 * y0) / 10.0, 2.0, 3.0)
            opt_x1 = 6.0 - 2.0 * opt_x2
            # multiplier on wall 1: \nabla f = mu1 * (1, 2)
            grad_x = 2.0 * (x0 - opt_x1)
            mu1 = grad_x
            mu2 = 0.0
            slack1 = 0.0
            slack2 = 6.0 - (2.0 * opt_x1 + opt_x2)
            state_title = "제약벽 1면 최적 (벽 2 슬랙)"
        else:
            opt_x1 = 2.0
            opt_x2 = 2.0
            grad = np.array([2.0 * (x0 - 2.0), 2.0 * (y0 - 2.0)])
            mu1 = (2.0 * grad[1] - grad[0]) / 3.0
            mu2 = (2.0 * grad[0] - grad[1]) / 3.0
            slack1 = 0.0
            slack2 = 0.0
            state_title = "코너해: 두 제약벽 교차 모서리 (동시 바인딩)"

        opt_z = -(opt_x1 - x0)**2 - (opt_x2 - y0)**2 + 25.0

        # Optimum point marker
        ax1.scatter([opt_x1], [opt_x2], [opt_z], color=GOLD_COLOR, s=150, edgecolor='black', lw=1.8, zorder=10)

        # Summit marker
        ax1.scatter([x0], [y0], [25.0], color=GOLD_COLOR, s=160, marker='*', edgecolor='black', lw=1.8, zorder=9)

        # Arrow from optimum to summit
        ax1.quiver(opt_x1, opt_x2, opt_z, (x0 - opt_x1) * 0.45, (y0 - opt_x2) * 0.45, (25.0 - opt_z) * 0.45,
                   color=BLUE_COLOR, lw=3.2, arrow_length_ratio=0.25, zorder=11)

        ax1.set_xlim(0, 4.5)
        ax1.set_ylim(0, 4.5)
        ax1.set_zlim(0, 28.0)
        ax1.set_xlabel(r'$x_1$', fontsize=9.5)
        ax1.set_ylabel(r'$x_2$', fontsize=9.5)
        ax1.set_zlabel('고도 $f(x)$', fontsize=9.5)
        ax1.view_init(elev=32, azim=-50)
        ax1.set_title(f"[3D 코너해] {state_title}\n산 정상 각도 = {deg:.1f}°", fontsize=11, fontweight='bold', color=INK_COLOR)

        # ----------------------------------------------------------------------
        # Right Panel: Multipliers & Slacks Dashboard
        # ----------------------------------------------------------------------
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.set_facecolor(BG_COLOR)
        ax2.grid(True, linestyle="--", alpha=0.55, color=GRID_COLOR, axis='x')

        bars = ax2.barh([3, 2, 1, 0], [mu1, mu2, slack1, slack2],
                        height=0.45, color=[RED_COLOR, TEAL_COLOR, RED_COLOR, TEAL_COLOR],
                        edgecolor=INK_COLOR, lw=1.2)
        for bar, a in zip(bars, [0.9, 0.9, 0.35, 0.35]):
            bar.set_alpha(a)
        ax2.set_yticks([3, 2, 1, 0])
        ax2.set_yticklabels([
            r"제약벽 1 승수 $\mu_1^*$",
            r"제약벽 2 승수 $\mu_2^*$",
            r"제약벽 1 여유 $s_1$",
            r"제약벽 2 여유 $s_2$"
        ], fontsize=10, fontweight='bold', color=INK_COLOR)
        ax2.set_xlim(0, 3.2)
        ax2.set_xlabel("값 (승수 = 벽 완화 한계가치 / 여유도 = 남은 자원)", fontsize=9.5, color=INK_COLOR)
        ax2.set_title("각 제약벽의 한계 기여도와 상보여유성 대시보드", fontsize=11, fontweight='bold', color=INK_COLOR)

        # Text on bars
        ax2.text(mu1 + 0.08, 3, f"{mu1:.2f} (벽 1 그림자 가격)", va='center', fontsize=9.5, fontweight='bold', color=RED_COLOR)
        ax2.text(mu2 + 0.08, 2, f"{mu2:.2f} (벽 2 그림자 가격)", va='center', fontsize=9.5, fontweight='bold', color=TEAL_COLOR)
        ax2.text(slack1 + 0.08, 1, f"{slack1:.2f} ({'바인딩' if slack1 < 0.01 else '슬랙'})", va='center', fontsize=9.5, fontweight='bold', color=RED_COLOR)
        ax2.text(slack2 + 0.08, 0, f"{slack2:.2f} ({'바인딩' if slack2 < 0.01 else '슬랙'})", va='center', fontsize=9.5, fontweight='bold', color=TEAL_COLOR)

        msg = (
            "★ 3D 코너해의 직관:\n"
            "· 두 제약벽이 만나는 모서리 꼭짓점에 걸려 있을 때,\n"
            "  제약벽 1을 1m 밀면 올라가는 고도 = μ₁*\n"
            "  제약벽 2를 1m 밀면 올라가는 고도 = μ₂*\n"
            "· 상보여유성 검증: 여유가 있는 벽은 가치가 0 (μ* · s = 0)\n"
            "→ 두 승수는 각 자원이 나의 목표를 얼마나 강하게\n"
            "  가로막고 있는가(병목 강도)를 정확히 분해합니다."
        )
        ax2.text(0.04, 0.44, msg, transform=ax2.transAxes, fontsize=9.5, fontweight="bold", color=INK_COLOR,
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor=GOLD_COLOR, lw=1.5))

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    gif_path = os.path.join(GIF_DIR, "kkt-corner-slackness-cone.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=130, loop=0, optimize=True)
    print(f"3D GIF 2 generated: {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_multiplier_shadow_price()
    generate_gif_corner_slackness_cone()
    print("All 3D KKT Multiplier GIFs generated successfully!")
