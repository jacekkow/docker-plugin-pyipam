FROM alpine

RUN apk add python3 py3-pip
RUN mkdir -p /run/docker/plugins /usr/src/app \
	&& chown -R nobody:nobody /run/docker/plugins /usr/src/app
USER nobody
ENV HOME=/usr/src/app
WORKDIR /usr/src/app

COPY --chown=nobody:nobody requirements.txt .
RUN python -m venv venv && ./venv/bin/pip install --no-cache-dir -r requirements.txt

COPY --chown=nobody:nobody . .

CMD [ "./venv/bin/python", "run.py" ]
