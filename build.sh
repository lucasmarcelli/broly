#!/bin/bash

rm -rf dist/ build/ broly.egg-info/ broly/__pycache__
sleep 1
python3 setup.py sdist bdist_wheel
sleep 1
twine upload dist/*