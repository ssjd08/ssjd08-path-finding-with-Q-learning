from network_creation import Mininet_Network
from networkx_graph import Network_Graph
from q_learning import Q_Learning_Path_Finding
import threading
import time
import os



class SDN_Network_Path_Finding_With_Qlearning:
    def __init__(self, source, destination):
        """
        Initialize the SDN network with Q-learning and Dijkstra path-finding.

        Args:
            source (str): The source host.
            destination (str): The destination host.
        """
        self.mininet = Mininet_Network()
        self.mininet.create_mesh_network(4, 2)
        self.nx_graph = Network_Graph("network_topology.csv")
        self.q_learning = Q_Learning_Path_Finding(self.nx_graph, source, destination)
        self.source = source
        self.destination = destination
        self.threads = []

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
                    link_info_split = link_info.split(',')  # Assuming link_info is a string
                    if link_info_split[0].startswith(f"{node0}"):
                        in_port = link_info_split[1].split('-')[-1][-1]
                    else:
                        in_port = link_info_split[0].split('-')[-1][-1]
                
                link_info2 = link_details.get((node1, node2)) or link_details.get((node2, node1))
                if link_info2:
                    link_info2_split = link_info2.split(',')
                    if link_info2_split[0].startswith(f"{node1}"):
                        out_port = link_info2_split[0].split('-')[-1][-1]
                    else:
                        out_port = link_info2_split[1].split('-')[-1][-1]

                if node1.startswith("s") and in_port is not None and out_port is not None:
                    # Add flow command for routing the packet to the destination IP
                    file.write(f'sh ovs-ofctl add-flow {node1} "in_port={in_port},dl_type=0x0800,nw_dst={dest_ip},action=output:{out_port}"\n')
                    file.write(f'sh ovs-ofctl add-flow {node1} "in_port={out_port},dl_type=0x0800,nw_dst={source_ip},action=output:{in_port}"\n')
            
            for node in path:
                if node.startswith("s"):
                    file.write(f'sh ovs-ofctl add-flow {node} "dl_type=0x0806,action=flood"\n')

        print(f"Forwarding rules written to {output_file}")

    def Q_learning_path_finding(self):
        """Perform path finding using Q-learning and optionally generate forwarding rules."""
        start_time = time.time()
        path = self.q_learning.Q_learning_path_finding(method=1)
        end_time = time.time()
        if path:
            # self.generate_routing_commands(path, output_file="qlearning_forwarding_rules.sh")
            pass
        else:
            print("No path found between the given nodes")    
        print(f"Shortest path found using Q-learning: {path} in {end_time - start_time} seconds")
        print("----------------------------------")

    def dijkstra_path_finding(self):
        """Perform path finding using Dijkstra's algorithm and generate forwarding rules."""
        start_time = time.time()
        path = self.nx_graph.dijkstra_path_findings(self.source, self.destination)
        end_time = time.time()
        if path:
            self.generate_routing_commands(path, output_file="dijkstra_forwarding_rules.sh")
        else:
            print("No path found between the given nodes")
        print(f"Shortest path found using Dijkstra's algorithm: {path} in {end_time - start_time} seconds")
        print("----------------------------------")

    def run(self):
        """Run the path-finding algorithms and start the network with generated rules."""
        vis_thread = threading.Thread(target=self.visualize_network)
        q_thread = threading.Thread(target=self.Q_learning_path_finding)
        dik_thread = threading.Thread(target=self.dijkstra_path_finding)
        q_thread.start()
        dik_thread.start()
        vis_thread.start()

        self.threads.append(q_thread)
        self.threads.append(dik_thread)
        self.threads.append(vis_thread)
        q_thread.join()
        dik_thread.join()
        
        os.chmod("dijkstra_forwarding_rules.sh", 0o755)
        os.chmod("qlearning_forwarding_rules.sh", 0o755)

        self.mininet.start_network("dijkstra_forwarding_rules.sh")
        self.stop()

    def stop(self):
        """Stop all threads."""
        for thread in self.threads:
            thread.join()

if __name__ == "__main__":
    x = SDN_Network_Path_Finding_With_Qlearning("h2", "h5")
    x.run()
