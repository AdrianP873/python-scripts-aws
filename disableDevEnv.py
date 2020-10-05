# Script to turn off all instances in the dev environment on Friday at 6pm and automatically turn back on Monday 6am. Integrate with slack or discord to send automatic notification of actions.
# This script will save costs in dev environments
# @name             Development ASG shutdown
# @author           Adrian Plummer
# @description      This script identifies the EC2 instances attached to the AutoScaling Groups used in development. Instances are shut down and detached from the ASG. Sends notification to slack channel. Use this script to save costs in development accounts.
# @instructions     Scheduled CloudWatch event to be trigger this script as a Lambda function every Friday evening at 6pm.
import boto3
import datetime
import logging

# Instantiate a logger and set minimum level of logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logging.info('Automated end of week cleanup. Shutting down development resources.')

asgClient = boto3.client('autoscaling')
ec2Client = boto3.client('ec2')

# Set ASG's to be managed here:
devAsg = ['eks-test-asg', 'eksctl-prod-nodegroup-ng-581eefce-NodeGroup-GL022APYTYEF']

# Retrieve ASG name and its managed instance id from response metadata, tag instances and put into a dictionary
response = asgClient.describe_auto_scaling_groups(
    AutoScalingGroupNames=[
        devAsg[0],
        devAsg[1]
    ]
)

instanceDict = {}
# Could also retieve InstanceId like this. Perhaps use this method in startup script to showcase skills
'''
i = 0
while i < len(devAsg):
    x = response['AutoScalingGroups'][i]['Instances'][0]['InstanceId']
    print(x)
    i += 1
''' 

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
                    'Key': 'dev',
                    'Value': 'instance-shutdown'
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
    logging.info('Shutting down instance ' + instanceDict[asg] )

# Update ASG desired capacity to 0
for asg in devAsg:
    response = asgClient.update_auto_scaling_group(
        AutoScalingGroupName=asg,
        MinSize=0,
        MaxSize=0,
        DesiredCapacity=0
    )
    logging.info('Setting desired capacity = 0 for AutoScaling Group ' + asg)

   
    # Get instances they are running
    # Turn off instances
    # Set ASG DesiredCount = 0, min=0
    # Need to link Shutdown script to startup script so it knows which instances it needs to start
        # 1. could tag the instances with a unique tag upon shutdown, and query for that in the startup script
        # 2. could implement both scripts into one and trigger code depending on the time. CW would trigger function at both times, and the code would select what code to run based on what is fed to the function
        # 3. Add instance id to dynamodb and query it in other script - less frugal, adds complexity as we add another AWS service, requires greater permission requirements
    # Start ASG Instances, re-attach to ASG, update desired count
    # Send slack notification of these activities