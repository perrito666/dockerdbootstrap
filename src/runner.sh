#!/bin/sh
export PYTHONPATH=$PYTHONPATH:$(dirname $(readlink -f $0))
python3 main.py
