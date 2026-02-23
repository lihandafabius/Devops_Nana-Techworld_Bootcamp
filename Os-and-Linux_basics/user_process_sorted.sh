#!/bin/bash

echo "Reading user input..."

read -p "Sort by memory (M) or by CPU consumption (C): " sorting_criteria

if [ "$sorting_criteria" = "M" ]
then
    echo "You are sorting by memory"
    ps aux --sort=-%mem | grep "$USER"

elif [ "$sorting_criteria" = "C" ]
then
    echo "You are sorting by CPU consumption"
    ps aux --sort=-%cpu | grep "$USER"

else
    echo "Choose either C or M for sorting the processes"
fi

