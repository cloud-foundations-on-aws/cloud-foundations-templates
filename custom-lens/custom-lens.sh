#!/bin/bash

echo "installing python packages..."

pip install boto3 requests

echo "installation complete, starting custom lens..."

download_url="https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/custom-lens/app.py"

curl -sS $download_url | python