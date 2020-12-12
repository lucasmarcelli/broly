#!/bin/bash

rm -rf dist/ build/ aws_goku.egg-info/
sleep 1
python3 setup.py sdist bdist_wheel
sleep 1
# twine upload dist/*