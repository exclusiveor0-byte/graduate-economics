"""Generate publication-grade animated GIFs for the Repeated Games and Folk Theorem supplement.

Outputs:
  - assets/gif/repeated-game-convex-hull-folk-theorem.gif
  - assets/gif/repeated-game-grim-trigger-dynamics.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIF_DIR = os.path.join(ROOT, "assets", "gif")
os.makedirs(GIF_DIR, exist_ok=True)

# Styling parameters (Warm Editorial Theme matching the site)
BG_COLOR = "#fcf9f2"
INK_COLOR = "#2d251e"
MUTED_COLOR = "#75665b"
GRID_COLOR = "#e5ded3"
PRIMARY_COLOR = "#0f4c81"    # Navy blue for GT
ACCENT_COLOR = "#c0392b"     # Crimson for defection / punishment
GREEN_COLOR = "#1b7a43"      # Emerald green for cooperation
GOLD_COLOR = "#d97706"       # Amber gold for Pareto frontier
PURPLE_COLOR = "#6b4c7a"     # Violet for minimax / reservations

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ==============================================================================
# 1. GIF 1: Convex Hull & SPE Payoff Set Expansion with Discount Factor delta
# ==============================================================================
def generate_gif_convex_hull_folk():
    print("Generating GIF 1: repeated-game-convex-hull-folk-theorem.gif ...")
    
    # Prisoner's Dilemma payoffs:
    # (C, C) -> (3, 3)
    # (D, C) -> (5, 0)
    # (C, D) -> (0, 5)
    # (D, D) -> (1, 1)  (Minimax / stage Nash)
    p_DD = np.array([1.0, 1.0])
    p_DC = np.array([5.0, 0.0])
    p_CC = np.array([3.0, 3.0])
    p_CD = np.array([0.0, 5.0])
    
    hull_pts = np.array([p_DD, p_DC, p_CC, p_CD])
    
    # Minimax reservation level
    v1, v2 = 1.0, 1.0
    
    # Vertices of strictly individually rational feasible set V*
    # Segment (0,5) to (3,3): line u2 - 5 = -2/3 u1 => u2 = 5 - (2/3)u1.
    # At u1 = 1: u2 = 5 - 2/3 = 13/3 ~ 4.333
    # Segment (5,0) to (3,3): line u2 - 0 = -3/2(u1 - 5) => u2 = 7.5 - 1.5u1.
    # At u2 = 1: 1 = 7.5 - 1.5u1 => 1.5u1 = 6.5 => u1 = 13/3 ~ 4.333
    sir_top_left = np.array([1.0, 13.0 / 3.0])
    sir_bottom_right = np.array([13.0 / 3.0, 1.0])
    sir_pts = np.array([p_DD, sir_bottom_right, p_CC, sir_top_left])

    # Delta sweep from 0.05 to 0.95
    # For Friedman's trigger strategy with Nash reversal:
    # A payoff (u1, u2) is sustainable iff for each i:
    # u_i / (1 - delta) >= max_dev_i(u) + delta/(1-delta)*v_i
    # For simplicity of visualization, scaling the attainable set from Nash (1,1)
    # towards the full V* as delta goes from delta_min to 1.
    deltas = np.concatenate([
        np.linspace(0.05, 0.49, 15),
        np.linspace(0.50, 0.92, 20),
        np.linspace(0.92, 0.92, 5) # pause at the end
    ])
    
    frames = []
    
    for delta in deltas:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.4), facecolor=BG_COLOR)
        
        # --- Left Panel: Payoff Space (u1, u2) ---
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(-0.5, 5.6)
        ax1.set_ylim(-0.5, 5.6)
        ax1.set_aspect("equal")
        ax1.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.7)
        ax1.set_xlabel("플레이어 1 평균 보수 ($u_1$)", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel("플레이어 2 평균 보수 ($u_2$)", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax1.set_title("보수 공간과 Folk Theorem 가능 영역", fontsize=11.5, color=PRIMARY_COLOR, fontweight="bold", pad=10)
        
        # Draw Convex Hull
        hull_poly = Polygon(hull_pts, closed=True, facecolor="#e8ecf2", edgecolor="#8ba3c7", linewidth=1.5, linestyle="--", label="실행가능 보수 볼록껍질 co(u(A))")
        ax1.add_patch(hull_poly)
        
        # Draw Minimax lines
        ax1.axvline(v1, color=PURPLE_COLOR, linestyle=":", linewidth=1.2, alpha=0.8)
        ax1.axhline(v2, color=PURPLE_COLOR, linestyle=":", linewidth=1.2, alpha=0.8)
        ax1.text(v1 + 0.08, -0.3, "미니맥스 $v_1=1$", color=PURPLE_COLOR, fontsize=8.5, fontweight="bold")
        ax1.text(-0.4, v2 + 0.08, "미니맥스 $v_2=1$", color=PURPLE_COLOR, fontsize=8.5, fontweight="bold")
        
        # Pareto Frontier line
        pareto_x = [sir_top_left[0], p_CC[0], sir_bottom_right[0]]
        pareto_y = [sir_top_left[1], p_CC[1], sir_bottom_right[1]]
        ax1.plot(pareto_x, pareto_y, color=GOLD_COLOR, linewidth=2.4, label="파레토 프론티어 (Pareto Frontier)", zorder=3)
        
        # Sustainable SPE payoff region V(delta)
        # As delta increases, region expands from (1,1) towards sir_pts
        # At delta < 0.5, (3,3) is NOT inside V(delta)
        # Expansion factor lambda(delta): 0 at delta=0, 1 at delta=1
        expansion = min(1.0, max(0.0, (delta - 0.05) / 0.87))
        curr_sir_pts = p_DD + expansion * (sir_pts - p_DD)
        
        spe_poly = Polygon(curr_sir_pts, closed=True, facecolor="#cce5ff", edgecolor=PRIMARY_COLOR, linewidth=2.0, alpha=0.75, label="SPE 균형 보수집합 $V(\\delta)$", zorder=4)
        ax1.add_patch(spe_poly)
        
        # Plot pure action points
        pts = [
            (p_CC, "협조 (C, C)\n(3, 3)", GREEN_COLOR),
            (p_DC, "배반·유혹 (D, C)\n(5, 0)", ACCENT_COLOR),
            (p_CD, "희생 (C, D)\n(0, 5)", MUTED_COLOR),
            (p_DD, "단계 내쉬 (D, D)\n(1, 1)", PURPLE_COLOR)
        ]
        for pt, label, col in pts:
            ax1.plot(pt[0], pt[1], "o", color=col, markersize=7.5, zorder=6)
            offset = (0.12, 0.12) if pt[0] > 2 else (-0.4, 0.15)
            if np.allclose(pt, p_CC):
                offset = (-0.45, 0.18)
            elif np.allclose(pt, p_DC):
                offset = (0.1, 0.15)
            elif np.allclose(pt, p_CD):
                offset = (0.12, -0.35)
            elif np.allclose(pt, p_DD):
                offset = (-0.45, -0.4)
            ax1.text(pt[0] + offset[0], pt[1] + offset[1], label, color=col, fontsize=8, fontweight="bold", zorder=7)
            
        # Is (3,3) sustainable?
        coop_sustained = (delta >= 0.50)
        status_box = dict(boxstyle="round,pad=0.4", facecolor="#ffffff" if coop_sustained else "#fff1f0", edgecolor=GREEN_COLOR if coop_sustained else ACCENT_COLOR, linewidth=1.3)
        status_text = "상호 협조 (3, 3) 달성 가능! (SPE)" if coop_sustained else "협조 불가 (배반 유인 지배)"
        ax1.text(0.1, 4.9, f"현재 할인인자 $\\delta = {delta:.2f}$\n{status_text}", fontsize=9, color=GREEN_COLOR if coop_sustained else ACCENT_COLOR, fontweight="bold", bbox=status_box, zorder=8)
        
        ax1.legend(loc="lower right", fontsize=7.8, framealpha=0.9, facecolor="#ffffff", edgecolor=GRID_COLOR)

        # --- Right Panel: Incentive Constraint & Threshold delta* ---
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(0, 1.0)
        ax2.set_ylim(0, 32)
        ax2.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.7)
        ax2.set_xlabel("할인인자 $\\delta$ (Discount Factor)", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel("정규화 총 보수 (Lifetime Payoff)", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax2.set_title("Grim Trigger 일탈 유인과 임계치 $\\delta^* = 0.50$", fontsize=11.5, color=PRIMARY_COLOR, fontweight="bold", pad=10)
        
        delta_arr = np.linspace(0.05, 0.92, 100)
        # Payoff from cooperation: 3 / (1 - delta)
        pay_coop = 3.0 / (1.0 - delta_arr)
        # Payoff from one-shot deviation: 5 + delta * 1 / (1 - delta)
        pay_defect = 5.0 + (delta_arr * 1.0) / (1.0 - delta_arr)
        
        ax2.plot(delta_arr, pay_coop, color=GREEN_COLOR, linewidth=2.2, label="협조 지속 보수: $\\frac{3}{1-\\delta}$")
        ax2.plot(delta_arr, pay_defect, color=ACCENT_COLOR, linewidth=2.2, linestyle="--", label="1기 배반 후 처벌: $5 + \\frac{\\delta}{1-\\delta}$")
        
        # Mark delta* = 0.5
        delta_star = 0.50
        val_star = 3.0 / (1.0 - delta_star)  # 6.0
        ax2.axvline(delta_star, color=GOLD_COLOR, linestyle="-.", linewidth=1.5, label="임계 할인인자 $\\delta^* = 0.50$")
        ax2.plot([delta_star], [val_star], "o", color=GOLD_COLOR, markersize=7.5, zorder=5)
        
        # Shade cooperation zone
        ax2.axvspan(delta_star, 1.0, color="#d4edda", alpha=0.25, label="협조 유지 가능 구간 $(\\delta \\geq 0.50)$")
        ax2.axvspan(0.0, delta_star, color="#f8d7da", alpha=0.2, label="배반 우세 구간 $(\\delta < 0.50)$")
        
        # Current delta point
        curr_coop = 3.0 / (1.0 - delta)
        curr_defect = 5.0 + (delta * 1.0) / (1.0 - delta)
        ax2.plot([delta], [curr_coop], "o", color=GREEN_COLOR, markersize=8, zorder=6)
        ax2.plot([delta], [curr_defect], "s", color=ACCENT_COLOR, markersize=7.5, zorder=6)
        
        diff = curr_coop - curr_defect
        diff_str = f"협조 순이득: {diff:+.2f}"
        diff_col = GREEN_COLOR if diff >= 0 else ACCENT_COLOR
        ax2.text(0.05, 27.5, f"$\\delta = {delta:.2f}$\n협조 보수 = {curr_coop:.1f}\n배반 보수 = {curr_defect:.1f}\n{diff_str}", 
                 fontsize=8.5, color=diff_col, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor=diff_col, linewidth=1.2))

        ax2.legend(loc="upper left", fontsize=7.8, framealpha=0.9, facecolor="#ffffff", edgecolor=GRID_COLOR)

        plt.tight_layout()
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)

    gif_path = os.path.join(GIF_DIR, "repeated-game-convex-hull-folk-theorem.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=150, loop=0)
    print(f"Saved: {gif_path} ({len(frames)} frames)")


# ==============================================================================
# 2. GIF 2: Grim Trigger vs Defection Dynamics Across Time Horizons
# ==============================================================================
def generate_gif_grim_trigger_dynamics():
    print("Generating GIF 2: repeated-game-grim-trigger-dynamics.gif ...")
    
    # Simulate time paths for t = 0 to 12
    # Two scenarios:
    # 1. Patient player (delta = 0.70 > 0.50): Cooperation is optimal
    # 2. Impatient player (delta = 0.35 < 0.50): Defection temptation dominates
    T = 12
    time_steps = np.arange(0, T + 1)
    
    # Scenario A: Full Cooperation
    pay_A1 = np.full(T + 1, 3.0)
    pay_A2 = np.full(T + 1, 3.0)
    
    # Scenario B: Defection at tau = 3
    tau = 3
    pay_B1 = np.zeros(T + 1)
    pay_B2 = np.zeros(T + 1)
    for t in range(T + 1):
        if t < tau:
            pay_B1[t], pay_B2[t] = 3.0, 3.0  # (C, C)
        elif t == tau:
            pay_B1[t], pay_B2[t] = 5.0, 0.0  # (D, C) Defection!
        else:
            pay_B1[t], pay_B2[t] = 1.0, 1.0  # Grim Trigger punishment forever (D, D)

    # Frame animation sweeping through time t = 0 to T
    frames = []
    
    for cur_t in range(0, T + 1):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.5, 6.2), facecolor=BG_COLOR)
        
        # --- Top Panel: Period-by-Period Payoff Timeline ---
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(-0.5, T + 0.5)
        ax1.set_ylim(-0.5, 6.0)
        ax1.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.7)
        ax1.set_xlabel("게임 진행 기간 ($t$)", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel("기간별 보수 ($u_{1,t}$)", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax1.set_title("시간 흐름에 따른 기간별 보수: 지속적 협조 vs 3기 일탈(Grim Trigger)", fontsize=11, color=PRIMARY_COLOR, fontweight="bold", pad=8)
        
        # Plot Path A (Cooperation) up to cur_t
        ax1.plot(time_steps[:cur_t+1], pay_A1[:cur_t+1], "-o", color=GREEN_COLOR, linewidth=2.2, markersize=6.5, label="경로 A: 지속적 협조 (C, C) 계속")
        
        # Plot Path B (Defection at tau=3) up to cur_t
        ax1.plot(time_steps[:cur_t+1], pay_B1[:cur_t+1], "-s", color=ACCENT_COLOR, linewidth=2.2, markersize=6.5, label="경로 B: 3기 일탈 후 영구 응징")
        
        # Highlight deviation period tau = 3
        if cur_t >= tau:
            ax1.axvline(tau, color=ACCENT_COLOR, linestyle=":", linewidth=1.5)
            ax1.annotate("3기 일탈 ($u_1 = 5$)\n배반의 단기 유혹!", xy=(tau, 5.0), xytext=(tau + 0.5, 5.2),
                         arrowprops=dict(facecolor=ACCENT_COLOR, shrink=0.08, width=1.5, headwidth=6),
                         fontsize=8.5, color=ACCENT_COLOR, fontweight="bold")
        if cur_t > tau:
            ax1.annotate("4기 이후: 영구 내쉬 처벌 ($u_1 = 1$)", xy=(cur_t, 1.0), xytext=(max(tau+1.2, cur_t - 2.5), 1.9),
                         arrowprops=dict(facecolor=PURPLE_COLOR, shrink=0.08, width=1.2, headwidth=5),
                         fontsize=8.5, color=PURPLE_COLOR, fontweight="bold")
            
        ax1.legend(loc="upper right", fontsize=8.2, framealpha=0.9, facecolor="#ffffff", edgecolor=GRID_COLOR)

        # --- Bottom Panel: Cumulative Discounted Payoff Comparison (delta = 0.7 vs delta = 0.35) ---
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(-0.5, T + 0.5)
        ax2.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.7)
        ax2.set_xlabel("게임 진행 기간 ($t$)", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel("누적 할인 보수 $\\sum_{\\tau=0}^t \\delta^\\tau u_{1,\\tau}$", fontsize=9.5, color=INK_COLOR, fontweight="bold")
        ax2.set_title("할인인자 크기에 따른 누적 보수 역전: 인내심($\\delta=0.7$) vs 조급함($\\delta=0.35$)", fontsize=11, color=PRIMARY_COLOR, fontweight="bold", pad=8)
        
        # Calculate discounted cumulative sums
        delta_high = 0.70
        delta_low = 0.35
        
        cum_coop_high = np.cumsum(pay_A1 * (delta_high ** time_steps))
        cum_dev_high = np.cumsum(pay_B1 * (delta_high ** time_steps))
        
        cum_coop_low = np.cumsum(pay_A1 * (delta_low ** time_steps))
        cum_dev_low = np.cumsum(pay_B1 * (delta_low ** time_steps))
        
        # Plot for delta = 0.70
        ax2.plot(time_steps[:cur_t+1], cum_coop_high[:cur_t+1], "-o", color=GREEN_COLOR, linewidth=2.0, markersize=5.5, label="인내심 충분 ($\\delta=0.70$): 협조 유지")
        ax2.plot(time_steps[:cur_t+1], cum_dev_high[:cur_t+1], "--o", color=ACCENT_COLOR, linewidth=2.0, markersize=5.5, label="인내심 충분 ($\\delta=0.70$): 일탈 (장기 손실!)")
        
        # Plot for delta = 0.35
        ax2.plot(time_steps[:cur_t+1], cum_coop_low[:cur_t+1], "-s", color="#3b82f6", linewidth=1.5, alpha=0.7, markersize=4.5, label="조급함 ($\\delta=0.35$): 협조")
        ax2.plot(time_steps[:cur_t+1], cum_dev_low[:cur_t+1], "--s", color="#f97316", linewidth=1.5, alpha=0.7, markersize=4.5, label="조급함 ($\\delta=0.35$): 일탈이 영구 우세!")
        
        if cur_t >= 6:
            # Show payoff reversal annotation for delta = 0.7
            diff_high = cum_coop_high[cur_t] - cum_dev_high[cur_t]
            ax2.text(cur_t - 2.8, cum_coop_high[cur_t] - 1.2, f"$\\delta=0.70$ 역전!\n협조 우위 (+{diff_high:.2f})", 
                     fontsize=8, color=GREEN_COLOR, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="#e8f5e9", edgecolor=GREEN_COLOR))
            
        ax2.legend(loc="upper left", fontsize=7.8, framealpha=0.9, facecolor="#ffffff", edgecolor=GRID_COLOR)

        plt.tight_layout()
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)
        
    # Append a few static pause frames at the end
    frames.extend([frames[-1]] * 6)

    gif_path = os.path.join(GIF_DIR, "repeated-game-grim-trigger-dynamics.gif")
    frames[0].save(gif_path, save_all=True, append_images=frames[1:], duration=280, loop=0)
    print(f"Saved: {gif_path} ({len(frames)} frames)")


if __name__ == "__main__":
    generate_gif_convex_hull_folk()
    generate_gif_grim_trigger_dynamics()
    print("All Repeated Game GIFs successfully generated!")
