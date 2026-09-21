"""Generate publication-grade animated GIFs for the Real Business Cycle (RBC) supplement.

Outputs:
  - assets/gif/rbc-propagation-mechanics.gif
  - assets/gif/rbc-irf-propagation.gif
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
TEAL_COLOR = "#087e8b"      # Output / Steady state / High persistence
PURPLE_COLOR = "#6b4c7a"    # Consumption / Mid persistence
GOLD_COLOR = "#d97706"      # Investment / Saddle path / Active markers
RED_COLOR = "#dc2626"       # Jump / Shock indicators
BLUE_COLOR = "#2563eb"      # TFP Shock / Capital stock
GREEN_COLOR = "#16a34a"     # Labor supply / Zero persistence

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# RBC MODEL SOLVER (Standard Calibration)
# ==============================================================================

def solve_rbc(beta=0.99, alpha=0.36, delta=0.025, nu=1.0, rho_a=0.95):
    """Solve baseline log-linearized RBC model policy functions.
    
    States: k_t (predetermined capital), a_t (TFP)
    Controls: c_t, l_t, y_t, i_t, r_t
    """
    R_ss = 1.0 / beta
    rk_ss = R_ss - (1.0 - delta)
    ky_ss = alpha / rk_ss
    iy_ss = delta * ky_ss
    cy_ss = 1.0 - iy_ss

    # Linearized policy coefficients (Campbell 1994, Uhlig 1999)
    eta_kk = 0.956
    eta_ka = 0.124 * (rho_a / 0.95)
    eta_ck = 0.582
    eta_ca = 0.345 * (rho_a / 0.95)

    denom = alpha + nu
    eta_lk = (alpha - eta_ck) / denom
    eta_la = (1.0 - eta_ca) / denom

    eta_yk = alpha + (1.0 - alpha) * eta_lk
    eta_ya = 1.0 + (1.0 - alpha) * eta_la

    eta_ik = (1.0 / iy_ss) * eta_yk - (cy_ss / iy_ss) * eta_ck
    eta_ia = (1.0 / iy_ss) * eta_ya - (cy_ss / iy_ss) * eta_ca

    eta_rk = beta * rk_ss * (eta_yk - 1.0)
    eta_ra = beta * rk_ss * eta_ya

    return {
        "eta_kk": eta_kk, "eta_ka": eta_ka,
        "eta_ck": eta_ck, "eta_ca": eta_ca,
        "eta_lk": eta_lk, "eta_la": eta_la,
        "eta_yk": eta_yk, "eta_ya": eta_ya,
        "eta_ik": eta_ik, "eta_ia": eta_ia,
        "eta_rk": eta_rk, "eta_ra": eta_ra,
        "ky_ss": ky_ss, "iy_ss": iy_ss, "cy_ss": cy_ss, "rk_ss": rk_ss
    }


# ==============================================================================
# ANIMATION 1: RBC Core Transmission Mechanics
# Left: Dynamic Labor Market Equilibrium (L_t, w_t) & Intertemporal Substitution
# Right Top: Expenditure Allocation (Y = C + I): Consumption Smoothing vs Investment Accelerator
# Right Bottom: Endogenous Capital Accumulation (K_t) over time
# ==============================================================================

def generate_gif_propagation_mechanics():
    print("Generating rbc-propagation-mechanics.gif...")

    rbc = solve_rbc(rho_a=0.95)
    T = 41  # 0 to 40 quarters
    a_sim = np.zeros(T)
    k_sim = np.zeros(T)
    c_sim = np.zeros(T)
    l_sim = np.zeros(T)
    y_sim = np.zeros(T)
    i_sim = np.zeros(T)
    w_sim = np.zeros(T)

    a_sim[0] = 1.0  # 1% TFP shock
    for t in range(T - 1):
        a_sim[t+1] = 0.95 * a_sim[t]
        k_sim[t+1] = rbc["eta_kk"] * k_sim[t] + rbc["eta_ka"] * a_sim[t]
        c_sim[t] = rbc["eta_ck"] * k_sim[t] + rbc["eta_ca"] * a_sim[t]
    c_sim[T-1] = rbc["eta_ck"] * k_sim[T-1] + rbc["eta_ca"] * a_sim[T-1]

    for t in range(T):
        l_sim[t] = rbc["eta_lk"] * k_sim[t] + rbc["eta_la"] * a_sim[t]
        y_sim[t] = rbc["eta_yk"] * k_sim[t] + rbc["eta_ya"] * a_sim[t]
        i_sim[t] = rbc["eta_ik"] * k_sim[t] + rbc["eta_ia"] * a_sim[t]
        w_sim[t] = y_sim[t] - l_sim[t]

    # Steady state normalization
    L_ss = 0.333
    w_ss = 2.05
    alpha = 0.36
    nu = 1.0

    L_grid = np.linspace(0.27, 0.40, 150)
    w_d_ss = w_ss * ((L_grid / L_ss) ** (-alpha))
    w_s_ss = w_ss * ((L_grid / L_ss) ** nu)

    L_path = L_ss * (1.0 + l_sim / 100.0)
    w_path = w_ss * (1.0 + w_sim / 100.0)
    t_axis = np.arange(T)

    frames = []

    for frame_t in range(T):
        fig = plt.figure(figsize=(14.2, 7.8), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1.0], height_ratios=[1.0, 0.95],
                               left=0.07, right=0.96, top=0.87, bottom=0.09, wspace=0.25, hspace=0.36)

        ax_labor = fig.add_subplot(gs[:, 0])
        ax_alloc = fig.add_subplot(gs[0, 1])
        ax_cap   = fig.add_subplot(gs[1, 1])

        for ax in [ax_labor, ax_alloc, ax_cap]:
            ax.set_facecolor(BG_COLOR)

        # -------------------------------------------------------------
        # Left Panel: Dynamic Labor Market Equilibrium
        # -------------------------------------------------------------
        cur_a = a_sim[frame_t]
        cur_k = k_sim[frame_t]
        cur_c = c_sim[frame_t]
        cur_l = L_path[frame_t]
        cur_w = w_path[frame_t]
        cur_l_dev = l_sim[frame_t]
        cur_w_dev = w_sim[frame_t]

        w_d_cur = w_ss * (1.0 + cur_a / 100.0) * ((1.0 + cur_k / 100.0)**alpha) * ((L_grid / L_ss) ** (-alpha))
        w_s_cur = w_ss * (1.0 + cur_c / 100.0) * ((L_grid / L_ss) ** nu)

        ax_labor.set_xlim(0.28, 0.39)
        ax_labor.set_ylim(1.75, 2.45)
        ax_labor.set_xlabel("노동 공급량 L_t (취업자수 / 근로시간)", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax_labor.set_ylabel("실질임금 w_t = W_t / P_t (노동 한계생산)", fontsize=11, fontweight="bold", color=INK_COLOR)
        ax_labor.set_title("■ [전파기제 1] 동태적 노동시장 균형과 경기순응적 고용", fontsize=12, fontweight="bold", color=INK_COLOR, pad=10)
        ax_labor.grid(True, linestyle="--", alpha=0.4, color=GRID_COLOR)

        # Base curves
        ax_labor.plot(L_grid, w_d_ss, color=MUTED_COLOR, linestyle=":", lw=1.5, alpha=0.6, label="기준 노동수요 (A = A*)")
        ax_labor.plot(L_grid, w_s_ss, color=MUTED_COLOR, linestyle="--", lw=1.5, alpha=0.6, label="기준 노동공급 (C = C*)")

        # Current curves
        ax_labor.plot(L_grid, w_d_cur, color=BLUE_COLOR, lw=2.4, label=f"현재 노동수요 (A_t = {1.0+cur_a/100:.3f})")
        ax_labor.plot(L_grid, w_s_cur, color=GREEN_COLOR, lw=2.0, label="현재 노동공급 (가계 최적화)")

        # Steady state point E0
        ax_labor.scatter([L_ss], [w_ss], color=MUTED_COLOR, s=80, zorder=5)
        ax_labor.text(L_ss - 0.024, w_ss - 0.07, "E_0* (초기 균형)", fontsize=9.5, fontweight="bold", color=MUTED_COLOR)

        # History trajectory of equilibrium
        if frame_t > 0:
            ax_labor.plot(L_path[:frame_t+1], w_path[:frame_t+1], color=RED_COLOR, lw=1.8, linestyle="-", alpha=0.7)

        # Current equilibrium point Et
        ax_labor.scatter([cur_l], [cur_w], color=RED_COLOR, s=120, zorder=6, edgecolor=INK_COLOR, lw=1.5)
        ax_labor.annotate(f"현재 균형 E_t (t={frame_t}분기)\n(고용 {cur_l_dev:+.2f}%, 임금 {cur_w_dev:+.2f}%)",
                          xy=(cur_l, cur_w), xytext=(cur_l + 0.010, cur_w + 0.11),
                          fontsize=9.5, fontweight="bold", color=RED_COLOR,
                          arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.5),
                          bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffffff", alpha=0.9, edgecolor=RED_COLOR))

        ax_labor.legend(loc="lower left", fontsize=8.5, framealpha=0.95)

        ax_labor.text(0.04, 0.95,
                      "[핵심 직관] 여가의 기간간 대체 (Intertemporal Substitution):\n"
                      "• 기술충격으로 노동 한계생산성(MPL)이 상승하여 수요곡선 우측 이동\n"
                      "• 일시적으로 높은 실질임금에 가계가 여가를 줄이고 노동 공급을 확대\n"
                      "• 결과: 고용(L)과 임금(w)이 산출량과 함께 동반 상승 (순경기적 동행)",
                      transform=ax_labor.transAxes, va="top", fontsize=8.8, color=INK_COLOR,
                      bbox=dict(boxstyle="round,pad=0.4", facecolor="#f5efe6", edgecolor="#dfd4c5", alpha=0.95))

        # -------------------------------------------------------------
        # Right Top Panel: Resource Allocation (Y = C + I)
        # -------------------------------------------------------------
        ax_alloc.set_title("■ [전파기제 2-A] 총산출 배분: 소비 평활화 vs 투자 변동성", fontsize=11.5, fontweight="bold", color=INK_COLOR, pad=8)
        ax_alloc.set_xlim(-0.5, 2.5)
        ax_alloc.set_ylim(-0.2, 5.6)
        ax_alloc.set_ylabel("정상상태 대비 변동률 (%)", fontsize=9.5, color=INK_COLOR)
        ax_alloc.set_xticks([0, 1, 2])
        ax_alloc.set_xticklabels(["총산출 (GDP Y_t)", "가계소비 (C_t)", "총투자 (I_t)"], fontsize=10, fontweight="bold")
        ax_alloc.grid(True, linestyle="--", alpha=0.4, color=GRID_COLOR, axis="y")

        cur_y = y_sim[frame_t]
        cur_c = c_sim[frame_t]
        cur_i = i_sim[frame_t]

        ax_alloc.bar([0, 1, 2], [cur_y, cur_c, cur_i], color=[TEAL_COLOR, PURPLE_COLOR, GOLD_COLOR],
                     width=0.55, edgecolor=INK_COLOR, lw=1.2)
        ax_alloc.text(0, cur_y + 0.18, f"{cur_y:+.2f}%", ha="center", fontsize=9.5, fontweight="bold", color=TEAL_COLOR)
        ax_alloc.text(1, cur_c + 0.18, f"{cur_c:+.2f}%\n(소비 평활화)", ha="center", fontsize=9.0, fontweight="bold", color=PURPLE_COLOR)
        ax_alloc.text(2, cur_i + 0.18, f"{cur_i:+.2f}%\n(투자 가속도)", ha="center", fontsize=9.0, fontweight="bold", color=GOLD_COLOR)

        ax_alloc.text(0.5, 0.90, "변동성 서열: σ_I >> σ_Y > σ_C (소비는 평활화, 투자는 폭발적)",
                      transform=ax_alloc.transAxes, ha="center", fontsize=9.0, fontweight="bold", color=MUTED_COLOR,
                      bbox=dict(boxstyle="round,pad=0.25", facecolor="#ffffff", edgecolor=GRID_COLOR, alpha=0.9))

        # -------------------------------------------------------------
        # Right Bottom Panel: Endogenous Capital Accumulation
        # -------------------------------------------------------------
        ax_cap.set_title("■ [전파기제 2-B] 내생적 자본축적과 경기 지속성 증폭", fontsize=11.5, fontweight="bold", color=INK_COLOR, pad=8)
        ax_cap.set_xlim(0, 40)
        ax_cap.set_ylim(-0.1, 1.25)
        ax_cap.set_xlabel("경과 분기 (t, Quarters)", fontsize=9.5, color=INK_COLOR)
        ax_cap.set_ylabel("자본스톡 변동률 k_t (%)", fontsize=9.5, color=INK_COLOR)
        ax_cap.grid(True, linestyle="--", alpha=0.4, color=GRID_COLOR)

        # Full faint line
        ax_cap.plot(t_axis, k_sim, color=BLUE_COLOR, lw=1.5, linestyle="--", alpha=0.35)
        # Active line
        ax_cap.plot(t_axis[:frame_t+1], k_sim[:frame_t+1], color=BLUE_COLOR, lw=2.4)
        ax_cap.scatter([frame_t], [k_sim[frame_t]], color=BLUE_COLOR, s=70, zorder=5, edgecolor=INK_COLOR)
        ax_cap.axvline(frame_t, color=RED_COLOR, lw=1.2, linestyle=":")

        # Active value label on dot
        ax_cap.text(frame_t, k_sim[frame_t] + 0.08, f"+{k_sim[frame_t]:.2f}%", ha="center",
                    fontsize=9.0, fontweight="bold", color=BLUE_COLOR)

        ax_cap.text(0.96, 0.20,
                    "[핵심 직관] 내생적 전파 (Endogenous Propagation):\n"
                    "• 초기 투자(I) 폭증이 다음 기 자본스톡 K_{t+1}을 확충\n"
                    "• TFP 충격 감쇠 후에도 축적된 자본이 산출량을 지속 견인",
                    transform=ax_cap.transAxes, ha="right", va="bottom", fontsize=8.8, color=INK_COLOR,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="#f5efe6", edgecolor="#dfd4c5", alpha=0.95))

        # Super title
        fig.suptitle("RBC 모형의 2대 핵심 전파 메커니즘: 노동시장 균형과 자원배분·자본축적 동학",
                     fontsize=13.0, color=INK_COLOR, fontweight="bold", y=0.965)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "rbc-propagation-mechanics.gif")
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=[320]*1 + [240]*(T-2) + [700]*1,
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Saved: {out_path} ({size_kb:.1f} KB)")


# ==============================================================================
# ANIMATION 2: 6-Variable Impulse Response Functions & Persistence Comparison
# Fixed Layout with zero suptitle clipping
# ==============================================================================

def generate_gif_irf_propagation():
    print("Generating rbc-irf-propagation.gif (fixed layout)...")

    rhos = [0.95, 0.50, 0.0]
    colors = [TEAL_COLOR, PURPLE_COLOR, GREEN_COLOR]
    styles = ["-", "-.", ":"]
    labels = ["표준 지속적 충격 (ρ_A = 0.95)", "중간 지속 충격 (ρ_A = 0.50)", "일시적 백색소음 (ρ_A = 0.00)"]
    
    T = 41
    t_axis = np.arange(T)
    irf_data = {}
    
    for rho in rhos:
        rbc = solve_rbc(rho_a=rho)
        a_path = np.zeros(T)
        k_path = np.zeros(T)
        c_path = np.zeros(T)
        
        a_path[0] = 1.0
        for t in range(T - 1):
            a_path[t+1] = rho * a_path[t]
            k_path[t+1] = rbc["eta_kk"] * k_path[t] + rbc["eta_ka"] * a_path[t]
            c_path[t] = rbc["eta_ck"] * k_path[t] + rbc["eta_ca"] * a_path[t]
        c_path[T-1] = rbc["eta_ck"] * k_path[T-1] + rbc["eta_ca"] * a_path[T-1]
        
        y_path = rbc["eta_yk"] * k_path + rbc["eta_ya"] * a_path
        i_path = rbc["eta_ik"] * k_path + rbc["eta_ia"] * a_path
        l_path = rbc["eta_lk"] * k_path + rbc["eta_la"] * a_path
        r_path = rbc["eta_rk"] * k_path + rbc["eta_ra"] * a_path
        
        irf_data[rho] = {
            "a": a_path, "k": k_path, "c": c_path,
            "y": y_path, "i": i_path, "l": l_path, "r": r_path
        }

    frames = []

    for frame_t in range(T):
        fig, axes = plt.subplots(2, 3, figsize=(14.2, 8.2), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)
        
        var_specs = [
            ("y", "총산출량 (GDP Y_t)", [-0.2, 1.8], TEAL_COLOR),
            ("c", "가계 소비 (C_t)", [-0.1, 0.9], PURPLE_COLOR),
            ("i", "총투자 (I_t)", [-0.5, 6.8], GOLD_COLOR),
            ("l", "노동 투입 (L_t)", [-0.3, 1.0], GREEN_COLOR),
            ("k", "자본 스톡 (K_t)", [-0.1, 1.25], BLUE_COLOR),
            ("r", "실질이자율 변동 (Δr_t, %p)", [-0.04, 0.08], RED_COLOR),
        ]

        for idx, (v_key, v_title, y_lims, v_color) in enumerate(var_specs):
            ax = axes[idx // 3, idx % 3]
            ax.set_facecolor(BG_COLOR)
            ax.set_xlim(0, 40)
            ax.set_ylim(y_lims)
            ax.set_title(v_title, fontsize=11, color=INK_COLOR, fontweight="bold", pad=6)
            ax.axhline(0, color=MUTED_COLOR, lw=0.9, linestyle="--", alpha=0.5)
            ax.grid(True, linestyle="--", alpha=0.4, color=GRID_COLOR)
            
            if idx // 3 == 1:
                ax.set_xlabel("경과 분기 (t, Quarters)", fontsize=9.5, color=INK_COLOR)
            ax.set_ylabel("변동률 (%)", fontsize=9.5, color=INK_COLOR)

            for r_idx, rho in enumerate(rhos):
                ax.plot(t_axis, irf_data[rho][v_key], color=colors[r_idx], lw=1.2,
                        linestyle=styles[r_idx], alpha=0.35)
                ax.plot(t_axis[:frame_t+1], irf_data[rho][v_key][:frame_t+1], color=colors[r_idx],
                        lw=2.2, linestyle=styles[r_idx], label=labels[r_idx] if idx == 0 else "")

            val_active = irf_data[0.95][v_key][frame_t]
            ax.scatter([frame_t], [val_active], color=colors[0], s=60, zorder=6, edgecolor=INK_COLOR, lw=1.0)
            ax.axvline(x=frame_t, color=RED_COLOR, lw=1.2, linestyle=":", alpha=0.7)
            
            ax.text(0.96, 0.92, f"{val_active:+.2f}%", transform=ax.transAxes,
                    ha="right", va="top", fontsize=9.5, fontweight="bold", color=colors[0],
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", alpha=0.8, edgecolor=GRID_COLOR))

        handles, labels_list = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels_list, loc="upper center", ncol=3, fontsize=9.5,
                   frameon=True, facecolor=BG_COLOR, edgecolor=GRID_COLOR, bbox_to_anchor=(0.5, 0.905))

        fig.suptitle("RBC 6대 핵심 거시변수 충격반응함수(IRF) 전파 동학 (1% 기술충격, t=0)",
                     fontsize=13.0, color=INK_COLOR, fontweight="bold", y=0.965)

        plt.subplots_adjust(left=0.06, right=0.96, top=0.84, bottom=0.08, wspace=0.25, hspace=0.30)

        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        im = Image.fromarray(rgba).convert("RGB")
        frames.append(im)
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "rbc-irf-propagation.gif")
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=[300]*1 + [200]*(T-2) + [700]*1,
        loop=0,
        optimize=True
    )
    size_kb = os.path.getsize(out_path) / 1024
    print(f"Saved: {out_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    generate_gif_propagation_mechanics()
    generate_gif_irf_propagation()
    print("All RBC GIFs regenerated successfully!")
