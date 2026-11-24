import csv
import os
import platform
import gurobipy as gp
from solver_milp import solve_plp_milp

# --- CONFIGURAZIONE SPERIMENTALE ---
TIME_LIMIT = 60.0       # Time limit in secondi (da dichiarare nelle slide)
THREADS = 4             # Numero di core usati da Gurobi (es. 1 o 4)
MODES = ["base", "new"] # Puoi mettere ["base", "normal", "raster", "new"] per il test completo
OUTPUT_CSV = "benchmark_results.csv"

# Set di 12 istanze variegate tra Cover I (area_ratio < 51) e Cover II (51 <= area_ratio < 101)
INSTANCES = [
    # (L, W, a, b, "Categoria")
    (11, 10, 4, 3, "Cover I"),     # Esempio Tabella 1 del paper
    (15, 11, 4, 3, "Cover I"),
    (22, 16, 5, 3, "Cover I"),
    (27, 17, 5, 3, "Cover I"),     # Esempio Sezione 4 del paper
    (30, 22, 7, 4, "Cover I"),
    (34, 23, 5, 4, "Cover I"),
    (40, 25, 7, 3, "Cover I"),
    (43, 26, 7, 4, "Cover I"),
    (49, 28, 8, 3, "Cover II"),
    (56, 39, 9, 4, "Cover II"),
    (61, 38, 10, 4, "Cover II"),
    (89, 75, 10, 7, "Cover II"),   # Istanza difficile citata nel paper (Sez. 9.3)
]


def print_hardware_info():
    print("=" * 75)
    print("CONFIGURAZIONE HARDWARE E PARAMETRI DI TEST")
    print(f"  Sistema Operativo : {platform.system()} {platform.release()}")
    print(f"  Processore        : {platform.processor() or platform.machine()}")
    print(f"  Core logici tot.  : {os.cpu_count()}")
    print(f"  Threads Gurobi    : {THREADS}")
    print(f"  Time Limit        : {TIME_LIMIT} s")
    print("=" * 75)


def run_benchmark():
    print_hardware_info()
    rows = []

    for (L, W, a, b, cover_cat) in INSTANCES:
        area_ub = (L * W) // (a * b)
        inst_name = f"({L},{W},{a},{b})"
        print(f"\nIstanza {inst_name:14s} [{cover_cat:8s} | Area UB = {area_ub:2d}]")

        for mode in MODES:
            try:
                res = solve_plp_milp(
                    L, W, a, b,
                    mode=mode,
                    time_limit=TIME_LIMIT,
                    threads=THREADS,
                    verbose=False,
                )
                status = "OPT" if res["is_optimal"] else ("TL" if res["is_time_limit"] else "OTHER")
                gap_pct = round(res["gap"] * 100, 2) if res["gap"] is not None else None
                runtime = round(res["runtime"], 4)

                row = {
                    "instance": inst_name,
                    "cover": cover_cat,
                    "area_ub": area_ub,
                    "mode": mode,
                    "vars": res["num_vars"],
                    "constrs": res["num_constrs"],
                    "obj_val": res["obj_val"],
                    "status": status,
                    "gap_pct": gap_pct,
                    "runtime_s": runtime,
                    "nodes": res["nodes"],
                }
                gap_str = f"{gap_pct:.2f}%" if gap_pct is not None else "N/A"
                print(
                    f"  {mode:6s} | Vars: {row['vars']:5d} | Constrs: {row['constrs']:5d} | "
                    f"Obj: {str(row['obj_val']):>4s} | {status:3s} | Gap: {gap_str:6s} | "
                    f"Time: {runtime:7.4f}s | Nodes: {row['nodes']}"
                )

            except gp.GurobiError as e:
                # Cattura eventuale limite della licenza gratuita pip (2000 vars/constrs)
                row = {
                    "instance": inst_name,
                    "cover": cover_cat,
                    "area_ub": area_ub,
                    "mode": mode,
                    "vars": "LIC_LIMIT",
                    "constrs": "LIC_LIMIT",
                    "obj_val": None,
                    "status": "LIC_LIMIT",
                    "gap_pct": None,
                    "runtime_s": None,
                    "nodes": None,
                }
                print(f"  {mode:6s} | Saltata (limite licenza Gurobi: {e.message})")

            rows.append(row)

    # Salvataggio su file CSV
    fieldnames = [
        "instance", "cover", "area_ub", "mode",
        "vars", "constrs", "obj_val", "status", "gap_pct", "runtime_s", "nodes"
    ]
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nRisultati salvati con successo in '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    run_benchmark()