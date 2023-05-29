import string
import unittest
import boto3
from moto import mock_cognitoidp
from config import cognito, region
import random


class CognitoMockTests(unittest.TestCase):
    @mock_cognitoidp
    def test_create_user_and_verify_attributes(self):
        region_name = region

        # Create a user pool
        user_pool_name = cognito
        user_pool_id = self.create_user_pool(user_pool_name, region_name)

        # Create a user
        username = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
        )
        email = (
            "".join(
                random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
            )
            + "@example.com"
        )
        temporary_password = "".join(
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(10)
        )
        self.create_user(user_pool_id, username, temporary_password, email)

        # Verify user attributes
        email_verified, custom_attribute = self.get_user_attributes(
            user_pool_id, username
        )
        print(self.get_user_attributes(user_pool_id, username))

        # Assert the user attributes
        self.assertTrue(email_verified)
        self.assertEqual(custom_attribute, "CustomValue")

    def create_user_pool(self, user_pool_name, region_name):
        cognito_client = boto3.client("cognito-idp", region_name=region_name)
        user_pool_response = cognito_client.create_user_pool(
            PoolName=user_pool_name,
            Policies={
                "PasswordPolicy": {
                    "MinimumLength": 8,
                    "RequireLowercase": False,
                    "RequireNumbers": False,
                    "RequireSymbols": False,
                    "RequireUppercase": False,
                }
            },
            AutoVerifiedAttributes=["email"],
        )
        return user_pool_response["UserPool"]["Id"]

    def create_user(self, user_pool_id, username, temporary_password, email):
        cognito_client = boto3.client("cognito-idp")
        cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            TemporaryPassword=temporary_password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "custom:attribute", "Value": "CustomValue"},
            ],
        )

    def get_user_attributes(self, user_pool_id, username):
        cognito_client = boto3.client("cognito-idp")
        user_response = cognito_client.admin_get_user(
            UserPoolId=user_pool_id, Username=username
        )
        user_attributes = user_response["UserAttributes"]
        email_verified = False
        custom_attribute = None

        for attribute in user_attributes:
            if attribute["Name"] == "email":
                email_verified = True
            elif attribute["Name"] == "custom:attribute":
                custom_attribute = attribute["Value"]

        return email_verified, custom_attribute


if __name__ == "__main__":
    unittest.main()
