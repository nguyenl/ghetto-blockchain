import requests


def get_ledger(peer_address):
    url = "{}/{}".format(peer_address, 'ledger.json')
    r = requests.get(url)
    return r.json()


def invoke(peer_address, key, input_value):
    url = "{}/{}".format(peer_address, 'invoke')
    payload = {
        'key': key,
        'input': input_value,
        }
    r = requests.post(url, data=payload)
    return r
