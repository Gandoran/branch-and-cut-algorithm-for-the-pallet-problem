import gurobipy as gp
from preprocessing import get_valid_positions,build_constraints
from gurobipy import GRB

def solve_plp_milp(L, W, a, b, mode="new", time_limit=60.0, threads=None, verbose=False, upper_bound_B=None):
    h_pos, v_pos = get_valid_positions(L,W,a,b,mode=mode)
    constraints = build_constraints(L,W,a,b,h_pos,v_pos,reduce=(mode!="base"))
    model = gp.Model(f"PLP_{mode}")
    model.Params.OutputFlag = 1 if verbose else 0
    model.Params.TimeLimit = time_limit
    if threads is not None:
        model.Params.Threads = threads

    vars_dict={}
    for (k,j) in h_pos:
        vars_dict[('H',k,j)] = model.addVar(vtype=GRB.BINARY,name=f"h_{k}_{j}")
    for (k,j) in v_pos:
        vars_dict[('V',k,j)] = model.addVar(vtype=GRB.BINARY,name=f"v_{k}_{j}")

    model.setObjective(gp.quicksum(vars_dict.values()), GRB.MAXIMIZE)

    if upper_bound_B is not  None:
        U = L*W-upper_bound_B*a*b
        model.addConstr(gp.quicksum(vars_dict.values()) <= upper_bound_B, name="upper_bound")
    for idx, (var_set, q) in enumerate(constraints):
        expr = gp.quicksum(vars_dict[key] for key in var_set)
        if upper_bound_B is not None and q > U: model.addConstr(expr == 1, name=f"cov_eq_{idx}")
        else: model.addConstr(expr <= 1, name=f"cov_{idx}")

    model.optimize()

    if model.SolCount > 0:
        obj_val = int(round(model.ObjVal))
        gap = model.MIPGap
        placed_h, placed_v = [],[]
        for key, var in vars_dict.items():
            if var.X > 0.5:
                if(key[0] == "V"): placed_v.append((key[1],key[2]))
                elif(key[0] == "H"): placed_h.append((key[1],key[2]))
    else:
        obj_val, gap = None, None
        placed_h, placed_v = [],[]

    is_optimal = (model.Status == GRB.OPTIMAL)
    is_time_limit = (model.Status == GRB.TIME_LIMIT)

    return {
        "mode": mode,
        "num_vars": len(vars_dict),
        "num_constrs": len(constraints),
        "obj_val": obj_val,
        "is_optimal": is_optimal,
        "is_time_limit": is_time_limit,
        "gap": gap,
        "runtime": model.Runtime,
        "nodes": int(model.NodeCount),
        "placed_h": placed_h,
        "placed_v": placed_v,
    }

if __name__ == "__main__":
    test_instances = [
        (11, 10, 4, 3),
        (27, 17, 5, 3),
    ]

    for (L, W, a, b) in test_instances:
        print(f"\n=== Istance ({L}, {W}, {a}, {b}) ===")
        for mode in ["base", "normal", "raster", "new"]:
            res = solve_plp_milp(L, W, a, b, mode=mode, time_limit=60.0)
            status = "OPT" if res["is_optimal"] else ("TL" if res["is_time_limit"] else "OTHER")
            gap_str = f"{res['gap']*100:.2f}%" if res["gap"] is not None else "N/A"
            print(
                f"Mode: {mode:6s} | Vars: {res['num_vars']:4d} | Constrs: {res['num_constrs']:4d} | "
                f"Obj: {res['obj_val']} | Status: {status:3s} | Gap: {gap_str:6s} | "
                f"Time: {res['runtime']:.4f}s | Nodes: {res['nodes']}"
            )