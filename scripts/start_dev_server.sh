#!/bin/bash

echo -e "\033[0;94mSetting up\033[00m"
source ../../venv/bin/activate

echo -e "\033[0;94mStarting server\033[00m"
nohup uvicorn main:app --host 0.0.0.0 --port 5000 --uds="/tmp/development_server.sock" > uvicorn.log 2> uvicorn_error.log &

echo -e "\033[0;32mDevelopment server up and running\033[00m"
