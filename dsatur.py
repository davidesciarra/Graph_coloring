def dsatur_coloring(G):
    color_map = {}
    degrees = sorted(G.nodes, key=lambda x: G.degree[x], reverse=True)
    available_colors = {}

    for node in degrees:
        neighbor_colors = {color_map.get(neigh) for neigh in G.neighbors(node) if neigh in color_map}
        color = 0
        while color in neighbor_colors:
            color += 1
        color_map[node] = color
        available_colors[node] = color

    for node in G.nodes:
        G.nodes[node]['color'] = color_map[node]

