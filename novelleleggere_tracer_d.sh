#!/bin/sh

if [ -e "${0%/*}/bin/activate" ]; then
    . "${0%/*}/bin/activate"
fi

if [ "$TOKEN" = "" ]; then
    export TOKEN="000000000:AAAAAA-aaaaaaaaaaaaaaaaaa_AAAAAAAAA"
fi
if [ "$CHATID" = "" ]; then
    export CHATID="-1000000000000"
fi
if [ "$DBFILE" = "" ]; then
    export DBFILE="database.json"
fi

while true; do
    # run every minute if there are problems
    while ! python3 novelleleggere_tracer.py -r; do
        sleep 60
    done
    sleep 2700  # 45 minutes
done

