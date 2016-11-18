import hashlib
import json


HASHER = hashlib.sha256()
LEDGER_FILE = 'ledger.json'


def simple_chaincode(key, input_value):
    '''
    A default simple chaincode function that sets the output value as
    the input value.
    '''
    return input_value


class Ledger(object):
    def __init__(self, ledger_file, chaincode=None):
        self.values = {}
        self.blockchain = []
        self.ledger_file = ledger_file
        self.chaincode = simple_chaincode if chaincode is None else chaincode
        if self.ledger_file is not None:
            self.load_ledger(ledger_file)

    def load_ledger(self, filename):
        '''
        Loads a saved ledger from the given filename.

        Recreates the ledger state from the blockchain.
        '''
        try:
            f = open(filename, 'r')
            json_ledger = f.read()
            f.close()

            ledger = json.loads(json_ledger)
        except:
            print "Unable to load the ledger file {}. Continuing with empty ledger.".format(filename)
            ledger = []

        # Convert the json blocks to Block objects, also validate the
        # chain while iterating.
        for new_block in ledger:
            # Create the block
            block = Block(self.current_block,
                         new_block['key'],
                         new_block['input'],
                         new_block['output'])

            # Verify block chain is valid.
            assert new_block['hash'] == block.hash, "Block chain hash not equal. Corrupt ledger! Invalid block hash: {}".format(new_block.hash)

            # Append to the block chain
            self.blockchain.append(block)

            # Set the new ledger value
            self.values[block.key] = block.output

    def write_ledger(self, filename):
        '''
        Writes this ledger into the given filename.
        Saves the ledger as a json object.
        '''
        json_ledger = self.blockchain_to_json()
        f = open(filename, 'w')
        f.write(json_ledger)
        f.close()

    def update_ledger(self, key, input_value):
        '''
        Runs the key and input_value into the chaincode function, and
        sets the ledger key to the output.

        Also updates the block chain and persists to the file.
        '''
        output = self.exec_chaincode(key, input_value)
        block = Block(self.current_block, key, input_value, output)
        self.blockchain.append(block)
        self.values[key] = output
        self.write_ledger(self.ledger_file)

    def exec_chaincode(self, key, input_value):
        output = self.chaincode(key, input_value)
        return output

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
       
    def __repr__(self):
        return str(self.create_dict())


if __name__ == '__main__':
    ledger = Ledger(LEDGER_FILE)
    ledger.update_ledger('hello', 'world')
    ledger.update_ledger('hello', 'foo')
    ledger.update_ledger('hello', 'you')
    print ledger.blockchain_to_json()
    print ledger.values
