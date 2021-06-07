#!/bin/sh

cd "${0%/*}"

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
    while ! timeout -k 200s 180s python3 novelleleggere_tracer.py -r; do
        printf "Timeout, retrying in 60s"
        sleep 60
    done
    sleep 2700  # 45 minutes
done

