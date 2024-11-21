import networkx as nx
import csv
import matplotlib.pyplot as plt

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

    def load_network_topology(self, csv_file):
        """
        Load network topology from a CSV file, adding nodes, edges, and IP addresses.

        Args:
            csv_file (str): Path to the CSV file containing network topology details.
        """
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  
            for row in reader:
                node1, node2, link_details, ip_address = row
                self.graph.add_edge(node1, node2)
                self.link_details[(node1, node2)] = link_details
                self.link_details[(node2, node1)] = link_details
                if node1.startswith("h"):
                    self.IPs[node1] = ip_address

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
        
        # Create a legend
        switch_patch = plt.Line2D([0], [0], marker='o', color='w', label='Switches', markerfacecolor='lightblue', markersize=10)
        host_patch = plt.Line2D([0], [0], marker='o', color='w', label='Hosts', markerfacecolor='lightgreen', markersize=10)
        plt.legend(handles=[switch_patch, host_patch])
        
        plt.show()

    def get_networkx_graph(self):
        return self.graph  # Return the internal NetworkX graph
