from flask import Flask, render_template, request, redirect, url_for
import json
import pandas as pd
import networkx as nx


app = Flask(__name__)
G1 = None

def analyze_graph(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)

    # Extract nodes and edges
    nodes = df.columns[1:]  # Assuming first column is just labels
    edges = [(row['Unnamed: 0'], node) for _, row in df.iterrows() for node in nodes if row[node] > 0]

    # Create a directed graph
    global G1
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    G1 = G

    # Check if the graph is connected
    # For a directed graph, checking if the underlying undirected graph is connected
    undirected_G = G.to_undirected()
    is_connected = nx.is_connected(undirected_G)

    # Check if the graph is a DAG
    is_dag = nx.is_directed_acyclic_graph(G)

    # Check if the graph is a Tree
    # A DAG is a tree if every node except the root has exactly one parent
    is_tree = is_dag and all(len(list(G.predecessors(node))) == 1 for node in nodes if node != nodes[0])

    # Determine the type of graph
    graph_type = "general graph"
    if is_dag:
        if is_tree:
            graph_type = "tree"
        else:
            graph_type = "DAG"
    elif is_connected:
        graph_type = "general graph"

    return is_connected, graph_type

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            is_connected, graph_type = analyze_graph(file)
            if is_connected:
                if graph_type == "general graph":
                    return render_template("general_graph_select.html")
                elif graph_type == "DAG":
                    return render_template("DAG_Select.html")
                elif graph_type == "tree":
                    return render_template("Tree_Select.html")
                else:
                    return f"The graph is {graph_type}."
            else:
                return "The graph is not connected."

    return render_template("index.html")

@app.route("/longest_path", methods=["GET", "POST"])
def longest_path():
    # Find the node with the longest path
    longest_path_node = max(nx.single_source_dijkstra_path_length(G1, list(G1.nodes())[0]).items(), key=lambda x: x[1])[0]

    nodes_data = [{'id': node} for node in G1.nodes()]
    links_data = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges()]

    # Extract nodes and links along the longest path
    longest_path_nodes = set(nx.shortest_path(G1, source=list(G1.nodes())[0], target=longest_path_node))
    longest_path_links = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges() if edge[0] in longest_path_nodes and edge[1] in longest_path_nodes]

    graph_data = {'nodes': nodes_data, 'links': longest_path_links}
    return render_template("Directed_Sugiyama.html", graph_data=json.dumps(graph_data))



@app.route("/general_graph_select", methods=["GET","POST"])
def general_graph_select():
    diagram_type = request.form.get("diagram_type")
    print(diagram_type)
    if diagram_type == "grid":
        nodes_data = [{'id': node} for node in G1.nodes()]
        links_data = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges()]
        graph_data = {'nodes': nodes_data, 'links': links_data}
        print(graph_data)    
        return render_template("grid_layout.html", graph_data=json.dumps(graph_data))
    elif diagram_type == "chord":
        nodes_data = [{'id': node} for node in G1.nodes()]
        links_data = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges()]
        graph_data = {'nodes': nodes_data, 'links': links_data}
        print(graph_data)    
        return render_template("chord_layout.html", graph_data=json.dumps(graph_data))



@app.route("/DAG_Select", methods=["GET","POST"])
def DAG_select():
    diagram_type = request.form.get("diagram_type")
    print(diagram_type)
    if diagram_type == "DSL":
        nodes_data = [{'id': node} for node in G1.nodes()]
        links_data = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges()]
        graph_data = {'nodes': nodes_data, 'links': links_data}
        print(graph_data)    
        return render_template("Directed_Sugiyama.html", graph_data=json.dumps(graph_data))
    elif diagram_type == "RSL":
        nodes_data = [{'id': node} for node in G1.nodes()]
        links_data = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges()]
        graph_data = {'nodes': nodes_data, 'links': links_data}
        print(graph_data)    
        return render_template("Radial_Sugiyama.html", graph_data=json.dumps(graph_data))

@app.route("/tree_select", methods=["GET","POST"])
def tree_select():
    diagram_type = request.form.get("diagram_type")
    print(diagram_type)
    if diagram_type == "Rheingold_Tilford":
        nodes_data = [{'id': node} for node in G1.nodes()]
        links_data = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges()]
        graph_data = {'nodes': nodes_data, 'links': links_data}
        print(graph_data)    
        return render_template("Rheingold_Tilford_layout.html", graph_data=json.dumps(graph_data))
    elif diagram_type == "Icicle":
        nodes_data = [{'id': node} for node in G1.nodes()]
        links_data = [{'source': edge[0], 'target': edge[1]} for edge in G1.edges()]
        graph_data = {'nodes': nodes_data, 'links': links_data}
        print(graph_data)    
        return render_template("Icicle_layout.html", graph_data=json.dumps(graph_data))



if __name__ == "__main__":
    app.run(debug=True)