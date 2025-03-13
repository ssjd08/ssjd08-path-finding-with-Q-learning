import numpy as np
import random
import networkx as nx

class QLearningPathFinder:
    def __init__(self, network_graph):
        self.graph = network_graph.get_networkx_graph()
        self.num_nodes = len(self.graph.nodes)
        self.R = np.full((self.num_nodes, self.num_nodes), -500)  # Default penalty for bad moves
        self.Q = np.zeros((self.num_nodes, self.num_nodes))
        self.node_to_index = {node: i for i, node in enumerate(self.graph.nodes)}
        self.index_to_node = {i: node for node, i in self.node_to_index.items()}
        self.goal_node = None  # Goal node to adjust rewards dynamically
        self._initialize_rewards()

    def _initialize_rewards(self):
        print("Initializing rewards...")
        for node in self.graph.nodes:
            for neighbor in self.graph[node]:
                delay = self.graph[node][neighbor]['delay']
                bandwidth = self.graph[node][neighbor]['bandwidth']
                node_index = self.node_to_index[node]
                neighbor_index = self.node_to_index[neighbor]

                # Normal reward calculation (avoid negative infinite rewards)
                self.R[node_index, neighbor_index] = 100 - delay - (1 / bandwidth)
                # print(f"Reward from {node} to {neighbor}: {self.R[node_index, neighbor_index]}")

    def set_goal(self, goal_node):
        """Increase reward for reaching the goal."""
        if goal_node in self.node_to_index:
            self.goal_node = goal_node
            goal_index = self.node_to_index[goal_node]
            self.R[:, goal_index] = 1000  # Huge reward for reaching the goal
            print(f"Set goal node: {goal_node} (index: {goal_index})")

    def next_node(self, start, exploration_rate):
        if start not in self.graph:
            return None
        neighbors = list(self.graph.neighbors(start))
        if not neighbors:
            return None
        if random.uniform(0, 1) < exploration_rate:
            # print(f"Exploring: Randomly choosing a neighbor of {start}")
            return random.choice(neighbors)
        best_neighbor = max(neighbors, key=lambda n: self.Q[self.node_to_index[start], self.node_to_index[n]])
        # print(f"Exploiting: Choosing the best neighbor of {start} (Q-value: {self.Q[self.node_to_index[start], self.node_to_index[best_neighbor]]})")
        return best_neighbor if self.Q[self.node_to_index[start], self.node_to_index[best_neighbor]] > 0 else None

    def update_Q(self, node1, node2, learning_rate, discount_factor):
        if node1 not in self.graph or node2 not in self.graph[node1]:
            return
        node1_index = self.node_to_index[node1]
        node2_index = self.node_to_index[node2]
        max_future_value = np.max(self.Q[node2_index])
        new_q_value = (1 - learning_rate) * self.Q[node1_index, node2_index] + \
                      learning_rate * (self.R[node1_index, node2_index] + discount_factor * max_future_value)
        # print(f"Updating Q-value from {node1} to {node2}: {self.Q[node1_index, node2_index]} -> {new_q_value}")
        self.Q[node1_index, node2_index] = new_q_value

    def learn(self, start, end, exploration_rate, learning_rate, discount_factor, episodes):
        """Train the Q-learning model from start to end."""
        self.set_goal(end)  # Set goal reward before training

        for episode in range(episodes):
            # print(f"\nEpisode {episode + 1}/{episodes}")
            current_node = start
            visited_nodes = set()

            while True:
                visited_nodes.add(current_node)
                next_node = self.next_node(current_node, exploration_rate)
                if next_node is None or next_node in visited_nodes:
                    # print(f"Stopping episode: No valid next node from {current_node}")
                    break
                self.update_Q(current_node, next_node, learning_rate, discount_factor)
                current_node = next_node
                if current_node == end:
                    # print(f"Reached goal node: {end}")
                    break

            if exploration_rate > 0.01:
                exploration_rate *= 0.99  # Reduce exploration over time
            # print(f"Updated exploration rate: {exploration_rate}")

    def shortest_path(self, start, end):
        """Finds the best path using the learned Q-table."""
        if start not in self.graph or end not in self.graph:
            return "Invalid nodes"

        path = [start]
        visited_nodes = set()

        while path[-1] != end:
            current_node = path[-1]
            visited_nodes.add(current_node)

            neighbors = list(self.graph.neighbors(current_node))
            if not neighbors:
                print(f"No neighbors for {current_node}. Ending pathfinding.")
                return "No neighbors"

            # Find the neighbor with the highest Q-value that is not in the path
            best_neighbor = None
            best_q_value = -float('inf')  # Initialize with the smallest possible value

            for neighbor in neighbors:
                if neighbor not in path:
                    q_value = self.Q[self.node_to_index[current_node], self.node_to_index[neighbor]]
                    if q_value > best_q_value:
                        best_neighbor = neighbor
                        best_q_value = q_value

            if best_neighbor:
                path.append(best_neighbor)
                print(f"Added {best_neighbor} to path (Q-value: {best_q_value})")
            else:
                print(f"No valid next node from {current_node}. Ending pathfinding.")
                return "No valid path found"

        print(f"Final path: {path}")
        return path

    def evaluate_path(self, path):
        if len(path) < 2:
            return 0, 0
        total_delay = sum(self.graph[u][v]['delay'] for u, v in zip(path[:-1], path[1:]))
        min_bandwidth = min(self.graph[u][v]['bandwidth'] for u, v in zip(path[:-1], path[1:]))
        return total_delay, min_bandwidth

    def compare_with_dijkstra(self, start, end):
        """Compares Q-learning path with Dijkstra's algorithm."""
        q_path = self.shortest_path(start, end)
        q_delay, q_bandwidth = self.evaluate_path(q_path) if isinstance(q_path, list) else (None, None)

        try:
            d_path = nx.dijkstra_path(self.graph, start, end, weight='delay')
            d_delay, d_bandwidth = self.evaluate_path(d_path)
        except nx.NetworkXNoPath:
            d_path, d_delay, d_bandwidth = "No path", None, None

        return {
            "q_learning_path": q_path,
            "q_learning_delay": q_delay,
            "q_learning_bandwidth": q_bandwidth,
            "dijkstra_path": d_path,
            "dijkstra_delay": d_delay,
            "dijkstra_bandwidth": d_bandwidth,
        }