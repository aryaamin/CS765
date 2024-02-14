class Transaction:
    def __init__(self, txn_id, payer_id, payee_id, coins):
        self.txn_id = txn_id
        self.payer_id = payer_id
        self.receiver_id = payee_id
        self.coins = coins

class Block:
    def __init__(self, id, prev_id, chain_len, transaction_list):
        self.id = id
        self.prev_id = prev_id
        self.chain_len = chain_len
        self.transaction_list = transaction_list

        self.arrival_time = None

class Blockchain:
    def __init__(self):
        # TODO add genesis block
        self.id_blocks = {}
        self.head = None

    def add_block(self, block):
        # TODO handle branching
        block.prev = self.head
        self.head = block
        

    def has_block(self, block_id):
        return block_id in self.id_blocks
    
    def __str__(self):
        block = self.head
        s = ""
        while block:
            s += str(block.data) + " -> "
            block = block.next
        return s