from enum import Enum
from queue import PriorityQueue
import numpy as np
import argparse

class Transaction:
    def __init__(self, txn_id, payer_id, receiver_id, coins):
        self.txn_id = txn_id
        self.payer_id = payer_id
        self.receiver_id = receiver_id
        self.coins = coins

class Block:
    def __init__(self, data):
        self.data = data
        self.next = None

class Peer:
    ttx = 1
    def __init__(self, id, link_speed, cpu_speed):
        self.id = id
        self.link_speed = link_speed
        self.cpu_speed = cpu_speed
        self.connections = []

    def __str__(self):
        return str(self.id)
    
    def generate_transaction(self):
        pass
    
    # def receive_block(self, block):
    #     pass

    def generate_block(self):
        # choose random value t from exponential distribution using numpy
        t  = np.random.exponential(Node.ttx)
        pass

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

if __name__ == "__main__":
    # take command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_nodes", help="number of nodes in the network", type=int, default=10,)
    parser.add_argument("--z0", help="fraction of slow nodes in the network", type=float, default=0.5, required=False)
    parser.add_argument("--z1", help="fraction of nodes with low CPU in the  network", type=float, default=0.5, required=False)
    parser.add_argument("--ttx", help="mean generation time", type=float, default=1.0, required=False)

    Node.ttx = parser.parse_args().ttx

    # create nodes
    nodes = []
    for i in range(parser.parse_args().num_nodes):
        nodes.append(Node(i))
    
    Network.create_network(nodes, 4, 8)

    # print connections
    for node in nodes:
        print(node, ":", [x.id for x in node.connections])

    
    
    