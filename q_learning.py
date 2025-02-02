# import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
# import optuna


class Q_Learning_Path_Finding:
    # def __init__(self, graph, source, destination, learning_rate=0.1, discount_rate=0.9, exploration_rate=0.1):
    #     self.graph = graph
    #     self.source = source
    #     self.destination = destination
    #     self.Q_table = np.zeros((len(graph.nodes), len(graph.nodes))) - 10
    #     self.lr = learning_rate
    #     self.dis = discount_rate
    #     self.er = exploration_rate

    def __init__(self, graph, source, destination, learning_rate=0.1, discount_rate=0.9, exploration_rate=0.1):
        """
        Initialize the Q-learning path-finding algorithm with a graph, source, and destination nodes.

        Args:
            graph (networkx.Graph): Graph representing the network.
            source (node): Starting node of the path.
            destination (node): Target node of the path.
            learning_rate (float): Learning rate for Q-learning updates.
            discount_rate (float): Discount factor for future rewards.
            exploration_rate (float): Probability of exploring new paths over exploiting known ones.
        """
        self.graph = graph
        self.node_to_index = {node: i for i, node in enumerate(graph.nodes)}  # Node name to index
        self.index_to_node = {i: node for i, node in enumerate(graph.nodes)}  # Index to node name
        self.source = self.node_to_index[source]
        self.destination = self.node_to_index[destination]
        self.Q_table = np.random.uniform(low=-1, high=1, size=(len(graph.nodes), len(graph.nodes)))
        self.lr = learning_rate
        self.dis = discount_rate
        self.er = exploration_rate


    def calculate_reward(self, state, next_state):
        """
        Calculate the reward for moving from the current state to the next state.

        Args:
            state (int): Current node index.
            next_state (int): Next node index.

        Returns:
            int: Reward value based on the transition.
        """
        if next_state == self.destination:
            return 1000
        elif self.graph.has_edge(state, next_state):
            return 10
        else:
            return -10
    
    # def next_node(self, current_node):
    #     #explore:
    #     random_number = np.random.rand()
    #     if random_number < self.er:
    #         neighbors = list(self.graph.neighbors(current_node))
    #         if not neighbors:  # Check if there are no neighbors
    #             print(f"No neighbors for node {current_node}. Choosing the current node again.")
    #             return current_node  # Return the current node or handle it differently

    #         return np.random.choice(neighbors)
    #     #expolite:
    #     else:
    #         return np.argmax(self.Q_table[current_node])

    def next_node(self, current_node_index):
        """
        Select the next node based on exploration or exploitation.

        Args:
            current_node_index (int): Index of the current node in the graph.

        Returns:
            int: Index of the next node to visit.
        """
        current_node = self.index_to_node[current_node_index]
        random_number = np.random.rand()
        # Explore:
        if random_number < self.er:
            neighbors = list(self.graph.graph.neighbors(current_node))
            if not neighbors:  # No neighbors
                print(f"No neighbors for node {current_node}.")
                return current_node_index
            neighbor_indices = [self.node_to_index[neighbor] for neighbor in neighbors]
            chosen = np.random.choice(neighbor_indices)
            # print(f"Explore: Current={current_node}, Next={self.index_to_node[chosen]}")
            return chosen
        # Exploit:
        else:
            chosen = np.argmax(self.Q_table[current_node_index])
            # print(f"Exploit: Current={current_node}, Next={self.index_to_node[chosen]}")
            return chosen
            
    def update_Q_table(self, current_node, next_node):
        """
        Update the Q-table based on the current state, action, and resulting state.

        This function implements the Q-learning update rule to adjust the Q-value
        for the current state-action pair.

        Args:
            current_node (int): Index of the current node (state).
            next_node (int): Index of the next node (resulting state after taking an action).

        Returns:
            None: The function updates the Q-table in-place and doesn't return a value.
        """
        reward = self.calculate_reward(current_node, next_node)
        best_future_Q = np.max(self.Q_table[next_node])
        self.Q_table[current_node, next_node] += self.lr * (reward + self.dis * best_future_Q - self.Q_table[current_node, next_node])

    def learn_with_source_and_destination(self, episodes=50000):
        """
        Train the Q-learning algorithm using a fixed source and destination.

        This method performs Q-learning iterations to find the optimal path
        from the predefined source to the destination node.

        Args:
            episodes (int): The number of training episodes to perform. Default is 50000.

        Returns:
            None: The function updates the Q-table in-place and doesn't return a value.
        """
        for i in range(episodes):
            # print(f"Learning with source and destination number{i}")
            current_node = self.source
            while current_node != self.destination:
                next_node = self.next_node(current_node)
                self.update_Q_table(current_node, next_node)
                current_node = next_node
        
    
    def learn_with_random_source_and_destination(self, episodes=50000):
        """
        Train the Q-learning algorithm using random source and destination nodes.

        This method performs Q-learning iterations to find optimal paths between
        randomly selected source and destination nodes in the graph. It helps
        the algorithm learn general navigation strategies across the entire graph.

        Args:
            episodes (int): The number of training episodes to perform. Default is 50000.

        Returns:
            None: The function updates the Q-table in-place and doesn't return a value.
        """
        for i in range(episodes):
            current_node = self.source
            steps = 0  # Step counter to avoid infinite loops
            max_steps = 1000  # Set a reasonable maximum number of steps
            while current_node != self.destination and steps < max_steps:
                next_node = self.next_node(current_node)
                self.update_Q_table(current_node, next_node)
                current_node = next_node
                steps += 1
            # if steps >= max_steps:
                # print(f"Episode {i}: Reached maximum steps without finding destination.")

    # def find_shortest_path(self, max_steps=100):
    #     path = [self.source]
    #     current_node = self.source  # Initialize current_node
    #     steps = 0

    #     # Ensure next_node has an initial value
    #     next_node = np.argmax(self.Q_table[current_node, :].flatten())  # Best next node

    #     while current_node != self.destination and steps < max_steps:
    #         path.append(next_node)

    #         # Update current_node for the next iteration
    #         current_node = next_node
    #         next_node = np.argmax(self.Q_table[current_node, :].flatten())  # Best next node for the new current_node
    #         steps += 1

    #     # Only append destination if it's not already the last node in the path
    #     if path[-1] != self.destination:
    #         path.append(self.destination)  # Append destination if it was not reached

    #     return path

    def find_shortest_path(self, max_steps=100):
        """
        Find the shortest path from the source to the destination using the learned Q-table.

        This method uses the Q-values to determine the best path from the source to the
        destination node. It follows the path with the highest Q-values until reaching
        the destination or exceeding the maximum number of steps.

        Args:
            max_steps (int): The maximum number of steps allowed in the path. Default is 100.

        Returns:
            list: A list of node names representing the shortest path from source to destination.
                  If the destination is not reached within max_steps, the path will be truncated
                  and the destination will be appended at the end.
        """
        path = [self.index_to_node[self.source]]
        current_index = self.source
        steps = 0

        while current_index != self.destination and steps < max_steps:
            next_index = np.argmax(self.Q_table[current_index, :].flatten())
            path.append(self.index_to_node[next_index])
            current_index = next_index
            steps += 1

        if path[-1] != self.index_to_node[self.destination]:
            path.append(self.index_to_node[self.destination])

        return path

    def Q_learning_path_finding(self, method:bool=1):
        """
        Perform Q-learning to find a path from source to destination.

        Args:
            method (bool): If 1, use fixed source and destination. If 0, use random source and destination.

        Returns:
            list: Sequence of nodes representing the shortest path from source to destination.
        """
        if method == 1:
            self.learn_with_source_and_destination()
        elif method == 0:
            self.learn_with_random_source_and_destination()
        else:
            print("Invalid method.")
            return None
        
        return self.find_shortest_path()

    