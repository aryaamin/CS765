import numpy as np
import argparse
from node import Node, LinkSpeed, CpuSpeed
from network import Network
from simulator import Simulator

if __name__ == "__main__":
    # take command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_nodes", help="number of nodes in the network", type=int, default=10,)
    parser.add_argument("--z0", help="fraction of slow nodes in the network", type=float, default=0.5, required=False)
    parser.add_argument("--z1", help="fraction of nodes with low CPU in the  network", type=float, default=0.5, required=False)
    parser.add_argument("--ttx", help="mean generation time", type=float, default=1.0, required=False)

    Node.ttx = parser.parse_args().ttx

    num_nodes = parser.parse_args().num_nodes
    z0 = parser.parse_args().z0
    z1 = parser.parse_args().z1


    # create nodes
    nodes = []
    for i in range(num_nodes):
        nodes.append(Node(i))
    
    # mark z0 fraction of nodes as slow
    slow_nodes = np.random.choice(nodes, int(z0*len(nodes)), replace=False)
    for node in slow_nodes:
        node.link = LinkSpeed.SLOW
    # mark z1 fraction of nodes as lowCPU
    low_cpu_nodes = np.random.choice(nodes, int(z1*len(nodes)), replace=False)
    for node in low_cpu_nodes:
        node.CPU = CpuSpeed.SLOW

    # create network connections
    Network.create_network(nodes, 4, 8)


    sim = Simulator(nodes)
    Node.simulator = sim
    sim.run()
    print(nodes[0].ledger)
    print(nodes[1].ledger)

    # print connections
    for node in nodes:
        print(node, ":", [x.id for x in node.connections])


    