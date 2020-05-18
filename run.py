#!/usr/bin/env python3

import logging
import os

import docker_plugin_api.Plugin
import flask
import waitress

app = flask.Flask('pyIPAM')
app.logger.setLevel(logging.DEBUG)

app.register_blueprint(docker_plugin_api.Plugin.app)

import lib.IpamDriver
docker_plugin_api.Plugin.functions.append('IpamDriver')
app.register_blueprint(lib.IpamDriver.app)

if __name__ == '__main__':
	if os.environ.get('ENVIRONMENT', 'dev') == 'dev':
		app.run(debug=True)
	else:
		waitress.serve(app, unix_socket='/run/docker/plugins/pyipam.sock', threads=1)
