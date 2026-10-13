#!/usr/bin/env bash
set -e

python -m venv --copies /opt/venv
source /opt/venv/bin/activate

python -m pip install --upgrade pip
python -m pip install --no-cache-dir --timeout 120 --resume-retries 10 torch --index-url https://download.pytorch.org/whl/cpu
python -m pip install --no-cache-dir --timeout 120 --resume-retries 10 -r requirements-coolify.txt
