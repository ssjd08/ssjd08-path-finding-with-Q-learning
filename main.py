from network_creation import Mininet_Network
from networkx_graph import Network_Graph
from q_learning import QLearningPathFinder
import threading
import time
import os
import networkx as nx
import signal
import sys



class SDN_Network_creator:
    """
    A class to create and manage an SDN (Software-Defined Networking) network using Mininet.

    This class provides functionality to create a network topology, visualize it, find paths using Dijkstra's algorithm,
    generate routing commands, and start/stop the network.

    Attributes:
        mininet (Mininet_Network): An instance of the Mininet_Network class to manage the network topology.
        nx_graph (Network_Graph): An instance of the Network_Graph class to represent the network as a graph.
        source (str): The source host for path finding.
        destination (str): The destination host for path finding.
        threads (list): A list to keep track of active threads for visualization and path finding.
    """

    def __init__(self, network_switch_number:int=20, network_host_number_per_switch:int=2,
                 load_existing_network:bool=False, network_topology_file_add:str="network_topology.csv"):
        """
        Initialize the SDN network.

        Args:
            source (str): The source host for path finding.
            destination (str): The destination host for path finding.
            network_switch_number (int): The number of switches to create in the network. Default is 20.
            network_host_number_per_switch (int): The number of hosts to create per switch. Default is 2.
            load_existing_network (bool): If True, load the network topology from a CSV file. Default is False.
            network_topology_file_add (str): The path to the CSV file containing the network topology. Default is "network_topology.csv".

        Raises:
            FileNotFoundError: If the specified CSV file is not found when `load_existing_network` is True.
            Exception: If any other error occurs during network initialization.
        """
        self.mininet = Mininet_Network(network_topology_file_add, network_switch_number, network_host_number_per_switch)
        
        if not load_existing_network:
            self.mininet_setup(network_switch_number, network_host_number_per_switch)
        else:
            try:
                self.mininet.load_network_from_csv(network_topology_file_add)
            except FileNotFoundError:
                raise FileNotFoundError("No network topology file found.")
            except Exception as e:
                raise e
            
        self.nx_graph = Network_Graph("network_topology.csv")
        self.q_learning = QLearningPathFinder(self.nx_graph)
        # self.source = source
        # self.destination = destination
        self.threads = []

    def mininet_setup(self, network_switch_number, network_host_number_per_switch):
        """
        Set up the Mininet network by creating switches, hosts, and links.

        Args:
            network_switch_number (int): The number of switches to create.
            network_host_number_per_switch (int): The number of hosts to create per switch.
        """
        self.mininet.create_n_switches(network_switch_number)
        self.mininet.create_hosts_for_all_switches(network_host_number_per_switch)
        self.mininet.generate_random_connected_network_with_connectivity_percentage(connectivity_percentage=50, connectivity_ensurence=True)
        self.mininet.save_network_to_csv()

    def visualize_network(self):
        """
        Visualize the network graph using NetworkX.

        This method creates a graphical representation of the network topology.
        """
        self.nx_graph.visualize_graph()

    def generate_routing_commands_based_on_path(self, path, output_file="path_based_flow_commands.sh"):
        """
        Generate routing commands based on a given path and save them in a shell script.

        Args:
            path (list): A list of nodes representing the path from source to destination.
            output_file (str): The name of the output shell script file. Default is "routing_commands_file.sh".

        Raises:
            ValueError: If `path` is empty or invalid.
            AttributeError: If the network graph is not properly initialized.
        """
        if not path:
            raise ValueError("Path cannot be empty.")
    
        if not hasattr(self.nx_graph, "link_details") or not hasattr(self.nx_graph, "IPs"):
            raise AttributeError("Network graph is not properly initialized.")
        
        link_details = self.nx_graph.link_details  # Assuming you have link details in nx_graph
        IPs = self.nx_graph.IPs  # Assuming you have IPs in nx_graph
        # print("Link Details:", self.nx_graph.link_details)
        with open(output_file, "w") as file:
            file.write("#!/bin/bash\n\n")
            file.write(f"# Forwarding rules for path: {path}\n")
            dest_ip = IPs.get(path[-1])
            source_ip = IPs.get(path[0])  # Get the destination IP
            # Iterate through the path to generate routing commands
            for i in range(1, len(path) - 1):
                node0 = path[i - 1]  # Previous node
                node1 = path[i]      # Current node
                node2 = path[i + 1]  # Next node
                in_port = None  # Initialize in_port
                out_port = None  # Initialize out_port
                
                # Extract link details for the link between node1 and node2
                link_info = link_details.get((node0, node1)) or link_details.get((node1, node0))
                if link_info:
                    # print(link_info)
                    link_info_split = link_info.split(',')  # Assuming link_info is a string
                    if link_info_split[0].startswith(f"{node0}"):
                        in_port = link_info_split[1].split('-')[-1][-1]
                    else:
                        in_port = link_info_split[0].split('-')[-1][-1]
                    # print(f"inport = {in_port}")                
                link_info2 = link_details.get((node1, node2)) or link_details.get((node2, node1))
                if link_info2:
                    # print(link_info2)
                    link_info2_split = link_info2.split(',')
                    if link_info2_split[0].startswith(f"{node1}"):
                        out_port = link_info2_split[0].split('-')[-1][-1]
                    else:
                        out_port = link_info2_split[1].split('-')[-1][-1]
                    # print(f"outport = {out_port}")
                if node1.startswith("s") and in_port is not None and out_port is not None:
                    # Add flow command for routing the packet to the destination IP
                    file.write(f'/usr/bin/ovs-ofctl add-flow {node1} "in_port={in_port},dl_type=0x0800,nw_dst={dest_ip},action=output:{out_port}"\n')
                    file.write(f'/usr/bin/ovs-ofctl add-flow {node1} "in_port={out_port},dl_type=0x0800,nw_dst={source_ip},action=output:{in_port}"\n')
            
            for node in path:
                if node.startswith("s"):
                    file.write(f'/usr/bin/ovs-ofctl add-flow {node} "dl_type=0x0806,action=flood"\n')

        os.chmod(output_file, 0o755)  # Set execute permissions
        print(f"Forwarding rules written to {output_file}")

    def generate_normal_routing_commands(self, output_file="normal_flow_commands.sh"):
        with open(output_file, 'w') as file:
            file.write("#!/bin/bash\n")
            file.write(f"# Normal forwarding rules:\n")
            for node in self.nx_graph.graph.nodes():
                if node.startswith("s"):
                    file.write(f'/usr/bin/ovs-ofctl add-flow {node} action=normal\n')

        os.chmod(output_file, 0o755)
        print(f"Commands written to {output_file}")

    def dijkstra_path_finding(self, source, dest):
        """
        Perform path finding using Dijkstra's algorithm and generate forwarding rules.

        This method calculates the shortest path between the source and destination hosts using Dijkstra's algorithm
        and generates the corresponding forwarding rules.
        """
        start_time = time.time()
        d_path = self.nx_graph.dijkstra_path_findings(source, dest)
        end_time = time.time()
        if d_path:
            self.generate_routing_commands_based_on_path(d_path, "dijkstra_flow_commands.sh")
        else:
            print("No path found between the given nodes")
        print(f"Shortest path found using Dijkstra's algorithm: {d_path} in {end_time - start_time} seconds")
        print("----------------------------------")
        return d_path

    def Q_learning_path_finding(self, source, dest, exploration_rate=1.0, learning_rate=0.6, discount_factor=0.9, learn_episodes=20000):
        
        self.q_learning.learn(source, dest, exploration_rate, learning_rate, discount_factor, learn_episodes)
        start_time = time.time()
        q_path = self.q_learning.shortest_path(source, dest)
        end_time = time.time()
        if q_path:
            self.generate_routing_commands_based_on_path(q_path, "q_learning_flow_commands.sh")
        else:
            print("No path found between the given nodes")
        print(f"Shortest path found using Q-learning algorithm: {q_path} in {end_time - start_time} seconds")
        print("----------------------------------")
        return q_path

    def evaluate_path(self, path):
        """
        Evaluate the total delay and minimum bandwidth of a given path.
        """
        if len(path) < 2:
            return 0, 0
        total_delay = sum(self.nx_graph.graph[u][v]['delay'] for u, v in zip(path[:-1], path[1:]))
        min_bandwidth = min(self.nx_graph.graph[u][v]['bandwidth'] for u, v in zip(path[:-1], path[1:]))
        return total_delay, min_bandwidth
    
    def path_finding(self, source, dest, exploration_rate=1.0, learning_rate=0.6, discount_factor=0.9, learn_episodes=20000):
        # print(self.q_learning.compare_with_dijkstra(source, dest))
        q_path = self.Q_learning_path_finding(source, dest, exploration_rate, learning_rate, discount_factor, learn_episodes)
        d_path = self.dijkstra_path_finding(source, dest)
        q_delay, q_bandwidth = self.evaluate_path(q_path) if isinstance(q_path, list) else (None, None)
        d_delay, d_bandwidth = self.evaluate_path(d_path)
        print(f"q_learning_path_metrics = (delay :{q_delay}, bandwidth:{q_bandwidth})")
        print(f"dijkstra_path_metrics = (delay :{d_delay}, bandwidth:{d_bandwidth})")
        
    
    def run(self, source, dest):
        """
        Run the path-finding algorithms and start the network with generated rules.

        This method starts threads for visualization and path finding, executes the routing commands,
        and stops the network after completion.
        """
        path_finding_thread = threading.Thread(target=self.path_finding, args=(source, dest,))
        path_finding_thread.start()

        self.visualize_network()
        path_finding_thread.join()
        self.mininet.start_network("dijkstra_flow_commands.sh")
        self.stop()

    def stop(self):
        """
        Stop all active threads.

        This method ensures that all threads are properly joined before exiting.
        """
        for thread in self.threads:
            thread.join()


def get_user_inputs():
    source = input("please enter your source node:").lower()
    destination = input("please enter your dest node:").lower()
    return source, destination

if __name__ == "__main__":
    # signal.signal(signal.SIGINT, signal_handler)
    x = SDN_Network_creator(5, 2)
    source , dest = get_user_inputs()
    x.run(source , dest)
    print("done!")