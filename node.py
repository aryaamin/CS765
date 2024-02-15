from enum import Enum
from queue import PriorityQueue
import numpy as np
import argparse
import random
from simulator import EventType, Event,Simulator
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
        self.pending_block_events = []

        self.block_idx = 0
        self.trxn_idx = 0


        # open file to log events
        self.log = open("log_"+str(self.id)+".txt", "w")

    def log_event(self, string):
        self.log.write(string + "\n")

    def print_blockchain(self):
        self.blockchain.log("blockchain_"+str(self.id)+".txt")

    def __str__(self):
        return str(self.id)
    
    def start(self, ledger):
        self.ledger = ledger
        self.num_nodes = len(ledger)
        
    def find_closest_parent(self, new_block):
        head1 = self.blockchain.head
        while head1.chain_len != self.blockchain.get_block(new_block.prev_id).chain_len:
            head1 = self.blockchain.get_block(head1.prev_id)

        head2 = self.blockchain.get_block(new_block.prev_id)
        
        while head1.id != head2.id:
            head1 = self.blockchain.get_block(head1.prev_id)
            head2 = self.blockchain.get_block(head2.prev_id)
        return head1
        
    def get_new_ledger_and_pending_transaction(self, closest_parent, new_block):
        head = self.blockchain.head
        ledger_copy = self.ledger.copy()
        pending_transactions_copy = self.pending_transactions.copy()
    
        while head.id != closest_parent.id:
            for t in head.transaction_list:
                if t.payer_id:
                    ledger_copy[t.payer_id] += t.coins
                    ledger_copy[t.payee_id] -= t.coins
                    pending_transactions_copy.add(t)
                else:
                    ledger_copy[t.payee_id] -= t.coins
            head = self.blockchain.get_block(head.prev_id)
            
        head = self.blockchain.get_block(new_block.prev_id)
        
        while head.id != closest_parent.id:
            for t in head.transaction_list:
                if t.payer_id:
                    ledger_copy[t.payer_id] += t.coins
                    ledger_copy[t.payee_id] -= t.coins
                    pending_transactions_copy.remove(t)
                else:
                    ledger_copy[t.payee_id] += 50            
            head = self.blockchain.get_block(head.prev_id)
            
        return ledger_copy, pending_transactions_copy
        
        
    def generate_transaction_event(self, curr_time):
        if self.ledger[self.id] == 0:
            return
        new_event = Event(curr_time + np.random.exponential(Node.ttx), self, EventType.SEND_TRANSACTION)
        random.randint(0, self.num_nodes)
        txn_id = str(self.id) + "_" + str(self.trxn_idx)
        self.trxn_idx += 1
        num_coins = random.randint(1, self.ledger[self.id])
        t = Transaction(
            txn_id=txn_id,
            payer_id=self.id,
            payee_id=random.randint(0, self.num_nodes-1),
            coins=num_coins)
        
        new_event.transaction = t

        Node.simulator.add_event(new_event)
        pass

    def send_transaction(self, event, curr_time):
        t=event.transaction
        if not t:
            raise Exception("send_transaction: called without a transaction.")

        self.log_event("Sending transaction: " + str(t.txn_id) + " to " + str(t.payee_id) + " of " + str(t.coins) + " coins")

        self.received_transactions.add(t.txn_id)
        self.pending_transactions.add(t)

        for conn in self.connections:
            delay = Node.simulator.network.get_delay(self, conn, 1)
            new_event = Event(curr_time+delay, conn, EventType.RECEIVE_TRANSACTION)
            new_event.transaction = t
            new_event.from_node = self
            Node.simulator.add_event(new_event)

        if(not self.is_mining):
            self.generate_block_event(curr_time)

        # adding next transaction event
        self.generate_transaction_event(curr_time)

    def receive_transaction(self, event, curr_time):
        t=event.transaction
        if not t:
            raise Exception("receive_transaction: called without a transaction.")
        from_node = event.from_node
        if not from_node:
            raise Exception("receive_transaction: called without a from_node.")
        
        if t in self.received_transactions:
            return
        
        self.log_event("Received transaction: " + str(t.txn_id) + " from " + str(t.payer_id) + " of " + str(t.coins) + " coins")

        self.received_transactions.add(t)
        self.pending_transactions.add(t)

        for conn in self.connections:
            if conn != from_node:
                delay = Node.simulator.network.get_delay(self, conn, 1)
                new_event = Event(curr_time+delay, conn, EventType.RECEIVE_TRANSACTION)
                new_event.transaction = t
                new_event.from_node = self
                Node.simulator.add_event(new_event)
        
        if(not self.is_mining):
            self.generate_block_event(curr_time)
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

        blk_id = str(self.id) + "_" + str(self.block_idx)
        self.block_idx += 1
        new_block = Block(
            id = blk_id,
            prev_id = self.blockchain.head.id,
            chain_len = self.blockchain.head.chain_len+1,
            transaction_list = t_list)
        
        new_event = Event(curr_time + np.random.exponential(Node.ttx), self, EventType.SEND_BLOCK)
        new_event.block = new_block
        self.simulator.add_event(new_event)
        self.is_mining = True
        pass
    
    def send_block(self, event, curr_time):
        b = event.block
        if not b:
            raise Exception("send_block: called without a block.")
        
        
        # if longest chain has changed this block wudnt be generated
        if(self.blockchain.head.id != b.prev_id):
            return

        b.arrival_time = curr_time
        self.log_event("Sending block: " + str(b))

        if not self.add_block_to_current_head(b):
            print(b)
            raise Exception("send_block: block could not be added to current head.")
        
        for conn in self.connections:
            delay = Node.simulator.network.get_delay(self, conn, 1+len(b.transaction_list))
            new_event = Event(curr_time+delay, conn, EventType.RECEIVE_BLOCK)
            new_event.block = Block(b.id, b.prev_id, b.chain_len, b.transaction_list.copy())
            new_event.from_node = self
            Node.simulator.add_event(new_event)

        # restart mining if pending transactions are still there
        if len(self.pending_transactions) > 0:
            self.is_mining = False
            self.generate_block_event(curr_time)
            

    def validate_block(self, b:Block, ledger_copy):
        if b.transaction_list:
            for t in b.transaction_list:
                if t.payer_id is not None:
                    ledger_copy[t.payer_id] -= t.coins
                    ledger_copy[t.payee_id] += t.coins
                else:
                    if t.coins != 50:
                        # discard block due to bad mining reward
                        return False
                ledger_copy[t.payee_id] += t.coins

        for k, v in ledger_copy.items():
            if v < 0:
                # discard block due to negative balance transactions
                return False
        return True
    
    # def add_block(self, b:Block, ledger_copy, pending_transactions):

    def add_block_to_current_head(self, b:Block):
        ledger_copy = self.ledger.copy()
        if not self.validate_block(b, ledger_copy):
            print("Block validation failed", ledger_copy)
            return False
        
        self.ledger = ledger_copy
        # add block to longest chain in blockchain
        self.blockchain.add_block(b)
        self.pending_transactions = self.pending_transactions.difference(set(b.transaction_list))
        self.received_transactions = self.received_transactions.union(set(b.transaction_list))
        return True

    def add_block_to_other_chain(self, b:Block):
        closest_parent = self.find_closest_parent(b)
        ledger_copy, pending_transactions_copy = self.get_new_ledger_and_pending_transaction(closest_parent, b)

        if not self.validate_block(b, ledger_copy):
            return False

        # if head has changed to new block
        if self.blockchain.head.chain_len < b.chain_len:
            self.ledger = ledger_copy
            self.pending_transactions = pending_transactions_copy
            self.pending_transactions = self.pending_transactions.difference(set(b.transaction_list))

        # add block to longest chain in blockchain
        self.blockchain.add_block(b)
        self.received_transactions = self.received_transactions.union(set(b.transaction_list))
        return True

    def receive_block(self, event, curr_time):
        b=event.block
        if not b:
            raise Exception("receive_block: called without a block.")
        from_node = event.from_node
        if not from_node:
            raise Exception("receive_block: called without a from_node.")
        
        # block already received
        if(self.blockchain.has_block(b.id)):
            return
        
        if not b.prev_id:
            # discard block due to invalid previous block
            return False
        
        if b not in self.pending_block_events:
            b.arrival_time = curr_time
        
        self.log_event("Received block from " + str(from_node.id) + " : " + str(b))

        if b.prev_id and not self.blockchain.has_block(b.prev_id):
            # previous block hasnt been received yet
            self.pending_block_events.append(event)
            return

        if b.chain_len != self.blockchain.get_block(b.prev_id).chain_len + 1:
            # discard block due to invalid chain length
            return False
        
        head = self.blockchain.head
        # previous block is the longest chain
        if self.blockchain.get_block(b.prev_id) == head:
            if not self.add_block_to_current_head(b):
                return False
        else:
            if not self.add_block_to_other_chain(b):
                return False
        
        for conn in self.connections:
            if conn != from_node:
                delay = Node.simulator.network.get_delay(self, conn, 1+len(b.transaction_list))
                new_event = Event(curr_time+delay, conn, EventType.RECEIVE_BLOCK)
                new_event.block = Block(b.id, b.prev_id, b.chain_len, b.transaction_list.copy())
                new_event.from_node = self
                Node.simulator.add_event(new_event)

        # if longest chain has changed restart mining
        if head != self.blockchain.head:
            self.is_mining = False
            if len(self.pending_transactions) > 0:
                self.generate_block_event(curr_time)
        
        # process pending blocks
        if b not in self.pending_block_events:
            for pbe in self.pending_block_events:
                if self.blockchain.has_block(pbe.block.prev_id):
                    self.receive_block(pbe, curr_time)
        else:
            self.pending_block_events.remove(b)
