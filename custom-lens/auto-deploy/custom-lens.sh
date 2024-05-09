#!/bin/bash

echo "installing python packages..."

pip install boto3 requests

echo "installation complete, starting custom lens..."

download_url="https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/custom-lens-install-script/custom-lens/auto-deploy/app.py"

curl -sS $download_url | python3