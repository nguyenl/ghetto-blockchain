#!/bin/sh
python peer.py --name NavCanada --port 8000 --peer-address http://127.0.0.1:8001&
python peer.py --name FAA --port 8001 --peer-address http://127.0.0.1:8000&

cd examples/flightplanner

python planner.py --name NavCanada --port 8080 --peer-address http://127.0.0.1:8000&
python planner.py --name FAA --port 8081 --peer-address http://127.0.0.1:8001

