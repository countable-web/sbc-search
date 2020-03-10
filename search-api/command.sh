#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME
ldconfig
#flask run --host 0.0.0.0
gunicorn -b 0.0.0.0:5000 wsgi
