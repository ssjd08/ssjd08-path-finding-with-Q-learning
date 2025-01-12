import networkx as nx
import csv
import matplotlib.pyplot as plt
print(nx.__version__)

class Network_Graph:
    def __init__(self, csv_file):
        """
        Initialize the Network_Graph object by loading a network topology from a CSV file.

        Args:
            csv_file (str): Path to the CSV file containing the network topology.
        """
        self.graph = nx.Graph()
        self.link_details = {}
        self.IPs = {}
        self.switches = []
        self.hosts = []
        self.load_network_topology(csv_file)

    @property
    def nodes(self):
        """
        Return the nodes of the graph.

        Returns:
            NodeView: All nodes in the network graph.
        """
        return self.graph.nodes  # Return the nodes of the graph

    def has_edge(self, u, v):
        """
        Check if there is an edge between two nodes.

        Args:
            u (str): The first node.
            v (str): The second node.

        Returns:
            bool: True if an edge exists between u and v, False otherwise.
        """
        return self.graph.has_edge(u, v)  # Delegate to NetworkX method

    def neighbors(self, node):
        """
        Get the neighbors of a given node.

        Args:
            node (str): The node for which neighbors are sought.

        Returns:
            iterator: An iterator over the neighbors of the specified node.
        """ 
        return self.graph.neighbors(node)  # Delegate to NetworkX method

    def load_network_topology(self, csv_file:str="network_topology.csv"):
        """
        Load network topology from a CSV file, adding nodes, edges, link properties, and IP addresses.
        Args:
            csv_file (str): Path to the CSV file containing network topology details.
        """
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node1 = row["Node1"]
                node2 = row["Node2"]
                delay = float(row["Delay(ms)"])
                bandwidth = float(row["Bandwidth"])
                loss = float(row["Loss"])
                ip = row.get("IP Address", None)
                # Calculate the edge cost using a weighted sum (adjust alpha, beta, gamma as needed)
                cost = 0.5 * delay + 0.3 * (1 / bandwidth) + 0.2 * loss

                # Add the edge with the computed cost as the weight
                self.graph.add_edge(node1, node2, weight=cost, delay=delay, bandwidth=bandwidth, loss=loss)

                # Store IP addresses for hosts
                if node1.startswith('h'):  # If node1 is a host
                    self.IPs[node1] = ip
                if node2.startswith('h'):  # If node2 is a host
                    self.IPs[node2] = ip

    def categorize_nodes(self):
        """
        Categorize nodes into switches and hosts based on their naming convention.
        """
        self.switches = [node for node in self.graph if node.startswith("s")]
        self.hosts = [node for node in self.graph if node.startswith("h")]

    def dijkstra_path_findings(self, source, destination):
        """
        Find the shortest path between two nodes using Dijkstra's algorithm.

        Args:
            source (str): The source node.
            destination (str): The destination node.

        Returns:
            list or str: List of nodes in the shortest path if a path exists, 
                         otherwise a message indicating no path is found.
        """
        try:
            path = nx.dijkstra_path(self.graph, source, destination)
            return path
        except nx.NetworkXNoPath:
            return "No path found between the given nodes"

    def visualize_graph(self):
        """
        Visualize the network graph with nodes categorized as switches and hosts.
        """
        pos = nx.spring_layout(self.graph)
        self.categorize_nodes()  # Get switches and hosts
        nx.draw(self.graph, pos, nodelist=self.switches, with_labels=True, node_color='lightblue', node_size=3000)
        nx.draw(self.graph, pos, nodelist=self.hosts, with_labels=True, node_color='lightgreen', node_size=1500)
        nx.draw_networkx_edges(self.graph, pos)
        
        # Prepare edge labels (delay, bandwidth, loss)
        edge_labels = {}
        for u, v, data in self.graph.edges(data=True):
            # You can format the label to display delay, bandwidth, and loss as needed
            label = f"Delay: {data['delay']} ms\nBW: {data['bandwidth']} Mbps\nLoss: {data['loss']}%"
            edge_labels[(u, v)] = label

        # Draw edge labels
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)

        # Create a legend for switches and hosts
        switch_patch = plt.Line2D([0], [0], marker='o', color='w', label='Switches', markerfacecolor='lightblue', markersize=10)
        host_patch = plt.Line2D([0], [0], marker='o', color='w', label='Hosts', markerfacecolor='lightgreen', markersize=10)
        plt.legend(handles=[switch_patch, host_patch])

        plt.show()

    def get_networkx_graph(self):
        return self.graph  # Return the internal NetworkX graph

    def weighted_dijkstra_path_finding(self, source, destination):
        """
        Find the shortest path between two nodes using Dijkstra's algorithm.
        
        Args:
            source (str): The source node.
            destination (str): The destination node.
            
        Returns:
            list or str: List of nodes in the shortest path if a path exists, 
                        otherwise a message indicating no path is found.
        """
        try:
            # Find the shortest path using the weight of the edges (cost)
            path = nx.dijkstra_path(self.graph, source, destination, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return "No path found between the given nodes"