#!/bin/bash

mkdir ./cfat -p
cd ./cfat
echo "installing npm packages..."

for i in \
  '@aws-sdk/client-sts' \
  '@aws-sdk/client-cloudtrail' \
  '@aws-sdk/client-config-service' \
  '@aws-sdk/client-ec2' \
  '@aws-sdk/client-controltower' \
  '@aws-sdk/client-iam' \
  '@aws-sdk/client-cost-and-usage-report-service' \
  '@aws-sdk/client-cloudformation' \
  '@aws-sdk/client-organizations' \
  '@aws-sdk/client-sso-admin' \
  '@types/archiver' 'archiver' \
   ; do npm install "$i" --silent; done

echo "installation complete, starting cloud foundation assessment..."
download_url="https://raw.githubusercontent.com/cloud-foundations-on-aws/cloud-foundations-templates/main/cfat/dist/cfat.js"
curl -sS $download_url | node
