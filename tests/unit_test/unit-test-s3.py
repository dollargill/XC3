import unittest
import boto3
from moto import mock_s3
from config import region, s3_bucket, s3_bucket_tags


class S3MockTests(unittest.TestCase):
    @mock_s3
    def test_create_bucket(self):
        bucket_name = s3_bucket

        s3_client = boto3.client("s3")
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
        print("Bucket created successfully:", bucket_name)

        response = s3_client.list_buckets()
        buckets = response["Buckets"]
        self.assertEqual(len(buckets), 1)
        self.assertEqual(buckets[0]["Name"], bucket_name)

    @mock_s3
    def test_check_bucket_tags(self):
        bucket_name = s3_bucket

        s3_client = boto3.client("s3")
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )

        tags = s3_bucket_tags

        tag_set = [{"Key": key, "Value": value} for key, value in tags.items()]
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={"TagSet": tag_set},
        )
        response = s3_client.get_bucket_tagging(Bucket=bucket_name)
        tags_res = response["TagSet"]
        if tags:
            print("Tags for bucket", bucket_name)
            for tag in tags_res:
                print(tag["Key"], ":", tag["Value"])
        else:
            print("No tags found for bucket:", bucket_name)

        self.assertEqual(len(tags_res), 4)

        for index, tag_key in enumerate(tags.keys()):
            self.assertEqual(tags_res[index]["Key"], tag_key)
            self.assertEqual(tags_res[index]["Value"], tags[tag_key])


if __name__ == "__main__":
    unittest.main()
