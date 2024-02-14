from enum import Enum
from queue import PriorityQueue
import numpy as np
import argparse
import random
from simulator import Event,Simulator
from blockchain import Block, Blockchain, Transaction


class LinkSpeed(Enum):
    SLOW = 1
    FAST = 2

class CpuSpeed(Enum):
    SLOW = 1
    FAST = 2

class Node:
    ttx = 1.0
    simulator:Simulator = None
    def __init__(self, id):
        self.id = id
        self.connections = []
        # self.blocks = []
        # self.transactions = []
        self.CPU = CpuSpeed.FAST
        self.link = LinkSpeed.FAST


        self.blockchain = Blockchain()
        self.ledger = None
        self.is_mining = False
        self.received_transactions = set()
        self.pending_transactions = set()
        self.pending_blocks = []


    def __str__(self):
        return str(self.id)
    
    def start(self, ledger):
        self.ledger = ledger
        self.num_nodes = len(ledger)
        self.generate_transaction_event(0.0)
        
    def generate_transaction_event(self, curr_time):
        new_event = Event(curr_time + np.random.exponential(Node.ttx), self, "generate_transaction")
        random.randint(0, self.num_nodes)
        txn_id = str(self.id) + "_" + str(int(curr_time*1e6))
        t = Transaction(
            txn_id=txn_id,
            payer_id=self.id,
            payee_id=random.randint(0, self.num_nodes),
            coins=random.randint(1, 100))
        
        new_event.transaction = t

        self.simulator.add_event(new_event)
        pass

    def send_transaction(self, t, curr_time):
        
        self.received_transactions.add(t.txn_id)
        self.pending_transactions.add(t)

        for conn in self.connections:
            Node.simulator.send_transaction(self, conn, t, curr_time)

        if(not self.is_mining):
            self.generate_block_event()

        # adding next transaction event
        self.generate_transaction_event(curr_time)

    def receive_transaction(self, from_node, t:Transaction, curr_time):
        if t.txn_id in self.received_transactions:
            return
        
        self.received_transactions.add(t.txn_id)
        self.pending_transactions.add(t)

        for conn in self.connections:
            if conn != from_node:
                Node.simulator.send_transaction(self, conn, t, curr_time)
        
        if(not self.is_mining):
            self.generate_block_event()
        pass

    def generate_block_event(self, curr_time):
        t_list = []

        if len(self.pending_transactions) == 0:
            raise Exception("generate_block_event: called with no pending transactions.")

        for t in self.pending_transactions:
            if(self.ledger[t.payer_id] < t.coins):
                continue
            t_list.append(t)
            if(len(t_list)>=999):
                break        
        if len(t_list) == 0:
            self.is_mining = False
            return
        
        # add mining reward to self
        txn_id = str(self.id) + "_" + str(int(curr_time*1e6))
        t_list.append(Transaction(txn_id=txn_id, payer_id=None, payee_id=self.id, coins=50))

        blk_id = str(self.id) + "_" + str(int(curr_time*1e6))
        new_block = Block(
            id = blk_id,
            prev_id = self.blockchain.head.id,
            chain_len = self.blockchain.head.chain_len+1,
            transaction_list = t_list)
        
        new_event = Event(curr_time + np.random.exponential(Node.ttx), self, "generate_block")
        new_event.block = new_block
        self.simulator.add_event(new_event)
        self.is_mining = True
        pass
    
    def send_block(self, to_node, b:Block, curr_time):
        # if longest chain hasn't changed
        if(self.blockchain.head == b.prev_id):
            for conn in self.connections:
                if conn != to_node:
                    Node.simulator.send_block(self, conn, b, curr_time)


        # restart mining
        self.is_mining = False
        if len(self.pending_transactions) > 0:
            self.generate_block_event(curr_time)
        pass

    def receive_block(self, from_node, b:Block, curr_time):
        # TODO add validation, handle branching etc
        if(self.blockchain.has_block(b.id)):
            return
        
        if not b.prev_id:
            # discard block due to invalid previous block
            return False
        
        b.arrival_time = curr_time
        if b.prev_id and not self.blockchain.has_block(b.prev_id):
            self.pending_blocks.append(b)
            return

        head = self.blockchain.head
        # previous block is the longest chain
        if self.blockchain.get_block(b.prev_id) == head:
            if b.chain_len != head.chain_len + 1:
                # discard block due to invalid chain length
                return False
            ledger_copy = self.ledger.copy()
            if b.transaction_list:
                for t in b.transaction_list:
                    if t.payer_id:
                        ledger_copy[t.payer_id] -= t.coins
                    else:
                        if t.coins != 50:
                            # discard block to bad mining reward
                            return False
                    ledger_copy[t.payee_id] += t.coins
            for k, v in ledger_copy.items():
                if v < 0:
                    # discard block due to negative balance transactions
                    return False
            # add block to longest chain in blockchain
            
            self.blockchain.add_block(b)
            self.ledger = ledger_copy
            # update pending transactions
            self.pending_transactions = self.pending_transactions - set(b.transaction_list)
            # update received transactions
            self.received_transactions = self.received_transactions + set(b.transaction_list)


        else:
            pass


            for conn in self.connections:
                if conn != from_node:
                    Node.simulator.send_block(self, conn, b, curr_time)
        
        # if longest chain has changed restart mining
        if head != self.blockchain.head:
            self.is_mining = False
            if len(self.pending_transactions) > 0:
                self.generate_block_event(curr_time)
        pass
