"""Generate publication-grade animated GIFs for the Solow Growth Model supplement.

Outputs:
  - assets/gif/solow-capital-convergence.gif
  - assets/gif/solow-saving-rate-shock.gif
  - assets/gif/solow-golden-rule.gif
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
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
TEAL_COLOR = "#087e8b"      # Investment sf(k)
AMBER_COLOR = "#b46f45"     # Dilution (n+g+delta)k
GOLD_COLOR = "#a16207"      # Steady-state
PURPLE_COLOR = "#6b4c7a"    # Consumption
DARK_COLOR = "#44342b"      # Output
RED_COLOR = "#c0392b"       # Dynamic inefficiency

plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Pretendard", "Segoe UI", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# Model Baseline Parameters
# ==============================================================================
alpha = 0.33
n = 0.01
g = 0.02
delta = 0.05
dilution = n + g + delta  # 0.08
s_base = 0.22

k_star_base = (s_base / dilution) ** (1.0 / (1.0 - alpha))  # ~ 4.409
y_star_base = k_star_base ** alpha                          # ~ 1.603
c_star_base = (1.0 - s_base) * y_star_base                  # ~ 1.251

k_gold = (alpha / dilution) ** (1.0 / (1.0 - alpha))        # ~ 8.290
s_gold = alpha                                              # 0.33
c_gold = (1.0 - s_gold) * (k_gold ** alpha)                 # ~ 1.346


# ==============================================================================
# 1. GIF 1: Capital Convergence Dynamics
# ==============================================================================
def generate_gif_convergence():
    print("Generating GIF 1: solow-capital-convergence.gif ...")
    k_grid = np.linspace(0.001, 9.0, 300)
    y_curve = k_grid ** alpha
    sf_curve = s_base * y_curve
    dep_line = dilution * k_grid

    # Closed-form continuous time solution:
    # k(t) = [k*^(1-alpha) + (k0^(1-alpha) - k*^(1-alpha)) * exp(-lambda*t)]^(1/(1-alpha))
    lam = (1.0 - alpha) * dilution  # 0.67 * 0.08 = 0.0536
    t_max = 60.0
    n_frames = 36
    t_vals = np.linspace(0, t_max, n_frames)

    k0_low = 0.8
    k0_high = 8.2

    def get_k(k0, t):
        term = (k_star_base ** (1.0 - alpha)) + (k0 ** (1.0 - alpha) - k_star_base ** (1.0 - alpha)) * np.exp(-lam * t)
        return term ** (1.0 / (1.0 - alpha))

    frames = []

    for idx, t in enumerate(t_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 5.2), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        k_low = get_k(k0_low, t)
        k_high = get_k(k0_high, t)

        # Panel 1: Solow Diagram
        ax1.set_facecolor(BG_COLOR)
        ax1.plot(k_grid, y_curve, color=DARK_COLOR, linestyle="--", linewidth=1.4, alpha=0.7, label=r"$y = f(k) = k^\alpha$")
        ax1.plot(k_grid, sf_curve, color=TEAL_COLOR, linewidth=2.4, label=r"$s f(k) = 0.22 k^{0.33}$")
        ax1.plot(k_grid, dep_line, color=AMBER_COLOR, linewidth=2.0, label=r"$(n+g+\delta)k = 0.08k$")

        # Steady state marker
        ax1.axvline(k_star_base, color=GOLD_COLOR, linestyle=":", linewidth=1.5, alpha=0.8)
        ax1.plot(k_star_base, dilution * k_star_base, "o", color=GOLD_COLOR, markersize=8, zorder=5)
        ax1.annotate(r"$k^* = 4.41$", xy=(k_star_base, dilution * k_star_base),
                     xytext=(k_star_base + 0.3, dilution * k_star_base - 0.08),
                     fontweight="bold", color=GOLD_COLOR, fontsize=10)

        # Economy A (Low capital)
        sf_low = s_base * (k_low ** alpha)
        dep_low = dilution * k_low
        ax1.plot(k_low, sf_low, "o", color=TEAL_COLOR, markersize=7, zorder=6)
        if abs(sf_low - dep_low) > 0.02:
            ax1.annotate("", xy=(k_low, sf_low), xytext=(k_low, dep_low),
                         arrowprops=dict(arrowstyle="->", color=TEAL_COLOR, lw=1.8))
        ax1.text(k_low, 0.03, f"A ($k_t$={k_low:.2f})", color=TEAL_COLOR, fontsize=8.5, ha="center", fontweight="bold")

        # Economy B (High capital)
        sf_high = s_base * (k_high ** alpha)
        dep_high = dilution * k_high
        ax1.plot(k_high, sf_high, "o", color=RED_COLOR, markersize=7, zorder=6)
        if abs(dep_high - sf_high) > 0.02:
            ax1.annotate("", xy=(k_high, sf_high), xytext=(k_high, dep_high),
                         arrowprops=dict(arrowstyle="->", color=RED_COLOR, lw=1.8))
        ax1.text(k_high, 0.03, f"B ($k_t$={k_high:.2f})", color=RED_COLOR, fontsize=8.5, ha="center", fontweight="bold")

        ax1.set_xlim(0, 9.0)
        ax1.set_ylim(0, 2.2)
        ax1.set_xlabel("유효노동 단위 자본 $k_t$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel("투자 및 산출 ($y, i$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_title("Solow 다이어그램 상의 수렴 동학", fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.legend(loc="upper left", fontsize=8.5, framealpha=0.9)

        # Panel 2: Capital Time Path k(t)
        ax2.set_facecolor(BG_COLOR)
        t_hist = t_vals[:idx + 1]
        k_hist_low = [get_k(k0_low, s) for s in t_hist]
        k_hist_high = [get_k(k0_high, s) for s in t_hist]

        ax2.axhline(k_star_base, color=GOLD_COLOR, linestyle="--", linewidth=1.5, label=r"정상상태 $k^* = 4.41$")
        ax2.plot(t_hist, k_hist_low, color=TEAL_COLOR, linewidth=2.2, label=r"경제 A ($k_0 = 0.8 < k^*$)")
        ax2.plot(t_hist, k_hist_high, color=RED_COLOR, linewidth=2.2, label=r"경제 B ($k_0 = 8.2 > k^*$)")

        ax2.plot(t, k_low, "o", color=TEAL_COLOR, markersize=7)
        ax2.plot(t, k_high, "o", color=RED_COLOR, markersize=7)

        ax2.set_xlim(0, t_max)
        ax2.set_ylim(0, 9.0)
        ax2.set_xlabel("시간 $t$ (년)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel("자본 경로 $k(t)$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_title(f"시간경로 수렴 (경과시간: t = {t:.1f}년)", fontsize=11.5, fontweight="bold", color=INK_COLOR)
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.legend(loc="right", fontsize=8.5, framealpha=0.9)

        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.22)
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "solow-capital-convergence.gif")
    frames_to_save = frames + [frames[-1]] * 6
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=120, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# ==============================================================================
# 2. GIF 2: Saving Rate Shock (Level vs Growth Effect)
# ==============================================================================
def generate_gif_saving_shock():
    print("Generating GIF 2: solow-saving-rate-shock.gif ...")
    s0 = 0.18
    s1 = 0.30
    k0_star = (s0 / dilution) ** (1.0 / (1.0 - alpha))  # ~ 3.32
    k1_star = (s1 / dilution) ** (1.0 / (1.0 - alpha))  # ~ 6.84
    lam = (1.0 - alpha) * dilution                      # 0.0536

    t_shock = 15.0
    t_end = 65.0
    n_frames = 40
    t_vals = np.linspace(0, t_end, n_frames)

    def get_k(t):
        if t <= t_shock:
            return k0_star
        dt = t - t_shock
        term = (k1_star ** (1.0 - alpha)) + (k0_star ** (1.0 - alpha) - k1_star ** (1.0 - alpha)) * np.exp(-lam * dt)
        return term ** (1.0 / (1.0 - alpha))

    def get_y(t):
        return get_k(t) ** alpha

    def get_c(t):
        kt = get_k(t)
        st = s0 if t < t_shock else s1
        return (1.0 - st) * (kt ** alpha)

    def get_growth_y(t):
        if t < t_shock:
            return g
        kt = get_k(t)
        # dk/dt / k = s1 * k^(alpha-1) - dilution
        g_k = s1 * (kt ** (alpha - 1.0)) - dilution
        return g + alpha * g_k

    k_grid = np.linspace(0.001, 8.5, 300)
    y_curve = k_grid ** alpha
    sf0_curve = s0 * y_curve
    sf1_curve = s1 * y_curve
    dep_line = dilution * k_grid

    frames = []

    for idx, t in enumerate(t_vals):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 5.2), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        kt = get_k(t)
        ct = get_c(t)
        st_current = s0 if t < t_shock else s1

        # Panel 1: Solow Diagram Shift
        ax1.set_facecolor(BG_COLOR)
        ax1.plot(k_grid, dep_line, color=AMBER_COLOR, linewidth=1.8, label=r"$(n+g+\delta)k$")
        ax1.plot(k_grid, sf0_curve, color=TEAL_COLOR, linestyle="--", linewidth=1.6, alpha=0.7, label=r"$s_0 f(k) (s=0.18)$")

        if t >= t_shock:
            ax1.plot(k_grid, sf1_curve, color=TEAL_COLOR, linewidth=2.4, label=r"$s_1 f(k) (s=0.30)$ [도약]")
        else:
            ax1.plot(k_grid, sf1_curve, color=TEAL_COLOR, linewidth=1.0, alpha=0.3)

        # Steady state markers
        ax1.axvline(k0_star, color=MUTED_COLOR, linestyle=":", alpha=0.6)
        ax1.axvline(k1_star, color=GOLD_COLOR, linestyle=":", alpha=0.6)

        # Moving point on diagram
        current_invest = st_current * (kt ** alpha)
        ax1.plot(kt, current_invest, "o", color=PURPLE_COLOR, markersize=8, zorder=6)
        ax1.annotate(f"$k_t$={kt:.2f}", xy=(kt, current_invest), xytext=(kt + 0.25, current_invest + 0.05),
                     fontweight="bold", color=PURPLE_COLOR, fontsize=9.5)

        ax1.set_xlim(0, 8.5)
        ax1.set_ylim(0, 2.0)
        ax1.set_xlabel("유효노동 단위 자본 $k_t$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel(r"투자 및 자본유지 ($i, (n+g+\delta)k$)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        status_text = "초기 정상상태 (s=0.18)" if t < t_shock else f"저축률 충격 발생! (s=0.30, t={t:.1f})"
        ax1.set_title(f"솔로우 다이어그램 ({status_text})", fontsize=11.0, fontweight="bold", color=INK_COLOR)
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.legend(loc="upper left", fontsize=8.5, framealpha=0.9)

        # Panel 2: Consumption and Growth rate response
        ax2.set_facecolor(BG_COLOR)
        t_hist = t_vals[:idx + 1]
        c_hist = [get_c(s) for s in t_hist]
        g_hist = [get_growth_y(s) * 100 for s in t_hist]

        # Dual axis: left for Consumption, right for Growth rate
        color_c = PURPLE_COLOR
        ax2.set_xlabel("시간 $t$ (년)", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel("유효노동 1인당 소비 $c(t)$", color=color_c, fontsize=10.5, fontweight="bold")
        line_c, = ax2.plot(t_hist, c_hist, color=color_c, linewidth=2.4, label="소비 $c(t)$")
        ax2.tick_params(axis="y", labelcolor=color_c)
        ax2.set_ylim(0.95, 1.45)
        ax2.axvline(t_shock, color=RED_COLOR, linestyle="--", alpha=0.5)

        ax2_right = ax2.twinx()
        color_g = TEAL_COLOR
        ax2_right.set_ylabel("1인당 소득성장률 (%)", color=color_g, fontsize=10.5, fontweight="bold")
        line_g, = ax2_right.plot(t_hist, g_hist, color=color_g, linewidth=2.0, linestyle="-.", label="성장률 $g_y(t)$ (%)")
        ax2_right.tick_params(axis="y", labelcolor=color_g)
        ax2_right.set_ylim(1.0, 4.5)

        ax2.set_xlim(0, t_end)
        ax2.set_title("소비의 수직 급락 후 반등과 성장률의 일시적 도약", fontsize=11.0, fontweight="bold", color=INK_COLOR)
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)

        # Add joint legend
        lines = [line_c, line_g]
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc="lower right", fontsize=8.5, framealpha=0.9)

        fig.subplots_adjust(left=0.07, right=0.92, bottom=0.12, top=0.90, wspace=0.25)
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "solow-saving-rate-shock.gif")
    frames_to_save = frames + [frames[-1]] * 6
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=120, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


# ==============================================================================
# 3. GIF 3: Golden Rule Sweep (Dynamic Inefficiency)
# ==============================================================================
def generate_gif_golden_rule():
    print("Generating GIF 3: solow-golden-rule.gif ...")
    s_sweep = np.linspace(0.08, 0.52, 36)
    s_dense = np.linspace(0.06, 0.58, 300)

    # Steady states as function of s
    k_star_dense = (s_dense / dilution) ** (1.0 / (1.0 - alpha))
    y_star_dense = k_star_dense ** alpha
    c_star_dense = (1.0 - s_dense) * y_star_dense

    k_grid = np.linspace(0.001, 19.0, 300)
    dep_line = dilution * k_grid
    y_curve = k_grid ** alpha

    frames = []

    for idx, s_curr in enumerate(s_sweep):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 5.2), dpi=100)
        fig.patch.set_facecolor(BG_COLOR)

        k_curr = (s_curr / dilution) ** (1.0 / (1.0 - alpha))
        y_curr = k_curr ** alpha
        c_curr = (1.0 - s_curr) * y_curr
        is_inefficient = (s_curr > s_gold)

        # Panel 1: Solow Diagram with variable s
        ax1.set_facecolor(BG_COLOR)
        sf_curr_curve = s_curr * y_curve
        ax1.plot(k_grid, dep_line, color=AMBER_COLOR, linewidth=2.0, label=r"$(n+g+\delta)k$")
        curve_color = RED_COLOR if is_inefficient else TEAL_COLOR
        ax1.plot(k_grid, sf_curr_curve, color=curve_color, linewidth=2.4, label=f"$s f(k)$ ($s={s_curr:.2f}$)")

        # Golden rule reference
        ax1.axvline(k_gold, color=GOLD_COLOR, linestyle="--", alpha=0.6, label=f"황금률 자본 ($k_{{gold}}={k_gold:.2f}$)")

        ax1.plot(k_curr, dilution * k_curr, "o", color=curve_color, markersize=8, zorder=6)
        x_txt = k_curr - 3.0 if k_curr > 13.0 else k_curr + 0.4
        ax1.annotate(f"$k^*={k_curr:.2f}$", xy=(k_curr, dilution * k_curr),
                     xytext=(x_txt, dilution * k_curr + 0.1),
                     fontweight="bold", color=curve_color, fontsize=9.5)

        ax1.set_xlim(0, 19.0)
        ax1.set_ylim(0, 3.0)
        ax1.set_xlabel("유효노동 단위 자본 $k$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_ylabel("투자 및 자본유지", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax1.set_title("저축률에 따른 솔로우 교차점 이동", fontsize=11.0, fontweight="bold", color=INK_COLOR)
        ax1.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax1.legend(loc="upper left", fontsize=8.5, framealpha=0.9)

        # Panel 2: Golden Rule Consumption Curve
        ax2.set_facecolor(BG_COLOR)
        ax2.plot(s_dense, c_star_dense, color=PURPLE_COLOR, linewidth=2.4, label=r"정상상태 소비 $c^*(s) = (1-s)k^{*\alpha}$")

        # Shading dynamic inefficiency region
        ax2.axvspan(s_gold, 0.58, color="#f9e8e8", alpha=0.7, label=r"동태적 비효율 영역 ($s > \alpha$)")
        ax2.axvline(s_gold, color=GOLD_COLOR, linestyle="--", linewidth=1.5)
        ax2.plot(s_gold, c_gold, "*", color=GOLD_COLOR, markersize=12, zorder=7, label=f"황금률 저축률 ($s={s_gold:.2f}$)")

        # Moving current point with guide dashed lines
        ax2.plot([s_curr, s_curr], [0.60, c_curr], linestyle=":", color=curve_color, linewidth=1.2, alpha=0.5)
        ax2.plot([0.05, s_curr], [c_curr, c_curr], linestyle=":", color=curve_color, linewidth=1.2, alpha=0.5)
        ax2.plot(s_curr, c_curr, "o", color=curve_color, markersize=8, zorder=8)

        text_label = "비효율 과잉저축!" if is_inefficient else "동태적 효율 영역"
        x_ann = s_curr - 0.13 if s_curr > 0.35 else s_curr + 0.02
        y_ann = c_curr - 0.20 if c_curr > 1.1 else c_curr + 0.08
        ax2.annotate(f"$s={s_curr:.2f}$\n$c^*={c_curr:.3f}$\n({text_label})",
                     xy=(s_curr, c_curr),
                     xytext=(x_ann, y_ann),
                     fontweight="bold", color=curve_color, fontsize=9,
                     arrowprops=dict(arrowstyle="->", color=curve_color, lw=1.2))

        ax2.set_xlim(0.05, 0.58)
        ax2.set_ylim(0.60, 1.50)
        ax2.set_xlabel("저축률 $s$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_ylabel("정상상태 소비 $c^*$", fontsize=10.5, color=INK_COLOR, fontweight="bold")
        ax2.set_title("황금률과 동태적 비효율성 (저축률 vs 장기 소비)", fontsize=11.0, fontweight="bold", color=INK_COLOR)
        ax2.grid(True, color=GRID_COLOR, linestyle="-", linewidth=0.7)
        ax2.legend(loc="lower left", fontsize=8.0, framealpha=0.9)

        fig.subplots_adjust(left=0.07, right=0.96, bottom=0.12, top=0.90, wspace=0.22)
        fig.canvas.draw()
        rgba = np.asarray(fig.canvas.buffer_rgba())
        frames.append(Image.fromarray(rgba))
        plt.close(fig)

    out_path = os.path.join(GIF_DIR, "solow-golden-rule.gif")
    frames_to_save = frames + [frames[-1]] * 6
    frames_to_save[0].save(out_path, save_all=True, append_images=frames_to_save[1:], duration=120, loop=0)
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


if __name__ == "__main__":
    generate_gif_convergence()
    generate_gif_saving_shock()
    generate_gif_golden_rule()
    print("All Solow GIFs generated successfully!")
