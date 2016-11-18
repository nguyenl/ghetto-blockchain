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
    peername = name
    ledger = Ledger(ledger_filename)
    app.run(host='0.0.0.0', port=port, debug=True)


@app.route("/")
def index():
    '''
    Displays the state of the key/value ledger.
    '''
    return render_template('index.html', ledger=ledger.values, name=peername)


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
    ledger.update(key, input_value)
    return str(ledger.current_block)


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


if __name__ == '__main__':
    start_peer()
