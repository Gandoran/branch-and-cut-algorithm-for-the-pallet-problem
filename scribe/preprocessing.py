def compute_combination(limit,a,b):
    my_set = set()
    for alpha in range(limit // a+1): 
        for beta in range((limit - alpha * a) // b + 1):
           my_set.add(alpha*a+beta*b) 
    return sorted(my_set)

def round_down(S,value):
    return max(r for r in S if r<=value)

def get_valid_positions(L, W, a, b, mode="new"):
    S_L = compute_combination(L - b, a, b)
    S_W = compute_combination(W - b, a, b)
    if mode == "base":
        h_x = list(range(L-a+1))
        h_y = list(range(W-b+1))
        v_x = list(range(L-b+1))
        v_y = list(range(W-a+1))
    elif mode == "normal":
        h_x = [x for x in S_L if x <= L-a]
        h_y = [y for y in S_W if y <= W-b]
        v_x = [x for x in S_L if x <= L-b]
        v_y = [y for y in S_W if y <= W-a]
    elif mode == "raster":
        R_L = {0}
        R_W = {0}
        for r in S_L:
            R_L.add(round_down(S_L, L-r))
        for r in S_W:
            R_W.add(round_down(S_W, W-r))
        h_x = [x for x in sorted(R_L) if x <= L-a]
        h_y = [y for y in sorted(R_W) if y <= W-b]
        v_x = [x for x in sorted(R_L) if x <= L-b]
        v_y = [y for y in sorted(R_W) if y <= W-a]
    elif mode == "new":
        def reduced_axis(D,d):
            S_rem = compute_combination(D-d,a,b)
            return sorted({round_down(S_rem,D-d-r) for r in S_rem})
        h_x = reduced_axis(L, a)
        h_y = reduced_axis(W, b)
        v_x = reduced_axis(L, b)
        v_y = reduced_axis(W, a)
    h_positions=[]
    for k in h_x:
        for j in h_y:
            h_positions.append((k,j))
    v_positions=[]
    for k in v_x:
        for j in v_y:
            v_positions.append((k,j))
    return tuple(h_positions),tuple(v_positions)

def build_constraints(L,W,a,b,h_positions,v_positions,reduce=True):
    grid={}
    for r in range (L):
        for s in range (W):
            grid[(r,s)]=set()
    for (k,j) in h_positions:
        for r in range(k,k+a):
            for s in range(j,j+b):
                grid[(r,s)].add(('H',k,j))
    for (k,j) in v_positions:
        for r in range(k,k+b):
            for s in range(j,j+a):
                grid[(r,s)].add(('V',k,j))
    if reduce == True:
        counts={}
        for var_set in grid.values():
            if len(var_set) == 0: continue
            fset = frozenset(var_set)
            counts[fset] = counts.get(fset, 0)+1
        unique_sets = list(counts.keys())
        unique_sets.sort(key=len, reverse=True)
        kept = []
        for cand in unique_sets:
            if not any(cand.issubset(existing) for existing in kept): kept.append(cand)
        return [(fset, counts[fset]) for fset in kept]
    elif reduce == False:
        constraints=[]
        for var_set in grid.values():
            if len(var_set) > 0: constraints.append((frozenset(var_set), 1))
        return tuple(constraints)

if __name__ == "__main__":
    L, W, a, b = 11, 10, 4, 3
    for mode in ["base", "normal", "raster", "new"]:
        h_pos, v_pos = get_valid_positions(L, W, a, b, mode=mode)
        constraints = build_constraints(L, W, a, b, h_pos, v_pos, reduce=(mode != "base"))
        tot_vars = len(h_pos) + len(v_pos)
        print(f"Mode: {mode:6s} | H: {len(h_pos):2d} | V: {len(v_pos):2d} | Tot vars: {tot_vars:3d} | Constraints: {len(constraints):3d}")