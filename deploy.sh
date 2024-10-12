#!/usr/bin/env bash

poetry install
poetry run python compile_blogs.py
neocities push website
