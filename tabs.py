import streamlit as st
import json
from Model import metamodel_dict
import uuid
import graphviz
from streamlit_agraph import agraph, Node, Edge, Config
import networkx as nx
from graph_functions import output_nodes_and_edges, count_nodes, count_edges, density_graph, show_shortest_paths


def print_hi(name, age):
    # Use a breakpoint in the code line below to debug your script.
    st.info(f'Hi, My name is {name} and I am {age} years old')  # Press Ctrl+F8 to toggle the breakpoint.

def save_node(name, age):
    node_dict = {
        "name": name,
        "age": age,
        "id": str(uuid.uuid4()),
        "type": "Node"
    }
    st.session_state["node_list"].append(node_dict)


def save_edge(node1, relation, node2):
    edge_dict = {
        "source": node1,
        "target": node2,
        "type": relation,
        "id": str(uuid.uuid4()),
    }
    st.session_state["edge_list"].append(edge_dict)
def upload_graph():
    uploaded_graph = st.file_uploader("upload an existing graph", type="json")
    if uploaded_graph is not None:
        uploaded_graph_dict = json.load(uploaded_graph)
        uploaded_nodes = uploaded_graph_dict["nodes"]
        uploaded_edges = uploaded_graph_dict["edges"]
        st.json(uploaded_graph_dict, expanded=False)
    else:
        st.info("Please upload a graph if available")

    update_graph_button = st.button(
        "update graph via the upload",
        use_container_width=True,
        type="primary"
    )
    if update_graph_button and uploaded_graph:
        st.session_state["node_list"] = uploaded_nodes
        st.session_state["edge_list"] = uploaded_edges
        graph_dict = {
            "nodes": st.session_state["node_list"],
            "edges": st.session_state["edge_list"],
        }
        st.session_state["graph_dict"] = graph_dict
        #st.json(uploaded_graph_dict, expanded=False)

def create_node():
    name_node = st.text_input("Type in the name of the node")
    #type_n = st.selectbox("Node", "Node")
    age_node = st.number_input('Input the age of the node', value=0)
    # age_node = int(st.number_input('Input the age of the node', value=0))
    print_hi(name_node, age_node)
    save_node_button = st.button("Store Node", use_container_width=True, type="primary")
    if save_node_button:
        save_node(name_node, age_node)
    st.write(st.session_state["node_list"])

def create_relation():
    # UI rendering
    node1_col, relation_col, node2_col = st.columns(3)
    # Logic
    node_list = st.session_state["node_list"]
    node_name_list = []
    for node in node_list:
        node_name_list.append(node["name"])

    with node1_col:
        node1_select = st.selectbox(
            "select the first node",
            options=node_name_list,
            # key = "node1_select" # can be added
        )
    with relation_col:
        # Logic
        relation_list = metamodel_dict["edges"]
        # UI rendering
        relation_name = st.selectbox(
            "Specify the relation",
            options=relation_list
        )
    with node2_col:
        node2_select = st.selectbox(
            "select the second node",
            options=node_name_list,
            # key= "node2_select"  # can be added
        )

    store_edge_button = st.button("store relation", use_container_width=True, type="primary")
    if store_edge_button:
        save_edge(node1_select, relation_name, node2_select)

    st.write(f"{node1_select} is {relation_name}  {node2_select}")  # most pythonic way to do
    # st.write(node1_select + "is" + relation_name + node2_select) # does work but tedious

    st.write(st.session_state["edge_list"])

def store_graph():
    with st.expander("show individual lists"):
        st.json(st.session_state["node_list"], expanded=False)
        st.json(st.session_state["edge_list"], expanded=False)

    graph_dict = {
        "nodes": st.session_state["node_list"],
        "edges": st.session_state["edge_list"],
    }
    st.session_state["graph_dict"] = graph_dict
    with st.expander("Show graph JSON"):
        st.json(st.session_state["graph_dict"])

def visualization_graph():

    def set_color(node_type):
        color = "Green"
        if node_type=="Person":
            color = "Green"
        elif node_type=="pets":
            color = "Yellow"
        return color


    with st.expander("Visualise the Graph"):

        graph = graphviz.Digraph()

        visual_dict = {
            "nodes": st.session_state["node_list"],
            "edges": st.session_state["edge_list"],
        }
        st.session_state["visual_dict"] = visual_dict
        #visual_dict = st.session_state["graph_dict"]
        node_list = visual_dict["nodes"]
        edge_list = visual_dict["edges"]
        for node in node_list:
            node_name = node["name"]
            graph.node(node_name, node_name, color= set_color(node_type="Person"))
        for edge in edge_list:
            source = edge["source"]
            target = edge["target"]
            relation = edge["type"]
            graph.edge(source, target, relation)
        st.graphviz_chart(graph)

    with st.expander("AGraph Visualisation"):
        nodes = []
        edges = []
        graph_dict = {
           "nodes": st.session_state["node_list"],
           "edges": st.session_state["edge_list"],
        }
        st.session_state["graph_dict"] = graph_dict
        #graph_dict = st.session_state["graph_dict"]
        node_list = graph_dict["nodes"]
        edge_list = graph_dict["edges"]

        for node in node_list:
            # id = node["id"]
            node_name = node["name"]

            # nodes = []

            nodes.append(Node(id=node_name,
                              label=node_name,
                              size=25)
                         # shape="circularImage",
                         # image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png")
                         )  # includes **kwargs
        for edge in edge_list:
            source = edge["source"]
            target = edge["target"]
            relation = edge["type"]
            # edges = []
            edges.append(Edge(source=source,
                              label=relation,
                              target=target,
                              # **kwargs
                              )
                         )

        config = Config(width=750,
                        height=950,
                        directed=True,
                        physics=True,
                        hierarchical=False,
                        # **kwargs
                        )

        return_value = agraph(nodes=nodes,
                              edges=edges,
                              config=config)

    # graph.node("test")
    # graph.edge("run","intr")

def analyze_graph():
    G = nx.Graph()

    graph_dict = st.session_state["graph_dict"]
    node_list = graph_dict["nodes"]
    edge_list = graph_dict["edges"]
    node_tuple_list = []
    edge_tuple_list = []

    for node in node_list:
        # id = node["id"]
        # node_name = node["name"]
        node_tuple = (node["name"], node)
        node_tuple_list.append(node_tuple)

    for edge in edge_list:
        edge_tuple = (edge["source"], edge["target"], edge)
        edge_tuple_list.append(edge_tuple)

    G.add_nodes_from(node_tuple_list)
    G.add_edges_from(edge_tuple_list)
    # st.write(G.nodes)
    # st.write(G.edges)

    select_functions = st.selectbox(label="Select Function",
                                    options=["Output Nodes and Edges",
                                             "Count Nodes",
                                             "Count Edges",
                                             "Specific Edge",
                                             "Density",
                                             "Shortest Path"])
    if select_functions == "Output Nodes and Edges":
        output_nodes_and_edges(graph=G)
    elif select_functions == "Count Nodes":
        count_nodes(G)
    elif select_functions == "Count Edges":
        count_edges(G)
    elif select_functions == "Specific Edge":
        pass
    elif select_functions == "Density":
        density_graph(G)
    elif select_functions == "Shortest Path":
        show_shortest_paths(G)

    # st.write(G.number_of_nodes())
    # st.write(G.number_of_edges())

def export_graph():

    graph_string = json.dumps(st.session_state["graph_dict"])
    # st.write(graph_string)

    st.download_button(
        "Export Graph to JSON",
        file_name="graph.json",
        mime="application/json",
        data=graph_string,
        use_container_width=True,
        type="primary"
    )