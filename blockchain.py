import os

class Transaction:
    def __init__(self, txn_id, payer_id, payee_id, coins):
        self.txn_id = txn_id
        self.payer_id = payer_id
        self.payee_id = payee_id
        self.coins = coins
    
    def __str__(self):
        return "Transaction: " + str(self.txn_id) + " from " + str(self.payer_id) + " to " + str(self.payee_id) + " of " + str(self.coins) + " coins"

class Block:
    def __init__(self, id, prev_id, chain_len, transaction_list):
        self.id = id
        self.prev_id = prev_id
        self.chain_len = chain_len
        self.transaction_list = transaction_list

        self.arrival_time = None
    
    def __str__(self):
        string = "Block_id "+ str(self.id) + "\n"
        string += "\tprev_id "+ str(self.prev_id) + "\n"
        string += "\tchain_len "+ str(self.chain_len) + "\n"
        string += "\tarrival_time "+ str(self.arrival_time) + "\n"
        string += "\ttransactions\n"
        for txn in self.transaction_list:
            string += "\t" + str(txn) + "\n"
        return string

class Blockchain:
    def __init__(self):
        self.id_blocks = {}
        self.head = Block("_0", -1, 1, [])
        self.add_block(self.head)

    def add_block(self, block):
        self.id_blocks[block.id] = block
        if not self.head or block.chain_len > self.head.chain_len:
            self.head = block
        
    def has_block(self, block_id):
        return block_id in self.id_blocks
    
    def get_block(self, block_id):
        return self.id_blocks[block_id]
    
    def log(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as file:
            for block in self.id_blocks.values():
                file.write(str(block))
                file.write("\n")

    def log_longest_chain(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        block = self.head
        blist = []
        while block.prev_id != -1:
            blist.append(block)
            block = self.get_block(block.prev_id)

        with open(filename, "w") as file:
            for block in blist[::-1]:
                file.write(str(block))
                file.write("\n")
                
    def __str__(self):
        block = self.head
        s = ""
        while block:
            s += str(block.data) + " -> "
            block = block.next
        return s