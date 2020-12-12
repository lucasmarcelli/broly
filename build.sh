#!/bin/bash

rm -r dist/ build/
python3 setup.py sdist bdist_wheel
# twine upload dist/*