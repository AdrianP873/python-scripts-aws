# @name             Development ASG shutdown
# @author           Adrian Plummer
# @description      This script identifies the EC2 instances attached to the AutoScaling Groups used in development. Instances are shut down and detached from the ASG. Sends notification to slack channel. Use this script to save costs in development accounts.
# @instructions     Scheduled CloudWatch event to be trigger this script as a Lambda function every Friday evening at 6pm.
import boto3
import logging

# Set ASG's to be managed here:
devAsg = ['eks-test-asg', 'eksctl-prod-nodegroup-ng-581eefce-NodeGroup-GL022APYTYEF']

# === DO NOT MODIFY BELOW ===

# Instantiate a logger and set minimum level of logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logging.info('Automated end of week cleanup. Shutting down development resources.')

asgClient = boto3.client('autoscaling')
ec2Client = boto3.client('ec2')

def lambda_handler(event, context):
    # Retrieve ASG name and its managed instance id from response metadata, tag instances and put into a dictionary
    response = asgClient.describe_auto_scaling_groups(
        AutoScalingGroupNames=[
            devAsg[0],
            devAsg[1]
        ]
    )

    instanceDict = {}

    for asg in response['AutoScalingGroups']:
        asgName = asg['AutoScalingGroupName']
        for instance in asg['Instances']:
            instanceId = instance['InstanceId']

            tagInstance = ec2Client.create_tags(
                DryRun=False,
                Resources=[
                    instanceId
                ],
                Tags=[
                    {
                        'Key': 'dev-autoscalinggroup',
                        'Value': asgName
                    }
                ]
            )
            instanceDict[asgName] = instanceId

    print(instanceDict)

    # Detach instances from ASG and stop them 
    for asg in instanceDict:
        response = asgClient.detach_instances(
            InstanceIds=[instanceDict[asg]
        ],
        AutoScalingGroupName=asg,
        ShouldDecrementDesiredCapacity=False
    )

        shutdownInstance = ec2Client.stop_instances(
            InstanceIds=[
                instanceDict[asg]
            ]
        )
        logging.info('Shutting down instance ' + instanceDict[asg] + ' and detaching from autoscaling group ' + asg)

    # Update ASG desired capacity to 0
    for asg in devAsg:
        response = asgClient.update_auto_scaling_group(
            AutoScalingGroupName=asg,
            MinSize=0,
            DesiredCapacity=0
        )
        logging.info('Setting desired capacity = 0 for AutoScaling Group ' + asg)