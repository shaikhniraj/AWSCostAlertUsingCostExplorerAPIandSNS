Daily AWS Cost Alert Using Cost Explorer API and SNS
Objective: Build an automated alert when AWS spend exceeds a threshold.
Note: The old CloudWatch "Billing" metric is legacy — it only exists in us-east-1 and must be manually enabled. The modern, interview-relevant approach uses the Cost Explorer API (ce:GetCostAndUsage).
Instructions:
SNS Setup: Create a topic and subscribe your email (confirm the subscription email).
Lambda IAM Role: Inline policy with ce:GetCostAndUsage and sns:Publish (scoped to your topic).
Lambda Function (Boto3):
Initialize ce and sns clients.
Query month-to-date UnblendedCost with get_cost_and_usage.
Compare against a threshold (e.g., $50).
If exceeded, publish an SNS alert with the current spend.
Print the retrieved amount for logging.
EventBridge: Schedule daily.
Testing: Trigger manually with a low threshold (e.g., $0.01) to force an alert.
Discussion point: Mention AWS Budgets as the managed alternative and when custom Lambda logic wins (per-service breakdowns, Slack/Teams delivery, anomaly logic).
