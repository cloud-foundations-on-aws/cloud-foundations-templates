# S3 Bucket for Centralized AWS Config logging

Template creates an S3 Bucket to be deployed in your log archive account for centralized logging of Config. Template will deploy two S3 buckets: one for centralized config logging and another for access logging.

The centralized config logging bucket is configured so that AWS Config can write to it within your Organization. Deploy this bucket to your log archive account.
