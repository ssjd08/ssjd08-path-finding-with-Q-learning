from mininet.net import Mininet
from mininet.cli import CLI
import csv
import subprocess
import random

class Mininet_Network:
    def __init__(self):
        """
        Initialize the Mininet_Network object and create an empty network with switches and hosts.

        This method also initializes empty lists for switches and hosts and link properties.
        """
        self.network = Mininet()
        self.switches = []
        self.hosts = []
        self.link_properties = []

    def create_n_switches(self, switch_numbers: int):
        """
        Create a specified number of switches and add them to the network.

        Args:
            switch_numbers (int): The number of switches to create.
        """
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
            basic_ip (str): The base IP address to assign to the hosts.
        """
        for i in range(len(self.switches)):
            basic_ip_address = f"{basic_ip}{i}."  # Each switch gets its own subnet
            for j in range(host_number_for_each_switch):
                host = self.network.addHost(f"h{i*host_number_for_each_switch + j}")
                self.network.addLink(host, self.switches[i])
                intf = host.defaultIntf()
                
                if intf:
                    host.setIP(f"{basic_ip_address}{j+1}/24")  # Assign IP to default interface
                else:
                    print(f"Warning: {host.name} has no interface")
                
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
            if host.name == node_name:
                return host.IP()  # Use Mininet's `host.IP()` to get the IP address
        return "N/A"

    def save_network_to_csv(self, filename: str = "network_topology.csv"):
        """
        Save the network topology to a CSV file, including all links with correct interface names.
        Args:
            filename (str): Name of the CSV file to save the topology.
        """
        with open(filename, 'w', newline='') as csvfile:
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
                    ip_address = self.get_ip_for_node(node1)
                elif node2.startswith("h"):
                    ip_address = self.get_ip_for_node(node2)

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

        print(f"Network saved to {filename}")


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

    def start_network(self, routing_commands_file:str):
        """
        Start the network, save its topology to a CSV file, and execute a routing commands script.

        Args:
            routing_commands_file (str): Path to the shell script containing routing commands to execute.
        """
        self.network.start()
        subprocess.run(["bash", routing_commands_file], check=True)
        CLI(self.network)
        self.network.stop()

    def load_network_from_csv(self, csv_file_address: str):
        """
        Load a network topology from a CSV file, creating nodes (switches and hosts) and links.

        Args:
            csv_file_address (str): Path to the CSV file containing the network topology.
        """
        with open(csv_file_address, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers
            nodes = {}

            for row in reader:
                node1, node2, link_details, ip_address = row

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
                    # Add the link between nodes with the specified interface names
                    self.network.addLink(nodes[node1], nodes[node2], intfName1=intf1_name, intfName2=intf2_name)

                # Assign IP addresses to hosts only (ignore switches)
                if node1.startswith("h") and ip_address != "N/A":
                    if nodes[node1].defaultIntf():  # Check if interface exists
                        nodes[node1].setIP(ip_address)
                if node2.startswith("h") and ip_address != "N/A":
                    if nodes[node2].defaultIntf():  # Check if interface exists
                        nodes[node2].setIP(ip_address)

    def generate_random_link_properties(self):
        """
        Generate random link properties to connect all switches in the network into one group.
        This ensures every switch is directly connected to every other switch.
        """
        # Ensure there are enough switches to generate links
        if len(self.switches) < 2:
            print("Not enough switches to generate links.")
            return

        # Collect the names of all switches (hosts are excluded)
        switch_names = [switch.name for switch in self.switches]

        # Track generated links to avoid duplicates
        generated_links = set()

        # Generate links to fully connect all switches (clique)
        for i, node1 in enumerate(switch_names):
            for node2 in switch_names[i + 1:]:  # Avoid duplicate or self-links
                # Ensure the link is not already generated
                link_tuple = tuple(sorted((node1, node2)))  # Use sorted tuple to avoid order issues
                if link_tuple in generated_links:
                    continue

                # Generate random link properties
                delay = random.randint(1, 20)  # Random delay between 1ms and 20ms
                bw = random.choice([10, 50, 100, 1000])  # Random bandwidth in Mbps
                loss = round(random.uniform(0.0, 2.0), 2)  # Random packet loss between 0% and 2%

                # Append the generated properties to the list
                self.link_properties.append({
                    "node1": node1,
                    "node2": node2,
                    "delay": delay,
                    "bw": bw,
                    "loss": loss
                })

                # Add the link to the network using Mininet's getNodeByName method
                node1_obj = self.network.getNodeByName(node1)  # Fetch node by name
                node2_obj = self.network.getNodeByName(node2)  # Fetch node by name

                # Make sure the nodes were found in the network
                if node1_obj and node2_obj:
                    # Add link with properties to the network
                    self.network.addLink(node1_obj, node2_obj, bw=bw, delay=delay, loss=loss)
                    
                # Mark this link as generated
                generated_links.add(link_tuple)


    def print_all_link_interfaces(self):
        """
        Prints all link interfaces in the network for debugging.
        Args:
            network: The Mininet network instance.
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


# debug usecase: 

#if __name__ =="__main__":
#    x = Mininet_Network()
#    x.create_n_switches(20)
#    x.create_hosts_for_all_switches(1)
#    x.generate_random_link_properties()
#    print(x.link_properties)
#    x.save_network_to_csv()
#    x.print_all_link_interfaces()
