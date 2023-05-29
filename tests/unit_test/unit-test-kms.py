import unittest
import boto3
from moto import mock_kms
from config import region, kms_id


class KMSMockTests(unittest.TestCase):
    @mock_kms
    def test_encrypt_decrypt_data(self):
        kms_client = boto3.client("kms", region_name=region)

        # Create a KMS key
        key_alias = f"alias/{kms_id}"
        response = kms_client.create_key()
        key_id = response["KeyMetadata"]["KeyId"]
        kms_client.create_alias(AliasName=key_alias, TargetKeyId=key_id)

        # Encrypt data
        plaintext = "Hello, World!"
        encryption_response = kms_client.encrypt(
            KeyId=key_alias, Plaintext=plaintext.encode()
        )
        ciphertext = encryption_response["CiphertextBlob"]

        # Decrypt data
        decryption_response = kms_client.decrypt(CiphertextBlob=ciphertext)
        decrypted_plaintext = decryption_response["Plaintext"].decode()

        # Assert the original plaintext matches the decrypted plaintext
        self.assertEqual(plaintext, decrypted_plaintext)


if __name__ == "__main__":
    unittest.main()
