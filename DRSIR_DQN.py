import random
import numpy as np
import networkx as nx
from collections import deque
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam


class DRSIR_DQN:
    def __init__(self, graph, k_paths=None, state_features=4, 
                 learning_rate=0.001, gamma=0.9, epsilon_max=1.0, 
                 epsilon_min=0.1, epsilon_decay=0.995, 
                 replay_memory_size=1000, batch_size=32, 
                 target_update_freq=10, 
                 beta1=0.33, beta2=0.33, beta3=0.34):
        """
        Initialize the DRSIR Deep Q-Learning algorithm.
        
        Args:
            graph (networkx.Graph): Network topology
            k_paths (dict, optional): Precomputed k-shortest paths. Defaults to None.
            state_features (int, optional): Number of features per state. Defaults to 4.
            learning_rate (float, optional): Learning rate for neural network. Defaults to 0.001.
            gamma (float, optional): Discount factor. Defaults to 0.9.
            epsilon_max (float, optional): Initial exploration probability. Defaults to 1.0.
            epsilon_min (float, optional): Minimum exploration probability. Defaults to 0.1.
            epsilon_decay (float, optional): Decay rate for exploration. Defaults to 0.995.
            replay_memory_size (int, optional): Replay memory size. Defaults to 1000.
            batch_size (int, optional): Training batch size. Defaults to 32.
            target_update_freq (int, optional): Target network update frequency. Defaults to 10.
            beta1, beta2, beta3 (float, optional): Reward function weights. Defaults to 0.33, 0.33, 0.34.
        """
        self.graph = graph
        self.k_paths = k_paths or {}
        self.state_features = state_features
        self.action_size = len(graph.nodes)
        
        # Hyperparameters
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon_max
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        
        # Training parameters
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.beta1, self.beta2, self.beta3 = beta1, beta2, beta3
        
        # Replay memory
        self.replay_memory = deque(maxlen=replay_memory_size)
        
        # Neural networks
        self.online_model = self._build_model()
        self.target_model = self._build_model()
        self._update_target_model()

    def _build_model(self):
        """Build neural network model for Q-value estimation."""
        model = Sequential([
            Dense(64, input_dim=self.state_features, activation='relu'),
            Dense(64, activation='relu'),
            Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def _update_target_model(self):
        """Copy weights from online to target network."""
        self.target_model.set_weights(self.online_model.get_weights())

    def _extract_state_features(self, node):
        """
        Extract network state features for a node.
        
        Args:
            node (str): Network node
        
        Returns:
            np.array: Normalized features
        """
        features = [
            self.graph.degree(node),
            nx.clustering(self.graph, node),
            nx.betweenness_centrality(self.graph)[node],
            len(list(self.graph.neighbors(node)))
        ]
        return np.array(features) / np.max(features)

    def calculate_reward(self, path_metrics):
        """
        Calculate reward based on path metrics.
        
        Args:
            path_metrics (dict): Dictionary with bandwidth, delay, loss metrics
        
        Returns:
            float: Calculated reward
        """
        bwa_norm = path_metrics.get('bandwidth', 1)
        delay_norm = path_metrics.get('delay', 0)
        loss_norm = path_metrics.get('loss', 0)
        
        return (self.beta1 * (1 / bwa_norm) + 
                self.beta2 * delay_norm + 
                self.beta3 * loss_norm)

    def act(self, state):
        """
        Choose action using epsilon-greedy policy.
        
        Args:
            state (np.array): Current state
        
        Returns:
            int: Selected action (node)
        """
        if np.random.rand() <= self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        q_values = self.online_model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(q_values[0])

    def train(self, episodes=100, max_steps=50):
        """
        Train the DRSIR agent.
        
        Args:
            episodes (int, optional): Number of training episodes. Defaults to 100.
            max_steps (int, optional): Maximum steps per episode. Defaults to 50.
        """
        nodes = list(self.graph.nodes)
        
        for episode in range(episodes):
            source, destination = random.sample(nodes, 2)
            current_node = source
            state = self._extract_state_features(current_node)
            
            for step in range(max_steps):
                action = self.act(state)
                next_node = list(self.graph.neighbors(current_node))[action % len(list(self.graph.neighbors(current_node)))]
                
                # Compute path metrics (placeholder - replace with actual network metrics)
                path_metrics = {
                    'bandwidth': self.graph[current_node][next_node].get('bandwidth', 1),
                    'delay': self.graph[current_node][next_node].get('delay', 0),
                    'loss': self.graph[current_node][next_node].get('loss', 0)
                }
                
                reward = self.calculate_reward(path_metrics)
                done = next_node == destination
                
                next_state = self._extract_state_features(next_node)
                
                self.replay_memory.append((state, action, reward, next_state, done))
                
                if len(self.replay_memory) >= self.batch_size:
                    self._replay()
                
                state = next_state
                current_node = next_node
                
                if done:
                    break
            
            # Decay exploration
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def _replay(self):
        """Experience replay for training."""
        mini_batch = random.sample(self.replay_memory, self.batch_size)
        
        states, targets = [], []
        for state, action, reward, next_state, done in mini_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.max(self.target_model.predict(next_state.reshape(1, -1), verbose=0)[0])
            
            target_f = self.online_model.predict(state.reshape(1, -1), verbose=0)
            target_f[0][action] = target
            
            states.append(state)
            targets.append(target_f[0])
        
        self.online_model.fit(np.array(states), np.array(targets), epochs=1, verbose=0)

    def find_best_path(self, source, destination):
        """
        Find best path between source and destination.
        
        Args:
            source (str): Source node
            destination (str): Destination node
        
        Returns:
            list: Best path between source and destination
        """
        current_node = source
        path = [current_node]
        
        while current_node != destination:
            state = self._extract_state_features(current_node)
            action = self.act(state)
            
            neighbors = list(self.graph.neighbors(current_node))
            next_node = neighbors[action % len(neighbors)]
            
            path.append(next_node)
            current_node = next_node
        
        return path