"""Generate publication-grade animated GIFs for the Oligopoly Game Theory supplement.

Outputs:
  - assets/gif/oligopoly-reaction-dynamics.gif
  - assets/gif/oligopoly-market-welfare.gif
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
TEAL_COLOR = "#087e8b"      # Cournot / Best response 1
PURPLE_COLOR = "#6b4c7a"    # Best response 2 / Stackelberg
GOLD_COLOR = "#d97706"      # Collusion / Isoprofit curves
RED_COLOR = "#dc2626"       # Deadweight Loss / Defection
BLUE_COLOR = "#2563eb"      # Consumer Surplus / PC
GREEN_COLOR = "#16a34a"     # Producer Surplus

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# ANIMATION 1: Oligopoly Reaction Curves and Best-Response Dynamics
# Left: (q1, q2) Phase plane with BR1, BR2, Isoprofit curves, Cournot, Stackelberg, Collusion
# Right: Dynamic metric cards & Cobweb iteration trajectory
# ==============================================================================

def generate_gif_reaction_dynamics():
    print("Generating oligopoly-reaction-dynamics.gif...")

    # Market: P = 90 - (q1 + q2), c1 = c2 = 10
    # BR1(q2) = 40 - 0.5*q2
    # BR2(q1) = 40 - 0.5*q1
    # Cournot: q1 = q2 = 80/3 ≈ 26.67, P = 110/3 ≈ 36.67, pi1 = pi2 = 6400/9 ≈ 711.11
    # Stackelberg (1 is Leader): q1 = 40, q2 = 20, P = 30, pi1 = 800, pi2 = 400
    # Collusion: q1 = q2 = 20, P = 50, pi1 = pi2 = 800 (Total Pi = 1600)
    # Cheat from Collusion: q1 = BR1(20) = 30, q2 = 20, P = 40, pi1 = 900, pi2 = 600

    q_grid = np.linspace(0, 55, 300)
    br1_q2 = 80 - 2 * q_grid  # q2 as function of q1 along BR1 (since q1 = 40 - 0.5*q2 => q2 = 80 - 2*q1)
    br2_q2 = 40 - 0.5 * q_grid  # q2 as function of q1 along BR2

    # Pre-generate Cobweb steps: start from (q1=8, q2=48)
    cobweb_points = [(8.0, 48.0)]
    cur_q1, cur_q2 = 8.0, 48.0
    for _ in range(6):
        # Step 1: firm 1 adjusts
        cur_q1 = 40.0 - 0.5 * cur_q2
        cobweb_points.append((cur_q1, cur_q2))
        # Step 2: firm 2 adjusts
        cur_q2 = 40.0 - 0.5 * cur_q1
        cobweb_points.append((cur_q1, cur_q2))

    # Phase sequences for animation:
    # Phase A (Frames 0-17): Step-by-step cobweb convergence to Cournot
    # Phase B (Frames 18-28): Exploration along BR2 from Cournot (26.67, 26.67) to Stackelberg (40, 20) with tangency
    # Phase C (Frames 29-38): Transition to Collusion (20, 20) and Defection arrow to (30, 20)
    # Phase D (Frames 39-44): Full equilibrium summary pause

    frames = []
    total_steps = len(cobweb_points)

    # Frame plan: 45 frames total
    for frame_idx in range(45):
        fig, (ax_main, ax_info) = plt.subplots(
            1, 2, figsize=(13.2, 6.2), dpi=100,
            gridspec_kw={"width_ratios": [1.25, 0.95]}
        )
        fig.patch.set_facecolor(BG_COLOR)
        ax_main.set_facecolor(BG_COLOR)
        ax_info.set_facecolor(BG_COLOR)

        # -------------------------------------------------------------
        # Left Panel: (q1, q2) Reaction Function Space
        # -------------------------------------------------------------
        ax_main.set_xlim(-2, 55)
        ax_main.set_ylim(-2, 55)
        ax_main.set_xlabel("기업 1 생산량 $q_1$ (선도자 후보)", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_main.set_ylabel("기업 2 생산량 $q_2$ (추종자)", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_main.set_title("과점 반응곡선과 전략적 균형 기하 ($P=90-Q, c=10$)", fontsize=12, color=INK_COLOR, fontweight="bold", pad=10)
        ax_main.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

        # Draw 45-degree reference line
        ax_main.plot([0, 50], [0, 50], linestyle=":", color=MUTED_COLOR, alpha=0.4, label="대칭선 ($q_1=q_2$)")

        # Draw Best Response curves
        # BR1: q1 = 40 - 0.5*q2 => plotted with q1 in [0, 40]
        mask_br1 = (br1_q2 >= 0) & (br1_q2 <= 55)
        ax_main.plot(q_grid[mask_br1], br1_q2[mask_br1], color=TEAL_COLOR, lw=2.4, label=r"$BR_1(q_2): q_1 = 40 - 0.5q_2$")

        # BR2: q2 = 40 - 0.5*q1
        mask_br2 = (br2_q2 >= 0) & (br2_q2 <= 55)
        ax_main.plot(q_grid[mask_br2], br2_q2[mask_br2], color=PURPLE_COLOR, lw=2.4, label=r"$BR_2(q_1): q_2 = 40 - 0.5q_1$")

        # Draw Isoprofit Curves for Firm 1
        # pi1 = (80 - q1 - q2)*q1 => q2 = 80 - q1 - pi1/q1
        q1_iso = np.linspace(5, 52, 250)
        
        # Cournot isoprofit: pi1 = 6400/9 ≈ 711.11
        q2_iso_C = 80 - q1_iso - (6400.0 / 9.0) / q1_iso
        mask_iso_C = (q2_iso_C >= 0) & (q2_iso_C <= 55)
        ax_main.plot(q1_iso[mask_iso_C], q2_iso_C[mask_iso_C], color=TEAL_COLOR, lw=1.2, linestyle="--", alpha=0.5,
                     label=r"등이윤선 $\pi_1 = 711.1$ (Cournot)")

        # Stackelberg isoprofit: pi1 = 800
        q2_iso_S = 80 - q1_iso - 800.0 / q1_iso
        mask_iso_S = (q2_iso_S >= 0) & (q2_iso_S <= 55)
        ax_main.plot(q1_iso[mask_iso_S], q2_iso_S[mask_iso_S], color=GOLD_COLOR, lw=1.8, linestyle="-.", alpha=0.85,
                     label=r"등이윤선 $\pi_1 = 800$ (Stackelberg 외접)")

        # Plot key benchmark equilibrium points (faint or highlighted)
        # Cournot point
        q_C = 80.0 / 3.0
        ax_main.scatter([q_C], [q_C], color=TEAL_COLOR, s=80, zorder=5)
        ax_main.annotate(r"$E^C$ (Cournot)" + f"\n({q_C:.1f}, {q_C:.1f})", xy=(q_C, q_C),
                         xytext=(q_C + 2, q_C + 3), fontsize=9.5, fontweight="bold", color=TEAL_COLOR,
                         arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.2))

        # Stackelberg point
        ax_main.scatter([40], [20], color=PURPLE_COLOR, s=90, marker="s", zorder=5)
        ax_main.annotate(r"$E^S$ (Stackelberg)" + "\n(40, 20)", xy=(40, 20),
                         xytext=(41, 23), fontsize=9.5, fontweight="bold", color=PURPLE_COLOR,
                         arrowprops=dict(arrowstyle="->", color=PURPLE_COLOR, lw=1.2))

        # Collusion point
        ax_main.scatter([20], [20], color=GOLD_COLOR, s=80, marker="^", zorder=5)
        ax_main.annotate(r"$E^M$ (카르텔/담합)" + "\n(20, 20)", xy=(20, 20),
                         xytext=(10, 12), fontsize=9, fontweight="bold", color=GOLD_COLOR,
                         arrowprops=dict(arrowstyle="->", color=GOLD_COLOR, lw=1.0))

        # Dynamic Content by Phase
        current_state_title = ""
        current_q1, current_q2 = q_C, q_C
        current_mode = "cournot"

        if frame_idx <= 17:
            # Phase A: Cobweb convergence
            current_mode = "cobweb"
            step_progress = min(frame_idx, total_steps - 1)
            active_points = cobweb_points[:step_progress + 1]
            xs = [p[0] for p in active_points]
            ys = [p[1] for p in active_points]

            # Draw cobweb trajectory
            ax_main.plot(xs, ys, color=RED_COLOR, lw=2.2, linestyle="-", zorder=6)
            for i in range(len(xs) - 1):
                ax_main.annotate("", xy=(xs[i+1], ys[i+1]), xytext=(xs[i], ys[i]),
                                 arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.5, mutation_scale=10))
            
            # Current agent position
            current_q1, current_q2 = xs[-1], ys[-1]
            ax_main.scatter([current_q1], [current_q2], color=RED_COLOR, s=120, zorder=7, edgecolor=INK_COLOR, lw=1.5)
            current_state_title = f"[Phase 1] 최적대응 거미집 수렴 (Step {step_progress+1}/{total_steps})"

        elif frame_idx <= 28:
            # Phase B: Movement along BR2 from Cournot to Stackelberg
            current_mode = "stackelberg"
            t = (frame_idx - 18) / 10.0  # 0 to 1
            current_q1 = q_C + t * (40.0 - q_C)
            current_q2 = 40.0 - 0.5 * current_q1

            # Draw trajectory along BR2
            q1_path = np.linspace(q_C, current_q1, 30)
            q2_path = 40.0 - 0.5 * q1_path
            ax_main.plot(q1_path, q2_path, color=GOLD_COLOR, lw=3.0, zorder=6)
            ax_main.scatter([current_q1], [current_q2], color=GOLD_COLOR, s=130, marker="*", zorder=7, edgecolor=INK_COLOR, lw=1.5)
            
            # Show dynamic isoprofit curve through (current_q1, current_q2)
            cur_pi1 = (80.0 - current_q1 - current_q2) * current_q1
            q2_dyn = 80.0 - q1_iso - cur_pi1 / q1_iso
            mask_dyn = (q2_dyn >= 0) & (q2_dyn <= 55)
            ax_main.plot(q1_iso[mask_dyn], q2_dyn[mask_dyn], color=GOLD_COLOR, lw=1.5, linestyle=":", alpha=0.7)

            current_state_title = f"[Phase 2] Leader의 산출량 확장 및 외접 탐색 (t={t:.2f})"

        elif frame_idx <= 38:
            # Phase C: Collusion and Defection
            current_mode = "collusion"
            t = (frame_idx - 29) / 9.0  # 0 to 1
            # Move from Collusion (20, 20) toward Defection (30, 20)
            current_q1 = 20.0 + t * 10.0
            current_q2 = 20.0

            ax_main.plot([20, current_q1], [20, 20], color=RED_COLOR, lw=3.0, linestyle="--", zorder=6)
            ax_main.annotate("", xy=(current_q1, 20), xytext=(20, 20),
                             arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=2.2, mutation_scale=14))
            ax_main.scatter([current_q1], [current_q2], color=RED_COLOR, s=120, zorder=7, edgecolor=INK_COLOR, lw=1.5)
            
            # Cheat point annotation
            if t > 0.6:
                ax_main.scatter([30], [20], color=RED_COLOR, s=100, marker="X", zorder=6)
                ax_main.annotate(r"$E^{cheat}$ (이탈점)" + "\n(30, 20), " + r"$\pi_1=900$", xy=(30, 20),
                                 xytext=(32, 14), fontsize=9, fontweight="bold", color=RED_COLOR)

            current_state_title = r"[Phase 3] 카르텔 담합과 독자 이탈 유인 ($\pi_1: 800 \to 900$)"

        else:
            # Phase D: Summary pause
            current_mode = "summary"
            current_q1, current_q2 = 40.0, 20.0
            ax_main.scatter([40], [20], color=PURPLE_COLOR, s=140, marker="s", zorder=7, edgecolor=INK_COLOR, lw=2.0)
            current_state_title = "[Phase 4] 4대 과점 균형 기하학 총괄 비교"

        ax_main.legend(loc="upper right", fontsize=8.5, framealpha=0.9)

        # -------------------------------------------------------------
        # Right Panel: Real-time Economic Dashboard & Explanation
        # -------------------------------------------------------------
        ax_info.axis("off")

        # Compute real-time values
        cur_Q = current_q1 + current_q2
        cur_P = max(10.0, 90.0 - cur_Q)
        cur_pi1 = (cur_P - 10.0) * current_q1
        cur_pi2 = (cur_P - 10.0) * current_q2
        cur_CS = 0.5 * (90.0 - cur_P) * cur_Q
        cur_DWL = 0.5 * (cur_P - 10.0) * max(0.0, 80.0 - cur_Q)

        # Title block
        ax_info.text(0.02, 0.96, current_state_title, fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax_info.axhline(y=0.93, xmin=0.02, xmax=0.98, color=MUTED_COLOR, lw=0.8, alpha=0.5)

        # Real-time state metrics table/boxes
        box_y = 0.86
        ax_info.text(0.04, box_y, "■ 실시간 시장 및 기업 지표", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        
        metrics_text = [
            f"• 기업 1 생산량 ($q_1$): {current_q1:.2f}",
            f"• 기업 2 생산량 ($q_2$): {current_q2:.2f}",
            f"• 시장 총산출량 ($Q$):   {cur_Q:.2f}",
            f"• 시장 균형가격 ($P$):   {cur_P:.2f} (MC = 10)",
            f"• 기업 1 이윤 ($\\pi_1$):   {cur_pi1:.1f}",
            f"• 기업 2 이윤 ($\\pi_2$):   {cur_pi2:.1f}",
            f"• 소비자잉여 ($CS$):     {cur_CS:.1f}",
            f"• 사중손실 ($DWL$):       {cur_DWL:.1f}",
        ]
        
        for idx, m_text in enumerate(metrics_text):
            row_y = box_y - 0.05 * (idx + 1)
            ax_info.text(0.06, row_y, m_text, fontsize=9.5, color=INK_COLOR)

        # Core Economic Mechanisms Box
        mech_y = 0.38
        ax_info.text(0.04, mech_y, "■ 핵심 게임이론적 수리 메커니즘", fontsize=10.5, fontweight="bold", color=INK_COLOR)
        
        if current_mode == "cobweb":
            mech_lines = [
                "1. 전략적 대체 (Strategic Substitutes):",
                "   ∂²π₁/∂q₁∂q₂ = -b = -1 < 0",
                "   상대방 산출량 증가 시 나의 최적대응 감소 (우하향 BR).",
                "2. 안정적 수렴 조건 (Stability Condition):",
                "   |BR₁' × BR₂'| = |-0.5 × -0.5| = 0.25 < 1",
                "   축약사상(Contraction)으로 Cournot 균형에 무조건 수렴."
            ]
        elif current_mode == "stackelberg":
            mech_lines = [
                "1. 등이윤곡선과 Follower 반응선의 외접:",
                "   Leader는 Follower의 반응선 BR₂(q₁) 위에서",
                "   가장 높은 이윤을 주는 등이윤곡선과의 접점을 선택.",
                "2. 선도자 우위 (First-Mover Advantage):",
                "   등이윤곡선 기울기 = BR₂'(q₁) = -0.5",
                "   q1(S) = 40 > 26.67 => pi1(S) = 800 > 711.1 (이윤 증가)."
            ]
        elif current_mode == "collusion":
            mech_lines = [
                "1. 파레토 최적 담합 (Joint Profit Max):",
                "   독점 산출량 Q=40을 양분 (q₁=q₂=20), 총이윤 1600 극대화.",
                "2. 죄수의 딜레마 (Incentive to Defect):",
                "   상대가 q₂=20 유지 시, q₁=BR₁(20)=30으로 이탈하면",
                "   개별이윤 900으로 급증 => 담합은 내쉬균형이 아님."
            ]
        else:
            mech_lines = [
                "1. 시장구조별 총산출량 서열:",
                "   Q(M) 40 < Q(C) 53.3 < Q(S) 60 < Q(PC) 80",
                "2. 시장구조별 가격 및 후생손실 서열:",
                "   P(M) 50 > P(C) 36.7 > P(S) 30 > P(PC) 10",
                "   DWL(M) 800 > DWL(C) 355.6 > DWL(S) 200 > DWL(PC) 0"
            ]

        for idx, line in enumerate(mech_lines):
            row_y = mech_y - 0.045 * (idx + 1)
            c = TEAL_COLOR if "1." in line or "2." in line else MUTED_COLOR
            fw = "bold" if "1." in line or "2." in line else "normal"
            ax_info.text(0.06, row_y, line, fontsize=9.0, color=c, fontweight=fw)

        plt.subplots_adjust(left=0.07, right=0.96, top=0.92, bottom=0.10, wspace=0.25)

        # Convert plot to PIL Image
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "oligopoly-reaction-dynamics.gif")
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=[280]*18 + [260]*11 + [280]*10 + [700]*6,  # 45 frames total
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Saved: {out_path} ({size_kb:.1f} KB)")


# ==============================================================================
# ANIMATION 2: Market Equilibrium, Welfare Triangles, and N-Firm Convergence
# Left: (Q, P) Market Demand, MC, CS, PS, DWL across Market Structures
# Right: Welfare decomposition bars & N-firm Cournot convergence to PC
# ==============================================================================

def generate_gif_market_welfare():
    print("Generating oligopoly-market-welfare.gif...")

    # Market: P = 90 - Q, MC = 10
    # Perfect Competition: Q = 80, P = 10
    # Monopoly (N=1): Q = 40, P = 50
    # Cournot (N=2): Q = 53.33, P = 36.67
    # Stackelberg: Q = 60, P = 30
    # Cournot N=3: Q = 60, P = 30
    # Cournot N=5: Q = 66.67, P = 23.33
    # Cournot N=10: Q = 72.73, P = 17.27
    # PC: Q = 80, P = 10

    # We will animate a smooth transition along two acts:
    # Act 1 (Frames 0-24): Discrete/continuous transition through 4 Market Structures
    # [Monopoly (Q=40, P=50) -> Cournot (Q=53.3, P=36.7) -> Stackelberg (Q=60, P=30) -> PC (Q=80, P=10)]
    # Act 2 (Frames 25-45): N-firm Cournot expansion: N = 1, 2, 3, 4, 5, 8, 12, 20, 50
    # showing Q(N) -> 80, P(N) -> 10, DWL(N) -> 0

    Q_grid = np.linspace(0, 90, 300)
    demand_P = 90.0 - Q_grid
    mr_P = 90.0 - 2 * Q_grid

    # Pre-calculate points for Act 1
    # 25 frames for Act 1: 0 to 24
    # Structure segments:
    # 0-5: Monopoly hold
    # 6-12: Transition Monopoly -> Cournot
    # 13-18: Transition Cournot -> Stackelberg
    # 19-24: Transition Stackelberg -> PC

    # Act 2: N-firm Cournot convergence (frames 25 to 45)
    # N values from 1 to 25

    frames = []

    for frame_idx in range(46):
        fig, (ax_mkt, ax_welf) = plt.subplots(
            1, 2, figsize=(13.2, 6.2), dpi=100,
            gridspec_kw={"width_ratios": [1.15, 1.05]}
        )
        fig.patch.set_facecolor(BG_COLOR)
        ax_mkt.set_facecolor(BG_COLOR)
        ax_welf.set_facecolor(BG_COLOR)

        # -------------------------------------------------------------
        # Determine Current (Q, P, Market Title)
        # -------------------------------------------------------------
        if frame_idx <= 24:
            # Act 1: Market structure comparison
            if frame_idx <= 5:
                cur_Q = 40.0
                struct_name = "독점 / 카르텔 (Monopoly / Collusion)"
            elif frame_idx <= 12:
                t = (frame_idx - 5) / 7.0
                cur_Q = 40.0 + t * (53.333 - 40.0)
                struct_name = f"과점 전환: 독점 $\\to$ Cournot 동시 복점 (t={t:.2f})"
            elif frame_idx <= 18:
                t = (frame_idx - 12) / 6.0
                cur_Q = 53.333 + t * (60.0 - 53.333)
                struct_name = f"과점 전환: Cournot $\\to$ Stackelberg 순차 복점 (t={t:.2f})"
            else:
                t = (frame_idx - 18) / 6.0
                cur_Q = 60.0 + t * (80.0 - 60.0)
                struct_name = f"과점 전환: Stackelberg $\\to$ Bertrand / 완전경쟁 (t={t:.2f})"
            
            cur_N = 2.0
            act_mode = "structures"
        else:
            # Act 2: N-firm Cournot convergence
            act_mode = "n_firm"
            # N goes from 1 to 20
            t = (frame_idx - 25) / 20.0  # 0 to 1
            # Exponentially spaced N
            cur_N = 1.0 + (19.0) * (t ** 1.6)
            cur_Q = (cur_N / (cur_N + 1.0)) * 80.0
            struct_name = f"$N$-기업 대칭 Cournot 장기 수렴 ($N = {cur_N:.1f}$)"

        cur_P = 90.0 - cur_Q
        cur_CS = 0.5 * (90.0 - cur_P) * cur_Q
        cur_PS = (cur_P - 10.0) * cur_Q
        cur_DWL = 0.5 * (cur_P - 10.0) * (80.0 - cur_Q)
        cur_TS = cur_CS + cur_PS

        # -------------------------------------------------------------
        # Left Panel: Market Demand, Supply, and Welfare Areas
        # -------------------------------------------------------------
        ax_mkt.set_xlim(0, 92)
        ax_mkt.set_ylim(0, 95)
        ax_mkt.set_xlabel(r"시장 총산출량 $Q = \sum q_i$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_mkt.set_ylabel("시장 가격 $P$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_mkt.set_title(f"시장 균형과 후생 삼각형 분해\n[{struct_name}]", fontsize=11.5, color=INK_COLOR, fontweight="bold", pad=8)
        ax_mkt.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

        # Plot Demand and MC
        ax_mkt.plot(Q_grid, demand_P, color=INK_COLOR, lw=2.2, label=r"시장 역수요 $P(Q) = 90 - Q$")
        ax_mkt.axhline(y=10.0, color=MUTED_COLOR, lw=2.0, linestyle="-", label=r"한계비용 $MC = 10$")

        # Plot MR (for monopoly/reference)
        mask_mr = mr_P >= 0
        ax_mkt.plot(Q_grid[mask_mr], mr_P[mask_mr], color=MUTED_COLOR, lw=1.2, linestyle=":", alpha=0.6, label=r"한계수입 $MR = 90 - 2Q$")

        # Shading Welfare Areas
        # 1. Consumer Surplus (CS): Triangle between demand and cur_P for Q in [0, cur_Q]
        q_fill_cs = np.linspace(0, cur_Q, 100)
        p_demand_cs = 90.0 - q_fill_cs
        ax_mkt.fill_between(q_fill_cs, cur_P, p_demand_cs, color=BLUE_COLOR, alpha=0.25, label=f"소비자잉여 ($CS={cur_CS:.0f}$)")

        # 2. Producer Surplus (PS): Rectangle between cur_P and MC=10 for Q in [0, cur_Q]
        if cur_P > 10.0 and cur_Q > 0:
            ax_mkt.fill_between([0, cur_Q], 10.0, cur_P, color=GREEN_COLOR, alpha=0.25, label=f"생산자잉여 ($PS={cur_PS:.0f}$)")

        # 3. Deadweight Loss (DWL): Triangle between demand and MC=10 for Q in [cur_Q, 80]
        if cur_Q < 80.0:
            q_fill_dwl = np.linspace(cur_Q, 80.0, 100)
            p_demand_dwl = 90.0 - q_fill_dwl
            ax_mkt.fill_between(q_fill_dwl, 10.0, p_demand_dwl, color=RED_COLOR, alpha=0.30, label=f"사중손실 ($DWL={cur_DWL:.0f}$)")

        # Dotted projection lines to axes
        ax_mkt.plot([cur_Q, cur_Q], [0, cur_P], color=RED_COLOR, linestyle="--", lw=1.5)
        ax_mkt.plot([0, cur_Q], [cur_P, cur_P], color=RED_COLOR, linestyle="--", lw=1.5)

        # Equilibrium point marker
        ax_mkt.scatter([cur_Q], [cur_P], color=RED_COLOR, s=120, zorder=6, edgecolor=INK_COLOR, lw=1.5)
        ax_mkt.annotate(f"$E$\n$Q={cur_Q:.1f}$\n$P={cur_P:.1f}$", xy=(cur_Q, cur_P),
                        xytext=(cur_Q + 3, cur_P + 4), fontsize=9.5, fontweight="bold", color=INK_COLOR,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", alpha=0.85, edgecolor=RED_COLOR))

        ax_mkt.legend(loc="upper right", fontsize=8.0, framealpha=0.9)

        # -------------------------------------------------------------
        # Right Panel: Welfare Bars & N-firm Convergence Function
        # -------------------------------------------------------------
        if act_mode == "structures":
            # Bar chart comparing 4 benchmark structures + current point
            bench_names = ["독점(M)", "Cournot(C)", "Stackelberg(S)", "완전경쟁(PC)"]
            bench_CS = [800.0, 1422.2, 1800.0, 3200.0]
            bench_PS = [1600.0, 1422.2, 1200.0, 0.0]
            bench_DWL = [800.0, 355.6, 200.0, 0.0]

            x_pos = np.arange(len(bench_names))
            width = 0.55

            # Stacked bars
            p1 = ax_welf.bar(x_pos, bench_CS, width, label="소비자잉여 (CS)", color=BLUE_COLOR, alpha=0.7)
            p2 = ax_welf.bar(x_pos, bench_PS, width, bottom=bench_CS, label="생산자잉여 (PS)", color=GREEN_COLOR, alpha=0.7)
            p3 = ax_welf.bar(x_pos, bench_DWL, width, bottom=np.array(bench_CS) + np.array(bench_PS),
                             label="사중손실 (DWL)", color=RED_COLOR, alpha=0.7)

            ax_welf.set_xticks(x_pos)
            ax_welf.set_xticklabels(bench_names, fontsize=10, fontweight="bold", color=INK_COLOR)
            ax_welf.set_ylabel("사회적 잉여 가치 ($)", fontsize=11, color=INK_COLOR, fontweight="bold")
            ax_welf.set_title("시장구조별 총후생 분해 (CS vs PS vs DWL)", fontsize=11.5, color=INK_COLOR, fontweight="bold", pad=8)
            ax_welf.set_ylim(0, 3600)
            ax_welf.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR, axis="y")
            ax_welf.axhline(y=3200, color=GOLD_COLOR, linestyle=":", lw=1.5, label="파레토 최적 총잉여 ($3,200)")

            # Indicator arrow pointing to which market structure is currently active
            if cur_Q <= 44:
                active_idx = 0
            elif cur_Q <= 56:
                active_idx = 1
            elif cur_Q <= 66:
                active_idx = 2
            else:
                active_idx = 3

            ax_welf.annotate("현재 상태", xy=(active_idx, 3350), xytext=(active_idx, 3500),
                             ha="center", fontsize=9.5, fontweight="bold", color=RED_COLOR,
                             arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.8))
            ax_welf.legend(loc="lower right", fontsize=8.5, framealpha=0.9)

        else:
            # Plot N-firm Cournot convergence curves
            n_vals = np.linspace(1, 25, 200)
            p_vals = 10.0 + 80.0 / (n_vals + 1.0)
            dwl_vals = 3200.0 / ((n_vals + 1.0) ** 2)

            ax_welf.set_xlim(1, 25)
            ax_welf.set_ylim(0, 55)
            ax_welf.set_xlabel("과점 시장 내 대칭 기업 수 $N$", fontsize=11, color=INK_COLOR, fontweight="bold")
            ax_welf.set_ylabel("시장 가격 $P(N)$ ($)", fontsize=11, color=TEAL_COLOR, fontweight="bold")
            ax_welf.set_title(r"대칭 Cournot $N \to \infty$ 완전경쟁 수렴 동학", fontsize=11.5, color=INK_COLOR, fontweight="bold", pad=8)
            ax_welf.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)

            # Left axis: Price P(N)
            l1 = ax_welf.plot(n_vals, p_vals, color=TEAL_COLOR, lw=2.4, label=r"가격 $P(N) = 10 + \frac{80}{N+1}$")
            ax_welf.axhline(y=10.0, color=MUTED_COLOR, linestyle="--", lw=1.5, label="완전경쟁 한계비용 ($P=10$)")

            # Active point
            ax_welf.scatter([cur_N], [cur_P], color=RED_COLOR, s=110, zorder=6)
            ax_welf.annotate(f"$N={cur_N:.1f}$\n$P={cur_P:.1f}$\n$DWL={cur_DWL:.1f}$", xy=(cur_N, cur_P),
                             xytext=(cur_N + 1.5, cur_P + 5), fontsize=9.0, fontweight="bold", color=INK_COLOR,
                             bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", alpha=0.85, edgecolor=TEAL_COLOR))

            # Twin axis for DWL
            ax_dwl = ax_welf.twinx()
            ax_dwl.set_ylim(0, 900)
            ax_dwl.set_ylabel("사중손실 $DWL(N)$ ($)", fontsize=11, color=RED_COLOR, fontweight="bold")
            l2 = ax_dwl.plot(n_vals, dwl_vals, color=RED_COLOR, lw=2.0, linestyle="-.", label=r"사중손실 $DWL(N) = \frac{3200}{(N+1)^2}$")
            ax_dwl.tick_params(axis="y", labelcolor=RED_COLOR)

            # Joint legend
            lines = l1 + [plt.Line2D([0], [0], color=MUTED_COLOR, linestyle="--", lw=1.5)] + l2
            labels = [l.get_label() for l in lines]
            ax_welf.legend(lines, labels, loc="upper right", fontsize=8.0, framealpha=0.9)

        plt.subplots_adjust(left=0.07, right=0.93, top=0.90, bottom=0.12, wspace=0.28)

        # Convert plot to PIL Image
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "oligopoly-market-welfare.gif")
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=[320]*6 + [240]*7 + [240]*6 + [260]*6 + [220]*15 + [600]*6,  # 46 frames total
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Saved: {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_gif_reaction_dynamics()
    generate_gif_market_welfare()
    print("All oligopoly GIFs generated successfully!")
