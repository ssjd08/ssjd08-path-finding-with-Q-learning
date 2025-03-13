# Path Finding with Q-Learning in Mininet

This project implements a Q-Learning algorithm to determine optimal paths in a network topology created in Mininet. The goal is to find paths that minimize delay and maximize bandwidth between nodes.

## Table of Contents

- [Introduction](#introduction)  
- [Features](#features)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Files](#files)  
- [Contributing](#contributing)  

## Introduction

Q-Learning is a reinforcement learning technique used to find optimal actions in a given environment. In this project, we apply Q-Learning to identify the most efficient paths in a network created in Mininet by considering factors such as delay and bandwidth.

## Features

- Dynamic network topology creation in **Mininet**  
- Q-Learning implementation for path optimization  
- Comparison with Dijkstra's algorithm  
- **Flow entry generation** for SDN controllers  
- **Network visualization** using NetworkX  

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ssjd08/ssjd08-path-finding-with-Q-learning.git
   cd ssjd08-path-finding-with-Q-learning
   ```
   
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Install Mininet** (if not already installed):  
   ```bash
   sudo apt-get install mininet
   ```

## Usage

### Start the Project:

Run the following command to start the project:

```bash
sudo python main.py
```

This script performs the following tasks:
- **Creates a network topology** in Mininet and saves it to `network_topology.csv`.
- **Builds a NetworkX graph** representation of the network.
- **Initializes Q-Learning instances** for path optimization.
- **Allows user customization** of the number of switches and hosts per switch by modifying the script.
- **Receives user input** for source and destination nodes.
- **Finds the best path** using both Dijkstra’s algorithm and Q-Learning.
- **Generates flow commands** for the discovered paths and saves them to `dijkstra_flow_commands.sh` and `q_learning_flow_commands.sh`.
- **Executes flow commands** to configure the Mininet network for user interaction.
- **Starts the Mininet environment**, allowing users to work with the optimized paths.

## Files

- `main.py` - Main script to execute the project.  
- `network_creation.py` - Script to create the Mininet network topology.  
- `network_topology.csv` - CSV file representing the network topology.  
- `networkx_graph.py` - Script to visualize the network graph.  
- `q_learning.py` - Implementation of the Q-Learning algorithm for path finding.  
- `q_learning_flow_commands.sh` - Script to generate flow commands for Mininet.  
- `requirements.txt` - List of required Python packages.  
- `.gitignore` - Specifies files and directories to be ignored by git.  

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

