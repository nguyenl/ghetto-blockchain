from flask import Flask
from flask import render_template, request
import click
import requests
import json
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
    ledger_filename = "{}.json".format(name)
    global ledger
    global peername
    global peers
    peername = name
    ledger = Ledger(ledger_filename)
    peers = [peer_address]
    app.run(host='0.0.0.0', port=port, debug=True)


@app.route("/")
def index():
    '''
    Displays the state of the key/value ledger.
    '''
    return render_template('index.html', ledger=ledger.values, name=peername)


@app.route("/ledger.json")
def ledger_json():
    '''
    Returns the ledger as a json document.
    '''
    return json.dumps(ledger.values)


@app.route("/blockchain")
def blockchain():
    '''
    Display the entire block chain as an html file.
    '''
    template = render_template('blockchain.html', blockchain=ledger.blockchain, name=peername)
    return template


@app.route("/invoke", methods=['POST'])
def invoke():
    '''
    Invokes the chaincode to modify the ledger.
    Creates a new block in the process, and adds that block if there
    is a peer.
    '''
    key = request.form['key']
    input_value = request.form['input']
    block = ledger.update(key, input_value)
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
    json_block = json.loads(request.get_data())
    try:
        ledger.add_dict_block(json_block)
        return str(ledger.current_block)
    except Exception as e:
        return str(e)


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
