#!/bin/bash
black src/ tests/
flake8 src/ tests/
mypy src/
