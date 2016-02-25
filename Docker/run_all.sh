#!/bin/bash
#Run DataOperator , DataSink and DataSource

# Kill all
echo "Killing all existing instances and waiting a bit for ports to free up"
pkill python
sleep 3
echo "Done!"

# DataOperator
echo "Starting up DataOperator and waiting a bit for it to finish starting."
cd /~/mydataoperator
nohup python DO/app.py &
sleep 10
echo "Done!"

# DataSource
echo "Starting DataSources and Sinks!"
cd /~/RunningFree
nohup python run.py &

cd /~/MyLocation
nohup python run.py &

cd /~/Sesko
nohup python run.py &

cd /~/SWH-Source
nohup python run.py &


# DataSink
cd /~/PHR
nohup python run.py &

cd /~/SWH-Sink
nohup python run.py &

echo "Done! Waiting 15 sec to let them finish starting up!"
sleep 15

echo "Registering testuser to sinks!"
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"testuser","password":"Hello"}' http://127.0.0.1:20001/api/v0.1/user
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"testuser","password":"Hello"}' http://127.0.0.1:20002/api/v0.1/user
curl -i -X POST -H "Content-Type: application/json" -d '{"username":"testuser","password":"Hello"}' http://127.0.0.1:20003/api/v0.1/user
echo "Done!"
echo "Finished starting up the PoC environment!"
