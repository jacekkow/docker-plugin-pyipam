#!/bin/bash

if [ -d venv ]; then
  . ./venv/bin/activate
fi

python -m unittest discover -v -s test -t . -p '*.py'
