import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

# Use formal, publication-ready font settings
plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = "assets/gif"
SCRATCH_DIR = os.path.join(
    r"C:\Users\ohj40\.gemini\antigravity\brain\d1db846a-c35b-4cd1-90bf-879be5872011\scratch",
    "topology_frames"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SCRATCH_DIR, exist_ok=True)


def generate_sequence_closedness_gif():
    print("Generating Animation 1: Sequential Closedness in R^2 (High FPS & Ample Headroom)...")
    frames_dir = os.path.join(SCRATCH_DIR, "seq_closedness")
    os.makedirs(frames_dir, exist_ok=True)

    n_motion = 50       # Smooth motion frames (50 frames)
    n_pre_hold = 12     # Pause at boundary before closure (12 frames)
    n_transition = 10   # Smooth transition to closure (10 frames)
    n_post_hold = 1     # Single long hold frame at the end
    total_frames = n_motion + n_pre_hold + n_transition + n_post_hold

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

    theta = np.linspace(0, 2 * np.pi, 250)
    circle_x = np.cos(theta)
    circle_y = np.sin(theta)

    frame_paths = []
    durations = []

    for frame_idx in range(total_frames):
        # Determine animation phase
        if frame_idx < n_motion:
            # Motion phase
            progress = frame_idx / (n_motion - 1)
            # Smooth diminishing factor approaching boundary: 0.15 -> 0.97
            s_factor = 0.15 + 0.82 * (1.0 - np.exp(-3.5 * progress)) / (1.0 - np.exp(-3.5))
            k_display = int(progress * 25) + 1
            closure_alpha = 0.0
            frame_duration = 55
        elif frame_idx < n_motion + n_pre_hold:
            # Pre-closure hold: show boundary arrival and failure of closedness
            s_factor = 0.97
            k_display = 25
            closure_alpha = 0.0
            frame_duration = 75
        elif frame_idx < n_motion + n_pre_hold + n_transition:
            # Transition phase: closure operation taking place smoothly
            trans_idx = frame_idx - (n_motion + n_pre_hold)
            closure_alpha = (trans_idx + 1) / n_transition
            s_factor = 0.97
            k_display = 25
            frame_duration = 80
        else:
            # Post-closure hold
            closure_alpha = 1.0
            s_factor = 0.97
            k_display = 25
            frame_duration = 2600  # 2.6 second final hold

        durations.append(frame_duration)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 7.8), dpi=100)
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
        ax1.set_xlabel(r'$x$ 좌표', fontsize=11, fontweight='bold', labelpad=6)
        ax1.set_ylabel(r'$y$ 좌표', fontsize=11, fontweight='bold', labelpad=6)

        if closure_alpha == 0.0:
            # Pure open disk
            ax1.fill(circle_x, circle_y, color='#FEF2F2', alpha=0.85, zorder=1)
            ax1.plot(circle_x, circle_y, linestyle='--', color='#DC2626', linewidth=2.4, zorder=2)
            title_text = "비폐집합 (Non-Closed Set)\n" r"$E = \{(x, y) \in \mathbb{R}^2 : x^2 + y^2 < 1\}$"
            title_color = '#991B1B'
        elif closure_alpha < 1.0:
            # Transitioning
            ax1.fill(circle_x, circle_y, color='#FEF2F2', alpha=0.85 * (1 - closure_alpha), zorder=1)
            ax1.fill(circle_x, circle_y, color='#ECFDF5', alpha=0.90 * closure_alpha, zorder=1)
            ax1.plot(circle_x, circle_y, linestyle='--', color='#DC2626', linewidth=2.4 * (1 - closure_alpha), alpha=1 - closure_alpha, zorder=2)
            ax1.plot(circle_x, circle_y, linestyle='-', color='#059669', linewidth=2.6 * closure_alpha, alpha=closure_alpha, zorder=2)
            title_text = "폐포 연산 진행 중...\n" r"$\overline{E} = E \cup E'$"
            title_color = '#0D9488'
        else:
            # Closure fully applied
            ax1.fill(circle_x, circle_y, color='#ECFDF5', alpha=0.9, zorder=1)
            ax1.plot(circle_x, circle_y, linestyle='-', color='#059669', linewidth=2.6, zorder=2)
            title_text = "폐포 연산 적용 (Closure Operation)\n" r"$\overline{E} = E \cup E' = \{(x, y) \in \mathbb{R}^2 : x^2 + y^2 \leq 1\}$"
            title_color = '#065F46'

        ax1.set_title(title_text, fontsize=12.5, fontweight='bold', color=title_color, pad=14)

        # Plot sequences on Left Panel
        for i in range(len(targets)):
            target = targets[i]
            start = starts[i]
            color = seq_colors[i]

            # Generate trail of points
            trail_steps = max(2, int(k_display))
            t_factors = [0.15 + (s_factor - 0.15) * (step / trail_steps) for step in range(trail_steps)]
            pts = np.array([start + factor * (target - start) for factor in t_factors])

            ax1.plot(pts[:, 0], pts[:, 1], color=color, linewidth=1.5, alpha=0.5, zorder=3)
            if len(pts) > 1:
                ax1.scatter(pts[:-1, 0], pts[:-1, 1], s=22, color=color, alpha=0.45, zorder=4)

            curr_pt = pts[-1]
            ax1.scatter([curr_pt[0]], [curr_pt[1]], s=75, color=color, edgecolor='#0F172A', linewidth=1.2, zorder=5)

            # Target marker behavior on Left Panel:
            if closure_alpha < 0.5:
                # Target is outside E: red hollow circle with cross
                ax1.scatter([target[0]], [target[1]], s=110, facecolor='none', edgecolor='#DC2626', linewidth=2.0, zorder=6)
                ax1.plot([target[0] - 0.05, target[0] + 0.05], [target[1] - 0.05, target[1] + 0.05], color='#DC2626', linewidth=1.8, zorder=7)
                ax1.plot([target[0] - 0.05, target[0] + 0.05], [target[1] + 0.05, target[1] - 0.05], color='#DC2626', linewidth=1.8, zorder=7)
            else:
                # Target is included in closure: solid green circle
                ax1.scatter([target[0]], [target[1]], s=110, facecolor='#22C55E', edgecolor='#15803D', linewidth=2.0, zorder=6)

        # Info Box Left
        if closure_alpha < 0.5:
            info_text_left = (
                f"수열 진행 단계: k = {k_display}\n"
                "• 경계점 미포함 (점선: x^2 + y^2 = 1 제외)\n"
                r"• $\forall k \in \mathbb{N}, \; z_k \in E$ (수열 원소는 집합 내부)" "\n"
                r"• $\lim_{k \to \infty} z_k = z^* \notin E$ (극한점은 집합 외부)" "\n"
                r"• 극한점 미포함: $z^* \in E'$ 이나 $z^* \notin E \;\Rightarrow\; E \neq \overline{E}$"
            )
            box_fc, box_ec = '#FEF2F2', '#DC2626'
        else:
            info_text_left = (
                "폐포화 완료: E의 모든 극한점(도집합 E') 결합\n"
                "• 경계점 포함 (실선: x^2 + y^2 = 1 포함)\n"
                r"• $\overline{E} = E \cup E'$ [최소 닫힌 확대집합]" "\n"
                r"• $\forall (z_k) \subseteq E, \; \lim z_k \in \overline{E}$ (극한점 포섭)" "\n"
                r"• $\overline{E}$는 닫힌집합 (Sequential Closedness 확보)"
            )
            box_fc, box_ec = '#ECFDF5', '#059669'

        ax1.text(0.04, 0.04, info_text_left, transform=ax1.transAxes, fontsize=9.2,
                 verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.6', facecolor=box_fc, edgecolor=box_ec, linewidth=1.3),
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
        ax2.set_xlabel(r'$x$ 좌표', fontsize=11, fontweight='bold', labelpad=6)
        ax2.set_ylabel(r'$y$ 좌표', fontsize=11, fontweight='bold', labelpad=6)

        # Draw closed set: solid emerald boundary, light emerald fill
        ax2.fill(circle_x, circle_y, color='#F0FDF4', alpha=0.85, zorder=1)
        ax2.plot(circle_x, circle_y, linestyle='-', color='#16A34A', linewidth=2.6, zorder=2)

        ax2.set_title("닫힌집합 (Closed Set)\n" r"$F = \{(x, y) \in \mathbb{R}^2 : x^2 + y^2 \leq 1\}$",
                      fontsize=12.5, fontweight='bold', color='#166534', pad=14)

        # Plot identical sequences on Right Panel
        for i in range(len(targets)):
            target = targets[i]
            start = starts[i]
            color = seq_colors[i]

            trail_steps = max(2, int(k_display))
            t_factors = [0.15 + (s_factor - 0.15) * (step / trail_steps) for step in range(trail_steps)]
            pts = np.array([start + factor * (target - start) for factor in t_factors])

            ax2.plot(pts[:, 0], pts[:, 1], color=color, linewidth=1.5, alpha=0.5, zorder=3)
            if len(pts) > 1:
                ax2.scatter(pts[:-1, 0], pts[:-1, 1], s=22, color=color, alpha=0.45, zorder=4)

            curr_pt = pts[-1]
            ax2.scatter([curr_pt[0]], [curr_pt[1]], s=75, color=color, edgecolor='#0F172A', linewidth=1.2, zorder=5)

            # Target point is in F: solid check dot
            ax2.scatter([target[0]], [target[1]], s=110, facecolor='#22C55E', edgecolor='#15803D', linewidth=1.8, zorder=6)

        right_info_text = (
            f"수열 진행 단계: k = {k_display}\n"
            "• 경계점 포함 (실선: x^2 + y^2 = 1 포함)\n"
            r"• $\forall k \in \mathbb{N}, \; z_k \in F$ (수열 원소는 집합 내부)" "\n"
            r"• $\lim_{k \to \infty} z_k = z^* \in F$ (극한점도 집합 내부 보존)" "\n"
            r"• $F' \subseteq F \;\Leftrightarrow\; F = \overline{F}$ [닫힌집합 / Closed Set]"
        )
        ax2.text(0.04, 0.04, right_info_text, transform=ax2.transAxes, fontsize=9.2,
                 verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.6', facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=1.3),
                 zorder=10)

        # Clear headroom margin: top=0.82 leaves 18% whitespace for title and superscripts!
        fig.subplots_adjust(top=0.82, bottom=0.12, left=0.08, right=0.95, wspace=0.24)
        frame_path = os.path.join(frames_dir, f"frame_{frame_idx:03d}.png")
        fig.savefig(frame_path, dpi=100)
        plt.close(fig)
        frame_paths.append(frame_path)

    # Compile GIF
    images = [Image.open(p) for p in frame_paths]
    output_gif_path = os.path.join(OUTPUT_DIR, "topology-2d-sequences-closedness.gif")
    images[0].save(
        output_gif_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Animation 1 saved: {output_gif_path} ({os.path.getsize(output_gif_path):,} bytes, {len(images)} frames)")


def generate_budget_weierstrass_gif():
    print("Generating Animation 2: Economic Choice & Weierstrass Extreme Value Theorem in R^2 (High FPS & Ample Headroom)...")
    frames_dir = os.path.join(SCRATCH_DIR, "budget_weierstrass")
    os.makedirs(frames_dir, exist_ok=True)

    n_motion = 60       # Smooth motion frames (60 frames)
    n_post_hold = 1     # Single long hold frame at the end
    total_frames = n_motion + n_post_hold

    # Model parameters:
    # Commodity space R_+^2
    # Utility u(x1, x2) = (x1 * x2)^(1/2)
    # Budget: p1*x1 + p2*x2 <= w with p1=1, p2=1, w=4
    # Tangency optimum x* = (2, 2), u(x*) = 2
    x_star = np.array([2.0, 2.0])
    u_star = 2.0

    # Grid for indifference curves
    x1_grid = np.linspace(0.1, 4.4, 250)
    x2_grid = np.linspace(0.1, 4.4, 250)
    X1, X2 = np.meshgrid(x1_grid, x2_grid)
    U = np.sqrt(np.maximum(X1 * X2, 0.0))

    frame_paths = []
    durations = []

    for frame_idx in range(total_frames):
        if frame_idx < n_motion:
            progress = frame_idx / (n_motion - 1)
            # Smooth diminishing factor approaching (2, 2): 0.50 -> 0.99
            t_factor = 0.50 + 0.49 * (1.0 - np.exp(-3.5 * progress)) / (1.0 - np.exp(-3.5))
            k_display = int(progress * 28) + 1
            frame_duration = 55
        else:
            t_factor = 0.99
            k_display = 29
            frame_duration = 3000  # 3.0 second hold at end

        durations.append(frame_duration)

        curr_x = t_factor * x_star
        curr_u = np.sqrt(curr_x[0] * curr_x[1])
        curr_cost = curr_x[0] + curr_x[1]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 7.8), dpi=100)
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
        ax1.plot([0, 4], [4, 0], linestyle='--', color='#DC2626', linewidth=2.5, zorder=3)

        # Indifference curve at current consumption bundle
        ax1.contour(X1, X2, U, levels=[curr_u], colors=['#F59E0B'], linewidths=[1.8], linestyles=['-'], zorder=4)
        # Target optimal indifference curve u = 2
        ax1.contour(X1, X2, U, levels=[u_star], colors=['#DC2626'], linewidths=[1.8], linestyles=[':'], zorder=4)

        # Plot consumption sequence history trail
        trail_steps = max(2, int(k_display))
        k_hist = np.array([0.50 + (t_factor - 0.50) * (s / trail_steps) for s in range(trail_steps)])
        pts_hist = np.outer(k_hist, x_star)
        ax1.plot(pts_hist[:, 0], pts_hist[:, 1], color='#D97706', linewidth=1.5, alpha=0.6, zorder=5)
        if len(pts_hist) > 1:
            ax1.scatter(pts_hist[:-1, 0], pts_hist[:-1, 1], s=24, color='#D97706', alpha=0.45, zorder=6)

        # Current bundle
        ax1.scatter([curr_x[0]], [curr_x[1]], s=85, color='#D97706', edgecolor='#0F172A', linewidth=1.2, zorder=7)
        ax1.text(curr_x[0] - 0.22, curr_x[1] + 0.16, rf'$x^{{({k_display})}}$', fontsize=10, fontweight='bold', color='#B45309', zorder=8)

        # Target optimum marker: hollow circle with cross (escaped from open budget set)
        ax1.scatter([x_star[0]], [x_star[1]], s=130, facecolor='none', edgecolor='#DC2626', linewidth=2.2, zorder=9)
        ax1.plot([x_star[0] - 0.08, x_star[0] + 0.08], [x_star[1] - 0.08, x_star[1] + 0.08], color='#DC2626', linewidth=2.0, zorder=10)
        ax1.plot([x_star[0] - 0.08, x_star[0] + 0.08], [x_star[1] + 0.08, x_star[1] - 0.08], color='#DC2626', linewidth=2.0, zorder=10)
        ax1.text(x_star[0] + 0.16, x_star[1] + 0.16, r'$x^*=(2, 2) \notin B_{\mathrm{open}}$', fontsize=10, fontweight='bold', color='#DC2626', zorder=11)

        ax1.set_title("열린 예산집합 (비폐집합)\n" r"$B_{\mathrm{open}} = \{(x_1, x_2) \in \mathbb{R}_+^2 : x_1 + x_2 < 4\}$",
                      fontsize=12.5, fontweight='bold', color='#991B1B', pad=14)

        info_left = (
            f"소비 수열 단계: k = {k_display}\n"
            f"• 소비점: x^({k_display}) = ({curr_x[0]:.2f}, {curr_x[1]:.2f}) ∈ B_open\n"
            f"• 지출액: p·x = {curr_cost:.2f} < 4.00 (예산 한도 내부)\n"
            f"• 효용 수준: u(x^({k_display})) = {curr_u:.3f} → sup = 2.000\n"
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
        # Budget line p·x = 4 included: solid green line
        ax2.plot([0, 4], [4, 0], linestyle='-', color='#16A34A', linewidth=2.8, zorder=3)

        # Indifference curve at current consumption bundle
        ax2.contour(X1, X2, U, levels=[curr_u], colors=['#059669'], linewidths=[1.8], linestyles=['-'], zorder=4)
        # Optimal indifference curve u = 2
        ax2.contour(X1, X2, U, levels=[u_star], colors=['#15803D'], linewidths=[2.0], linestyles=['-'], zorder=4)

        # Plot consumption sequence history
        ax2.plot(pts_hist[:, 0], pts_hist[:, 1], color='#047857', linewidth=1.5, alpha=0.6, zorder=5)
        if len(pts_hist) > 1:
            ax2.scatter(pts_hist[:-1, 0], pts_hist[:-1, 1], s=24, color='#047857', alpha=0.45, zorder=6)

        # Current bundle
        ax2.scatter([curr_x[0]], [curr_x[1]], s=85, color='#047857', edgecolor='#0F172A', linewidth=1.2, zorder=7)
        ax2.text(curr_x[0] - 0.22, curr_x[1] + 0.16, rf'$x^{{({k_display})}}$', fontsize=10, fontweight='bold', color='#047857', zorder=8)

        # Target optimum marker: solid green dot with checkmark label
        ax2.scatter([x_star[0]], [x_star[1]], s=130, facecolor='#22C55E', edgecolor='#15803D', linewidth=2.2, zorder=9)
        ax2.text(x_star[0] + 0.16, x_star[1] + 0.16, r'$x^*=(2, 2) \in B_{\mathrm{closed}}$ (최적해)', fontsize=10, fontweight='bold', color='#15803D', zorder=11)

        ax2.set_title("닫힌 예산집합 (유계 닫힌집합 = 콤팩트)\n" r"$B_{\mathrm{closed}} = \{(x_1, x_2) \in \mathbb{R}_+^2 : x_1 + x_2 \leq 4\}$",
                      fontsize=12.5, fontweight='bold', color='#166534', pad=14)

        info_right = (
            f"소비 수열 단계: k = {k_display}\n"
            f"• 소비점: x^({k_display}) = ({curr_x[0]:.2f}, {curr_x[1]:.2f}) ∈ B_closed\n"
            f"• 지출액: p·x = {curr_cost:.2f} ≤ 4.00 (예산 한도 내부)\n"
            f"• 효용 수준: u(x^({k_display})) = {curr_u:.3f} → max = 2.000\n"
            r"• $\lim_{k \to \infty} x^{(k)} = (2, 2) \in B_{\mathrm{closed}}$ [경계 접점 안착]" "\n"
            r"• $\mathrm{argmax}_{x \in B_{\mathrm{closed}}} u(x) = \{(2, 2)\}$ (최댓값 존재 보장!)" "\n"
            "※ 근거: 바이어슈트라스 극값정리 (연속함수 + 유계닫힌집합)"
        )
        ax2.text(0.04, 0.04, info_right, transform=ax2.transAxes, fontsize=9.2,
                 verticalalignment='bottom', bbox=dict(boxstyle='round,pad=0.6', facecolor='#F0FDF4', edgecolor='#16A34A', linewidth=1.3),
                 zorder=12)

        # Clear headroom margin: top=0.82 leaves 18% whitespace for title and superscripts!
        fig.subplots_adjust(top=0.82, bottom=0.12, left=0.08, right=0.95, wspace=0.24)
        frame_path = os.path.join(frames_dir, f"frame_{frame_idx:03d}.png")
        fig.savefig(frame_path, dpi=100)
        plt.close(fig)
        frame_paths.append(frame_path)

    # Compile GIF
    images = [Image.open(p) for p in frame_paths]
    output_gif_path = os.path.join(OUTPUT_DIR, "topology-2d-budget-weierstrass.gif")
    images[0].save(
        output_gif_path,
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=0,
        optimize=True
    )
    print(f"Animation 2 saved: {output_gif_path} ({os.path.getsize(output_gif_path):,} bytes, {len(images)} frames)")


if __name__ == "__main__":
    generate_sequence_closedness_gif()
    generate_budget_weierstrass_gif()
    print("All GIFs generated successfully!")
