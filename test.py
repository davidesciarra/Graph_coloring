import networkx as nx
import random
import matplotlib.pyplot as plt
import time
import numpy as np
from algo import smallest_unassigned_color, dc_local_insert, dc_local_delete, dc_local_recolor
from dsatur import dsatur_coloring
import os

def get_new_test_id():
    base_folder = "graph_images"
    os.makedirs(base_folder, exist_ok=True)

    # Trova il numero del prossimo test
    existing_tests = [d for d in os.listdir(base_folder) if d.startswith("TEST_")]
    test_numbers = [int(d.split("_")[1]) for d in existing_tests if d.split("_")[1].isdigit()]

    new_test_id = max(test_numbers) + 1 if test_numbers else 1
    test_folder = f"{base_folder}/TEST_{new_test_id}"

    os.makedirs(test_folder, exist_ok=True)
    return test_folder


# Genera la cartella per il test corrente
test_folder = get_new_test_id()


def save_graph_image(G, step, num_nodes, num_edges, graph_type, algorithm):
    node_colors = [G.nodes[n]['color'] for n in G.nodes]
    plt.figure(figsize=(10, 8))
    nx.draw(G, node_color=node_colors, with_labels=False, cmap=plt.cm.rainbow, node_size=50)
    plt.title(f"{graph_type} - {num_nodes} nodi, {num_edges} archi ({algorithm})")

    # Creazione della cartella
    graph_folder = f"{test_folder}/{graph_type}/{num_nodes}_nodes_{num_edges}_edges"
    os.makedirs(graph_folder, exist_ok=True)

    # Salvataggio dell'immagine
    plt.savefig(f"{graph_folder}/graph_{step}_{algorithm}.png")
    plt.close()


def save_comparison_chart(graph_type, num_nodes, num_edges, dc_time, dsatur_time):
    # Percorso per la cartella
    graph_folder = f"graph_images/{graph_type}/{num_nodes}_nodes_{num_edges}_edges"
    os.makedirs(graph_folder, exist_ok=True)

    # Creazione del grafico
    fig, ax = plt.subplots()
    labels = ["DC-Local", "DSATUR"]
    times = [dc_time, dsatur_time]
    ax.bar(labels, times, color=['blue', 'red'])

    ax.set_xlabel("Algoritmo")
    ax.set_ylabel("Tempo di Esecuzione (s)")
    ax.set_title(f"Confronto Tempi - {graph_type} ({num_nodes} nodi, {num_edges} archi)")

    # Salvataggio nella cartella
    plt.savefig(f"{graph_folder}/comparison_chart.png")
    plt.close()



