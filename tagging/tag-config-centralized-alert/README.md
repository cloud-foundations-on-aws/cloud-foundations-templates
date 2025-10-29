# Centralized Tag Config Rule Alerting System

## Overview
Two-part CloudFormation solution for centralized tag compliance alerting across AWS Organization.

## Templates

### 1. central-event-bus.yaml (central account)
Creates shared infrastructure in central account:
- Custom EventBridge event bus (tag-config-alerts-bus)
- SNS topic for tag compliance notifications
- Cross-account event bus policy

**Parameters:**
- `NotificationEmail`: Email for alerts

### 2. required-tags-stackset.yaml
Deploy via StackSet to member accounts:
- Required tags Config rule
- EventBridge rule to forward tag compliance events

**Parameters:**
- `CentralEventBusArn`: Tag event bus ARN from central template output
- `RequiredTags`: Comma-delimited list of required tag keys

## Deployment
1. Deploy central-event-bus.yaml in central account
2. Deploy required-tags-stackset.yaml via StackSet to member accounts
3. Use EventBusArn output from step 1 as parameter in step 2