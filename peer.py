from flask import Flask
from flask import render_template
import click
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
    return render_template('index.html', ledger=ledger.values, name=peername)


@app.route("/blockchain")
def blockchain():
    template = render_template('blockchain.html', blockchain=ledger.blockchain, name=peername)
    return template


if __name__ == '__main__':
    start_peer()
