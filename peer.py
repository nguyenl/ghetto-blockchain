from flask import Flask
from flask import render_template, request
import click
import requests
import json
import redis
from ledger import Ledger


app = Flask(__name__)



@click.command()
@click.option('--port', default=8000, help='Listening port.')
@click.option('--name', help='Peer name.')
@click.option('--peer-address', help='The URL of the peer to sync with.')
def start_peer(port, name, peer_address):
    '''
    Starts the ghetto-ledger peer service.
    '''
    start(name, peer_address)
    app.run(host='0.0.0.0', port=port, debug=False)


def start(name, peer_address):
    global peername
    global peers
    global redis_connection
    peername = name
    peers = [peer_address]
    redis_connection = redis.StrictRedis(host='localhost', port=6379, db=0)
    return app
    

def get_ledger():
    '''
    Creates a new ledger object based on the blockchain stored in
    redis.
    '''
    blockchain = read_from_redis()
    ledger = Ledger()
    ledger.load_blockchain(blockchain)
    return ledger


@app.route("/")
def index():
    '''
    Displays the state of the key/value ledger.
    '''
    ledger = get_ledger()
    return render_template('index.html',
                           ledger=ledger.values,
                           blockchain=ledger.blockchain,
                           name=peername)


@app.route("/ledger.json")
def ledger_json():
    '''
    Returns the ledger as a json document.
    '''
    ledger = get_ledger()
    return json.dumps(ledger.values)


@app.route("/blockchain")
def blockchain():
    '''
    Display the entire block chain as an html file.
    '''
    ledger = get_ledger()
    template = render_template('blockchain.html', blockchain=ledger.blockchain, name=peername)
    return template


@app.route("/invoke", methods=['POST'])
def invoke():
    '''
    Invokes the chaincode to modify the ledger.
    Creates a new block in the process, and adds that block if there
    is a peer.
    '''
    ledger = get_ledger()    
    key = request.form['key']
    input_value = request.form['input']
    block = ledger.update(key, input_value)
    write_to_redis(ledger)    
    try:
        if peers:
            send_peers('add_block', block.to_json())
    except Exception as e:
        print str(e)

    return str(block)


@app.route("/add_block", methods=['POST'])
def add_block():
    '''
    Adds a block to the ledger from another peer.

    Returns 500 if the block is not valid.
    '''
    ledger = get_ledger()    
    json_block = json.loads(request.get_data())
    try:
        ledger.add_dict_block(json_block)
        write_to_redis(ledger)
        return str(ledger.current_block)
    except Exception as e:
        return str(e)


def read_from_redis():
    '''
    Returns the blockchain from redis.
    '''
    blockchain_json = redis_connection.get('blockchain')
    if blockchain_json is not None:
        return json.loads(blockchain_json)
    else:
        return []


def write_to_redis(ledger):
    '''
    Given a ledger, write its blockchain to redis.
    '''
    blockchain_json = ledger.blockchain_to_json()
    redis_connection.set('blockchain', blockchain_json)
    

def send_peers(endpoint, payload):
    '''
    A helper function to POST an arbitrary payload to other peers on
    the network.
    '''
    responses = []
    for peer in peers:
        try:
            url = "{}/{}".format(peer, endpoint)
            print url
            r = requests.post(url, data=payload)
            responses.append(r)
        except Exception as e:
            print 'Exception: Unable to post to peer {}: {}'.format(str(e))
    return responses


if __name__ == '__main__':
    start_peer()
