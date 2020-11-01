FROM python:3-alpine

RUN mkdir -p /srv && apk --update --upgrade add gcc musl-dev libffi-dev \
    openssl-dev && rm -rf /var/cache/apk

COPY . /srv

RUN pip install --no-cache-dir -r /srv/requirement.txt

CMD [ "/srv/novelleleggere_tracer_d.sh" ]

