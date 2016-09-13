#!/bin/sh
export PYTHONPATH=$PYTHONPATH:$(dirname $(readlink -f $0))
python main.py
