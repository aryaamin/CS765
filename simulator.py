import random
from queue import PriorityQueue
from enum import Enum


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
        self.block = None
        self.transaction = None
    
    def __lt__(self, other):
        return self.time < other.time

class Simulator:
    def __init__(self, nodes):
        self.events = PriorityQueue()
        self.time = 0
        self.nodes = nodes

    def add_event(self, event:Event):
        self.events.put(event)

    def run(self):
        ledger={}
        for i in range(len(self.nodes)):
            ledger[i] = random.randint(50, 1000)
        for node in self.nodes:
            node.start(ledger.copy())
        for node in self.nodes:
            node.generate_transaction_event(self.time)



        while not self.events.empty():
            event = self.events.get()
            self.time = event.time
            self.process_event(event)

    def process_event(self, event:Event):
        if event.event_type == EventType.SEND_TRANSACTION:
            event.node.send_transaction()
        else:
            pass
        pass