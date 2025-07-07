#!/bin/bash
# Development environment setup
pip install -r requirements-dev.txt
pip install -e ".[dev]"
pre-commit install
