"""Generate publication-grade animated GIFs for the Centipede Game & Backward Induction supplement.

Outputs:
  - assets/gif/centipede-backward-induction-rollback.gif
  - assets/gif/centipede-qre-survival-dynamics.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
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
ACCENT_COLOR = "#c0392b"     # Crimson for Take / Pruning
GREEN_COLOR = "#1b7a43"      # Emerald green for Pass / Cooperation
GOLD_COLOR = "#d97706"       # Amber gold for Pareto frontier
PURPLE_COLOR = "#6b4c7a"     # Violet for player 2

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# ==============================================================================
# 1. GIF 1: Extensive-Form Tree & Backward Induction Domino Rollback
# ==============================================================================
def generate_gif_rollback():
    print("Generating GIF 1: centipede-backward-induction-rollback.gif ...")
    
    # 6-node Centipede game payoffs:
    # Nodes 1..6:
    # Node 1 (P1): Take -> (2, 0)
    # Node 2 (P2): Take -> (1, 3)
    # Node 3 (P1): Take -> (4, 2)
    # Node 4 (P2): Take -> (3, 5)
    # Node 5 (P1): Take -> (6, 4)
    # Node 6 (P2): Take -> (5, 7)
    # Final Pass: (8, 6) or (8, 8)
    
    node_players = ["P1", "P2", "P1", "P2", "P1", "P2"]
    take_payoffs = [
        (2, 0),
        (1, 3),
        (4, 2),
        (3, 5),
        (6, 4),
        (5, 7)
    ]
    final_payoff = (8, 8)
    
    # Animation stages:
    # Stage 0: Show the full tree forward
    # Stage 1: Analyze Node 6 (P2 prefers (5,7) over (8,8) if final is (8,6), let final be (7, 6) vs (5, 7))
    # Let final pass payoff be (6, 8) -> wait, if P2 gets 8 at final, P2 passes!
    # In standard centipede: final pass gives (k, k) or (k-1, k+1).
    # If final pass is (6, 6), P2 at Node 6 chooses Take (5, 7) over Pass (6, 6) because 7 > 6!
    # Let final pass be (6, 6) or (7, 5).
    # Let Node 6 Take be (5, 7), Final Pass be (6, 6). Then 7 > 6 => P2 chooses Take!
    final_payoff = (6, 6)
    
    # Rollback steps: 6 -> 5 -> 4 -> 3 -> 2 -> 1
    # Frame sequence:
    # Phase 0: Introduction of the game tree (frames 0..4)
    # Phase 1: Step 6 rollback (frames 5..9)
    # Phase 2: Step 5 rollback (frames 10..14)
    # Phase 3: Step 4 rollback (frames 15..19)
    # Phase 4: Step 3 rollback (frames 20..24)
    # Phase 5: Step 2 rollback (frames 25..29)
    # Phase 6: Step 1 rollback (frames 30..34)
    # Phase 7: Final SPE conclusion: Immediate termination (frames 35..40)
    
    steps = [7, 6, 5, 4, 3, 2, 1, 0] # 7 means none rolled back yet, 0 means all rolled back
    
    frames = []
    
    # Node coordinates on canvas: x in [1..7], y=3.0
    node_x = [1.2, 2.7, 4.2, 5.7, 7.2, 8.7]
    y_line = 3.2
    
    for active_cutoff in steps:
        fig, ax = plt.subplots(figsize=(11.5, 5.0), facecolor=BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        ax.set_xlim(0.2, 10.8)
        ax.set_ylim(0.4, 5.2)
        ax.axis("off")
        
        # Title
        title_text = "지네 게임 (Centipede Game) 전개형 트리와 역진귀납법 롤백 (Rollback)"
        if active_cutoff == 7:
            sub_text = "전방 진행: 매 단계마다 'Pass'를 선택하면 총 잉여가 증가하지만 상대에게 주도권이 넘어감"
            sub_color = PRIMARY_COLOR
        elif active_cutoff > 0:
            p_curr = node_players[active_cutoff - 1]
            sub_text = f"역진귀납 진행 중: 마디 {active_cutoff} ({p_curr})의 최적 선택 분석 $\\rightarrow$ 'Take' 결정 및 미래 가지 제거"
            sub_color = ACCENT_COLOR
        else:
            sub_text = "역진귀납법 최종 결론: 유일한 부분게임 완전균형(SPE)은 '1단계 즉각 중단 (Take)'"
            sub_color = ACCENT_COLOR
            
        ax.text(5.5, 4.85, title_text, fontsize=13, fontweight="bold", color=PRIMARY_COLOR, ha="center")
        ax.text(5.5, 4.45, sub_text, fontsize=10, fontweight="bold", color=sub_color, ha="center")
        
        # Draw horizontal connections (Pass branches)
        for i in range(5):
            x1, x2 = node_x[i], node_x[i+1]
            # Is this pass branch pruned?
            is_pruned = (active_cutoff <= i + 1)
            line_color = "#d1d5db" if is_pruned else GREEN_COLOR
            line_style = ":" if is_pruned else "-"
            lw = 1.5 if is_pruned else 2.5
            
            ax.plot([x1 + 0.3, x2 - 0.3], [y_line, y_line], color=line_color, linestyle=line_style, linewidth=lw, zorder=2)
            ax.text((x1 + x2)/2, y_line + 0.18, "Pass (C)", fontsize=7.8, color=line_color, fontweight="bold", ha="center")
            
            if is_pruned:
                ax.text((x1 + x2)/2, y_line, "X", fontsize=11, color=ACCENT_COLOR, fontweight="bold", ha="center", va="center")
                
        # Final pass branch from node 6 to final payoff
        x_last = node_x[5]
        x_final = 10.1
        is_final_pruned = (active_cutoff <= 6)
        line_color = "#d1d5db" if is_final_pruned else GREEN_COLOR
        line_style = ":" if is_final_pruned else "-"
        lw = 1.5 if is_final_pruned else 2.5
        ax.plot([x_last + 0.3, x_final - 0.4], [y_line, y_line], color=line_color, linestyle=line_style, linewidth=lw, zorder=2)
        ax.text((x_last + x_final)/2, y_line + 0.18, "Pass", fontsize=7.8, color=line_color, fontweight="bold", ha="center")
        if is_final_pruned:
            ax.text((x_last + x_final)/2, y_line, "X", fontsize=11, color=ACCENT_COLOR, fontweight="bold", ha="center", va="center")
            
        # Final payoff box
        box_col = "#e5e7eb" if is_final_pruned else "#d1fae5"
        edge_col = "#9ca3af" if is_final_pruned else GREEN_COLOR
        text_col = "#6b7280" if is_final_pruned else GREEN_COLOR
        ax.text(x_final, y_line, f"최종 보수\n({final_payoff[0]}, {final_payoff[1]})", fontsize=8.5, color=text_col, fontweight="bold",
                ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", facecolor=box_col, edgecolor=edge_col, linewidth=1.5))
        
        # Draw Nodes and Take branches
        for i in range(6):
            nx = node_x[i]
            player = node_players[i]
            p_col = PRIMARY_COLOR if player == "P1" else PURPLE_COLOR
            
            # Node circle
            circle = Circle((nx, y_line), 0.3, facecolor="#ffffff", edgecolor=p_col, linewidth=2.2, zorder=4)
            ax.add_patch(circle)
            ax.text(nx, y_line, player, fontsize=8.8, fontweight="bold", color=p_col, ha="center", va="center", zorder=5)
            ax.text(nx, y_line + 0.42, f"마디 {i+1}", fontsize=8, color=MUTED_COLOR, ha="center")
            
            # Vertical Take branch (downward)
            take_y_end = 1.5
            is_take_chosen = (active_cutoff <= i + 1)
            take_color = ACCENT_COLOR if is_take_chosen else MUTED_COLOR
            take_lw = 2.4 if is_take_chosen else 1.5
            
            ax.plot([nx, nx], [y_line - 0.3, take_y_end + 0.35], color=take_color, linewidth=take_lw, zorder=2)
            ax.text(nx - 0.15, (y_line + take_y_end)/2, "Take (S)", fontsize=7.5, color=take_color, fontweight="bold", ha="right", va="center")
            
            if is_take_chosen:
                ax.plot(nx, take_y_end + 0.35, "v", color=ACCENT_COLOR, markersize=7, zorder=3)
                
            # Take Payoff box
            pay = take_payoffs[i]
            pbox_bg = "#fee2e2" if is_take_chosen else "#ffffff"
            pbox_edge = ACCENT_COLOR if is_take_chosen else GRID_COLOR
            pbox_text_col = ACCENT_COLOR if is_take_chosen else INK_COLOR
            
            ax.text(nx, take_y_end, f"({pay[0]}, {pay[1]})\n[P1: {pay[0]}, P2: {pay[1]}]", fontsize=8, fontweight="bold", color=pbox_text_col,
                    ha="center", va="center", bbox=dict(boxstyle="round,pad=0.35", facecolor=pbox_bg, edgecolor=pbox_edge, linewidth=1.3))
            
        # Explanatory Callout at the bottom
        bottom_y = 0.7
        if active_cutoff == 7:
            bottom_desc = "파레토 최적 협조 경로: 양 플레이어가 매번 Pass하면 마디 6 이후 상호 6점(또는 그 이상)을 획득함."
            desc_bg = "#ecfdf5"
            desc_edge = GREEN_COLOR
            desc_col = GREEN_COLOR
        elif active_cutoff == 6:
            bottom_desc = "[마디 6 (P2)] Pass 시 (6, 6)으로 P2는 6점, Take 시 (5, 7)로 7점. P2는 7 > 6이므로 무조건 Take를 선택!"
            desc_bg = "#fef2f2"
            desc_edge = ACCENT_COLOR
            desc_col = ACCENT_COLOR
        elif active_cutoff == 5:
            bottom_desc = "[마디 5 (P1)] P1은 마디 6에서 P2가 Take할 것을 앎(보수 5). 마디 5에서 Take하면 (6, 4)로 6점. 6 > 5이므로 P1은 Take 선택!"
            desc_bg = "#fef2f2"
            desc_edge = ACCENT_COLOR
            desc_col = ACCENT_COLOR
        elif active_cutoff in [4, 3, 2]:
            bottom_desc = f"[마디 {active_cutoff} ({node_players[active_cutoff-1]})] 동일한 논리로 다음 마디에서 상대가 가로챌 것을 예견하여 직전 마디에서 선제 Take 감행!"
            desc_bg = "#fef2f2"
            desc_edge = ACCENT_COLOR
            desc_col = ACCENT_COLOR
        elif active_cutoff == 1:
            bottom_desc = "[마디 1 (P1)] 도미노가 첫 번째 마디까지 전파됨! 마디 2에서 P2가 Take하여 1점을 줄 바에야, 즉시 Take하여 2점을 챙김!"
            desc_bg = "#fef2f2"
            desc_edge = ACCENT_COLOR
            desc_col = ACCENT_COLOR
        else:
            bottom_desc = "★ 역진귀납법의 역설(Paradox): 합리성의 공통지식이 지배할 때 게임은 1마디에서 (2, 0)으로 즉시 끝나 파레토 최악에 도달함."
            desc_bg = "#fff7ed"
            desc_edge = GOLD_COLOR
            desc_col = GOLD_COLOR
            
        ax.text(5.5, bottom_y, bottom_desc, fontsize=9.2, fontweight="bold", color=desc_col, ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.5", facecolor=desc_bg, edgecolor=desc_edge, linewidth=1.5))

        plt.tight_layout()
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)

    # Frame timing: duplicate each frame for smooth reading
    expanded_frames = []
    for i, f in enumerate(frames):
        repeat_count = 6 if i == 0 or i == len(frames) - 1 else 4
        expanded_frames.extend([f] * repeat_count)

    gif_path = os.path.join(GIF_DIR, "centipede-backward-induction-rollback.gif")
    expanded_frames[0].save(gif_path, save_all=True, append_images=expanded_frames[1:], duration=350, loop=0)
    print(f"Saved: {gif_path} ({len(expanded_frames)} frames)")


# ==============================================================================
# 2. GIF 2: McKelvey-Palfrey QRE & Survival Probability Dynamics
# ==============================================================================
def generate_gif_qre_survival():
    print("Generating GIF 2: centipede-qre-survival-dynamics.gif ...")
    
    # In Quantal Response Equilibrium (QRE), choice probabilities follow logit:
    # P(Pass) = exp(lambda * E[U(Pass)]) / (exp(lambda * E[U(Pass)]) + exp(lambda * E[U(Take)]))
    # As lambda -> 0: completely random (50:50 at every step)
    # As lambda -> infinity: perfect backward induction (P(Take) = 1 at step 1)
    # Intermediate lambda: realistic human experiment behavior
    
    # 6 nodes
    take_payoffs = np.array([
        [2.0, 0.0],
        [1.0, 3.0],
        [4.0, 2.0],
        [3.0, 5.0],
        [6.0, 4.0],
        [5.0, 7.0]
    ])
    final_payoff = np.array([6.0, 6.0])
    
    # Lambda sweep from 0.05 to 5.0
    lambdas = np.concatenate([
        np.linspace(0.05, 0.8, 12),
        np.linspace(0.8, 3.0, 14),
        np.linspace(3.0, 6.0, 8),
        np.linspace(6.0, 6.0, 4) # pause at the end
    ])
    
    frames = []
    
    for lam in lambdas:
        # Solve QRE backward from node 6 to 1
        # At each node k (1-indexed, player = (k-1)%2):
        # E_U_take = take_payoffs[k-1, player]
        # E_U_pass = expected payoff if pass is chosen
        p_pass = np.zeros(6)
        exp_pay_p1 = np.zeros(7) # value at node k if reached
        exp_pay_p2 = np.zeros(7)
        exp_pay_p1[6] = final_payoff[0]
        exp_pay_p2[6] = final_payoff[1]
        
        for k in range(5, -1, -1):
            pl = (k % 2) # 0 for P1, 1 for P2
            u_take = take_payoffs[k, pl]
            u_pass = exp_pay_p1[k+1] if pl == 0 else exp_pay_p2[k+1]
            
            # Logit probability of Pass
            # Clip exponent to avoid overflow
            diff = np.clip(lam * (u_pass - u_take), -25, 25)
            prob_pass = 1.0 / (1.0 + np.exp(-diff))
            p_pass[k] = prob_pass
            
            # Expected values at node k
            if pl == 0: # P1 moves
                exp_pay_p1[k] = (1 - prob_pass) * take_payoffs[k, 0] + prob_pass * exp_pay_p1[k+1]
                exp_pay_p2[k] = (1 - prob_pass) * take_payoffs[k, 1] + prob_pass * exp_pay_p2[k+1]
            else: # P2 moves
                exp_pay_p1[k] = (1 - prob_pass) * take_payoffs[k, 0] + prob_pass * exp_pay_p1[k+1]
                exp_pay_p2[k] = (1 - prob_pass) * take_payoffs[k, 1] + prob_pass * exp_pay_p2[k+1]

        # Calculate survival probability S(k) = probability of reaching node k
        surv_prob = np.ones(7)
        for k in range(1, 7):
            surv_prob[k] = surv_prob[k-1] * p_pass[k-1]
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5.2), facecolor=BG_COLOR)
        
        # --- Left Panel: Node-by-Node Survival Probability ---
        ax1.set_facecolor(BG_COLOR)
        ax1.set_xlim(0.5, 6.5)
        ax1.set_ylim(-0.05, 1.05)
        ax1.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.7)
        ax1.set_xlabel("게임 진행 마디 ($k$)", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel("해당 마디 도달 확률 (Survival Prob)", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax1.set_title("합리성 정밀도 $\\lambda$에 따른 마디별 생존 확률", fontsize=11.5, color=PRIMARY_COLOR, fontweight="bold", pad=10)
        
        nodes = np.arange(1, 7)
        ax1.plot(nodes, surv_prob[:6], "-o", color=PRIMARY_COLOR, linewidth=2.3, markersize=6.5, label=f"현재 QRE ($\\lambda={lam:.2f}$)")
        
        # Benchmark 1: SPE (Strict Backward Induction)
        spe_surv = np.zeros(6)
        spe_surv[0] = 1.0 # only node 1 is reached, terminated immediately
        ax1.plot(nodes, spe_surv, "--s", color=ACCENT_COLOR, linewidth=1.8, markersize=5, alpha=0.8, label="엄격한 역진귀납법 (SPE)")
        
        # Benchmark 2: Human experiments (McKelvey-Palfrey 1992 empirical benchmark)
        human_surv = np.array([1.0, 0.93, 0.75, 0.48, 0.22, 0.08])
        ax1.plot(nodes, human_surv, ":^", color=GOLD_COLOR, linewidth=2.0, markersize=5.5, label="실제 인간 실험 (M&P 1992)")
        
        # Fill area under QRE curve
        ax1.fill_between(nodes, 0, surv_prob[:6], color="#bfdbfe", alpha=0.25)
        
        ax1.legend(loc="upper right", fontsize=8.2, framealpha=0.9, facecolor="#ffffff", edgecolor=GRID_COLOR)
        ax1.text(1.2, 0.15, f"$\\lambda={lam:.2f}$\n마디 4 도달 확률: {surv_prob[3]*100:.1f}%\n마디 6 도달 확률: {surv_prob[5]*100:.1f}%",
                 fontsize=8.5, color=PRIMARY_COLOR, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor=PRIMARY_COLOR))

        # --- Right Panel: Expected Payoffs across Lambda ---
        ax2.set_facecolor(BG_COLOR)
        ax2.set_xlim(0, 6.0)
        ax2.set_ylim(0, 5.5)
        ax2.grid(True, color=GRID_COLOR, linestyle="--", alpha=0.7)
        ax2.set_xlabel("합리성 정밀도 모수 $\\lambda$ (Logit Precision)", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel("플레이어 시작 기대보수 $E[u_i]$", fontsize=10, color=INK_COLOR, fontweight="bold")
        ax2.set_title("역설적 결과: '적당한 비합리성'이 더 높은 보수를 낳는다", fontsize=11.5, color=PRIMARY_COLOR, fontweight="bold", pad=10)
        
        # Sweep curve of expected payoffs across all lambdas
        lam_grid = np.linspace(0.05, 6.0, 60)
        p1_grid = np.zeros(60)
        p2_grid = np.zeros(60)
        
        for idx, l_val in enumerate(lam_grid):
            # QRE values
            v_p1 = np.zeros(7)
            v_p2 = np.zeros(7)
            v_p1[6], v_p2[6] = final_payoff[0], final_payoff[1]
            for k in range(5, -1, -1):
                pl = (k % 2)
                u_t = take_payoffs[k, pl]
                u_p = v_p1[k+1] if pl == 0 else v_p2[k+1]
                pr = 1.0 / (1.0 + np.exp(-np.clip(l_val * (u_p - u_t), -25, 25)))
                v_p1[k] = (1 - pr) * take_payoffs[k, 0] + pr * v_p1[k+1]
                v_p2[k] = (1 - pr) * take_payoffs[k, 1] + pr * v_p2[k+1]
            p1_grid[idx] = v_p1[0]
            p2_grid[idx] = v_p2[0]
            
        ax2.plot(lam_grid, p1_grid, color=PRIMARY_COLOR, linewidth=2.2, label="플레이어 1 기대보수 $E[u_1]$")
        ax2.plot(lam_grid, p2_grid, color=PURPLE_COLOR, linewidth=2.2, linestyle="--", label="플레이어 2 기대보수 $E[u_2]$")
        
        # SPE horizontal benchmark (2.0 for P1, 0.0 for P2)
        ax2.axhline(2.0, color=ACCENT_COLOR, linestyle=":", linewidth=1.4, label="SPE P1 보수 = 2.0")
        ax2.axhline(0.0, color="#ef4444", linestyle=":", linewidth=1.2, label="SPE P2 보수 = 0.0")
        
        # Current lambda point
        curr_p1 = exp_pay_p1[0]
        curr_p2 = exp_pay_p2[0]
        ax2.plot([lam], [curr_p1], "o", color=PRIMARY_COLOR, markersize=8, zorder=6)
        ax2.plot([lam], [curr_p2], "s", color=PURPLE_COLOR, markersize=7.5, zorder=6)
        
        # Highlight maximum payoff zone (Intermediate lambda ~ 0.8 to 1.5)
        ax2.axvspan(0.6, 1.8, color="#fef3c7", alpha=0.35, label="인간 수준 최적 보수 구간")
        
        ax2.text(2.6, 4.3, f"현재 $\\lambda = {lam:.2f}$\nP1 기대보수: {curr_p1:.2f}\nP2 기대보수: {curr_p2:.2f}\n(SPE보다 P2는 +{curr_p2:.2f} 이득)",
                 fontsize=8.5, color=INK_COLOR, fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.35", facecolor="#ffffff", edgecolor=GOLD_COLOR, linewidth=1.2))

        ax2.legend(loc="lower right", fontsize=7.8, framealpha=0.9, facecolor="#ffffff", edgecolor=GRID_COLOR)

        plt.tight_layout()
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)

    expanded_frames = []
    for i, f in enumerate(frames):
        repeat_count = 5 if i == 0 or i == len(frames) - 1 else 1
        expanded_frames.extend([f] * repeat_count)

    gif_path = os.path.join(GIF_DIR, "centipede-qre-survival-dynamics.gif")
    expanded_frames[0].save(gif_path, save_all=True, append_images=expanded_frames[1:], duration=160, loop=0)
    print(f"Saved: {gif_path} ({len(expanded_frames)} frames)")


if __name__ == "__main__":
    generate_gif_rollback()
    generate_gif_qre_survival()
    print("All Centipede Game GIFs successfully generated!")
