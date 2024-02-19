import random
from queue import PriorityQueue
from enum import Enum
import sys, os
import networkx as nx
import matplotlib.pyplot as plt

class EventType(Enum):
    SEND_TRANSACTION = 1
    SEND_BLOCK = 2
    RECEIVE_TRANSACTION = 3
    RECEIVE_BLOCK = 4
            
class Event:
    def __init__(self, time:float, node, event_type:EventType):
        self.time = time
        self.node = node
        self.event_type = event_type

        self.from_node = None
        self.block = None
        self.transaction = None
    
    def __lt__(self, other):
        return self.time < other.time

class Simulator:
    def __init__(self, nodes, network):
        self.events = PriorityQueue()
        self.time = 0.0
        self.nodes = nodes
        self.network = network

    def add_event(self, event:Event):
        # print("Adding event: ", event.event_type, " at time: ", event.time)
        self.events.put(event)

    def run(self):
        ledger={}
        for i in range(len(self.nodes)):
            ledger[i] = random.randint(50, 1000)

        print("Initial Ledger: ", ledger)

        for node in self.nodes:
            node.start(ledger.copy())
        for node in self.nodes:
            node.generate_transaction_event(self.time)

        while not self.events.empty():
            event = self.events.get()
            self.time = event.time
            self.process_event(event)
        
        for node in self.nodes:
            print(str(node.id) + " Ledger: ", node.ledger)
            node.log_blockchain()
        
        orig_out = sys.stdout
        filename = "output/connections.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            sys.stdout = file
            for node in self.nodes:
                print(node.id, [x.id for x in node.connections])
        sys.stdout = orig_out
        
        nodes = []
        edges = []
        # Define edges as tuples (source, target)
        for node in self.nodes:
            nodes.append(node.id)
            for x in node.connections:
                if x.id > node.id:
                    edges.append((node.id, x.id))
                    
        # Create a graph object
        G = nx.Graph()

        # Add nodes to the graph
        G.add_nodes_from(nodes)

        # Add edges to the graph
        G.add_edges_from(edges)

        # Draw the graph
        pos = nx.spring_layout(G)  # positions for all nodes

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=700)

        # Draw edges
        nx.draw_networkx_edges(G, pos, edgelist=edges, width=2)

        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')

        # Display the graph
        plt.axis('off')
        plt.savefig('output/connections.png', format='png')


    def process_event(self, event:Event):
        if event.event_type==EventType.SEND_TRANSACTION and self.time > 20:
            return
        
        if event.event_type == EventType.SEND_TRANSACTION:
            event.node.send_transaction(event, self.time)
        elif event.event_type == EventType.SEND_BLOCK:
            event.node.send_block(event, self.time)
        elif event.event_type == EventType.RECEIVE_TRANSACTION:
            event.node.receive_transaction(event, self.time)
        elif event.event_type == EventType.RECEIVE_BLOCK:
            event.node.receive_block(event, self.time)
