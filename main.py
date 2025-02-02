from network_creation import Mininet_Network
from networkx_graph import Network_Graph
from DRSIR_DQN import DRSIR_DQN  
import threading
import time
import os

class SDN_Network_Path_Finding:
    def __init__(self, source, destination, network_switch_number:int=20, network_host_number_per_switch:int=2):
        """
        Initialize the SDN network with Q-learning and Dijkstra path-finding.

        Args:
            source (str): The source host.
            destination (str): The destination host.
        """
        self.mininet = Mininet_Network()
        self.mininet_setup(network_switch_number, network_host_number_per_switch)
        self.nx_graph = Network_Graph("network_topology.csv")
        self.source = source
        self.destination = destination
        
        # Initialize DRL agent
        self.drl_agent = DRSIR_DQN(
            graph=self.nx_graph.get_networkx_graph(),
            state_features=4  # Using 4 features as defined in the DRL implementation
        )
        
        self.threads = []

    def mininet_setup(self, network_switch_number, network_host_number_per_switch):
        """Set up the Mininet network."""
        self.mininet.create_n_switches(network_switch_number)
        self.mininet.create_hosts_for_all_switches(network_host_number_per_switch)
        self.mininet.generate_random_link_properties()
        self.mininet.save_network_to_csv()

    def visualize_network(self):
        """Visualize the network graph."""
        self.nx_graph.visualize_graph()

    def generate_routing_commands(self, path, output_file="forwarding_rules.sh"):
        """
        Generate routing commands based on a given path and save them in a shell script.

        Args:
            path (list): The list of nodes representing the path.
            output_file (str): The name of the output shell script file.
        """
        link_details = self.nx_graph.link_details  # Assuming you have link details in nx_graph
        IPs = self.nx_graph.IPs  # Assuming you have IPs in nx_graph
        with open(output_file, "w") as file:
            file.write("#!/bin/bash\n\n")
            file.write(f"# Forwarding rules for path: {path}\n")
            dest_ip = IPs.get(path[-1])
            source_ip = IPs.get(path[0])

            for i in range(1, len(path) - 1):
                node0, node1, node2 = path[i-1], path[i], path[i+1]
                
                # Get interface details
                link_info = link_details.get((node0, node1)) or link_details.get((node1, node0))
                link_info2 = link_details.get((node1, node2)) or link_details.get((node2, node1))
                
                if link_info and link_info2:
                    # Extract port numbers
                    in_port = self._extract_port(link_info, node0, node1)
                    out_port = self._extract_port(link_info2, node1, node2)
                    
                    if node1.startswith("s") and in_port and out_port:
                        file.write(f'sh ovs-ofctl add-flow {node1} "in_port={in_port},dl_type=0x0800,'
                                 f'nw_dst={dest_ip},action=output:{out_port}"\n')
                        file.write(f'sh ovs-ofctl add-flow {node1} "in_port={out_port},dl_type=0x0800,'
                                 f'nw_dst={source_ip},action=output:{in_port}"\n')

            # Add ARP handling
            for node in path:
                if node.startswith("s"):
                    file.write(f'sh ovs-ofctl add-flow {node} "dl_type=0x0806,action=flood"\n')

        print(f"Forwarding rules written to {output_file}")

    def _extract_port(self, link_info, node1, node2):
        """Helper method to extract port numbers from link information."""
        if not link_info:
            return None
            
        link_info_split = link_info.split(',')
        if link_info_split[0].startswith(node1):
            return link_info_split[1].split('-')[-1][-1]
        return link_info_split[0].split('-')[-1][-1]

    def drl_path_finding(self):
        """Perform path finding using DRL."""
        start_time = time.time()
        
        # Train the DRL agent
        print("Training DRL agent...")
        self.drl_agent.train(episodes=100)  # Adjust episodes as needed
        
        # Find the best path
        path = self.drl_agent.find_best_path(self.source, self.destination)
        
        end_time = time.time()
        
        if path:
            self.generate_routing_commands(path, output_file="drl_forwarding_rules.sh")
            print(f"Path found using DRL: {path}")
        else:
            print("No path found between the given nodes")
            
        print(f"Time taken: {end_time - start_time} seconds")
        print("----------------------------------")

    def dijkstra_path_finding(self):
        """Perform path finding using Dijkstra's algorithm."""
        start_time = time.time()
        path = self.nx_graph.dijkstra_path_findings(self.source, self.destination)
        end_time = time.time()
        
        if path:
            self.generate_routing_commands(path, output_file="dijkstra_forwarding_rules.sh")
        else:
            print("No path found between the given nodes")
            
        print(f"Path found using Dijkstra: {path}")
        print(f"Time taken: {end_time - start_time} seconds")
        print("----------------------------------")

    def run(self):
        """Run both path-finding algorithms and start the network."""
        vis_thread = threading.Thread(target=self.visualize_network)
        drl_thread = threading.Thread(target=self.drl_path_finding)
        dijkstra_thread = threading.Thread(target=self.dijkstra_path_finding)
        
        # Start threads
        vis_thread.start()
        drl_thread.start()
        dijkstra_thread.start()
        
        # Store threads
        self.threads.extend([vis_thread, drl_thread, dijkstra_thread])
        
        # Wait for path finding to complete
        drl_thread.join()
        dijkstra_thread.join()
        
        # Make scripts executable
        os.chmod("dijkstra_forwarding_rules.sh", 0o755)
        os.chmod("drl_forwarding_rules.sh", 0o755)
        
        self.stop()

    def stop(self):
        """Stop all threads."""
        for thread in self.threads:
            thread.join()

if __name__ == "__main__":
    # Create network with DRL path finding
    sdn_network = SDN_Network_Path_Finding("h2", "h1", network_switch_number=20, network_host_number_per_switch=2)
    
    # Run path finding algorithms
    sdn_network.run()
    
    print("Path finding complete!")