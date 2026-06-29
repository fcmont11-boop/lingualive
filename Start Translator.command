#!/bin/bash
cd ~/translator
python3 server.py &
echo "Starting server..."
until curl -s http://localhost:5001 > /dev/null; do
    sleep 1
done
echo "Server ready! Opening browser..."
open "http://localhost:5001"
wait
