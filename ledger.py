import hashlib
import json


HASHER = hashlib.sha256()
BLOCKCHAIN_FILE = 'blockchain.json'


class InvalidBlockChainException(Exception):
    pass


def simple_chaincode(key, input_value):
    '''
    A default simple chaincode function that sets the output value as
    the input value.
    '''
    return input_value


class Ledger(object):
    def __init__(self, blockchain_file=None, chaincode=None):
        self.values = {}
        self.blockchain = []
        self.blockchain_file = blockchain_file
        self.chaincode = simple_chaincode if chaincode is None else chaincode
        if self.blockchain_file is not None:
            self.load_blockchain_file(blockchain_file)

    def load_blockchain_file(self, filename):
        '''
        Loads a saved ledger from the given filename.

        Recreates the ledger state from the blockchain.
        '''
        try:
            f = open(filename, 'r')
            json_blockchain = f.read()
            f.close()

            blockchain = json.loads(json_blockchain)
            self.load_blockchain(blockchain)
        except Exception as e:
            print(str(e))
            print "Unable to load the blockchain file {}. Continuing with empty ledger.".format(filename)
            self.blockchain = []
            self.ledger = {}

    def load_blockchain(self, blockchain):
        '''
        Given an existing blockchain, load and validate it.
        '''
        # Convert the json blocks to Block objects, also validate the
        # chain while iterating.
        for new_block in blockchain:
            # Create the block
            block = Block(self.current_block,
                         new_block['key'],
                         new_block['input'],
                         new_block['output'])

            # Verify block chain is valid.
            if new_block['hash'] != block.hash:
                raise InvalidBlockChainException("Block chain hash not equal. Corrupt blockchain! Invalid block hash: {}".format(new_block['hash']))

            # Append to the block chain
            self.blockchain.append(block)

            # Set the new ledger value
            self.values[block.key] = block.output

        print("Blockchain loaded and validated.")

    def write_blockchain(self, filename):
        '''
        Writes this ledger into the given filename.
        Saves the ledger as a json object.
        '''
        json_ledger = self.blockchain_to_json()
        f = open(filename, 'w')
        f.write(json_ledger)
        f.close()

    def update(self, key, input_value):
        '''
        Runs the key and input_value into the chaincode function, and
        sets the ledger key to the output.

        Also updates the block chain and persists to the file.

        Returns the newly added block.
        '''
        block = self.create_block(key, input_value)
        self.write_block_to_ledger(block)
        return block

    def write_block_to_ledger(self, block):
        '''
        Given a block, write its key/value to the ledger, add to the
        block chain, and persist to disk.
        '''
        self.values[block.key] = block.output
        self.blockchain.append(block)
        if self.blockchain_file is not None:
            self.write_blockchain(self.blockchain_file)

    def create_block(self, key, input_value):
        '''
        Creates a block based on the key, input value, and current block chain.
        '''
        output = self.exec_chaincode(key, input_value)
        block = Block(self.current_block, key, input_value, output)
        return block

    def exec_chaincode(self, key, input_value):
        output = self.chaincode(key, input_value)
        return output

    def add_dict_block(self, new_block):
        '''
        Given a block as a dict add it to the current block chain.

        Asserts that the block is valid.
        '''
        block = self.create_block(new_block['key'], new_block['input'])
        assert block.hash == new_block['hash'], 'Invalid block. Cannot add to block chain.'
        self.write_block_to_ledger(block)

    def blockchain_to_json(self):
        blocks = [block.create_dict() for block in self.blockchain]
        return json.dumps(blocks, indent=4)

    @property
    def current_block(self):
        return self.blockchain[-1] if len(self.blockchain) else None


class Block(object):
    def __init__(self, parent_block, key, input_value, output):
        self.parent_block = parent_block
        self.parent_hash = parent_block.hash if parent_block is not None else '0'
        self.key = key
        self.input = input_value
        self.output = output
        self.hash = self.create_hash(self.parent_hash, input_value, self.output)

    def create_hash(self, parent_hash, input, output):
        hash_func = hashlib.sha256()
        hash_func.update(parent_hash)
        hash_func.update(input)
        hash_func.update(output)
        return hash_func.hexdigest()

    def create_dict(self):
        return {
            "parent_hash": self.parent_hash,
            "hash": self.hash,
            "input": self.input,
            "key": self.key,
            "output": self.output
            }

    def to_json(self):
        return json.dumps(self.create_dict())

    def __repr__(self):
        return str(self.create_dict())


if __name__ == '__main__':
    '''
    You can run this file to write sample values to the ledger and
    have the blockchain persisted as a json file.
    '''
    ledger = Ledger(BLOCKCHAIN_FILE)
    # ledger.update('hello', 'world')
    # ledger.update('hello', 'foo')
    # ledger.update('hello', 'you')
    print ledger.blockchain_to_json()
    print ledger.values
