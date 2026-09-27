import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# Use formal, publication-ready font settings
plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = "assets/gif"
SCRATCH_DIR = "scratch/topology_frames"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)


def generate_sequence_closedness_gif():
    print("Generating Animation 1: Sequential Closedness in R^2...")
    frames_dir = os.path.join(SCRATCH_DIR, "seq_closedness")
    os.makedirs(frames_dir, exist_ok=True)

    n_steps = 20
    n_closure_hold = 8
    total_frames = n_steps + n_closure_hold

    # Sequence directions on R^2:
    # 1. East: (1, 0)
    # 2. North: (0, 1)
    # 3. North-East: (1/sqrt(2), 1/sqrt(2))
    # 4. North-West: (-1/sqrt(2), 1/sqrt(2))
    targets = [
        np.array([1.0, 0.0]),
        np.array([0.0, 1.0]),
        np.array([1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]),
        np.array([-1.0 / np.sqrt(2), 1.0 / np.sqrt(2)]),
    ]
    starts = [
        np.array([0.15, 0.0]),
        np.array([0.0, 0.15]),
        np.array([0.1, 0.1]),
        np.array([-0.1, 0.1]),
    ]
    seq_colors = ['#2563EB', '#D97706', '#7C3AED', '#0D9488']
    seq_names = [
        r'$z_k^{(1)} \to (1, 0)$',
        r'$z_k^{(2)} \to (0, 1)$',
        r'$z_k^{(3)} \to (1/\sqrt{2}, 1/\sqrt{2})$',
        r'$z_k^{(4)} \to (-1/\sqrt{2}, 1/\sqrt{2})$'
    ]

    frame_paths = []
    theta = np.linspace(0, 2 * np.pi, 200)
    circle_x = np.cos(theta)
    circle_y = np.sin(theta)

    for frame_idx in range(total_frames):
        k_step = min(frame_idx + 1, n_steps)
        is_closure_applied = frame_idx >= n_steps

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.2, 7.2), dpi=100)
        fig.patch.set_facecolor('#FAFAFA')

        # ----------------------------------------------------
        # Left Panel: Non-Closed Set vs Closure Operation
        # ----------------------------------------------------
        ax1.set_facecolor('#FFFFFF')
        ax1.set_xlim(-1.45, 1.45)
        ax1.set_ylim(-1.45, 1.45)
        ax1.set_aspect('equal')
        ax1.grid(True, linestyle=':', color='#E2E8F0', alpha=0.7)
        ax1.axhline(0, color='#94A3B8', linewidth=0.8, alpha=0.5)
        ax1.axvline(0, color='#94A3B8', linewidth=0.8, alpha=0.5)

        # Draw set region
        if not is_closure_applied:
            # Open disk: light amber/red fill, dashed red boundary
            ax1.fill(circle_x, circle_y, color='#FEF2F2', alpha=0.85, zorder=1)
            ax1.plot(circle_x, circle_y, linestyle='--', color='#DC2626', linewidth=2.4, zorder=2)
            title_text = "비폐집합 (Non-Closed Set)\n" r"$E = \{(x, y) \in \mathbb{R}^2 : x^2 + y^2 < 1\}$"
            subtitle_text = "경계 제외 (점선) : 수열의 극한이 집합 외부로 이탈"
            title_color = '#991B1B'
            bd_status = "경계점 미포함 (점선: x^2 + y^2 = 1 제외)"
        else:
            # Closure applied: emerald fill, solid emerald boundary
            ax1.fill(circle_x, circle_y, color='#ECFDF5', alpha=0.9, zorder=1)
            ax1.plot(circle_x, circle_y, linestyle='-', color='#059669', linewidth=2.6, zorder=2)
            title_text = "폐포 연산 적용 (Closure Operation)\n" r"$\overline{E} = E \cup E' = \{(x, y) \in \mathbb{R}^2 : x^2 + y^2 \leq 1\}$"
            subtitle_text = "도집합 E'을 합집합하여 모든 극한점을 집합 내로 포섭"
            title_color = '#065F46'
            bd_status = "경계점 포함 (실선: x^2 + y^2 = 1 포함)"

        ax1.set_title(title_text, fontsize=13, fontweight='bold', color=title_color, pad=12)

        # Plot sequences on Left Panel
        for i in range(len(targets)):
            target = targets[i]
            start = starts[i]
            color = seq_colors[i]

            # Sequence positions up to k_step
            # factor = 1 - 1/(k+1)
            t_factors = [1.0 - 1.0 / (step + 1.2) for step in range(1, k_step + 1)]
            pts = np.array([start + factor * (target - start) for factor in t_factors])

            # Trajectory line
            ax1.plot(pts[:, 0], pts[:, 1], color=color, linewidth=1.5, alpha=0.5, zorder=3)
            # Past points
            if len(pts) > 1:
                ax1.scatter(pts[:-1, 0], pts[:-1, 1], s=24, color=color, alpha=0.45, zorder=4)
            # Current point
            curr_pt = pts[-1]
            ax1.scatter([curr_pt[0]], [curr_pt[1]], s=75, color=color, edgecolor='#0F172A', linewidth=1.2, zorder=5)

            # Limit target marker
            if not is_closure_applied:
                # Target is NOT in E: hollow circle with red cross
                ax1.scatter([target[0]], [target[1]], s=110, facecolor='none', edgecolor='#DC2626', linewidth=2.0, zorder=6)
                ax1.plot([target[0] - 0.04, target[0] + 0.04], [target[1] - 0.04, target[1] + 0.04], color='#DC2626', linewidth=1.8, zorder=7)
                ax1.plot([target[0] - 0.04, target[0] + 0.04], [target[1] + 0.04, target[1] - 0.04], color='#DC2626', linewidth=1.8, zorder=7)
            else:
                # Target IS in closure: solid green marker
                ax1.scatter([target[0]], [target[1]], s=110, facecolor='#10B981', edgecolor='#065F46', linewidth=1.8, zorder=6)

        # Left Info Box
        if not is_closure_applied:
            info_text = (
                f"수열 진행 단계: k = {k_step}\n"
                f"• {bd_status}\n"
                r"• $\forall k \in \mathbb{N}, \; z_k \in E$ (수열 원소는 집합 내부)" "\n"
                r"• $\lim_{k \to \infty} z_k = z^* \notin E$ (극한점은 집합 외부)" "\n"
                r"• 극한점 미포함: $z^* \in E'$ 이나 $z^* \notin E \;\Rightarrow\; E \neq \overline{E}$"
            )
            box_edge = '#DC2626'
            box_face = '#FFF1F2'
        else:
            info_text = (
                f"폐포화 완료 (수열 극한 포섭)\n"
                f"• {bd_status}\n"
                r"• $E' = \{x^2 + y^2 \leq 1\}$ (도집합: 모든 극한점의 집합)" "\n"
                r"• $\overline{E} = E \cup E'$ (도집합을 추가하여 닫힌집합 완성)" "\n"
                r"• $\lim_{k \to \infty} z_k = z^* \in \overline{E}$ [수열 극한에 대해 닫힘]"
            )
            box_edge = '#059669'
            box_face = '#ECFDF5'

        ax1.text(0.03, 0.04, info_text, transform=ax1.transAxes, fontsize=9.5,
                 verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.6', facecolor=box_face, edgecolor=box_edge, linewidth=1.3),
                 zorder=10)

        # ----------------------------------------------------
        # Right Panel: Closed Set (Benchmark)
        # ----------------------------------------------------
        ax2.set_facecolor('#FFFFFF')
        ax2.set_xlim(-1.45, 1.45)
        ax2.set_ylim(-1.45, 1.45)
        ax2.set_aspect('equal')
        ax2.grid(True, linestyle=':', color='#E2E8F0', alpha=0.7)
        ax2.axhline(0, color='#94A3B8', linewidth=0.8, alpha=0.5)
        ax2.axvline(0, color='#94A3B8', linewidth=0.8, alpha=0.5)

        # Draw closed set: solid emerald boundary, light emerald fill
        ax2.fill(circle_x, circle_y, color='#F0FDF4', alpha=0.85, zorder=1)
        ax2.plot(circle_x, circle_y, linestyle='-', color='#16A34A', linewidth=2.6, zorder=2)

        ax2.set_title("닫힌집합 (Closed Set)\n" r"$F = \{(x, y) \in \mathbb{R}^2 : x^2 + y^2 \leq 1\}$",
                      fontsize=13, fontweight='bold', color='#166534', pad=12)

        # Plot identical sequences on Right Panel
        for i in range(len(targets)):
            target = targets[i]
            start = starts[i]
            color = seq_colors[i]

            t_factors = [1.0 - 1.0 / (step + 1.2) for step in range(1, k_step + 1)]
            pts = np.array([start + factor * (target - start) for factor in t_factors])

            ax2.plot(pts[:, 0], pts[:, 1], color=color, linewidth=1.5, alpha=0.5, zorder=3)
            if len(pts) > 1:
                ax2.scatter(pts[:-1, 0], pts[:-1, 1], s=24, color=color, alpha=0.45, zorder=4)

            curr_pt = pts[-1]
            ax2.scatter([curr_pt[0]], [curr_pt[1]], s=75, color=color, edgecolor='#0F172A', linewidth=1.2, zorder=5)

            # Target point is in F: solid check dot
            ax2.scatter([target[0]], [target[1]], s=110, facecolor='#22C55E', edgecolor='#15803D', linewidth=1.8, zorder=6)

        # Right Info Box
        right_info_text = (
            f"수열 진행 단계: k = {k_step}\n"
            "• 경계점 포함 (실선: x^2 + y^2 = 1 포함)\n"
            r"• $\forall k \in \mathbb{N}, \; z_k \in F$ (수열 원소는 집합 내부)" "\n"
            r"• $\lim_{k \to \infty} z_k = z^* \in F$ (극한점도 집합 내부 보존)" "\n"
            r"• $F' \subseteq F \;\Leftrightarrow\; F = \overline{F}$ [닫힌집합 / Closed Set]"
        )
        ax2.text(0.03, 0.04, right_info_text, transform=ax2.transAxes, fontsize=9.5,
                 verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.6', facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=1.3),
                 zorder=10)

        plt.tight_layout()
        frame_path = os.path.join(frames_dir, f"frame_{frame_idx:03d}.png")
        plt.savefig(frame_path, dpi=100)
        plt.close(fig)
        frame_paths.append(frame_path)

    # Compile GIF
    images = [Image.open(p) for p in frame_paths]
    durations = [280] * (n_steps - 1) + [900] + [350] * (n_closure_hold - 1) + [1800]
    output_gif_path = os.path.join(OUTPUT_DIR, "topology-2d-sequences-closedness.gif")
    images[0].save(
        output_gif_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Animation 1 saved: {output_gif_path} ({os.path.getsize(output_gif_path):,} bytes)")


def generate_budget_weierstrass_gif():
    print("Generating Animation 2: Economic Choice & Weierstrass Extreme Value Theorem in R^2...")
    frames_dir = os.path.join(SCRATCH_DIR, "budget_weierstrass")
    os.makedirs(frames_dir, exist_ok=True)

    n_steps = 22
    total_frames = n_steps + 6

    # Model parameters:
    # Commodity space R_+^2
    # Utility u(x1, x2) = (x1 * x2)^(1/2)
    # Budget: p1*x1 + p2*x2 <= w with p1=1, p2=1, w=4
    # Tangency optimum x* = (2, 2), u(x*) = 2
    # Consumption sequence: x^{(k)} = (1 - 1/(k+1)) * (2, 2)
    x_star = np.array([2.0, 2.0])
    u_star = 2.0

    # Grid for indifference curves
    x1_grid = np.linspace(0.1, 4.4, 250)
    x2_grid = np.linspace(0.1, 4.4, 250)
    X1, X2 = np.meshgrid(x1_grid, x2_grid)
    U = np.sqrt(np.maximum(X1 * X2, 0.0))

    frame_paths = []

    for frame_idx in range(total_frames):
        k = min(frame_idx + 1, n_steps)
        t_factor = 1.0 - 1.0 / (k + 1.2)
        curr_x = t_factor * x_star
        curr_u = np.sqrt(curr_x[0] * curr_x[1])
        curr_cost = curr_x[0] + curr_x[1]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.2, 7.2), dpi=100)
        fig.patch.set_facecolor('#FAFAFA')

        # ----------------------------------------------------
        # Left Panel: Open Budget Set B_open
        # ----------------------------------------------------
        ax1.set_facecolor('#FFFFFF')
        ax1.set_xlim(-0.2, 4.8)
        ax1.set_ylim(-0.2, 4.8)
        ax1.set_aspect('equal')
        ax1.grid(True, linestyle=':', color='#E2E8F0', alpha=0.7)
        ax1.axhline(0, color='#64748B', linewidth=1.2)
        ax1.axvline(0, color='#64748B', linewidth=1.2)
        ax1.set_xlabel(r'재화 1 소비량 ($x_1$)', fontsize=11, fontweight='bold', labelpad=6)
        ax1.set_ylabel(r'재화 2 소비량 ($x_2$)', fontsize=11, fontweight='bold', labelpad=6)

        # Fill open budget region: vertices (0,0), (4,0), (0,4)
        ax1.fill([0, 4, 0], [0, 0, 4], color='#FFFBEB', alpha=0.85, zorder=1)
        # Budget line p·x = 4 excluded: dashed red line
        ax1.plot([0, 4], [4, 0], linestyle='--', color='#DC2626', linewidth=2.5, zorder=3, label=r'예산선 $x_1 + x_2 = 4$ (제외)')

        # Indifference curve at current consumption bundle
        cs1 = ax1.contour(X1, X2, U, levels=[curr_u], colors=['#F59E0B'], linewidths=[1.8], linestyles=['-'], zorder=4)
        # Target optimal indifference curve u = 2
        ax1.contour(X1, X2, U, levels=[u_star], colors=['#DC2626'], linewidths=[1.8], linestyles=[':'], zorder=4)

        # Plot consumption sequence history
        k_hist = np.array([1.0 - 1.0 / (s + 1.2) for s in range(1, k + 1)])
        pts_hist = np.outer(k_hist, x_star)
        ax1.plot(pts_hist[:, 0], pts_hist[:, 1], color='#D97706', linewidth=1.5, alpha=0.6, zorder=5)
        if len(pts_hist) > 1:
            ax1.scatter(pts_hist[:-1, 0], pts_hist[:-1, 1], s=26, color='#D97706', alpha=0.45, zorder=6)

        # Current bundle
        ax1.scatter([curr_x[0]], [curr_x[1]], s=85, color='#D97706', edgecolor='#0F172A', linewidth=1.2, zorder=7)
        ax1.text(curr_x[0] - 0.22, curr_x[1] + 0.16, rf'$x^{{({k})}}$', fontsize=10, fontweight='bold', color='#B45309', zorder=8)

        # Target optimum marker: hollow circle with cross (escaped from open budget set)
        ax1.scatter([x_star[0]], [x_star[1]], s=130, facecolor='none', edgecolor='#DC2626', linewidth=2.2, zorder=9)
        ax1.plot([x_star[0] - 0.08, x_star[0] + 0.08], [x_star[1] - 0.08, x_star[1] + 0.08], color='#DC2626', linewidth=2.0, zorder=10)
        ax1.plot([x_star[0] - 0.08, x_star[0] + 0.08], [x_star[1] + 0.08, x_star[1] - 0.08], color='#DC2626', linewidth=2.0, zorder=10)
        ax1.text(x_star[0] + 0.16, x_star[1] + 0.16, r'$x^*=(2, 2) \notin B_{\mathrm{open}}$', fontsize=10, fontweight='bold', color='#DC2626', zorder=11)

        ax1.set_title("열린 예산집합 (비폐집합)\n" r"$B_{\mathrm{open}} = \{(x_1, x_2) \in \mathbb{R}_+^2 : x_1 + x_2 < 4\}$",
                      fontsize=12.5, fontweight='bold', color='#991B1B', pad=12)

        info_left = (
            f"소비 수열 단계: k = {k}\n"
            f"• 소비점: x^({k}) = ({curr_x[0]:.2f}, {curr_x[1]:.2f}) ∈ B_open\n"
            f"• 지출액: p·x = {curr_cost:.2f} < 4.00 (예산 한도 내부)\n"
            f"• 효용 수준: u(x^({k})) = {curr_u:.3f} → sup = 2.000\n"
            r"• $\lim_{k \to \infty} x^{(k)} = (2, 2) \notin B_{\mathrm{open}}$ [경계 이탈]" "\n"
            r"• $\mathrm{argmax}_{x \in B_{\mathrm{open}}} u(x) = \emptyset$ (극대원 부존재!)" "\n"
            "※ 사유: 실행가능집합의 비닫힘성(바이어슈트라스 정리 실패)"
        )
        ax1.text(0.04, 0.04, info_left, transform=ax1.transAxes, fontsize=9.2,
                 verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.6', facecolor='#FEF2F2', edgecolor='#DC2626', linewidth=1.3),
                 zorder=12)

        # ----------------------------------------------------
        # Right Panel: Closed Budget Set B_closed
        # ----------------------------------------------------
        ax2.set_facecolor('#FFFFFF')
        ax2.set_xlim(-0.2, 4.8)
        ax2.set_ylim(-0.2, 4.8)
        ax2.set_aspect('equal')
        ax2.grid(True, linestyle=':', color='#E2E8F0', alpha=0.7)
        ax2.axhline(0, color='#64748B', linewidth=1.2)
        ax2.axvline(0, color='#64748B', linewidth=1.2)
        ax2.set_xlabel(r'재화 1 소비량 ($x_1$)', fontsize=11, fontweight='bold', labelpad=6)
        ax2.set_ylabel(r'재화 2 소비량 ($x_2$)', fontsize=11, fontweight='bold', labelpad=6)

        # Fill closed budget region: vertices (0,0), (4,0), (0,4)
        ax2.fill([0, 4, 0], [0, 0, 4], color='#F0FDF4', alpha=0.85, zorder=1)
        # Budget line p·x = 4 included: solid navy line
        ax2.plot([0, 4], [4, 0], linestyle='-', color='#16A34A', linewidth=2.8, zorder=3, label=r'예산선 $x_1 + x_2 = 4$ (포함)')

        # Indifference curve at current consumption bundle
        ax2.contour(X1, X2, U, levels=[curr_u], colors=['#059669'], linewidths=[1.8], linestyles=['-'], zorder=4)
        # Optimal indifference curve u = 2
        ax2.contour(X1, X2, U, levels=[u_star], colors=['#15803D'], linewidths=[2.0], linestyles=['-'], zorder=4)

        # Plot consumption sequence history
        ax2.plot(pts_hist[:, 0], pts_hist[:, 1], color='#047857', linewidth=1.5, alpha=0.6, zorder=5)
        if len(pts_hist) > 1:
            ax2.scatter(pts_hist[:-1, 0], pts_hist[:-1, 1], s=26, color='#047857', alpha=0.45, zorder=6)

        # Current bundle
        ax2.scatter([curr_x[0]], [curr_x[1]], s=85, color='#047857', edgecolor='#0F172A', linewidth=1.2, zorder=7)
        ax2.text(curr_x[0] - 0.22, curr_x[1] + 0.16, rf'$x^{{({k})}}$', fontsize=10, fontweight='bold', color='#047857', zorder=8)

        # Target optimum marker: solid green dot with checkmark label
        ax2.scatter([x_star[0]], [x_star[1]], s=130, facecolor='#22C55E', edgecolor='#15803D', linewidth=2.2, zorder=9)
        ax2.text(x_star[0] + 0.16, x_star[1] + 0.16, r'$x^*=(2, 2) \in B_{\mathrm{closed}}$ (최적해)', fontsize=10, fontweight='bold', color='#15803D', zorder=11)

        ax2.set_title("닫힌 예산집합 (유계 닫힌집합 = 콤팩트)\n" r"$B_{\mathrm{closed}} = \{(x_1, x_2) \in \mathbb{R}_+^2 : x_1 + x_2 \leq 4\}$",
                      fontsize=12.5, fontweight='bold', color='#166534', pad=12)

        info_right = (
            f"소비 수열 단계: k = {k}\n"
            f"• 소비점: x^({k}) = ({curr_x[0]:.2f}, {curr_x[1]:.2f}) ∈ B_closed\n"
            f"• 지출액: p·x = {curr_cost:.2f} ≤ 4.00 (예산 한도 내부)\n"
            f"• 효용 수준: u(x^({k})) = {curr_u:.3f} → max = 2.000\n"
            r"• $\lim_{k \to \infty} x^{(k)} = (2, 2) \in B_{\mathrm{closed}}$ [경계 접점 안착]" "\n"
            r"• $\mathrm{argmax}_{x \in B_{\mathrm{closed}}} u(x) = \{(2, 2)\}$ (최댓값 존재 보장!)" "\n"
            "※ 근거: 바이어슈트라스 극값정리 (연속함수 + 유계닫힌집합)"
        )
        ax2.text(0.04, 0.04, info_right, transform=ax2.transAxes, fontsize=9.2,
                 verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.6', facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=1.3),
                 zorder=12)

        plt.tight_layout()
        frame_path = os.path.join(frames_dir, f"frame_{frame_idx:03d}.png")
        plt.savefig(frame_path, dpi=100)
        plt.close(fig)
        frame_paths.append(frame_path)

    # Compile GIF
    images = [Image.open(p) for p in frame_paths]
    durations = [280] * (n_steps - 1) + [1800] * (total_frames - n_steps + 1)
    output_gif_path = os.path.join(OUTPUT_DIR, "topology-2d-budget-weierstrass.gif")
    images[0].save(
        output_gif_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Animation 2 saved: {output_gif_path} ({os.path.getsize(output_gif_path):,} bytes)")


if __name__ == "__main__":
    generate_sequence_closedness_gif()
    generate_budget_weierstrass_gif()
    print("All GIFs generated successfully!")
