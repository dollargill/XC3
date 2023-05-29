import unittest
import boto3
from moto import mock_events
from config import (
    cloudwatch_list_linked_account,
    cloudwatch_list_linked_account_description,
    cloudwatch_list_linked_account_cron,
    cloudwatch_most_expensive_services,
    cloudwatch_most_expensive_services_description,
    cloudwatch_most_expensive_services_cron,
    cloudwatch_project_spend_cost,
    cloudwatch_project_spend_cost_description,
    cloudwatch_project_spend_cost_cron,
    cloudwatch_resource_list,
    cloudwatch_resource_list_description,
    cloudwatch_resource_list_cron,
    region,
)

events_client = boto3.client("events", region_name=region)


class CloudWatchEventMockTests(unittest.TestCase):
    @mock_events
    def test_create_cloudwatch_event_list_linked_account(self):
        # Create a CloudWatch Event rule
        rule_name = cloudwatch_list_linked_account
        rule_description = cloudwatch_list_linked_account_description
        rule_schedule_expression = cloudwatch_list_linked_account_cron
        response = events_client.put_rule(
            Name=rule_name,
            ScheduleExpression=rule_schedule_expression,
            State="ENABLED",
            Description=rule_description,
        )

        # Verify the rule was created
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

        # Describe the CloudWatch Event rule
        response = events_client.describe_rule(Name=rule_name)

        # Verify the rule attributes
        self.assertEqual(response["Name"], rule_name)
        self.assertEqual(response["State"], "ENABLED")
        self.assertEqual(response["Description"], rule_description)
        self.assertEqual(response["ScheduleExpression"], rule_schedule_expression)

    @mock_events
    def test_create_cloudwatch_event_most_expensive_services(self):
        # Create a CloudWatch Event rule
        rule_name = cloudwatch_most_expensive_services
        rule_description = cloudwatch_most_expensive_services_description
        rule_schedule_expression = cloudwatch_most_expensive_services_cron
        response = events_client.put_rule(
            Name=rule_name,
            ScheduleExpression=rule_schedule_expression,
            State="ENABLED",
            Description=rule_description,
        )

        # Verify the rule was created
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

        # Describe the CloudWatch Event rule
        response = events_client.describe_rule(Name=rule_name)

        # Verify the rule attributes
        self.assertEqual(response["Name"], rule_name)
        self.assertEqual(response["State"], "ENABLED")
        self.assertEqual(response["Description"], rule_description)
        self.assertEqual(response["ScheduleExpression"], rule_schedule_expression)

    @mock_events
    def test_create_cloudwatch_event_project_spend_cost(self):
        # Create a CloudWatch Event rule
        rule_name = cloudwatch_project_spend_cost
        rule_description = cloudwatch_project_spend_cost_description
        rule_schedule_expression = cloudwatch_project_spend_cost_cron
        response = events_client.put_rule(
            Name=rule_name,
            ScheduleExpression=rule_schedule_expression,
            State="ENABLED",
            Description=rule_description,
        )

        # Verify the rule was created
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

        # Describe the CloudWatch Event rule
        response = events_client.describe_rule(Name=rule_name)

        # Verify the rule attributes
        self.assertEqual(response["Name"], rule_name)
        self.assertEqual(response["State"], "ENABLED")
        self.assertEqual(response["Description"], rule_description)
        self.assertEqual(response["ScheduleExpression"], rule_schedule_expression)

    @mock_events
    def test_create_cloudwatch_event_resource_list(self):
        # Create a CloudWatch Event rule
        rule_name = cloudwatch_resource_list
        rule_description = cloudwatch_resource_list_description
        rule_schedule_expression = cloudwatch_resource_list_cron
        response = events_client.put_rule(
            Name=rule_name,
            ScheduleExpression=rule_schedule_expression,
            State="ENABLED",
            Description=rule_description,
        )

        # Verify the rule was created
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

        # Describe the CloudWatch Event rule
        response = events_client.describe_rule(Name=rule_name)

        # Verify the rule attributes
        self.assertEqual(response["Name"], rule_name)
        self.assertEqual(response["State"], "ENABLED")
        self.assertEqual(response["Description"], rule_description)
        self.assertEqual(response["ScheduleExpression"], rule_schedule_expression)


if __name__ == "__main__":
    unittest.main()
