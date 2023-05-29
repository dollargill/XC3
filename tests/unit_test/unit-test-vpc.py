import unittest
import boto3
from moto import mock_ec2
from config import region, vpc_cidr, vpc_public_subnet, vpc_private_subnet


class MyVPCTest(unittest.TestCase):
    @mock_ec2
    def test_create_vpc(self):
        ec2_client = boto3.client("ec2", region_name=region)

        # Create a mock VPC
        response = ec2_client.create_vpc(CidrBlock=vpc_cidr)
        vpc_id = response["Vpc"]["VpcId"]

        # Test VPC creation
        self.assertEqual(response["Vpc"]["CidrBlock"], vpc_cidr)

        # Test VPC retrieval
        vpc = ec2_client.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]
        self.assertEqual(vpc["VpcId"], vpc_id)
        self.assertEqual(vpc["CidrBlock"], vpc_cidr)

    @mock_ec2
    def test_vpc_with_igw_and_subnet(self):
        # Create a mock VPC
        ec2_client = boto3.client("ec2", region_name=region)
        response = ec2_client.create_vpc(CidrBlock=vpc_cidr)
        vpc_id = response["Vpc"]["VpcId"]

        # Create a mock internet gateway (IGW)
        response = ec2_client.create_internet_gateway()
        igw_id = response["InternetGateway"]["InternetGatewayId"]

        # Attach the IGW to the VPC
        ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

        # Create a mock subnet
        response = ec2_client.create_subnet(CidrBlock=vpc_cidr, VpcId=vpc_id)

        # Perform your test assertions
        self.assertEqual(response["Subnet"]["CidrBlock"], vpc_cidr)
        self.assertEqual(response["Subnet"]["VpcId"], vpc_id)

    @mock_ec2
    def test_delete_vpc(self):
        ec2_client = boto3.client("ec2", region_name=region)

        # Create a mock VPC
        response = ec2_client.create_vpc(CidrBlock=vpc_cidr)
        vpc_id = response["Vpc"]["VpcId"]

        # Delete the VPC
        response = ec2_client.delete_vpc(VpcId=vpc_id)

        # Test VPC deletion
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)

        # Try to retrieve the deleted VPC
        with self.assertRaises(ec2_client.exceptions.ClientError) as context:
            ec2_client.describe_vpcs(VpcIds=[vpc_id])

        self.assertEqual(
            context.exception.response["Error"]["Code"], "InvalidVpcID.NotFound"
        )

    @mock_ec2
    def test_create_route_table(self):
        # Create a mock VPC
        ec2_client = boto3.client("ec2", region_name=region)
        response = ec2_client.create_vpc(CidrBlock=vpc_cidr)
        vpc_id = response["Vpc"]["VpcId"]
        print(response)

        # Create a mock route table
        response = ec2_client.create_route_table(VpcId=vpc_id)
        route_table_id = response["RouteTable"]["RouteTableId"]

        # Perform your test assertions
        self.assertEqual(response["RouteTable"]["VpcId"], vpc_id)
        self.assertEqual(response["RouteTable"]["Associations"], [])
        self.assertEqual(response["RouteTable"]["RouteTableId"], route_table_id)

    @mock_ec2
    def test_route_table_association(self):
        # Create a mock VPC
        ec2_client = boto3.client("ec2", region_name=region)
        response = ec2_client.create_vpc(CidrBlock=vpc_cidr)
        vpc_id = response["Vpc"]["VpcId"]

        # Create a mock subnet
        response = ec2_client.create_subnet(CidrBlock=vpc_cidr, VpcId=vpc_id)
        subnet_id = response["Subnet"]["SubnetId"]

        # Create a mock route table
        response = ec2_client.create_route_table(VpcId=vpc_id)
        route_table_id = response["RouteTable"]["RouteTableId"]

        # Associate the route table with the subnet
        response = ec2_client.associate_route_table(
            RouteTableId=route_table_id, SubnetId=subnet_id
        )
        print(response)
        # Perform your test assertions
        self.assertEqual(response["AssociationId"], response["AssociationId"])

    @mock_ec2
    def test_create_vpc_public_private_subnets(self):
        # Create a VPC
        ec2_client = boto3.client("ec2", region_name=region)

        response = ec2_client.create_vpc(
            CidrBlock=vpc_cidr, AmazonProvidedIpv6CidrBlock=True
        )
        vpc_id = response["Vpc"]["VpcId"]

        # Create public subnet
        public_subnet_response = ec2_client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=vpc_public_subnet,
        )
        public_subnet_id = public_subnet_response["Subnet"]["SubnetId"]

        # Create private subnet
        private_subnet_response = ec2_client.create_subnet(
            VpcId=vpc_id,
            CidrBlock=vpc_private_subnet,
        )
        private_subnet_id = private_subnet_response["Subnet"]["SubnetId"]

        # Verify VPC and subnets
        vpcs = ec2_client.describe_vpcs(VpcIds=[vpc_id])["Vpcs"]
        self.assertEqual(len(vpcs), 1)
        self.assertEqual(vpcs[0]["VpcId"], vpc_id)

        subnets = ec2_client.describe_subnets(
            SubnetIds=[public_subnet_id, private_subnet_id]
        )["Subnets"]
        self.assertEqual(len(subnets), 2)
        self.assertIn(public_subnet_id, [subnet["SubnetId"] for subnet in subnets])
        self.assertIn(private_subnet_id, [subnet["SubnetId"] for subnet in subnets])

        # Clean up resources
        ec2_client.delete_subnet(SubnetId=public_subnet_id)
        ec2_client.delete_subnet(SubnetId=private_subnet_id)
        ec2_client.delete_vpc(VpcId=vpc_id)


if __name__ == "__main__":
    unittest.main()
