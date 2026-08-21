# AWS Cost Alert Using Cost Explorer API and SNS

A Python AWS Lambda function that checks the current month-to-date AWS spend using the Cost Explorer API and sends an email alert through Amazon SNS when the spend exceeds a configured threshold.

## Overview

This project uses the modern AWS Cost Explorer API instead of the legacy CloudWatch billing metric. It queries the current month's spend and compares it against a custom threshold. If the spend is greater than the threshold, the function publishes an alert message to an SNS topic.

This approach is useful for:
- Monthly cost monitoring and threshold-based alerts
- Basic cost governance in AWS accounts
- Alerting via email without creating a dedicated billing dashboard
- Extending logic for Slack, Teams, or custom dashboards

## Architecture

The solution consists of:
- AWS Lambda function written in Python
- AWS Cost Explorer API for spending data
- Amazon SNS topic for notifications
- EventBridge (CloudWatch Events) for scheduled execution

## Project Flow

1. Lambda reads the threshold from the environment variable `THRESHOLD`.
2. Lambda reads the SNS topic ARN from the environment variable `SNS_TOPIC_ARN`.
3. Lambda gets the first day of the current month and the current date.
4. It calls `ce.get_cost_and_usage()` with the metric `UnblendedCost`.
5. It compares the value with the threshold.
6. If spend exceeds the threshold, it publishes an SNS message.

## Code Behavior

The Lambda function performs the following steps:

- Creates Boto3 clients for:
  - Cost Explorer (`ce`)
  - SNS (`sns`)
- Builds a time range from the first day of the current month to tomorrow's date
- Uses:
  - `TimePeriod={"Start": start, "End": end}`
  - `Granularity="MONTHLY"`
  - `Metrics=["UnblendedCost"]`
- Extracts the current spend from the response:
  - `response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]`
- Prints the current spend to CloudWatch logs
- Publishes an SNS alert if `amount > threshold`

## Inputs

The function expects the following environment variables:

| Variable | Required | Description | Example |
| --- | --- | --- | --- |
| `THRESHOLD` | No | Maximum allowed spend in USD before alerting | `50` |
| `SNS_TOPIC_ARN` | Yes | ARN of the SNS topic used for notifications | `arn:aws:sns:us-east-1:123456789012:CostAlertTopic` |

### Default behavior

If `THRESHOLD` is not provided, the code uses:

- `50` as the default threshold

## Output

### Successful run

The function logs output similar to:

```python
Current spend: $12.45
Spend is within threshold.
```

### Alert triggered

When monthly cost exceeds the threshold, the function publishes an SNS message and logs:

```python
Current spend: $75.20
Alert published to SNS.
```

The SNS message body looks like this:

```text
AWS spend alert: $75.20 exceeds threshold $50.00
```

## AWS Setup

### 1. Create an SNS topic

- Open Amazon SNS
- Create a topic
- Subscribe your email address
- Confirm the email subscription

### 2. Create or update the Lambda IAM role

The Lambda execution role should include permissions similar to:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ce:GetCostAndUsage",
        "sns:Publish"
      ],
      "Resource": "*"
    }
  ]
}
```

For better least-privilege design, scope the SNS permission to the specific topic ARN.

### 3. Create the Lambda function

- Runtime: Python 3.x
- Handler: `index.lambda_handler`
- Add environment variables:
  - `THRESHOLD=50`
  - `SNS_TOPIC_ARN=<your-topic-arn>`

### 4. Upload the project code

Deploy the contents of this repository as the Lambda function package.

### 5. Schedule it with EventBridge

Create a daily schedule to trigger the Lambda and monitor AWS spend automatically.

## Testing

To test the alert flow quickly:

1. Set the threshold to a very low value such as `0.01`
2. Trigger the Lambda manually from the AWS console or AWS CLI
3. Confirm the SNS email is received

## Example Command

```bash
aws lambda invoke --function-name <your-function-name> output.json --log-type Tail
```

## Notes

- This solution uses month-to-date spend from the current billing month.
- It uses `UnblendedCost`, which is the raw spend metric without discounts applied.
- The legacy CloudWatch Billing metric is not the preferred modern solution because it is limited and not available in all regions.
- AWS Budgets is a managed alternative for cost threshold alerts, while Lambda provides more customization for business logic, service-level reporting, and integration with tools such as Slack or Microsoft Teams.

## Project Files

- `index.py` — Lambda function logic
- `README.md` — project documentation

## License

This project is intended for learning and demonstration purposes.
