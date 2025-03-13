from mininet.net import Mininet
from mininet.cli import CLI
import csv
import subprocess
import random
import os

class Mininet_Network:
    """
    A class to create and manage a Mininet network.

    This class provides functionality to create network topologies, save them to CSV files,
    load them from CSV files, and start/stop the network.

    Attributes:
        network (Mininet): The Mininet network instance.
        network_topology_file_add (str): The path to the CSV file for saving/loading the network topology.
        switches (list): A list of switches in the network.
        hosts (list): A list of hosts in the network.
        link_properties (list): A list of link properties (delay, bandwidth, loss) for the network.
    """

    def __init__(self, network_topology_file_add, network_switch_number, network_host_number_per_switch):
        """
        Initialize the Mininet_Network object.

        Args:
            network_topology_file_add (str): The path to the CSV file for saving/loading the network topology.
        """

        self.network = Mininet()
        self.network_topology_file_add = network_topology_file_add
        self.network_switch_number = network_switch_number
        self.network_host_number_per_switch = network_host_number_per_switch
        self.switches = []
        self.hosts = []
        self.link_properties = []

    def create_n_switches(self, switch_numbers: int):
        """
        Create a specified number of switches and add them to the network.

        Args:
            switch_numbers (int): The number of switches to create.

        Raises:
            ValueError: If `switch_numbers` is less than 1.
        """

        if switch_numbers < 1:
            raise ValueError("Number of switches must be at least 1.")
        for i in range(switch_numbers):
            switch = self.network.addSwitch(f"s{i}")
            self.switches.append(switch)


    def create_links_between_all_switches(self):
        """
        Create links between all pairs of switches in the network.

        This method checks if a link already exists between two switches before adding a new one.
        """

        for i in range(len(self.switches)):
            for j in range(len(self.switches)):
                if i != j:
                    if not self.network.linksBetween(self.switches[i], self.switches[j]):
                        self.network.addLink(self.switches[i], self.switches[j])
                    else:
                        print(f"Link already exists between {self.switches[i].name} and {self.switches[j].name}")

    def create_link_between_two_switches(self, switch1:str, switch2:str):
        """
        Create a link between two specific switches.

        Args:
            switch1 (str): The name of the first switch.
            switch2 (str): The name of the second switch.
        """
        if switch1 in self.switches and switch2 in self.switches:
            if not self.network.linksBetween(switch1, switch2):
                self.network.addLink(switch1, switch2)

    def create_hosts_for_all_switches(self, host_number_for_each_switch: int, basic_ip: str = "10.0."):
        """
        Create a specified number of hosts for each switch and assign IP addresses.

        Args:
            host_number_for_each_switch (int): Number of hosts to create for each switch.
            basic_ip (str): The base IP address to assign to the hosts. Default is "10.0.".

        Raises:
            ValueError: If `host_number_for_each_switch` is less than 1.
        """
        self.IPs = {}
        for i in range(len(self.switches)):
            basic_ip_address = f"{basic_ip}{i}."  # Each switch gets its own subnet
            for j in range(host_number_for_each_switch):
                host_name = f"h{i*host_number_for_each_switch + j}"
                ip_address = f"{basic_ip_address}{j+1}/16"  # Assign IP with netmask
                # print(f"Creating host {host_name} with IP {ip_address}")
                host = self.network.addHost(host_name, ip=ip_address)  # Assign IP during host creation
                self.IPs[host_name] = ip_address  
                self.network.addLink(host, self.switches[i])
                self.hosts.append(host)
                
                # Add the host-switch link to self.link_properties
                link_tuple = tuple(sorted((host.name, self.switches[i].name)))  # Ensure order doesn't matter
                delay = random.randint(1, 20)  # Random delay between 1ms and 20ms
                bw = random.choice([10, 50, 100, 1000])  # Random bandwidth in Mbps
                loss = round(random.uniform(0.0, 2.0), 2)  # Random packet loss between 0% and 2%

                # Add the link properties to self.link_properties
                self.link_properties.append({
                    "node1": host.name,
                    "node2": self.switches[i].name,
                    "delay": delay,
                    "bw": bw,
                    "loss": loss
                })


    def get_ip_for_node(self, node_name: str) -> str:
        """
        Retrieve the IP address of a given node.

        Args:
            node_name (str): The name of the node (host or switch).

        Returns:
            str: The IP address of the node, or None if not found.
        """
        for host in self.hosts:
            # print(f"Host {host.name} has IP: {host.IP()}")
            if host.name == node_name:
                return host.IP()  # Use Mininet's `host.IP()` to get the IP address
        return "N/A"

    def save_network_to_csv(self):
        """
        Save the network topology to a CSV file, including all links with correct interface names.

        The CSV file will contain the following columns:
        - Node1: The first node in the link.
        - Node2: The second node in the link.
        - Link Details: The interface names for the link.
        - IP Address: The IP address of the host (if applicable).
        - Delay(ms): The delay of the link.
        - Bandwidth: The bandwidth of the link.
        - Loss: The packet loss of the link.
        """
        with open(self.network_topology_file_add, 'w', newline='') as csvfile:
            fieldnames = ["Node1", "Node2", "Link Details", "IP Address", "Delay(ms)", "Bandwidth", "Loss"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Iterate over each link in the network
            for link in self.network.links:
                node1 = link.intf1.node.name
                node2 = link.intf2.node.name
                link_details = f"{link.intf1.name}, {link.intf2.name}"

                # Initialize default values
                ip_address = "N/A"
                delay = "N/A"
                bw = "N/A"
                loss = "N/A"

                # Assign IP for host-to-switch links
                if node1.startswith("h"):
                    ip_address = self.IPs.get(node1).split('/')[0]
                elif node2.startswith("h"):
                    ip_address = self.IPs.get(node2).split('/')[0]

                # Match link properties if available
                for prop in self.link_properties:
                    if {node1, node2} == {prop["node1"], prop["node2"]}:
                        delay = prop["delay"]
                        bw = prop["bw"]
                        loss = prop["loss"]

                # Write row to CSV
                writer.writerow({
                    "Node1": node1,
                    "Node2": node2,
                    "Link Details": link_details,
                    "IP Address": ip_address,
                    "Delay(ms)": delay,
                    "Bandwidth": bw,
                    "Loss": loss
                })

        print(f"Network saved to {self.network_topology_file_add}")

    def create_mesh_network(self, switch_number:int, host_number_per_switch:int):
        """
        Create a mesh network with the specified number of switches and hosts per switch.

        Args:
            switch_number (int): The number of switches to create.
            host_number_per_switch (int): The number of hosts to create for each switch.
        """
        self.create_n_switches(switch_number)
        self.create_links_between_all_switches()
        self.create_hosts_for_all_switches(host_number_per_switch)

    def start_network(self, routing_commands_file: str = "path_based_flow_commands.sh"):
        """
        Start the network, save its topology to a CSV file, and execute a routing commands script.

        Args:
            routing_commands_file (str): Path to the shell script containing routing commands to execute.

        Raises:
            FileNotFoundError: If the routing commands file does not exist.
            subprocess.CalledProcessError: If the script execution fails.
        """
        if not os.path.exists(routing_commands_file):
            raise FileNotFoundError(f"Routing commands file '{routing_commands_file}' not found.")

        if not os.access(routing_commands_file, os.X_OK):
            raise PermissionError(f"Routing commands file '{routing_commands_file}' is not executable.")

        # Start the network
        self.network.start()

        # Explicitly set custom IP addresses and netmask for all hosts after starting the network
        # for host in self.hosts:
            # print(f"Host {host.name} has IP: {host.IP()}")

        # Execute the routing commands
        try:
            subprocess.run(["bash", routing_commands_file], check=True)
            print("Routing rules executed successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error executing routing commands: {e}")

        # Start the Mininet CLI
        CLI(self.network)
        self.network.stop()

    def load_network_from_csv(self):
        """
        Load a network topology from a CSV file, creating nodes (switches and hosts) and links.

        Raises:
            FileNotFoundError: If the CSV file does not exist.
            KeyError: If the CSV file is missing required columns.
        """
        try:
            with open(self.network_topology_file_add, 'r') as file:
                reader = csv.DictReader(file)  # Use DictReader for easier access to columns
                nodes = {}

                for row in reader:
                    node1 = row["Node1"]
                    node2 = row["Node2"]
                    link_details = row["Link Details"]
                    ip_address = row["IP Address"]
                    delay = int(row["Delay(ms)"]) if row["Delay(ms)"] != "N/A" else None
                    bw = int(row["Bandwidth"]) if row["Bandwidth"] != "N/A" else None
                    loss = float(row["Loss"]) if row["Loss"] != "N/A" else None

                    # Create nodes (switches and hosts)
                    if node1 not in nodes:
                        if node1.startswith("s"):
                            nodes[node1] = self.network.addSwitch(node1)
                            self.switches.append(nodes[node1])
                        elif node1.startswith("h"):
                            nodes[node1] = self.network.addHost(node1)
                            self.hosts.append(nodes[node1])

                    if node2 not in nodes:
                        if node2.startswith("s"):
                            nodes[node2] = self.network.addSwitch(node2)
                            self.switches.append(nodes[node2])
                        elif node2.startswith("h"):
                            nodes[node2] = self.network.addHost(node2)
                            self.hosts.append(nodes[node2])

                    # Parse link details to get specific interfaces
                    intf1_name, intf2_name = link_details.split(', ')

                    # Check if the link already exists
                    if not self.network.linksBetween(nodes[node1], nodes[node2]):
                        # Add the link between nodes with the specified interface names and properties
                        self.network.addLink(
                            nodes[node1], nodes[node2],
                            intfName1=intf1_name, intfName2=intf2_name,
                            bw=bw, delay=f"{delay}ms", loss=loss
                        )

                    # Assign IP addresses to hosts only (ignore switches)
                    if node1.startswith("h") and ip_address != "N/A":
                        if nodes[node1].defaultIntf():  # Check if interface exists
                            nodes[node1].setIP(ip_address)
                    if node2.startswith("h") and ip_address != "N/A":
                        if nodes[node2].defaultIntf():  # Check if interface exists
                            nodes[node2].setIP(ip_address)

                    # Store link properties
                    self.link_properties.append({
                        "node1": node1,
                        "node2": node2,
                        "delay": delay,
                        "bw": bw,
                        "loss": loss
                    })
        except FileNotFoundError:
            print(f"Error: File '{self.network_topology_file_add}' not found.")
            raise
        except KeyError as e:
            print(f"Error in CSV file: {e}")
            raise

    def generate_fully_connected_network(self):
        """
        Generate random link properties to connect all switches in the network into one group.
        This ensures every switch is directly connected to every other switch.
        """
        
        if len(self.switches) < 2:
            print("Not enough switches to generate links.")
            return

        switch_names = [switch.name for switch in self.switches]

        generated_links = set()

        # Generate links to fully connect all switches (clique)
        for i, node1 in enumerate(switch_names):
            for node2 in switch_names[i + 1:]:
                
                link_tuple = tuple(sorted((node1, node2)))  
                if link_tuple in generated_links:
                    continue

                
                delay = random.randint(1, 20)  
                bw = random.choice([10, 50, 100, 1000])  
                loss = round(random.uniform(0.0, 2.0), 2)  

                # Append the generated properties to the list
                self.link_properties.append({
                    "node1": node1,
                    "node2": node2,
                    "delay": delay,
                    "bw": bw,
                    "loss": loss
                })

                node1_obj = self.network.getNodeByName(node1)  
                node2_obj = self.network.getNodeByName(node2)  

                if node1_obj and node2_obj:
                    # Add link with properties to the network
                    self.network.addLink(node1_obj, node2_obj, bw=bw, delay=delay, loss=loss)
                    
                # Mark this link as generated
                generated_links.add(link_tuple)


    def print_all_link_interfaces(self):
        """
        Prints all link interfaces in the network for debugging.
        """
        print("All Link Interfaces:")
        for link in self.network.links:
            node1 = link.intf1.node.name
            node2 = link.intf2.node.name
            intf1_name = link.intf1.name
            intf2_name = link.intf2.name

            print(f"Link between {node1} and {node2}:")
            print(f"  - Interface 1: {intf1_name} (Node: {node1})")
            print(f"  - Interface 2: {intf2_name} (Node: {node2})")
        print("Done listing all link interfaces.")
        
    def generate_connected_network(self):
        """
        Generate a connected network, ensuring all switches are connected, but not fully connected.
        This creates a spanning tree or a random connected graph.
        """
        if len(self.switches) < 2:
            print("Not enough switches to generate links.")
            return

        switch_names = [switch.name for switch in self.switches]

        # To track the links and ensure the network is connected
        generated_links = set()
        connected_switches = set() 
        connected_switches.add(switch_names[0]) 
        
        # Try to generate links randomly
        while len(generated_links) < len(self.switches) - 1:
            node1 = random.choice(list(connected_switches))
            node2 = random.choice([switch for switch in switch_names if switch not in connected_switches])

            # Generate a link only if it's not already created
            link_tuple = tuple(sorted((node1, node2)))  
            if link_tuple not in generated_links:
                delay = random.randint(1, 20)  
                bw = random.choice([10, 50, 100, 1000])  
                loss = round(random.uniform(0.0, 2.0), 2)  

                # Store link properties
                self.link_properties.append({
                    "node1": node1,
                    "node2": node2,
                    "delay": delay,
                    "bw": bw,
                    "loss": loss
                })

                # Add the link to the network
                node1_obj = self.network.getNodeByName(node1)
                node2_obj = self.network.getNodeByName(node2)
                if node1_obj and node2_obj:
                    self.network.addLink(node1_obj, node2_obj, bw=bw, delay=delay, loss=loss)

                # Add node2 to the set of connected switches
                connected_switches.add(node2)

                # Mark this link as generated
                generated_links.add(link_tuple)

    def generate_random_connected_network_with_connectivity_percentage(self, connectivity_percentage=50, connectivity_ensurence=True,
                                                                        bw_range:set=(10, 1000), delay_range:set=(1, 20)):
        """
        Generate a random but connected network topology with a specified connectivity percentage.

        Args:
            connectivity_percentage (int): Percentage of possible links to establish.
            connectivity_ensurence (bool): Ensure the network remains connected.

        """
        # Ensure that the network and switches are initialized
        if not hasattr(self, 'network') or not hasattr(self, 'switches'):
            raise AttributeError("Network or switches are not initialized.")

        switch_names = [switch.name for switch in self.switches]
        connected_switches = set()

        # Ensure at least one switch is connected
        if not switch_names:
            raise ValueError("No switches available to generate links.")

        # Start with the first switch
        connected_switches.add(switch_names[0])

        # Generate links until all switches are connected
        while len(connected_switches) < len(switch_names):
            node1 = random.choice(list(connected_switches))
            node2 = random.choice([switch for switch in switch_names if switch not in connected_switches])

            # Generate random link properties
            delay = random.randint(delay_range[0], delay_range[1])  # Random delay between 1ms and 20ms
            bw = random.randint(bw_range[0], bw_range[1])  # Random bandwidth in Mbps
            loss = round(random.uniform(0.0, 2.0), 2)  # Random packet loss between 0% and 2%

            # Add the link to the network
            node1_obj = self.network.getNodeByName(node1)
            node2_obj = self.network.getNodeByName(node2)
            if node1_obj and node2_obj:
                self.network.addLink(node1_obj, node2_obj, bw=bw, delay=f"{delay}ms", loss=loss)

            # Add the link properties to self.link_properties
            self.link_properties.append({
                "node1": node1,
                "node2": node2,
                "delay": delay,
                "bw": bw,
                "loss": loss
            })

            # Mark node2 as connected
            connected_switches.add(node2)

        # Optionally add additional links based on connectivity_percentage
        if connectivity_ensurence:
            total_possible_links = len(switch_names) * (len(switch_names) - 1) // 2
            additional_links = int((connectivity_percentage / 100) * total_possible_links) - len(self.link_properties)

            for _ in range(additional_links):
                node1 = random.choice(switch_names)
                node2 = random.choice(switch_names)
                if node1 != node2 and not self.network.linksBetween(node1, node2):
                    delay = random.randint(1, 20)
                    bw = random.choice([10, 50, 100, 1000])
                    loss = round(random.uniform(0.0, 2.0), 2)

                    node1_obj = self.network.getNodeByName(node1)
                    node2_obj = self.network.getNodeByName(node2)
                    if node1_obj and node2_obj:
                        self.network.addLink(node1_obj, node2_obj, bw=bw, delay=f"{delay}ms", loss=loss)

                    self.link_properties.append({
                        "node1": node1,
                        "node2": node2,
                        "delay": delay,
                        "bw": bw,
                        "loss": loss
                    })


# debug usecase: 

# if __name__ =="__main__":
#    x = Mininet_Network()
#    x.create_n_switches(20)
#    x.create_hosts_for_all_switches(1)
#    x.generate_random_link_properties()
#    print(x.link_properties)
#    x.save_network_to_csv()
#    x.print_all_link_interfaces()