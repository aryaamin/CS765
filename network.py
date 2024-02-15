import numpy as np
from node import LinkSpeed

class Network:
    def __init__(self, nodes):
        self.nodes = nodes
        pass
    
    def is_fully_connected(nodes):
        # check if graph is fully connected
        idx_set = {0}
        while True:
            new_addition=set()
            for idx in idx_set:
                for node in nodes[idx].connections:
                    if node.id not in idx_set:
                        new_addition.add(node.id)
            if len(new_addition) == 0:
                break
            else:
                idx_set = idx_set.union(new_addition)

        if len(idx_set) == len(nodes):
            return True
        else:
            return False

    def has_min_conns(nodes, min_conns):
        # check if each node has minimum number of connections
        for node in nodes:
            if len(node.connections) < min_conns:
                return False
        return True
    
    def get_delay(self, node1, node2, packet_size):
        p = self.propagation_delay[(node1, node2)]
        c = self.link_speed[(node1, node2)]*1000 # convert to kb per second
        d = np.random.exponential(96/c)
        delay = p + packet_size/c + d
        return delay

    def create_network(self, min_conns, max_conns):
        nodes=self.nodes
        if min_conns >= len(nodes):
            raise ValueError("min_conns should be less than number of nodes")
        while True:
            for node in nodes:
                num_conns = np.random.randint(min_conns, max_conns+1)
                # consider the connections that were already made
                num_conns = max(0, num_conns-len(node.connections))
                # nodes that can be connected to
                other_nodes = [nodes[x] for x in range(node.id+1, len(nodes)) if len(nodes[x].connections)<max_conns]
                if len(other_nodes) == 0:
                    break
                # choose random nodes to connect to
                new_connections = list(np.random.choice(other_nodes, min(num_conns, len(other_nodes)), replace=False))
                # make connections
                for other_node in new_connections:
                    other_node.connections.append(node)
                node.connections += (new_connections)
                
            if Network.is_fully_connected(nodes) and Network.has_min_conns(nodes, min_conns):
                break
            else:
                # reset connections
                for node in nodes:
                    node.connections = []
        
        self.propagation_delay = {}
        self.link_speed = {}
        for (node1, node2) in [(x, y) for x in nodes for y in x.connections]:
            prop_delay = np.random.uniform(0.01, .5)
            self.propagation_delay[(node1, node2)] = prop_delay
            self.propagation_delay[(node2, node1)] = prop_delay
            if node1.link == LinkSpeed.FAST and node2.link == LinkSpeed.FAST:
                self.link_speed[(node1, node2)] = 100
                self.link_speed[(node2, node1)] = 100
            else:
                self.link_speed[(node1, node2)] = 5 
                self.link_speed[(node2, node1)] = 5 