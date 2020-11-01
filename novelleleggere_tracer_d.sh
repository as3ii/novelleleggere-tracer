#!/bin/sh

while true; do
    # run every minute if there are problems
    while ! python3 novelleleggere_tracer.py -r; do
        sleep 60
    done
    sleep 2700  # 45 minutes
done

