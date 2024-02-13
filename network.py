import numpy as np

class Network:
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
    
    def create_network(nodes, min_conns, max_conns):
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