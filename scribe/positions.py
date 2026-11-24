def compute_combination(limit,a,b):
    my_set = set()
    for alpha in range(limit // a+1): 
        for beta in range((limit - alpha * a) // b + 1):
           my_set.add(alpha*a+beta*b) 
    return sorted(my_set)

def round_down(S,value):
    return max(r for r in S if r<=value)

def base_position(L,W,a,b):
    h_x = list(range(L-a+1))
    h_y = list(range(W-b+1))
    v_x = list(range(L-b+1))
    v_y = list(range(W-a+1))
    return h_x,h_y,v_x,v_y

def normal_position(S_L,S_W,L,W,a,b):
    h_x = [x for x in S_L if x <= L-a]
    h_y = [y for y in S_W if y <= W-b]
    v_x = [x for x in S_L if x <= L-b]
    v_y = [y for y in S_W if y <= W-a]
    return h_x,h_y,v_x,v_y

def raster_position(R_L,R_W,L,W,a,b):
    h_x = [x for x in sorted(R_L) if x <= L-a]
    h_y = [y for y in sorted(R_W) if y <= W-b]
    v_x = [x for x in sorted(R_L) if x <= L-b]
    v_y = [y for y in sorted(R_W) if y <= W-a]
    return h_x,h_y,v_x,v_y

def new_position(L,W,a,b):
    def reduced_axis(D,d):
        S_rem = compute_combination(D-d,a,b)
        return sorted({round_down(S_rem,D-d-r) for r in S_rem})
    h_x = reduced_axis(L, a)
    h_y = reduced_axis(W, b)
    v_x = reduced_axis(L, b)
    v_y = reduced_axis(W, a)
    return h_x,h_y,v_x,v_y
