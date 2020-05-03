#!/usr/bin/env python3

import logging

import docker_plugin_api.Plugin
import flask

app = flask.Flask('pyIPAM')
app.logger.setLevel(logging.DEBUG)

app.register_blueprint(docker_plugin_api.Plugin.app)

import lib.IpamDriver
docker_plugin_api.Plugin.functions.append('IpamDriver')
app.register_blueprint(lib.IpamDriver.app)

if __name__ == '__main__':
    app.run(debug=True)
