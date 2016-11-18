from flask import Flask
from flask import render_template, request, redirect
import click
import client


app = Flask(__name__)


@click.command()
@click.option('--port', default=8080, help='Listening port.')
@click.option('--name', default='NavCanada', help='Flightplanning website name.')
@click.option('--peer-address', default='http://127.0.0.1:8000', help='The URL of the peer to sync with.')
def run(port, name, peer_address):
    global site_name
    global peer
    site_name = name
    peer = peer_address
    app.run(host='0.0.0.0', port=port, debug=True)


@app.context_processor
def inject_site():
    '''
    Inject this into all the templates, so that we can style accordingly.
    '''
    return dict(site=site_name)


@app.route('/')
def index():
    ledger = client.get_ledger(peer)
    return render_template('index.html', ledger=ledger)


@app.route('/file', methods=['POST'])
def file_flightplan():
    acid = request.form.get('ACID')
    client.invoke(peer, acid, 'FILED')
    return redirect("/", code=302)


@app.route('/close', methods=['POST'])
def close():
    acid = request.form.get('ACID')
    state = 'CLOSED'
    client.invoke(peer, acid, state)
    return redirect("/", code=302)


@app.route('/activate', methods=['POST'])
def activate():
    acid = request.form.get('ACID')
    state = 'ACTIVE'
    client.invoke(peer, acid, state)
    return redirect("/", code=302)


if __name__ == '__main__':
    run()
