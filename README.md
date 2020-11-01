# novelleleggere tracer

Install dependencies using `pip3 install -r requirements.txt`
(needed only if not using the containerized version)

This script could be executed in the following methods:

1. `python3 novelleleggere_tracer.py` with the right parameters manually

2. setting the environment variable `TOKEN`, `CHATID` and `DBFILE` and running
`python3 novelleleggere_tracer.py` or the daemon script

3. building the image with `docker image build -t
novelleleggere_tracer:1.0 .` and running the container with
`docker container run -d -v .:/srv -e TOKEN=asd123 -e CHATID=123456
-e DBFILE=/srv/database.json --name novelleleggere novelleleggere_tracer:1.0`
You may want to run the container in interactive mode (substituting the
parameters '-d' with `-it` and adding `/bin/sh` at the end of the line)
to manage which novel you want to follow.

inspired by https://github.com/morrolinux/subito-it-searcher
