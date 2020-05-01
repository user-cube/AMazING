#!/bin/bash

echo "Setup venv" &&
	python3 -m venv venv &&
	echo "Entering on venv" &&
	source venv/bin/activate &&
	echo "Install requirements" &&
	pip install -r requirements.txt &&
	echo "Executing wssh" &&
	wssh
