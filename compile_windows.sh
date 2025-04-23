#!/bin/bash

wine python -m PyInstaller -w --onefile --optimize 2 --icon=./PhotoSelect.png ./main.py --name=PhotoSelect