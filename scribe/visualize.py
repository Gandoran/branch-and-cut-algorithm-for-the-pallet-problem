import matplotlib.pyplot as plt
import matplotlib.patches as patches
from solver_milp import solve_plp_milp


def verify_solution(L, W, a, b, placed_h, placed_v):
    boxes = []
    for (k, j) in placed_h:
        boxes.append((k, j, k + a, j + b))
    for (k, j) in placed_v:
        boxes.append((k, j, k + b, j + a))

    for (x_min, y_min, x_max, y_max) in boxes:
        if x_min < 0 or y_min < 0 or x_max > L or y_max > W:
            return False

    for i in range(len(boxes)):
        x1_min, y1_min, x1_max, y1_max = boxes[i]
        for m in range(i + 1, len(boxes)):
            x2_min, y2_min, x2_max, y2_max = boxes[m]
            overlap_x = (x1_min < x2_max) and (x2_min < x1_max)
            overlap_y = (y1_min < y2_max) and (y2_min < y1_max)
            if overlap_x and overlap_y:
                return False

    return True


def plot_pallet_solution(L, W, a, b, placed_h, placed_v, title=None, save_path=None):
    fig, ax = plt.subplots(figsize=(8, 6))

    pallet = patches.Rectangle((0, 0), L, W, facecolor="#eeeeee", edgecolor="black", linewidth=2)
    ax.add_patch(pallet)
    ax.set_xlim(0, L)
    ax.set_ylim(0, W)
    ax.set_aspect("equal")

    for (k, j) in placed_h:
        rect = patches.Rectangle((k, j), a, b, facecolor="#4C72B0", edgecolor="black", linewidth=1.2, alpha=0.85)
        ax.add_patch(rect)
        if L <= 40 and W <= 40:
            ax.text(k + a / 2, j + b / 2, "H", ha="center", va="center", color="white", fontweight="bold", fontsize=9)

    for (k, j) in placed_v:
        rect = patches.Rectangle((k, j), b, a, facecolor="#DD8452", edgecolor="black", linewidth=1.2, alpha=0.85)
        ax.add_patch(rect)
        if L <= 40 and W <= 40:
            ax.text(k + b / 2, j + a / 2, "V", ha="center", va="center", color="white", fontweight="bold", fontsize=9)

    if L <= 30 and W <= 30:
        ax.set_xticks(range(0, L + 1))
        ax.set_yticks(range(0, W + 1))
        ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)

    n_boxes = len(placed_h) + len(placed_v)
    waste = L * W - n_boxes * a * b
    fill_pct = (n_boxes * a * b) / (L * W) * 100

    if title is None:
        title = f"PLP ({L}, {W}, {a}, {b}) — {n_boxes} scatole | Scarto U = {waste} | Riempimento: {fill_pct:.1f}%"
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Lunghezza L")
    ax.set_ylabel("Larghezza W")

    legend_handles = [
        patches.Patch(facecolor="#4C72B0", edgecolor="black", label=f"H-box ({a}x{b}): {len(placed_h)}"),
        patches.Patch(facecolor="#DD8452", edgecolor="black", label=f"V-box ({b}x{a}): {len(placed_v)}"),
        patches.Patch(facecolor="#eeeeee", edgecolor="black", label=f"Scarto (U={waste})"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(1.02, 1))

    plt.tight_layout()
    if save_path is not None:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()


if __name__ == "__main__":
    for (L, W, a, b) in [(11, 10, 4, 3), (27, 17, 5, 3)]:
        res = solve_plp_milp(L, W, a, b, mode="new")
        valid = verify_solution(L, W, a, b, res["placed_h"], res["placed_v"])
        print(f"Istanza ({L},{W},{a},{b}) -> Obj: {res['obj_val']} | Valida: {valid}")
        plot_pallet_solution(L, W, a, b, res["placed_h"], res["placed_v"], save_path=f"pallet_{L}_{W}_{a}_{b}.png")