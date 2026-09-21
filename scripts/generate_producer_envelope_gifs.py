"""Generate publication-grade animated GIFs for the Producer Theory and Cost Envelope supplement.

Outputs:
  - assets/gif/producer-expansion-path.gif
  - assets/gif/producer-cost-envelope.gif
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
TEAL_COLOR = "#087e8b"      # Long-run cost / Expansion path / Pareto optimum
PURPLE_COLOR = "#6b4c7a"    # Short-run curves / Tangency
GOLD_COLOR = "#d97706"      # Optimum markers / Active curves
RED_COLOR = "#dc2626"       # Inefficiency / Excess cost
BLUE_COLOR = "#2563eb"

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# ANIMATION 1: Expansion Path and Short-Run vs Long-Run Cost (2-Panel)
# Left: Input space (L, K) with Isoquant, Isocost, Expansion Path, Fixed K
# Right: Cost space (y, Cost) with LRTC and SRTC
# ==============================================================================

def generate_gif_expansion_path():
    print("Generating producer-expansion-path.gif...")
    
    # Model: y = L^0.5 * K^0.5, w = 4, r = 2
    # MRTS = K/L = w/r = 2 => K = 2L (Expansion Path slope = 2)
    # L*(y) = y / sqrt(2), K*(y) = sqrt(2)*y
    # LRTC(y) = w*L* + r*K* = 4*(y/sqrt(2)) + 2*(sqrt(2)*y) = 4*sqrt(2)*y ≈ 5.657*y
    # Fixed K = 4.0:
    # L_SR(y; 4) = y^2 / 4
    # SRTC(y; 4) = 4*(y^2/4) + 2*4 = y^2 + 8
    # Optimal y for K=4: 4 = sqrt(2)*y => y_opt = 4/sqrt(2) = 2*sqrt(2) ≈ 2.828
    # At y_opt: L_SR = 8/4 = 2, K = 4 => L* = 2, K* = 4. SRTC = 8 + 8 = 16 = LRTC = 4*sqrt(2)*(2*sqrt(2)) = 16.
    
    w = 4.0
    r = 2.0
    K_bar = 4.0
    y_opt = 2.0 * np.sqrt(2.0)  # 2.8284
    
    # Sequence of y values for animation
    y_forward = np.linspace(1.2, 4.2, 35)
    y_backward = np.linspace(4.2, 1.2, 25)
    y_vals = np.concatenate([y_forward, y_backward])
    
    frames = []
    
    # Static ranges
    L_grid = np.linspace(0.2, 6.0, 300)
    y_curve_grid = np.linspace(0.8, 5.0, 300)
    LRTC_curve = 4.0 * np.sqrt(2.0) * y_curve_grid
    SRTC_curve = y_curve_grid**2 + 8.0
    
    fig, (ax_in, ax_c) = plt.subplots(1, 2, figsize=(13, 6.0), dpi=100)
    fig.patch.set_facecolor(BG_COLOR)
    plt.subplots_adjust(left=0.08, right=0.94, bottom=0.12, top=0.88, wspace=0.28)
    
    for idx, y_cur in enumerate(y_vals):
        ax_in.clear()
        ax_c.clear()
        
        ax_in.set_facecolor(BG_COLOR)
        ax_c.set_facecolor(BG_COLOR)
        
        # --- LEFT PANEL: Input Space (L, K) ---
        ax_in.set_xlim(0, 5.5)
        ax_in.set_ylim(0, 7.5)
        ax_in.set_xlabel("노동 투입량 $L$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_in.set_ylabel("자본 투입량 $K$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_in.set_title("요소 공간 $(L, K)$: 등량곡선과 확장경로", fontsize=12, color=INK_COLOR, fontweight="bold", pad=10)
        ax_in.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)
        
        # 1. Expansion path: K = 2L
        L_exp = np.linspace(0, 3.5, 100)
        ax_in.plot(L_exp, 2.0 * L_exp, color=GOLD_COLOR, linestyle="--", linewidth=2.0, label="장기 확장경로 ($K = 2L$)")
        
        # 2. Fixed capital line: K = K_bar = 4
        ax_in.axhline(K_bar, color=PURPLE_COLOR, linestyle=":", linewidth=2.0, label=f"단기 자본 고정 ($\overline{{K}} = {K_bar}$)")
        
        # 3. Current Isoquant: K = y_cur^2 / L
        iso_K = (y_cur**2) / L_grid
        ax_in.plot(L_grid, iso_K, color=TEAL_COLOR, linewidth=2.5, label=f"등량곡선 $y = {y_cur:.2f}$")
        
        # 4. Long-run optimal point: L*, K*
        L_star = y_cur / np.sqrt(2.0)
        K_star = np.sqrt(2.0) * y_cur
        LRTC_cur = w * L_star + r * K_star
        
        # Long-run Isocost line: w*L + r*K = LRTC_cur => K = LRTC_cur/2 - 2L
        isocost_LR_K = (LRTC_cur / r) - (w / r) * L_grid
        ax_in.plot(L_grid, isocost_LR_K, color=TEAL_COLOR, linestyle="-.", linewidth=1.5, alpha=0.7,
                   label=f"장기 등비용선 ($TC = {LRTC_cur:.1f}$)")
        
        # 5. Short-run choice: L_SR, K_bar
        L_sr = (y_cur**2) / K_bar
        SRTC_cur = w * L_sr + r * K_bar
        
        # Short-run Isocost line: w*L + r*K = SRTC_cur => K = SRTC_cur/2 - 2L
        isocost_SR_K = (SRTC_cur / r) - (w / r) * L_grid
        ax_in.plot(L_grid, isocost_SR_K, color=RED_COLOR, linestyle="--", linewidth=1.5, alpha=0.6,
                   label=f"단기 등비용선 ($TC = {SRTC_cur:.1f}$)")
        
        # Plot points
        ax_in.plot(L_star, K_star, marker="o", markersize=8, color=TEAL_COLOR, zorder=5)
        ax_in.plot(L_sr, K_bar, marker="s", markersize=8, color=RED_COLOR, zorder=5)
        
        # Annotation for points
        ax_in.annotate(f"장기 최적 $E^*$\n$({L_star:.2f}, {K_star:.2f})$",
                       (L_star, K_star), textcoords="offset points", xytext=(-50, 12),
                       fontsize=9, color=TEAL_COLOR, fontweight="bold",
                       arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1))
        
        ax_in.annotate(f"단기 선택 $E_{{SR}}$\n$({L_sr:.2f}, {K_bar:.1f})$",
                       (L_sr, K_bar), textcoords="offset points", xytext=(12, -25),
                       fontsize=9, color=RED_COLOR, fontweight="bold",
                       arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1))
        
        ax_in.legend(loc="upper right", fontsize=8.5, framealpha=0.9, facecolor=BG_COLOR, edgecolor=GRID_COLOR)
        
        # --- RIGHT PANEL: Cost Space (y, TC) ---
        ax_c.set_xlim(0.8, 4.8)
        ax_c.set_ylim(0, 32)
        ax_c.set_xlabel("목표 산출량 $y$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_c.set_ylabel("총생산비용 $TC$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_c.set_title("비용 공간 $(y, TC)$: 장단기 총비용과 포락선 접점", fontsize=12, color=INK_COLOR, fontweight="bold", pad=10)
        ax_c.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)
        
        # Curves
        ax_c.plot(y_curve_grid, LRTC_curve, color=TEAL_COLOR, linewidth=2.5, label="장기총비용 $LRTC(y) = 4\sqrt{2}y$")
        ax_c.plot(y_curve_grid, SRTC_curve, color=RED_COLOR, linewidth=2.2, linestyle="-", label=f"단기총비용 $SRTC(y; \overline{{K}}={K_bar:.0f})$")
        
        # Cost difference fill
        diff_y = np.linspace(0.8, 4.8, 200)
        diff_LR = 4.0 * np.sqrt(2.0) * diff_y
        diff_SR = diff_y**2 + 8.0
        ax_c.fill_between(diff_y, diff_LR, diff_SR, color=RED_COLOR, alpha=0.08, label="단기 제약 비효율 손실")
        
        # Current status markers
        ax_c.plot(y_cur, LRTC_cur, marker="o", markersize=8, color=TEAL_COLOR, zorder=5)
        ax_c.plot(y_cur, SRTC_cur, marker="s", markersize=8, color=RED_COLOR, zorder=5)
        ax_c.vlines(y_cur, LRTC_cur, SRTC_cur, color=INK_COLOR, linestyle=":", linewidth=1.5)
        
        # Tangency point mark
        ax_c.plot(y_opt, 16.0, marker="*", markersize=12, color=GOLD_COLOR, zorder=6, label="포락선 일치점 ($y^* \\approx 2.83$)")
        
        # Text badge of current cost wedge
        wedge = SRTC_cur - LRTC_cur
        status_text = "★ 최적 설비 규모 일치 (비용 쐐기 = 0)" if abs(wedge) < 0.08 else f"단기 초과비용 $\\Delta TC = {wedge:.2f}$"
        text_color = TEAL_COLOR if abs(wedge) < 0.08 else RED_COLOR
        
        ax_c.text(0.05, 0.78,
                  f"현재 산출량 $y = {y_cur:.2f}$\n"
                  f"• $LRTC = {LRTC_cur:.2f}$\n"
                  f"• $SRTC = {SRTC_cur:.2f}$\n"
                  f"• {status_text}",
                  transform=ax_c.transAxes, fontsize=10, color=INK_COLOR,
                  bbox=dict(boxstyle="round,pad=0.5", facecolor=BG_COLOR, edgecolor=text_color, lw=1.5))
        
        ax_c.legend(loc="lower right", fontsize=8.5, framealpha=0.9, facecolor=BG_COLOR, edgecolor=GRID_COLOR)
        
        # Render frame to canvas
        fig.canvas.draw()
        rgba = fig.canvas.buffer_rgba()
        image = Image.frombuffer("RGBA", fig.canvas.get_width_height(), rgba, "raw", "RGBA", 0, 1)
        frames.append(image.convert("P", palette=Image.ADAPTIVE))
        
    plt.close(fig)
    
    gif_path = os.path.join(GIF_DIR, "producer-expansion-path.gif")
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=90,
        loop=0,
        optimize=True
    )
    print(f"Saved: {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)")


# ==============================================================================
# ANIMATION 2: U-Shaped Short-Run AC/MC Curves & Long-Run Cost Envelope (2-Panel)
# Top: Total Cost space (y, TC)
# Bottom: Average & Marginal Cost space (y, AC/MC) showing Envelope Tangency
# ==============================================================================

def generate_gif_cost_envelope():
    print("Generating producer-cost-envelope.gif...")
    
    # Model with textbook U-shaped Long-run and Short-run Average Cost:
    # Technology: y = (L^0.4 * K^0.4), w = 2, r = 2
    # Returns to scale: alpha + beta = 0.8 < 1 (DRS)
    # Long-run optimal: K = L => y = L^0.8 => L*(y) = K*(y) = y^(1/0.8) = y^1.25
    # Long-run variable cost: LRVC = w*L* + r*K* = 4*y^1.25
    # Fixed overhead cost: F0 = 8.0
    # LRTC(y) = 4*y^1.25 + 8.0
    # LRAC(y) = 4*y^0.25 + 8.0/y
    # LRMC(y) = 5.0*y^0.25
    # MES (Minimum Efficient Scale):
    # LRMC = LRAC => 5*y^0.25 = 4*y^0.25 + 8/y => y^0.25 = 8/y => y^1.25 = 8 => y_MES = 8^(1/1.25) = 8^0.8 ≈ 5.278
    # At MES: K_MES = y_MES^1.25 = 8.0
    # Min LRAC = 5 * 5.278^0.25 = 5 * (8^0.2) ≈ 7.579
    
    F0 = 8.0
    
    def LRTC(y):
        return 4.0 * (y ** 1.25) + F0
    
    def LRAC(y):
        return 4.0 * (y ** 0.25) + F0 / y
    
    def LRMC(y):
        return 5.0 * (y ** 0.25)
    
    # Short-run cost for given capital K_val:
    # L_SR(y; K) = (y / K^0.4)^(1/0.4) = y^2.5 / K
    # SRTC(y; K) = w*L_SR + r*K + F0 = 2*(y^2.5 / K) + 2*K + F0
    # SRAC(y; K) = 2*(y^1.5 / K) + (2*K + F0) / y
    # SRMC(y; K) = 5*(y^1.5 / K)
    
    def SRTC(y, K):
        return 2.0 * (y ** 2.5) / K + 2.0 * K + F0
    
    def SRAC(y, K):
        return 2.0 * (y ** 1.5) / K + (2.0 * K + F0) / y
    
    def SRMC(y, K):
        return 5.0 * (y ** 1.5) / K
    
    # Capital levels for benchmark plant sizes
    K_plants = [3.5, 5.5, 8.0, 11.5, 16.0]
    plant_colors = ["#9ca3af", "#9ca3af", "#9ca3af", "#9ca3af", "#9ca3af"]
    plant_labels = [f"$SRAC_1 (K=3.5)$", f"$SRAC_2 (K=5.5)$", f"$SRAC_{{MES}} (K=8.0)$", f"$SRAC_4 (K=11.5)$", f"$SRAC_5 (K=16.0)$"]
    
    # Optimum y for each plant: K = y^1.25 => y = K^0.8
    y_opts = [k ** 0.8 for k in K_plants]
    
    # Sequence of animated y targets
    y_seq_fwd = np.linspace(2.2, 9.0, 38)
    y_seq_bwd = np.linspace(9.0, 2.2, 26)
    y_seq = np.concatenate([y_seq_fwd, y_seq_bwd])
    
    y_grid = np.linspace(1.2, 10.5, 350)
    
    frames = []
    
    fig, (ax_tc, ax_ac) = plt.subplots(2, 1, figsize=(11.5, 9.0), dpi=100)
    fig.patch.set_facecolor(BG_COLOR)
    plt.subplots_adjust(left=0.10, right=0.92, bottom=0.08, top=0.93, hspace=0.32)
    
    for idx, y_cur in enumerate(y_seq):
        ax_tc.clear()
        ax_ac.clear()
        
        ax_tc.set_facecolor(BG_COLOR)
        ax_ac.set_facecolor(BG_COLOR)
        
        # Active optimal capital for current y
        K_cur = y_cur ** 1.25
        
        # --- TOP PANEL: Total Cost (y, TC) ---
        ax_tc.set_xlim(1.2, 10.2)
        ax_tc.set_ylim(0, 95)
        ax_tc.set_ylabel("총비용 $TC$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_tc.set_title("패널 A: 장기총비용곡선($LRTC$)과 단기총비용곡선군($SRTC$)의 하단 포락선",
                        fontsize=12, color=INK_COLOR, fontweight="bold", pad=8)
        ax_tc.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)
        
        # Benchmark plants SRTC
        for kp in K_plants:
            ax_tc.plot(y_grid, SRTC(y_grid, kp), color="#cbd5e1", linewidth=1.2, linestyle="--")
            
        # Long-run TC
        ax_tc.plot(y_grid, LRTC(y_grid), color=TEAL_COLOR, linewidth=2.8, label="장기총비용 $LRTC(y)$")
        
        # Current active short-run TC
        ax_tc.plot(y_grid, SRTC(y_grid, K_cur), color=PURPLE_COLOR, linewidth=2.0,
                   label=f"현재 최적설비 $SRTC(y; K^*={K_cur:.1f})$")
        
        # Tangency point mark
        tc_val = LRTC(y_cur)
        ax_tc.plot(y_cur, tc_val, marker="o", markersize=8, color=GOLD_COLOR, zorder=6)
        ax_tc.annotate(f"접점 $y={y_cur:.1f}$\n$TC={tc_val:.1f}$",
                       (y_cur, tc_val), textcoords="offset points", xytext=(-25, 12),
                       fontsize=9, color=INK_COLOR, fontweight="bold")
        
        ax_tc.legend(loc="upper left", fontsize=9, framealpha=0.9, facecolor=BG_COLOR, edgecolor=GRID_COLOR)
        
        # --- BOTTOM PANEL: Average and Marginal Cost (y, AC/MC) ---
        ax_ac.set_xlim(1.2, 10.2)
        ax_ac.set_ylim(4.0, 16.0)
        ax_ac.set_xlabel("산출량 $y$", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_ac.set_ylabel("단위당 비용 ($AC, MC$)", fontsize=11, color=INK_COLOR, fontweight="bold")
        ax_ac.set_title("패널 B: 포락선 정리(Envelope Theorem)와 $LRAC / SRAC$의 접점 기하학",
                        fontsize=12, color=INK_COLOR, fontweight="bold", pad=8)
        ax_ac.grid(True, linestyle="--", alpha=0.5, color=GRID_COLOR)
        
        # Draw benchmark SRAC curves
        for i, kp in enumerate(K_plants):
            lbl = plant_labels[i] if idx == 0 else None
            ax_ac.plot(y_grid, SRAC(y_grid, kp), color="#94a3b8", linewidth=1.2, linestyle=":", alpha=0.85)
            # Mark minimum of benchmark SRAC
            y_srac_min = ((2.0 * kp + F0) / (3.0 * (2.0 / kp))) ** (1.0 / 2.5)
            # ax_ac.plot(y_srac_min, SRAC(y_srac_min, kp), marker=".", color="#94a3b8", markersize=4)
        
        # LRAC and LRMC
        ax_ac.plot(y_grid, LRAC(y_grid), color=TEAL_COLOR, linewidth=3.0, label="장기평균비용 $LRAC(y)$ (포락선)")
        ax_ac.plot(y_grid, LRMC(y_grid), color=TEAL_COLOR, linewidth=2.0, linestyle="--", label="장기한계비용 $LRMC(y)$")
        
        # Active SRAC and SRMC
        ax_ac.plot(y_grid, SRAC(y_grid, K_cur), color=PURPLE_COLOR, linewidth=2.4,
                   label=f"현재 설비 $SRAC(y; K^*={K_cur:.1f})$")
        ax_ac.plot(y_grid, SRMC(y_grid, K_cur), color=RED_COLOR, linewidth=1.8, linestyle="--",
                   label=f"현재 설비 $SRMC(y; K^*={K_cur:.1f})$")
        
        # Values at current y
        ac_val = LRAC(y_cur)
        mc_val = LRMC(y_cur)
        
        # Tangency point (SRAC touches LRAC)
        ax_ac.plot(y_cur, ac_val, marker="*", markersize=13, color=GOLD_COLOR, zorder=6, label="포락선 접점 ($SRAC = LRAC$)")
        
        # Marginal cost equality point (SRMC equals LRMC)
        ax_ac.plot(y_cur, mc_val, marker="o", markersize=7, color=RED_COLOR, zorder=6, label="한계비용 일치점 ($SRMC = LRMC$)")
        
        # Vertical alignment dashed line
        ax_ac.vlines(y_cur, min(ac_val, mc_val) - 0.5, max(ac_val, mc_val) + 0.5,
                     color=INK_COLOR, linestyle=":", linewidth=1.5, alpha=0.7)
        
        # MES marker
        y_mes = 8.0 ** 0.8  # 5.278
        ac_mes = LRAC(y_mes)
        ax_ac.plot(y_mes, ac_mes, marker="D", markersize=6, color=TEAL_COLOR, zorder=5)
        
        # Status text determination based on scale region
        if y_cur < y_mes - 0.3:
            region_text = "규모의 경제 구간 (IRS): $LRAC$ 우하향\n→ $SRAC$의 우하향 구간에서 접함 (최저점 왼쪽)"
            box_edge = BLUE_COLOR
        elif y_cur > y_mes + 0.3:
            region_text = "규모의 비경제 구간 (DRS): $LRAC$ 우상향\n→ $SRAC$의 우상향 구간에서 접함 (최저점 오른쪽)"
            box_edge = RED_COLOR
        else:
            region_text = "최적조업규모 (MES): $LRAC$ 최저점\n→ $SRAC$ 최저점과 $LRAC$ 최저점이 완벽 일치!"
            box_edge = GOLD_COLOR
            
        ax_ac.text(0.55, 0.76,
                   f"산출량 $y = {y_cur:.2f}$ (설비 $K^* = {K_cur:.1f}$)\n"
                   f"• $LRAC = SRAC = {ac_val:.2f}$\n"
                   f"• $LRMC = SRMC = {mc_val:.2f}$\n"
                   f"• {region_text}",
                   transform=ax_ac.transAxes, fontsize=9.5, color=INK_COLOR,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor=BG_COLOR, edgecolor=box_edge, lw=1.5))
        
        ax_ac.legend(loc="upper left", fontsize=8.2, framealpha=0.9, facecolor=BG_COLOR, edgecolor=GRID_COLOR, ncol=2)
        
        # Render frame to canvas
        fig.canvas.draw()
        rgba = fig.canvas.buffer_rgba()
        image = Image.frombuffer("RGBA", fig.canvas.get_width_height(), rgba, "raw", "RGBA", 0, 1)
        frames.append(image.convert("P", palette=Image.ADAPTIVE))
        
    plt.close(fig)
    
    gif_path = os.path.join(GIF_DIR, "producer-cost-envelope.gif")
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0,
        optimize=True
    )
    print(f"Saved: {gif_path} ({os.path.getsize(gif_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_expansion_path()
    generate_gif_cost_envelope()
    print("All producer theory GIFs generated successfully!")
