# @name             Development ASG shutdown
# @author           Adrian Plummer
# @description      This script identifies the EC2 instances attached to the AutoScaling Groups used in development. Instances are shut down and detached from the ASG. Use this script to save costs in development accounts.
# @instructions     Scheduled CloudWatch event to be trigger this script as a Lambda function every Friday evening at 6pm.
# @todo             Set ASG's via tags, slack/discord integration
import boto3
import logging

# Set ASG's to be managed here:
devAsg = ['eks-test-asg', 'eksctl-prod-nodegroup-ng-581eefce-NodeGroup-GL022APYTYEF']

# === DO NOT MODIFY BELOW ===

# Instantiate a logger and set minimum level of logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logging.info('Automated start of week bootup. Starting up development resources.')

asgClient = boto3.client('autoscaling')
ec2Client = boto3.client('ec2')

def lambda_handler(event, context):
    # Get the instances with a tag of Key=dev-autoscalinggroup and Value=<asg names>
    # Start instances
    # Attach instances to ASG
    # Remove Tags
    # Notify slack