import boto3
from moto import mock_ec2, settings
import pytest
from botocore.exceptions import ClientError
import re
from config import ec2_ami, region, ec2_az


@mock_ec2
def test_instance_launch_and_terminate():
    client = boto3.client("ec2", region_name=region)

    with pytest.raises(ClientError) as ex:
        client.run_instances(ImageId=ec2_ami, MinCount=1, MaxCount=1, DryRun=True)
    ex.value.response["ResponseMetadata"]["HTTPStatusCode"] == 412
    ex.value.response["Error"]["Code"] == "DryRunOperation"
    ex.value.response["Error"][
        "Message"
    ] == "An error occurred (DryRunOperation) when calling the RunInstances operation: Request would have succeeded, but DryRun flag is set"

    reservation = client.run_instances(ImageId=ec2_ami, MinCount=1, MaxCount=1)
    len(reservation["Instances"]) == 1
    instance = reservation["Instances"][0]
    instance["State"] == {"Code": 0, "Name": "pending"}
    instance_id = instance["InstanceId"]

    reservations = client.describe_instances(InstanceIds=[instance_id])["Reservations"]
    len(reservations) == 1
    reservations[0]["ReservationId"] == reservation["ReservationId"]
    instances = reservations[0]["Instances"]
    len(instances) == 1
    instance = instances[0]
    instance["InstanceId"] == instance_id
    instance["State"] == {"Code": 16, "Name": "running"}
    if settings.TEST_SERVER_MODE:
        # Exact value can't be determined in ServerMode
        instance.should.have.key("LaunchTime")
    else:
        launch_time = instance["LaunchTime"].strftime("%Y-%m-%dT%H:%M:%S.000Z")
        launch_time == "2014-01-01T05:00:00.000Z"
    instance["VpcId"] != None
    instance["Placement"]["AvailabilityZone"] == ec2_az

    root_device_name = instance["RootDeviceName"]
    mapping = instance["BlockDeviceMappings"][0]
    mapping["DeviceName"] == root_device_name
    mapping["Ebs"]["Status"] == "in-use"
    volume_id = mapping["Ebs"]["VolumeId"]
    # volume_id.match(r"vol-\w+")
    re.match(r"vol-\w+", volume_id)

    volume = client.describe_volumes(VolumeIds=[volume_id])["Volumes"][0]
    volume["Attachments"][0]["InstanceId"] == instance_id
    volume["State"] == "in-use"

    with pytest.raises(ClientError) as ex:
        client.terminate_instances(InstanceIds=[instance_id], DryRun=True)
    ex.value.response["ResponseMetadata"]["HTTPStatusCode"] == 412
    ex.value.response["Error"]["Code"] == "DryRunOperation"
    ex.value.response["Error"][
        "Message"
    ] == "An error occurred (DryRunOperation) when calling the TerminateInstances operation: Request would have succeeded, but DryRun flag is set"

    response = client.terminate_instances(InstanceIds=[instance_id])
    len(response["TerminatingInstances"]) == 1
    instance = response["TerminatingInstances"][0]
    instance["InstanceId"] == instance_id
    instance["PreviousState"] == {"Code": 16, "Name": "running"}
    instance["CurrentState"] == {"Code": 32, "Name": "shutting-down"}

    reservations = client.describe_instances(InstanceIds=[instance_id])["Reservations"]
    instance = reservations[0]["Instances"][0]
    instance["State"] == {"Code": 48, "Name": "terminated"}