# Tipi di grafo da testare
graph_types = {
    "Random Graph": lambda n, m: nx.gnm_random_graph(n, m),
    "Scale-Free Graph": lambda n, m: nx.barabasi_albert_graph(n, max(1, m // n)),
    "Small-World Graph": lambda n, m: nx.watts_strogatz_graph(n, k=4, p=0.1)
}

# Definizione delle dimensioni del grafo
graph_sizes = [(10, 20) , (20 , 40) , (30, 60) , (40 ,80) , (50 , 100) , (60 , 120) , (70 , 140) , (80 , 160) , ( 90 , 180) , (100 , 200)]

test_id = 1
timing_results = []

for graph_type, generator in graph_types.items():
    for num_nodes, num_edges in graph_sizes:
        while True:
            base_graph = generator(num_nodes, num_edges)
            if all(len(list(base_graph.neighbors(n))) > 0 for n in base_graph.nodes()):
                break

        # Test DC-Local Coloring
        G_dc = base_graph.copy()
        for node in G_dc.nodes:
            G_dc.nodes[node]['color'] = smallest_unassigned_color(G_dc, node)
        save_graph_image(G_dc, "iniziale", num_nodes, num_edges ,graph_type, "DC-Local")

        start_time_dc = time.time()
        modifications = [
            ("insert", 20),
            ("insert", 20),
            ("delete", 30),
            ("delete", 20),
            ("insert", 10)
        ]
        for i, (action, num) in enumerate(modifications, 1):
            if action == "insert":
                count = 0
                while count < num:
                    u, v = random.sample(range(num_nodes), 2)
                    if not G_dc.has_edge(u, v):
                        dc_local_insert(G_dc, u, v)
                        count += 1
            elif action == "delete":
                count = 0
                edges_to_remove = list(G_dc.edges)
                random.shuffle(edges_to_remove)
                while count < num and edges_to_remove:
                    u, v = edges_to_remove.pop()
                    dc_local_delete(G_dc, u, v)
                    count += 1
            save_graph_image(G_dc, f"modifica_{i}", num_nodes, num_edges, graph_type, "DC-Local")
        end_time_dc = time.time()

        # Test DSATUR Coloring
        G_dsatur = base_graph.copy()
        total_start_time_dsatur = time.time()
        dsatur_coloring(G_dsatur)
        save_graph_image(G_dsatur, "iniziale", num_nodes, num_edges, graph_type, "DSATUR")

        for i, (action, num) in enumerate(modifications, 1):
            if action == "insert":
                count = 0
                while count < num:
                    u, v = random.sample(range(num_nodes), 2)
                    if not G_dsatur.has_edge(u, v):
                        G_dsatur.add_edge(u, v)
                        dsatur_coloring(G_dsatur)
                        count += 1
            elif action == "delete":
                count = 0
                edges_to_remove = list(G_dsatur.edges)
                random.shuffle(edges_to_remove)
                while count < num and edges_to_remove:
                    u, v = edges_to_remove.pop()
                    G_dsatur.remove_edge(u, v)
                    dsatur_coloring(G_dsatur)
                    count += 1
            save_graph_image(G_dsatur, f"modifica_{i}", num_nodes, num_edges, graph_type, "DSATUR")
        total_end_time_dsatur = time.time()

        timing_results.append(
            (graph_type, num_nodes, num_edges, end_time_dc - start_time_dc,
             total_end_time_dsatur - total_start_time_dsatur)
        )

        save_comparison_chart(graph_type, num_nodes, num_edges, end_time_dc - start_time_dc,
                              total_end_time_dsatur - total_start_time_dsatur)

        test_id += 1



# Grafico comparativo
labels = [f"{g} {n} nodi, {m} archi" for g, n, m, _, _ in timing_results]
dc_times = [t[2] for t in timing_results]
dsatur_times = [t[3] for t in timing_results]
for graph_type, num_nodes, num_edges, dc_time, dsatur_time in timing_results:
    save_comparison_chart(graph_type, num_nodes, num_edges, dc_time, dsatur_time)



def plot_execution_time_trend(timing_results):
    graph_types = list(set([t[0] for t in timing_results]))  # Tipi di grafo unici

    for graph_type in graph_types:
        # Filtrare solo i dati relativi a questo tipo di grafo
        data = [(n, m, dc_time, dsatur_time) for g, n, m, dc_time, dsatur_time in timing_results if g == graph_type]
        data.sort(key=lambda x: x[0])  # Ordinare per numero di nodi

        # Estrarre i valori
        nodes = [d[0] for d in data]
        dc_times = [d[2] for d in data]
        dsatur_times = [d[3] for d in data]

        # Creazione del grafico
        plt.figure(figsize=(8, 6))
        plt.plot(nodes, dc_times, marker='o', linestyle='-', label="DC-Local", color='blue')
        plt.plot(nodes, dsatur_times, marker='s', linestyle='-', label="DSATUR", color='red')

        plt.xlabel("Numero di Nodi")
        plt.ylabel("Tempo di Esecuzione (s)")
        plt.title(f"Andamento Tempo di Esecuzione - {graph_type}")
        plt.legend()
        plt.grid(True)

        # Percorso: nella cartella del grafo
        graph_folder = f"{test_folder}/{graph_type}"
        os.makedirs(graph_folder, exist_ok=True)
        plt.savefig(f"{graph_folder}/execution_time_trend.png")
        plt.close()



def save_comparison_chart_per_graph_type(timing_results):
    graph_types = list(set([t[0] for t in timing_results]))  # Tipi di grafo unici

    for graph_type in graph_types:
        # Filtrare solo i dati relativi a questo tipo di grafo
        data = [(n, m, dc_time, dsatur_time) for g, n, m, dc_time, dsatur_time in timing_results if g == graph_type]
        data.sort(key=lambda x: x[0])  # Ordinare per numero di nodi

        # Estrarre i valori
        labels = [f"{n} nodi, {m} archi" for n, m, _, _ in data]
        dc_times = [d[2] for d in data]
        dsatur_times = [d[3] for d in data]

        # Creazione del grafico
        x = np.arange(len(labels))
        width = 0.35
        fig, ax = plt.subplots(figsize=(10, 6))
        rects1 = ax.bar(x - width / 2, dc_times, width, label='DC-Local', color='blue')
        rects2 = ax.bar(x + width / 2, dsatur_times, width, label='DSATUR', color='red')

        ax.set_xlabel('Numero di Nodi e Archi')
        ax.set_ylabel('Tempo di Esecuzione (s)')
        ax.set_title(f'Confronto DC-Local vs DSATUR - {graph_type}')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()

        # Percorso per salvare il grafico nella cartella del grafo
        graph_folder = f"{test_folder}/{graph_type}"
        os.makedirs(graph_folder, exist_ok=True)
        plt.savefig(f"{graph_folder}/comparison_chart.png")
        plt.close()




plot_execution_time_trend(timing_results)  #Trend salvato UNA VOLTA per ogni tipo di grafo
save_comparison_chart_per_graph_type(timing_results)  #Confronto generale per ogni grafo


