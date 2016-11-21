gunicorn -w 4 -b 0.0.0.0:8000 'peer:start("NavCanada", "http://127.0.0.1:8001")' &
gunicorn -w 4 -b 0.0.0.0:8001 'peer:start("FAA", "http://127.0.0.1:8000")' &

cd examples/flightplanner

gunicorn -w 4 -b 0.0.0.0:8080 'planner:start("NavCanada", "http://127.0.0.1:8000")' &
gunicorn -w 4 -b 0.0.0.0:8081 'planner:start("FAA", "http://127.0.0.1:8001")' &
