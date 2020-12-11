#!/bin/bash
trap "exit" SIGINT
while true
do 
python3 test_bot.py
done
