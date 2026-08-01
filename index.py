import boto3 # Boto3 is the AWS SDK for Python, allowing interaction with AWS services.
import datetime # The datetime module is used to handle date and time operations, such as getting the current date.
import os # The os module allows interaction with the operating system, such as reading environment variables.

def lambda_handler(event, context):
    # Step 1: Read threshold value from environment variable (default $50 if not set)
    # This is the spend limit you want to monitor.
    threshold = float(os.environ.get("THRESHOLD", "50"))

    # Step 2: Read SNS topic ARN from environment variable
    # This is where alerts will be published.
    sns_topic_arn = os.environ["SNS_TOPIC_ARN"]

    # Step 3: Initialize AWS clients for Cost Explorer and SNS
    # Cost Explorer provides spend data, SNS sends notifications.
    ce = boto3.client("ce")
    sns = boto3.client("sns")

    # Step 4: Define the time period for the cost query
    # Start = first day of current month, End = today.
    today = datetime.date.today()
    start = today.replace(day=1).strftime("%Y-%m-%d")
    end = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    # Step 5: Call Cost Explorer API to get month-to-date spend
    # Metric used: UnblendedCost (raw spend without discounts).
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"]
    )

    # Step 6: Extract the spend amount from the API response
    amount = float(response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"])

    # Step 7: Log the current spend for debugging/visibility
    print(f"Current spend: ${amount:.2f}")

    # Step 8: Compare spend against threshold
    # If exceeded, publish an alert to SNS.
    if amount > threshold:
        message = f"AWS spend alert: ${amount:.2f} exceeds threshold ${threshold:.2f}"
        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="AWS Spend Alert"
        )
        # Log confirmation that alert was sent
        print("Alert published to SNS.")
    else:
        # Log that spend is within safe limits
        print("Spend is within threshold.")
