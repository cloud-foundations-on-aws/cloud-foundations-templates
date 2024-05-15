#!/bin/bash

mkdir ./pathfinder -p
cd ./pathfinder
echo "installing npm packages..."

for i in \
  '@aws-sdk/client-cloudtrail' \
  '@aws-sdk/client-config-service' \
  '@aws-sdk/client-ec2' \
  '@aws-sdk/client-controltower' \
  '@aws-sdk/client-iam' \
  '@aws-sdk/client-cost-and-usage-report-service' \
  '@aws-sdk/client-cloudformation' \
  '@aws-sdk/client-organizations' \
  '@aws-sdk/client-sso-admin' \
   ; do npm install "$i" --silent; done

echo "installation complete, starting CFAT..."
download_url="https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/cfat/cfat/dist/cfat.js"
curl -sS $download_url | node
