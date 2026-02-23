#!/bin/bash

processes_running=$(ps aux | grep $USER)
echo "These are the processes running: $processes_running"
