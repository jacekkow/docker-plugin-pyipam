FROM alpine

RUN apk add python3 py3-pip
RUN mkdir -p /run/docker/plugins /usr/src/app \
	&& chown -R nobody:nobody /run/docker/plugins /usr/src/app
USER nobody
ENV HOME=/usr/src/app
WORKDIR /usr/src/app

COPY --chown=nobody:nobody requirements.txt .
RUN pip3 install --user --no-cache-dir -r requirements.txt

COPY --chown=nobody:nobody . .

CMD [ "./run.py" ]
