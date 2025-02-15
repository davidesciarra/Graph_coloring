def smallest_unassigned_color(G, u):
    C = set(range(G.degree[u] + 1))
    used_colors = {G.nodes[v]['color'] for v in G.neighbors(u) if 'color' in G.nodes[v]}
    return min(C - used_colors)

def dc_local_recolor(G, u):
    C = {G.nodes[v]['color'] for v in G.neighbors(u) if 'color' in G.nodes[v]}
    C.add(G.nodes[u]['color'])
    c_max = max(C)
    c_min = min(set(range(c_max + 1)) - C, default=c_max + 1)

    if c_min < c_max:
        G.nodes[u]['color'] = c_min
    else:
        mcolor = {c: 0 for c in C}
        for v in G.neighbors(u):
            if 'color' in G.nodes[v]:
                mcolor[G.nodes[v]['color']] = max(mcolor[G.nodes[v]['color']], len(set(G.neighbors(v))))

        c_cand = min(mcolor, key=mcolor.get)
        if c_cand < c_min - 1:
            G.nodes[u]['color'] = c_cand
            for v in G.neighbors(u):
                if G.nodes[v]['color'] == c_cand:
                    G.nodes[v]['color'] = smallest_unassigned_color(G, v)
        else:
            G.nodes[u]['color'] = c_min

def dc_local_insert(G, u, v):
    G.add_edge(u, v)
    if G.nodes[u]['color'] == G.nodes[v]['color']:
        min_deg_node = min((u, v), key=lambda x: len(set(G.neighbors(x))))
        dc_local_recolor(G, min_deg_node)

def dc_local_delete(G, u, v):
    if G.has_edge(u, v):
        G.remove_edge(u, v)
        dc_local_recolor(G, u)
        dc_local_recolor(G, v)

