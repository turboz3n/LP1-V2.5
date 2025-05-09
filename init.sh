#!/bin/bash

set -e

echo "[+] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "[+] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p lp1/data
mkdir -p lp1/tests

echo "[+] LP1 environment is ready. Run with: source venv/bin/activate && python lp1/main.py"