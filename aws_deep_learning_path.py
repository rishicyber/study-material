"""
================================================================================
 █████╗ ██╗    ██╗███████╗    ██████╗ ███████╗███████╗██████╗     
██╔══██╗██║    ██║██╔════╝    ██╔══██╗██╔════╝██╔════╝██╔══██╗    
███████║██║ █╗ ██║███████╗    ██║  ██║█████╗  █████╗  ██████╔╝    
██╔══██║██║███╗██║╚════██║    ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝     
██║  ██║╚███╔███╔╝███████║    ██████╔╝███████╗███████╗██║         
╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝    ╚═════╝ ╚══════╝╚══════╝╚═╝         
                                                                     
     ██╗     ███████╗ █████╗ ██████╗ ███╗   ██╗██╗███╗   ██╗ ██████╗     
     ██║     ██╔════╝██╔══██╗██╔══██╗████╗  ██║██║████╗  ██║██╔════╝     
     ██║     █████╗  ███████║██████╔╝██╔██╗ ██║██║██╔██╗ ██║██║  ███╗    
     ██║     ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║██║██║╚██╗██║██║   ██║    
     ███████╗███████╗██║  ██║██║  ██║██║ ╚████║██║██║ ╚████║╚██████╔╝    
     ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝ ╚═════╝     
                                                                             
                         P A T H
================================================================================

AWS DEEP LEARNING PATH — Advanced Interview Preparation Guide
Author      : AWS Expert Learning System
Python Ver  : 3.10+
Total Lines : ~3000
Purpose     : Comprehensive AWS learning with boto3 code, architecture patterns,
              cross-cutting questions, and senior/staff-level interview prep.

HOW TO USE THIS FILE:
  1. Read the section header comments carefully — they explain "WHY" not just "WHAT"
  2. Run the code snippets in your AWS sandbox account
  3. Answer the INTERVIEW QUESTIONS before looking at the hints
  4. Follow the CROSS QUESTIONS — they connect multiple AWS services together
  5. Study the GOTCHAS — these are the most common senior-interview trip wires

PREREQUISITES:
  pip install boto3 botocore awscli
  aws configure   # Set up your credentials

SECTIONS:
  01 — AWS Fundamentals & Global Infrastructure
  02 — IAM (Identity & Access Management)
  03 — EC2 (Elastic Compute Cloud)
  04 — S3 (Simple Storage Service)
  05 — VPC (Virtual Private Cloud) — Networking Deep Dive
  06 — RDS & Aurora — Managed Databases
  07 — DynamoDB — NoSQL at Scale
  08 — Lambda — Serverless Compute
  09 — SQS, SNS, EventBridge — Messaging & Events
  10 — EKS & ECS — Container Orchestration
  11 — CloudFormation & CDK — Infrastructure as Code
  12 — CloudWatch, X-Ray & Observability
  13 — Security — KMS, Secrets Manager, GuardDuty
  14 — Cost Optimization Patterns
  15 — Advanced Architecture Patterns & System Design

================================================================================
"""

import boto3
import json
import time
import hashlib
import datetime
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config
from typing import Optional, Dict, List, Any


# ================================================================================
# SECTION 01 — AWS FUNDAMENTALS & GLOBAL INFRASTRUCTURE
# ================================================================================
"""
CONCEPT: AWS Global Infrastructure is the physical backbone of all AWS services.
Understanding it is critical because:
  - It affects LATENCY (how close data is to users)
  - It affects AVAILABILITY (how resilient your system is)
  - It affects COMPLIANCE (where data physically lives)
  - It affects COST (data transfer between regions costs money)

KEY TERMS:
  - Region       : A geographic area (e.g., us-east-1, eu-west-1). Fully independent.
  - AZ           : Availability Zone. 1+ data centers within a region. Connected via
                   low-latency private fiber. Isolated from failures of other AZs.
  - Local Zone   : AWS infrastructure placed closer to dense population centers.
                   Not all services available. Good for ultra-low latency workloads.
  - Wavelength   : AWS infrastructure embedded in 5G networks for sub-10ms latency.
  - Edge Location: CDN PoP used by CloudFront & Route 53 (200+ worldwide).
  - Regional Edge Cache: Larger CloudFront cache tier between origin and edge.

INTERVIEW QUESTION 01-A:
  "An application in us-east-1 needs to call an API in eu-west-1. 
   The call costs $0.02/GB for data transfer. How would you minimize this cost
   while maintaining sub-100ms latency?"
  HINT: Think CloudFront, API caching, edge computing with Lambda@Edge, and
        whether you actually NEED cross-region calls vs. replication.

INTERVIEW QUESTION 01-B:
  "You have a regulatory requirement that data must NEVER leave Germany.
   How do you architect this in AWS?"
  HINT: eu-central-1 (Frankfurt) + eu-central-2 (Zurich) — but AWS Regions are
        NOT countries. You need AWS Data Residency controls + SCPs + Config rules
        to ENFORCE this, not just hope.

CROSS QUESTION 01-C:
  "If an AZ in us-east-1 fails, does your Multi-AZ RDS automatically failover?
   What about your EC2 Auto Scaling Group? What about your S3 bucket?"
  → Each service handles AZ failure DIFFERENTLY. This tests depth.
"""


def list_aws_regions_and_az():
    """
    Enumerate all AWS regions and their Availability Zones.
    
    WHY THIS MATTERS: Before deploying anything, you need to understand
    what infrastructure is available. Some services (e.g., EKS) need
    minimum 2 AZs. Some regions don't have all services.
    
    GOTCHA: Some regions are opt-in! (e.g., ap-east-1 Hong Kong, me-south-1 Bahrain)
    You must enable them in the console before using boto3 with them.
    """
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    print("=" * 60)
    print("AWS REGIONS & AVAILABILITY ZONES")
    print("=" * 60)
    
    try:
        # Get all regions — note: only returns opted-in regions by default
        regions_response = ec2.describe_regions(
            AllRegions=False  # True would show ALL regions including opt-in disabled ones
        )
        
        for region in regions_response['Regions'][:5]:  # Print first 5 for demo
            region_name = region['RegionName']
            opt_in_status = region.get('OptInStatus', 'opt-in-not-required')
            
            print(f"\nRegion: {region_name}")
            print(f"  Opt-in Status: {opt_in_status}")
            
            # Get AZs for each region
            regional_ec2 = boto3.client('ec2', region_name=region_name)
            az_response = regional_ec2.describe_availability_zones(
                Filters=[{'Name': 'state', 'Values': ['available']}]
            )
            
            for az in az_response['AvailabilityZones']:
                print(f"  AZ: {az['ZoneName']} — Type: {az['ZoneType']}")
                
    except ClientError as e:
        print(f"Error: {e.response['Error']['Message']}")
        print("Run 'aws configure' to set up your credentials")


# ================================================================================
# SECTION 02 — IAM: IDENTITY & ACCESS MANAGEMENT
# ================================================================================
"""
CONCEPT: IAM is the SECURITY FOUNDATION of AWS. Everything you do in AWS is
controlled by IAM. A misconfigured IAM policy is the #1 cause of AWS breaches.

THE IAM MENTAL MODEL — "Who can do What to Which resource":
  - Principal : WHO is making the request (User, Role, Service, Account)
  - Action    : WHAT operation (s3:GetObject, ec2:StartInstances)
  - Resource  : WHICH specific resource (arn:aws:s3:::my-bucket/*)
  - Condition : WHEN/WHERE (only from this IP, only with MFA, only in us-east-1)

POLICY EVALUATION ORDER (Critical for interviews!):
  1. Explicit DENY → Always wins. Period.
  2. SCP (Service Control Policy) → Organization-level ceiling. Even root can't bypass.
  3. Resource-based policy → Allows cross-account access without assume-role.
  4. Permission Boundary → Sets max permissions an identity can ever have.
  5. Identity-based policy → The permissions actually attached.
  6. Session Policy → Limits permissions for temporary credentials.

  If none of the above ALLOW the action → Implicit DENY.

INTERVIEW QUESTION 02-A (Senior Level):
  "A Lambda function has an execution role with s3:GetObject on * 
   AND there's a bucket policy with an explicit DENY for the Lambda ARN.
   Can the Lambda read from that bucket?"
  ANSWER: NO. Explicit DENY always wins, regardless of the ALLOW on the role.

INTERVIEW QUESTION 02-B (Staff Level):
  "You need to allow Account B to write to an S3 bucket in Account A,
   but Account B's admin shouldn't be able to grant this access to anyone else.
   How do you architect this?"
  HINT: Cross-account: bucket policy in A grants Account B. Permission boundary
        in B ensures only specific roles can access. External ID for Confused Deputy.

INTERVIEW QUESTION 02-C (Architecture):
  "What is the 'confused deputy' problem in AWS and how do you prevent it?"
  HINT: When you have a third-party SaaS that assumes a role in your account,
        they could be tricked into performing actions on behalf of another customer.
        Solution: Use ExternalId condition in trust policy.

CROSS QUESTION 02-D:
  "How does a Lambda function running in a VPC differ from one NOT in a VPC,
   from an IAM permissions perspective?"
  HINT: Both use execution roles. But the VPC Lambda also needs 
        ec2:CreateNetworkInterface, ec2:DescribeNetworkInterfaces, etc.
        This is a GOTCHA — forgetting these breaks VPC Lambdas silently.
"""


def demonstrate_iam_concepts():
    """
    Demonstrate IAM policy creation, role assumption, and best practices.
    
    CONCEPT: In production, you NEVER use long-term access keys.
    Instead: EC2/Lambda/ECS → IAM Roles (temporary credentials auto-rotated)
    External systems → OIDC federation or IAM Identity Center (SSO)
    """
    iam = boto3.client('iam')
    
    # --- PART 1: Create a least-privilege IAM policy ---
    # PRINCIPLE OF LEAST PRIVILEGE: Grant ONLY what's needed.
    # Bad: s3:* on * (full S3 access to everything)
    # Good: s3:GetObject on arn:aws:s3:::specific-bucket/specific-prefix/*
    
    least_privilege_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AllowReadFromSpecificBucket",
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:ListBucket"          # Note: ListBucket is on bucket, GetObject is on object
                ],
                "Resource": [
                    "arn:aws:s3:::my-app-bucket",           # ListBucket needs the bucket ARN
                    "arn:aws:s3:::my-app-bucket/read-only/*" # GetObject needs the object ARN
                ],
                "Condition": {
                    "StringEquals": {
                        "aws:RequestedRegion": "us-east-1"  # Restrict to specific region
                    },
                    "Bool": {
                        "aws:SecureTransport": "true"        # Force HTTPS only
                    }
                }
            },
            {
                "Sid": "DenyAllExceptAllowedActions",
                # GOTCHA: You don't need explicit denies for actions not allowed.
                # But you DO need explicit denies for sensitive actions that
                # other policies might grant (e.g., SCPs, resource policies)
                "Effect": "Deny",
                "Action": [
                    "s3:DeleteObject",
                    "s3:DeleteBucket"
                ],
                "Resource": "*"
            }
        ]
    }
    
    print("LEAST PRIVILEGE POLICY EXAMPLE:")
    print(json.dumps(least_privilege_policy, indent=2))
    
    # --- PART 2: Lambda Execution Role Trust Policy ---
    # Trust policy: WHO can assume this role
    # This is separate from the PERMISSIONS policy (what they can DO)
    
    lambda_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # --- PART 3: Cross-Account Role Assumption with ExternalId ---
    # This prevents the CONFUSED DEPUTY problem
    cross_account_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::EXTERNAL_ACCOUNT_ID:root"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        # ExternalId is a secret shared only between you and the 3rd party
                        # It prevents a malicious account from tricking the 3rd party
                        # into operating on YOUR resources
                        "sts:ExternalId": "unique-customer-specific-external-id-12345"
                    }
                }
            }
        ]
    }
    
    print("\nCROSS-ACCOUNT TRUST POLICY (with ExternalId for confused deputy protection):")
    print(json.dumps(cross_account_trust_policy, indent=2))
    
    # --- PART 4: Service Control Policy (SCP) Example ---
    # SCPs are organization-level. Root user in member accounts CANNOT bypass SCPs.
    # They are the CEILING of what any identity can do.
    
    scp_deny_non_approved_regions = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "DenyAllOutsideApprovedRegions",
                "Effect": "Deny",
                "NotAction": [
                    # These actions are global and cannot be region-restricted
                    "iam:*",
                    "organizations:*",
                    "route53:*",
                    "budgets:*",
                    "waf:*",
                    "cloudfront:*",
                    "sts:GetCallerIdentity",
                    "sts:AssumeRole"
                ],
                "Resource": "*",
                "Condition": {
                    "StringNotEquals": {
                        "aws:RequestedRegion": [
                            "us-east-1",
                            "us-west-2",
                            "eu-west-1"
                        ]
                    }
                }
            }
        ]
    }
    
    print("\nSCP — DENY ALL OUTSIDE APPROVED REGIONS:")
    print(json.dumps(scp_deny_non_approved_regions, indent=2))


def demonstrate_iam_roles_programmatic():
    """
    Show how to properly assume roles and work with temporary credentials.
    
    CONCEPT: Temporary credentials (STS) are ALWAYS preferred over long-term keys.
    - They auto-expire (15 min to 12 hours configurable)
    - They leave CloudTrail audit trails
    - They can be constrained by session policies
    
    INTERVIEW QUESTION: What's the difference between sts:AssumeRole,
    sts:GetFederationToken, and sts:GetSessionToken?
    
    ANSWER:
    - AssumeRole: Used to assume an IAM Role. The new session inherits the role's policies.
    - GetFederationToken: Creates temporary creds for a federated user (e.g., corporate IdP).
      Session permissions = intersection of caller's policies + optional session policy.
    - GetSessionToken: Adds MFA verification to existing long-term creds. Required for
      API calls that have MFA conditions.
    """
    sts = boto3.client('sts')
    
    try:
        # Get current identity — useful for debugging "who am I calling as?"
        identity = sts.get_caller_identity()
        print(f"\nCurrent identity:")
        print(f"  Account: {identity['Account']}")
        print(f"  User ID: {identity['UserId']}")
        print(f"  ARN    : {identity['Arn']}")
        
        # Assume a role (cross-account or same-account)
        # The role must have a trust policy allowing THIS identity to assume it
        """
        assumed_role = sts.assume_role(
            RoleArn='arn:aws:iam::TARGET_ACCOUNT_ID:role/TargetRoleName',
            RoleSessionName='MySession-' + str(int(time.time())),
            DurationSeconds=3600,  # 1 hour. Min 15 min, max 12 hours (if role allows)
            
            # Session Policy: Further RESTRICT the role's permissions for this session.
            # Cannot EXPAND permissions — only restrict. Useful for granting minimal
            # access to a specific task without creating a separate role.
            Policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::specific-bucket/*"
                }]
            }),
            
            # Tags passed to the session — useful for ABAC (Attribute-Based Access Control)
            Tags=[
                {'Key': 'Department', 'Value': 'Engineering'},
                {'Key': 'Project', 'Value': 'DataPipeline'}
            ]
        )
        
        # Use the temporary credentials
        temp_credentials = assumed_role['Credentials']
        scoped_s3 = boto3.client(
            's3',
            aws_access_key_id=temp_credentials['AccessKeyId'],
            aws_secret_access_key=temp_credentials['SecretAccessKey'],
            aws_session_token=temp_credentials['SessionToken']  # REQUIRED for temp creds
        )
        """
        print("\nRole assumption example (commented out — needs real ARN to run)")
        
    except ClientError as e:
        print(f"IAM Error: {e.response['Error']['Code']}: {e.response['Error']['Message']}")


# ================================================================================
# SECTION 03 — EC2: ELASTIC COMPUTE CLOUD
# ================================================================================
"""
CONCEPT: EC2 is the foundation of AWS compute. Even if you use "serverless",
understanding EC2 deeply matters because:
  - EKS nodes ARE EC2 instances
  - RDS runs ON EC2 (managed, but same hardware concepts apply)
  - Auto Scaling patterns affect ALL AWS compute
  - Spot/Reserved/Savings Plans affect cost for ALL compute

EC2 INSTANCE FAMILIES (memorize these for architecture interviews):
  - General Purpose  : t3, m6i, m7g (Graviton3) — balanced CPU/memory
  - Compute Optimized: c6i, c7g — high CPU-to-memory ratio (web servers, batch)
  - Memory Optimized : r6i, r7g, x2idn — high memory (in-memory DB, caches)
  - Storage Optimized: i4i, im4gn — high NVMe IOPS (NoSQL, data warehouses)
  - Accelerated      : p4d (A100 GPU), inf2 (Inferentia for ML inference)
  - HPC              : hpc6a — high performance computing (MPI workloads)

PURCHASING OPTIONS (crucial for cost optimization interviews):
  - On-Demand    : Pay per hour/second. No commitment. Highest cost.
  - Reserved     : 1 or 3 year commitment. Up to 72% discount. Standard vs Convertible.
  - Savings Plans: Flexible commitment ($/hour) across EC2, Fargate, Lambda.
  - Spot         : Up to 90% discount. Can be INTERRUPTED with 2-min warning.
  - Dedicated Host: Physical server dedicated to you. For licensing compliance.
  - Dedicated Instance: Instance on hardware dedicated to you (but shared server ok).
  - Capacity Reservation: Guarantee capacity in specific AZ. Pay regardless of use.

INTERVIEW QUESTION 03-A (Spot Deep Dive):
  "Your batch processing job uses Spot instances. A Spot interruption occurs.
   What happens? How do you handle it gracefully?"
  ANSWER: AWS sends a Spot Interruption Notice via EC2 instance metadata 2 minutes 
  before termination. You MUST poll this endpoint from your application:
  http://169.254.169.254/latest/meta-data/spot/interruption-action
  Handle it by: checkpointing work, draining from load balancer, notifying SQS.
  Use Spot Fleet or Auto Scaling with mixed instances for resilience.

INTERVIEW QUESTION 03-B (Networking):
  "What's the difference between EC2 Enhanced Networking (ENA) and 
   Elastic Fabric Adapter (EFA)? When would you use each?"
  ANSWER: ENA = high-performance networking (up to 100 Gbps). Standard for most instances.
  EFA = ENA + OS-bypass for MPI/ML training. Needed for HPC where microseconds matter.
  EFA requires Placement Groups (Cluster) for lowest latency.

INTERVIEW QUESTION 03-C (Boot Deep Dive):
  "An EC2 instance is launched via Auto Scaling. The health check passes 
   after 30 seconds but the application takes 3 minutes to warm up.
   Traffic is sent before the app is ready. How do you fix this?"
  HINT: ALB connection draining, Target Group slow_start.duration_seconds,
        EC2 Launch Lifecycle Hooks, warm pools.

CROSS QUESTION 03-D:
  "Your EC2 instance profile (IAM role) and EC2 instance metadata are both
   security-critical. How does IMDSv2 differ from IMDSv1 and why does it matter?"
  HINT: IMDSv1 is request/response. IMDSv2 is session-oriented with a PUT request
  to get a token first. IMDSv1 is vulnerable to SSRF attacks (attacker tricks server
  to fetch metadata). IMDSv2 prevents SSRF because the PUT can't be forwarded.
"""


def ec2_deep_dive():
    """
    Demonstrate EC2 operations with production-quality patterns.
    """
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    # --- PART 1: Launch an EC2 instance with all best practices ---
    
    # User Data: Bash script that runs at FIRST boot (as root).
    # GOTCHA: User data runs only once by default. To re-run on restart,
    # you need to modify cloud-init configuration.
    user_data_script = """#!/bin/bash
set -e  # Exit on any error
set -o pipefail

# Log everything for debugging
exec > >(tee /var/log/user-data.log) 2>&1
echo "User data script started at $(date)"

# Update packages
yum update -y

# Install SSM agent (allows Session Manager — no SSH/bastion needed!)
yum install -y amazon-ssm-agent
systemctl start amazon-ssm-agent
systemctl enable amazon-ssm-agent

# Install CloudWatch agent for metrics + logs
yum install -y amazon-cloudwatch-agent

# Signal CloudFormation if this is part of a CFN stack
# /opt/aws/bin/cfn-signal --success true --stack ${AWS::StackName} --region ${AWS::Region}

echo "User data script completed at $(date)"
"""
    
    import base64
    user_data_b64 = base64.b64encode(user_data_script.encode()).decode()
    
    # Instance specification with ALL recommended settings
    launch_config = {
        'ImageId': 'ami-0abcdef1234567890',  # Replace with actual AMI
        'InstanceType': 'm6i.large',          # Intel-based general purpose
        
        # Spot instance request — up to 90% cheaper for fault-tolerant workloads
        'InstanceMarketOptions': {
            'MarketType': 'spot',
            'SpotOptions': {
                'SpotInstanceType': 'one-time',   # vs 'persistent'
                'InstanceInterruptionBehavior': 'terminate'  # or 'stop', 'hibernate'
            }
        },
        
        # METADATA SERVICE v2 — Always enforce IMDSv2!
        'MetadataOptions': {
            'HttpTokens': 'required',      # Enforces IMDSv2 (PUT token required)
            'HttpPutResponseHopLimit': 1,  # Prevents containers from accessing metadata
            'HttpEndpoint': 'enabled',
            'InstanceMetadataTags': 'enabled'  # Allow access to instance tags via metadata
        },
        
        # Storage — EBS optimized is default on modern instances
        'BlockDeviceMappings': [
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': 30,               # GB
                    'VolumeType': 'gp3',            # gp3 > gp2 (cheaper + better performance)
                    'Iops': 3000,                   # Baseline IOPS for gp3 (vs gp2 which is 3/GB)
                    'Throughput': 125,              # MB/s (gp3 configurable, gp2 is not)
                    'Encrypted': True,              # ALWAYS encrypt at rest
                    'DeleteOnTermination': True     # Clean up EBS when instance terminates
                }
            }
        ],
        
        # Network — Disable public IP for private instances
        'NetworkInterfaces': [
            {
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': False,  # No public IP (private subnet)
                'SubnetId': 'subnet-xxxxx',
                'Groups': ['sg-xxxxx'],             # Security groups
                'DeleteOnTermination': True
            }
        ],
        
        # IAM Role — ALWAYS use roles, NEVER bake in access keys
        'IamInstanceProfile': {
            'Name': 'MyEC2InstanceProfile'  # Profile name, not role name
        },
        
        'UserData': user_data_b64,
        
        # Tags — Critical for cost allocation and automation
        'TagSpecifications': [
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': 'my-app-server'},
                    {'Key': 'Environment', 'Value': 'production'},
                    {'Key': 'Team', 'Value': 'platform'},
                    {'Key': 'CostCenter', 'Value': 'engineering-123'},
                    {'Key': 'PatchGroup', 'Value': 'production-linux'}  # For SSM Patch Manager
                ]
            }
        ],
        
        'MinCount': 1,
        'MaxCount': 1
    }
    
    print("EC2 LAUNCH CONFIGURATION (not executing — for reference):")
    # Remove non-serializable parts for display
    display_config = {k: v for k, v in launch_config.items() 
                      if k not in ['UserData']}
    print(json.dumps(display_config, indent=2))


def ec2_auto_scaling_deep_dive():
    """
    Auto Scaling Groups (ASG) — Production patterns and interview topics.
    
    CONCEPT: ASG is not just about scaling. It's about:
    - SELF-HEALING: Automatically replace failed instances
    - SCALING: Respond to demand changes
    - ROLLING UPDATES: Deploy new versions without downtime
    - COST: Mix Spot and On-Demand (instance refresh)
    
    SCALING POLICIES HIERARCHY:
    1. Scheduled Scaling: "At 8am Monday, set capacity to 10"
    2. Predictive Scaling: ML-based, scales before load hits
    3. Target Tracking: "Keep CPU at 50%"  ← Simplest, usually best
    4. Step Scaling: "CPU 70-80% → add 2; CPU 80%+ → add 5"
    5. Simple Scaling: "CPU > 70% → add 1" (cooldown period between actions)
    
    INTERVIEW QUESTION 03-E:
    "Target Tracking vs Step Scaling — when do you use each?"
    ANSWER: Target Tracking is simpler and works for most cases.
    Step Scaling is needed when you want different scaling magnitudes
    based on how severe the metric deviation is. Also Step Scaling
    can be triggered from different alarms (not just one metric).
    """
    autoscaling = boto3.client('autoscaling', region_name='us-east-1')
    
    # Create a mixed instances ASG (Spot + On-Demand)
    asg_config = {
        'AutoScalingGroupName': 'my-production-asg',
        'MinSize': 2,
        'MaxSize': 20,
        'DesiredCapacity': 4,
        
        # Health check — switch to ELB for application-level health checks
        'HealthCheckType': 'ELB',  # vs 'EC2' (just checks if instance is running)
        'HealthCheckGracePeriod': 300,  # Seconds before health checks start
        
        'AvailabilityZones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
        
        # Mixed instances policy — key for cost optimization
        'MixedInstancesPolicy': {
            'LaunchTemplate': {
                'LaunchTemplateSpecification': {
                    'LaunchTemplateName': 'my-app-launch-template',
                    'Version': '$Latest'
                },
                # Override with different instance types for diversification
                # IMPORTANT: Diversify instance types to reduce Spot interruption risk
                'Overrides': [
                    {'InstanceType': 'm6i.large'},
                    {'InstanceType': 'm6a.large'},     # AMD — usually cheaper
                    {'InstanceType': 'm7g.large'},     # Graviton3 — best price/perf
                    {'InstanceType': 'm5.large'},      # Older but wider pool
                    {'InstanceType': 'm5a.large'},
                ]
            },
            'InstancesDistribution': {
                'OnDemandBaseCapacity': 2,              # Always keep 2 On-Demand
                'OnDemandPercentageAboveBaseCapacity': 20,  # 20% On-Demand, 80% Spot above base
                'SpotAllocationStrategy': 'price-capacity-optimized',  # Best strategy in 2024
                # 'price-capacity-optimized' considers BOTH price AND capacity availability
                # vs 'lowest-price' which only considers price (more interruptions)
                # vs 'capacity-optimized' which only considers capacity (less savings)
            }
        },
        
        # Termination policy — which instances to terminate first when scaling in
        'TerminationPolicies': [
            'OldestLaunchTemplate',  # Remove instances using old config first
            'AllocationStrategy',     # Maintain Spot/OD ratio
            'Default'                 # Then default (oldest instance)
        ],
        
        # Warm Pool — pre-initialize instances so they're ready faster
        # Reduces scaling OUT latency for slow-to-initialize apps
        # Instances in warm pool are stopped (you pay for EBS, not compute)
        
        'Tags': [
            {'Key': 'Environment', 'Value': 'production', 'PropagateAtLaunch': True},
            {'Key': 'Name', 'Value': 'my-app-asg', 'PropagateAtLaunch': True}
        ]
    }
    
    print("AUTO SCALING GROUP CONFIGURATION:")
    print(json.dumps(asg_config, indent=2))


# ================================================================================
# SECTION 04 — S3: SIMPLE STORAGE SERVICE
# ================================================================================
"""
CONCEPT: S3 is not just "file storage". It's an:
  - Object store (11 nines durability, designed to sustain concurrent loss of 2 AZs)
  - Static website host
  - Data lake foundation
  - Event source (for Lambda, SQS, SNS)
  - CDN origin (for CloudFront)
  - Audit log destination (CloudTrail, Config, ALB logs)

S3 STORAGE CLASSES (know these cold for interviews):
  - Standard         : 11 9s durability, 4 9s availability. Hot data.
  - Intelligent-Tiering: Auto-moves between tiers. No retrieval fees. Small monitoring fee.
  - Standard-IA      : 11 9s durability, 3 9s availability. Retrieval fee. >30-day objects.
  - One Zone-IA      : Single AZ. 11 9s durability within AZ. 20% cheaper than IA.
  - Glacier Instant  : 11 9s durability. ms retrieval. >90 day objects.
  - Glacier Flexible : 11 9s durability. 1 min to 12 hour retrieval. >90 days.
  - Glacier Deep Archive: Cheapest. 12-48 hour retrieval. >180 days.
  - Express One Zone : Single-digit ms latency. 10x faster than Standard. For ML/analytics.

INTERVIEW QUESTION 04-A (Performance):
  "Your S3 bucket receives 50,000 PUT requests per second and you're seeing
   503 SlowDown errors. What's the cause and how do you fix it?"
  ANSWER: S3 has per-prefix request rate limits: 5,500 GET/HEAD/DELETE per prefix/second
  and 3,500 PUT/COPY/POST per prefix/second. If all traffic goes to one prefix (e.g.,
  date/YYYY-MM-DD/), you hit limits. Solution: Randomize prefixes (hash the key),
  or use S3 Transfer Acceleration, or distribute writes across prefixes.
  
  NOTE: As of 2018, S3 automatically partitions based on key name. Random prefixes
  are less critical NOW but still matter at very high scale.

INTERVIEW QUESTION 04-B (Security):
  "You have an S3 bucket with a public bucket policy (s3:GetObject Allow *).
   You then add an object-level ACL to deny public access.
   Can public users access the object?"
  ANSWER: NO if you use ACLs. But BEST PRACTICE is to disable ACLs entirely
  (Object Ownership = BucketOwnerEnforced) and manage access ONLY via bucket policies.
  ACLs are legacy and cause confusion.

CROSS QUESTION 04-C (S3 + Lambda + SQS):
  "An S3 event notification triggers Lambda directly vs via SQS.
   What are the failure modes for each, and which is better for 
   guaranteed processing?"
  ANSWER: Direct Lambda: if Lambda fails, S3 won't retry (events can be lost).
  S3 → SQS → Lambda: SQS retries until DLQ. Much more reliable. Use SQS for
  anything where you can't afford to miss events.

INTERVIEW QUESTION 04-D (Consistency):
  "Is S3 eventually consistent or strongly consistent?"
  ANSWER: AS OF 2021, S3 provides STRONG READ-AFTER-WRITE consistency for:
  - PUTs of new objects → immediately readable
  - Overwrites / DELETEs → immediately consistent
  - List operations → strongly consistent
  This changed in 2020 (was eventually consistent before). CRITICAL for interviews.
"""


def s3_deep_dive():
    """
    S3 operations with production patterns, security hardening, and performance.
    """
    s3 = boto3.client('s3', region_name='us-east-1')
    
    bucket_name = 'my-secure-production-bucket-unique-123'
    
    # --- PART 1: Create a bucket with ALL security best practices ---
    
    def create_secure_bucket(bucket_name: str, region: str = 'us-east-1'):
        """
        Create an S3 bucket with production security hardening.
        
        INTERVIEW: What's the minimal set of S3 security configurations
        you should ALWAYS apply to a new bucket?
        
        ANSWER: Block Public Access + Server-Side Encryption + Versioning +
        Access Logging + Object Lock (if compliance) + CloudTrail data events.
        """
        s3_client = boto3.client('s3', region_name=region)
        
        try:
            # 1. Create the bucket
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            # 2. Block ALL public access — ALWAYS do this unless you need public content
            # These 4 settings work together:
            # BlockPublicAcls: Reject requests to set public ACLs
            # IgnorePublicAcls: Ignore existing public ACLs
            # BlockPublicPolicy: Reject bucket policies that grant public access
            # RestrictPublicBuckets: Restrict access even if public policy exists
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
            # 3. Enable default encryption with KMS (not SSE-S3)
            # KMS gives you: key rotation, access control, CloudTrail audit, cross-account
            # SSE-S3 is simpler but less control
            # SSE-C is customer-managed keys — you manage key material (very advanced)
            s3_client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'aws:kms',
                                'KMSMasterKeyID': 'alias/my-s3-key'  # Use custom KMS key
                            },
                            'BucketKeyEnabled': True  # S3 Bucket Key — reduces KMS API calls by 99%!
                            # GOTCHA: Without BucketKeyEnabled, every S3 GET/PUT calls KMS.
                            # At high scale, this causes KMS throttling and cost.
                        }
                    ]
                }
            )
            
            # 4. Enable versioning — protects against accidental deletion/overwrite
            s3_client.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # 5. Enable MFA Delete — requires MFA to permanently delete versions
            # This is the LAST line of defense against ransomware/accidental deletion
            # GOTCHA: MFA Delete can only be enabled/disabled by the bucket OWNER using root credentials
            # Can't do this via boto3 easily — must use AWS CLI with MFA
            
            # 6. Object Ownership — disable ACLs (modern best practice)
            s3_client.put_bucket_ownership_controls(
                Bucket=bucket_name,
                OwnershipControls={
                    'Rules': [
                        {'ObjectOwnership': 'BucketOwnerEnforced'}
                        # This disables ACLs entirely. All objects owned by bucket owner.
                        # Simplifies security model dramatically.
                    ]
                }
            )
            
            # 7. Bucket Policy — enforce HTTPS and require specific principals
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "DenyNonHTTPS",
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:*",
                        "Resource": [
                            f"arn:aws:s3:::{bucket_name}",
                            f"arn:aws:s3:::{bucket_name}/*"
                        ],
                        "Condition": {
                            "Bool": {"aws:SecureTransport": "false"}
                        }
                    },
                    {
                        "Sid": "DenyUnencryptedUploads",
                        "Effect": "Deny",
                        "Principal": "*",
                        "Action": "s3:PutObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                        "Condition": {
                            "Null": {"s3:x-amz-server-side-encryption": "true"}
                            # Deny if no encryption header provided
                        }
                    }
                ]
            }
            
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            # 8. Lifecycle rules — automate storage class transitions and cleanup
            s3_client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration={
                    'Rules': [
                        {
                            'ID': 'transition-to-ia-then-glacier',
                            'Status': 'Enabled',
                            'Filter': {'Prefix': 'data/'},
                            'Transitions': [
                                {
                                    'Days': 30,
                                    'StorageClass': 'STANDARD_IA'
                                    # GOTCHA: Minimum 30 days in Standard before IA transition
                                },
                                {
                                    'Days': 90,
                                    'StorageClass': 'GLACIER_IR'  # Glacier Instant Retrieval
                                },
                                {
                                    'Days': 365,
                                    'StorageClass': 'DEEP_ARCHIVE'
                                }
                            ],
                            # Clean up old versions
                            'NoncurrentVersionTransitions': [
                                {'NoncurrentDays': 30, 'StorageClass': 'STANDARD_IA'}
                            ],
                            'NoncurrentVersionExpiration': {
                                'NoncurrentDays': 90  # Delete versions older than 90 days
                            },
                            # IMPORTANT: Clean up incomplete multipart uploads!
                            # These cost money and are easy to forget
                            'AbortIncompleteMultipartUpload': {
                                'DaysAfterInitiation': 7
                            }
                        }
                    ]
                }
            )
            
            print(f"✅ Secure bucket '{bucket_name}' created with all best practices")
            return True
            
        except ClientError as e:
            print(f"❌ Error: {e.response['Error']['Code']}: {e.response['Error']['Message']}")
            return False
    
    print("S3 SECURE BUCKET CREATION PATTERN (for reference):")
    print("Would create bucket with: Block Public Access + KMS + Versioning + HTTPS-only policy")
    

def s3_multipart_upload_pattern():
    """
    S3 Multipart Upload — for files larger than 100MB.
    
    INTERVIEW QUESTION:
    "What is S3 Multipart Upload and when should you use it?"
    
    ANSWER:
    - Required for objects > 5GB
    - Recommended for objects > 100MB
    - Benefits: parallel uploads, retry individual parts, resume interrupted uploads
    - Parts: 1MB to 5GB each, max 10,000 parts
    - CRITICAL: You must complete OR abort. Incomplete uploads cost money!
      (Use lifecycle AbortIncompleteMultipartUpload to auto-clean)
    
    INTERVIEW QUESTION:
    "S3 Transfer Acceleration vs Multipart Upload — what's the difference?"
    ANSWER: 
    - Multipart = splits file into chunks, uploads in parallel via regular internet
    - Transfer Acceleration = routes traffic through AWS edge locations to S3 via 
      AWS private network (faster for uploads from far away)
    - Can use BOTH together for maximum performance
    """
    s3 = boto3.client('s3')
    
    def upload_large_file(bucket: str, key: str, file_path: str, 
                          part_size_mb: int = 100):
        """Upload a large file using multipart upload with error handling."""
        
        part_size = part_size_mb * 1024 * 1024  # Convert to bytes
        parts = []
        
        try:
            # Initiate multipart upload
            mpu = s3.create_multipart_upload(
                Bucket=bucket,
                Key=key,
                ServerSideEncryption='aws:kms',
                Metadata={'uploaded-by': 'my-app', 'upload-timestamp': str(int(time.time()))}
            )
            upload_id = mpu['UploadId']
            print(f"Started multipart upload: {upload_id}")
            
            # Upload parts
            """
            with open(file_path, 'rb') as f:
                part_number = 1
                while True:
                    data = f.read(part_size)
                    if not data:
                        break
                    
                    response = s3.upload_part(
                        Bucket=bucket,
                        Key=key,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=data
                    )
                    
                    parts.append({
                        'PartNumber': part_number,
                        'ETag': response['ETag']
                    })
                    
                    print(f"Uploaded part {part_number}")
                    part_number += 1
            
            # Complete the multipart upload
            s3.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            print(f"✅ Multipart upload completed: s3://{bucket}/{key}")
            """
            
            # IMPORTANT: Always have error handling to abort on failure
            # Otherwise you pay for incomplete multipart upload storage!
            print("Multipart upload pattern demonstrated (file operation commented out)")
            
        except Exception as e:
            print(f"Upload failed: {e}")
            # CRITICAL: Clean up failed upload
            if 'upload_id' in locals():
                s3.abort_multipart_upload(
                    Bucket=bucket,
                    Key=key,
                    UploadId=upload_id
                )
                print(f"🧹 Aborted multipart upload {upload_id}")
            raise
    
    print("S3 MULTIPART UPLOAD PATTERN:")
    print("For files > 100MB: split into parts, upload in parallel, complete atomically")


# ================================================================================
# SECTION 05 — VPC: VIRTUAL PRIVATE CLOUD (NETWORKING DEEP DIVE)
# ================================================================================
"""
CONCEPT: VPC is your private network in AWS. Everything touches VPC:
  - EC2, EKS, ECS run IN your VPC
  - RDS, ElastiCache run IN your VPC  
  - Lambda CAN run in your VPC (needed for private resource access)
  - ALB/NLB/Gateway LB live in your VPC subnets
  - DynamoDB, S3, SQS are OUTSIDE your VPC (use VPC Endpoints to reach privately)

VPC ADDRESSING:
  - VPC CIDR: Your address space (e.g., 10.0.0.0/16 = 65,536 addresses)
  - Subnet CIDR: Subdivision of VPC (e.g., 10.0.1.0/24 = 256 addresses)
  - AWS reserves 5 IPs in each subnet: .0, .1, .2, .3, .255
  - GOTCHA: You CANNOT change a VPC's primary CIDR block after creation.
    You CAN add secondary CIDRs (up to 5 total).

TRAFFIC ROUTING:
  - Route Table: Tells where traffic goes. Each subnet has one.
  - Internet Gateway (IGW): Allows traffic to/from internet (for public subnets)
  - NAT Gateway: Allows PRIVATE subnet instances to reach internet. NOT inbound.
  - Virtual Private Gateway (VGW): For VPN connections to on-premises.
  - Transit Gateway (TGW): Hub-and-spoke for connecting many VPCs and on-prem.

SECURITY (Two layers — both matter):
  - Security Group: Stateful. Instance-level. Allow only (no deny rules).
    GOTCHA: "Stateful" means if you allow inbound port 80, the response traffic
    is automatically allowed outbound — you don't need an outbound rule for it.
  - Network ACL (NACL): Stateless. Subnet-level. Allow AND deny rules.
    GOTCHA: "Stateless" means you need BOTH inbound AND outbound rules.
    Response traffic uses ephemeral ports (1024-65535) — you must allow these!

INTERVIEW QUESTION 05-A (NACL vs Security Groups):
  "When would you use NACLs over Security Groups?"
  ANSWER: NACLs for:
  1. Blocking specific IP addresses (Security Groups can't deny IPs)
  2. Subnet-wide rules that apply to ALL instances regardless of SG config
  3. Defense in depth — additional layer
  GOTCHA: NACLs have numbered rules evaluated in order. Lower number = higher priority.
  Rule 100 is checked before Rule 200. If Rule 100 allows, Rule 200 is NOT checked.

INTERVIEW QUESTION 05-B (VPC Endpoints):
  "An EC2 instance in a private subnet needs to access S3.
   What are the options and what are the tradeoffs?"
  OPTION 1: NAT Gateway → Internet → S3.
    Cost: NAT Gateway hourly + $0.045/GB data processing. Traffic leaves VPC!
  OPTION 2: S3 Gateway Endpoint.
    Cost: FREE. Traffic stays on AWS network. BUT: route table-based, not ENI.
    Cannot be used from on-prem (VPN/Direct Connect sees the prefix list routes).
  OPTION 3: S3 Interface Endpoint (PrivateLink).
    Cost: $0.01/hour + $0.01/GB. Traffic stays on AWS. Can be reached from on-prem.
    Endpoint creates an ENI in your subnet with a private IP.

INTERVIEW QUESTION 05-C (Connectivity Patterns):
  "VPC Peering vs Transit Gateway vs PrivateLink — when do you use each?"
  ANSWER:
  - VPC Peering: Direct connection between 2 VPCs. No transitive routing.
    (A→B, B→C doesn't mean A→C). Best for few, static connections.
  - Transit Gateway: Hub-and-spoke. Transitive routing. Connect hundreds of VPCs.
    Also connects to VPN and Direct Connect. Best for large/complex networks.
  - PrivateLink: Expose a SERVICE from one VPC to consumers in other VPCs.
    Consumer doesn't see your VPC — only the service endpoint. Best for SaaS/
    shared services without full network access.

CROSS QUESTION 05-D:
  "Your application in VPC A uses PrivateLink to access a service in VPC B.
   Can the service in VPC B initiate connections back to VPC A?"
  ANSWER: NO. PrivateLink is unidirectional. The service PROVIDER cannot initiate
  connections back to consumers. Only consumers connect to providers.
"""


def vpc_deep_dive():
    """
    VPC architecture patterns for production environments.
    
    BEST PRACTICE ARCHITECTURE (3-tier):
    
    VPC: 10.0.0.0/16
    ├── Public Subnet AZ-a: 10.0.0.0/24  (ALB, NAT GW, Bastion if needed)
    ├── Public Subnet AZ-b: 10.0.1.0/24
    ├── Public Subnet AZ-c: 10.0.2.0/24
    ├── Private App Subnet AZ-a: 10.0.10.0/24  (EC2/EKS/Lambda)
    ├── Private App Subnet AZ-b: 10.0.11.0/24
    ├── Private App Subnet AZ-c: 10.0.12.0/24
    ├── Private DB Subnet AZ-a: 10.0.20.0/24  (RDS, ElastiCache)
    ├── Private DB Subnet AZ-b: 10.0.21.0/24
    └── Private DB Subnet AZ-c: 10.0.22.0/24
    
    INTERVIEW QUESTION: "Why separate App and DB subnets if both are private?"
    ANSWER: Network ACLs! You can put a NACL on DB subnets that ONLY allows
    traffic from the App subnet CIDRs. Even if App subnet is compromised,
    an attacker can't directly reach the DB from a compromised instance
    in a non-App subnet. Also: regulatory compliance often requires DB
    isolation at network layer.
    """
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    print("VPC ARCHITECTURE PATTERN:")
    
    vpc_design = {
        "vpc_cidr": "10.0.0.0/16",
        "subnets": {
            "public": [
                {"az": "us-east-1a", "cidr": "10.0.0.0/24", "purpose": "ALB, NAT Gateway"},
                {"az": "us-east-1b", "cidr": "10.0.1.0/24", "purpose": "ALB, NAT Gateway"},
                {"az": "us-east-1c", "cidr": "10.0.2.0/24", "purpose": "ALB, NAT Gateway"}
            ],
            "private_app": [
                {"az": "us-east-1a", "cidr": "10.0.10.0/24", "purpose": "EC2/EKS nodes"},
                {"az": "us-east-1b", "cidr": "10.0.11.0/24", "purpose": "EC2/EKS nodes"},
                {"az": "us-east-1c", "cidr": "10.0.12.0/24", "purpose": "EC2/EKS nodes"}
            ],
            "private_db": [
                {"az": "us-east-1a", "cidr": "10.0.20.0/24", "purpose": "RDS, ElastiCache"},
                {"az": "us-east-1b", "cidr": "10.0.21.0/24", "purpose": "RDS, ElastiCache"},
                {"az": "us-east-1c", "cidr": "10.0.22.0/24", "purpose": "RDS, ElastiCache"}
            ]
        },
        "route_tables": {
            "public": {
                "routes": [
                    {"destination": "0.0.0.0/0", "target": "igw-xxxxx (Internet Gateway)"},
                    {"destination": "10.0.0.0/16", "target": "local"}
                ]
            },
            "private_app": {
                "routes": [
                    {"destination": "0.0.0.0/0", "target": "nat-xxxxx (NAT Gateway in same AZ)"},
                    {"destination": "10.0.0.0/16", "target": "local"},
                    {"destination": "pl-xxxxx (S3 prefix list)", "target": "vpce-xxxxx (S3 Gateway Endpoint)"}
                ]
            }
        }
    }
    
    print(json.dumps(vpc_design, indent=2))
    
    # Security Group best practices
    security_group_rules = {
        "alb_sg": {
            "description": "ALB Security Group",
            "inbound": [
                {"port": 443, "protocol": "TCP", "source": "0.0.0.0/0", "reason": "HTTPS from internet"},
                {"port": 80, "protocol": "TCP", "source": "0.0.0.0/0", "reason": "HTTP (for redirect to HTTPS)"}
            ],
            "outbound": [
                {"port": 8080, "protocol": "TCP", "destination": "app_sg", "reason": "To app servers"}
            ]
        },
        "app_sg": {
            "description": "Application Server Security Group",
            "inbound": [
                {"port": 8080, "protocol": "TCP", "source": "alb_sg", "reason": "Only from ALB — NEVER from 0.0.0.0/0!"}
                # GOTCHA: Reference security groups by ID, not CIDR. 
                # This way, even if ALB subnet CIDR changes, the rule stays correct.
            ],
            "outbound": [
                {"port": 5432, "protocol": "TCP", "destination": "db_sg", "reason": "To PostgreSQL RDS"},
                {"port": 6379, "protocol": "TCP", "destination": "cache_sg", "reason": "To ElastiCache Redis"},
                {"port": 443, "protocol": "TCP", "destination": "0.0.0.0/0", "reason": "To internet via NAT GW (APIs, packages)"}
            ]
        },
        "db_sg": {
            "description": "Database Security Group",
            "inbound": [
                {"port": 5432, "protocol": "TCP", "source": "app_sg", "reason": "ONLY from app servers"}
                # NEVER allow 0.0.0.0/0 to database! This is a critical security violation.
            ],
            "outbound": []  # No outbound needed for DB
        }
    }
    
    print("\nSECURITY GROUP DESIGN:")
    print(json.dumps(security_group_rules, indent=2))


# ================================================================================
# SECTION 06 — RDS & AURORA: MANAGED DATABASES
# ================================================================================
"""
CONCEPT: RDS manages the heavy lifting of databases:
  - OS patching, DB engine upgrades (with maintenance window)
  - Automated backups (point-in-time recovery up to 35 days)
  - Multi-AZ failover (synchronous replication, ~60 second RTO)
  - Read replicas (asynchronous replication, can be in different regions)
  
  BUT: You still must make critical decisions:
  - Instance type (determines CPU/RAM — more important than storage for DB)
  - Storage type (gp3 vs io1/io2 Block Express — IOPS vs cost tradeoff)
  - Multi-AZ vs Read Replica (failover vs read scale — they're different!)
  - Aurora vs RDS (huge performance/feature difference)

RDS vs AURORA COMPARISON (Senior Interview Must-Know):
  
  RDS:
  - Standard MySQL/PostgreSQL/Oracle/SQL Server
  - Storage: EBS volume per instance (max 64TB)
  - Multi-AZ: Synchronous standby, failover ~60-120 seconds
  - Backups: From standby (no I/O impact on primary)
  
  AURORA:
  - MySQL-compatible (3x faster) or PostgreSQL-compatible (5x faster)
  - Storage: Distributed across 6 copies in 3 AZs (no EBS per instance)
  - Multi-AZ: Storage-level redundancy + Aurora Replicas (up to 15)
  - Failover: 30 seconds typically (much faster than RDS Multi-AZ)
  - Aurora Serverless v2: Auto-scales from 0.5 to 128 ACUs in seconds
  - Aurora Global: Cross-region replication with <1 second lag (RPO ~1s, RTO <60s)
  - Backtrack: Rewind the database to a point in time WITHOUT restoring a backup!

INTERVIEW QUESTION 06-A:
  "RDS Multi-AZ vs RDS Read Replica — what's the difference?"
  ANSWER:
  Multi-AZ: SYNCHRONOUS replication. Standby is NOT readable. 
  Used for HIGH AVAILABILITY (failover). Automatic failover on failure.
  
  Read Replica: ASYNCHRONOUS replication. Replica IS readable.
  Used for READ SCALING (offload reads). Manual promotion on failure.
  Can be cross-region (for disaster recovery + serving local reads).
  
  CRITICAL GOTCHA: In a disaster where your primary fails:
  Multi-AZ failover: Aurora endpoint automatically updates. App reconnects.
  Read Replica promotion: You manually promote it. The endpoint CHANGES.
  You must update your app config OR use Route 53 health checks.

INTERVIEW QUESTION 06-B (Aurora Deep Dive):
  "What is Aurora's 'quorum write' mechanism?"
  ANSWER: Aurora writes to 6 storage nodes across 3 AZs.
  A write is acknowledged when 4 of 6 nodes confirm (write quorum).
  A read is served when 3 of 6 nodes confirm (read quorum).
  This means Aurora can tolerate: 1 AZ failure + 1 additional node failure
  without any data loss. The data is NEVER stored on the instance itself.
  
INTERVIEW QUESTION 06-C (Connections):
  "Your application opens 1000 database connections and RDS is throwing 
   'too many connections' errors. How do you solve this?"
  ANSWER: 
  1. RDS Proxy — connection pooling managed service. Reduces connections by 99%.
     Also speeds up failover (proxy maintains connection pool during failover,
     app doesn't need to reconnect).
  2. PgBouncer (for PostgreSQL) on EC2 — open source connection pooler.
  3. Reduce connection pool size in app (set maxPoolSize appropriately).
  
  GOTCHA: RDS Proxy requires IAM authentication (can't use password auth with proxy
  directly... well, you can, but IAM is the recommended approach).

CROSS QUESTION 06-D:
  "Aurora Serverless v2 vs Aurora Provisioned — which do you choose for 
   a production API that gets 1000 req/s during day and 10 req/s at night?"
  ANSWER: Aurora Serverless v2! It scales from min ACUs to max ACUs in <1 second.
  At 10 req/s (night), it scales down and you pay less.
  At 1000 req/s (day), it scales up instantly.
  Provisioned: You'd size for peak (1000 req/s), paying for peak capacity 24/7.
  GOTCHA: Serverless v2 doesn't scale to 0 (minimum is 0.5 ACU, ~$0.12/hour).
  Use Serverless v1 (pause/resume) only for dev/test that can tolerate cold starts.
"""


def rds_deep_dive():
    """
    RDS and Aurora management patterns with production best practices.
    """
    rds = boto3.client('rds', region_name='us-east-1')
    
    # --- Aurora Cluster Creation with all best practices ---
    
    aurora_cluster_config = {
        'DBClusterIdentifier': 'my-aurora-production-cluster',
        'Engine': 'aurora-postgresql',
        'EngineVersion': '15.4',  # Always use latest minor version
        
        # Storage encryption — ALWAYS enabled for production
        'StorageEncrypted': True,
        'KmsKeyId': 'arn:aws:kms:us-east-1:123456789:key/your-key-id',
        
        # Network configuration
        'VpcSecurityGroupIds': ['sg-xxxxx'],
        'DBSubnetGroupName': 'my-db-subnet-group',
        
        # Authentication
        'MasterUsername': 'dbadmin',
        # NEVER hardcode passwords! Use Secrets Manager
        'ManageMasterUserPassword': True,  # Aurora manages the password in Secrets Manager
        'MasterUserSecret': {'KmsKeyId': 'alias/my-secrets-key'},
        
        # Backup configuration
        'BackupRetentionPeriod': 35,         # Maximum retention (35 days)
        'PreferredBackupWindow': '02:00-03:00',  # Off-peak hours
        'PreferredMaintenanceWindow': 'sun:04:00-sun:05:00',
        
        # Aurora-specific features
        'EnableCloudwatchLogsExports': [
            'postgresql',    # Slow query log, error log
            'upgrade'        # Version upgrade logs
        ],
        
        # Deletion protection — prevents accidental destruction
        'DeletionProtection': True,  # Must disable before deleting
        
        # Enhanced Monitoring — OS-level metrics every 1 second
        'MonitoringInterval': 1,
        'MonitoringRoleArn': 'arn:aws:iam::123456789:role/rds-monitoring-role',
        
        # Performance Insights — query-level performance data (90 day retention with KMS)
        'EnablePerformanceInsights': True,
        'PerformanceInsightsKMSKeyId': 'alias/my-pi-key',
        'PerformanceInsightsRetentionPeriod': 731,  # 2 years
        
        # Serverless v2 scaling configuration
        'ServerlessV2ScalingConfiguration': {
            'MinCapacity': 0.5,   # Minimum: 0.5 ACU (~1 GB RAM)
            'MaxCapacity': 128.0  # Maximum: 128 ACU (~256 GB RAM)
        },
        
        'Tags': [
            {'Key': 'Environment', 'Value': 'production'},
            {'Key': 'Team', 'Value': 'backend'}
        ]
    }
    
    print("AURORA CLUSTER CONFIGURATION:")
    print(json.dumps(aurora_cluster_config, indent=2))
    
    # RDS Proxy Configuration
    rds_proxy_config = {
        "DBProxyName": "my-aurora-proxy",
        "EngineFamily": "POSTGRESQL",
        "RoleArn": "arn:aws:iam::123456789:role/rds-proxy-role",
        "Auth": [
            {
                "Description": "IAM Auth for Aurora Proxy",
                "AuthScheme": "SECRETS",
                "SecretArn": "arn:aws:secretsmanager:us-east-1:123456789:secret:db-credentials",
                "IAMAuth": "REQUIRED"  # Require IAM authentication
            }
        ],
        "VpcSecurityGroupIds": ["sg-proxy"],
        "VpcSubnetIds": ["subnet-1", "subnet-2", "subnet-3"],
        "RequireTLS": True,  # Enforce TLS
        "IdleClientTimeout": 1800,  # 30 minutes idle timeout
        "DebugLogging": False,
        "Tags": [{"Key": "Purpose", "Value": "connection-pooling"}]
    }
    
    print("\nRDS PROXY CONFIGURATION:")
    print(json.dumps(rds_proxy_config, indent=2))


# ================================================================================
# SECTION 07 — DYNAMODB: NOSQL AT SCALE
# ================================================================================
"""
CONCEPT: DynamoDB is a fully managed, serverless NoSQL database that:
  - Delivers single-digit millisecond latency at ANY scale
  - Scales to unlimited throughput and storage
  - Has 99.999% availability (5 nines) with Global Tables
  - Stores data across 3 AZs by default

THE MOST CRITICAL CONCEPT: DATA MODELING IN DYNAMODB IS COMPLETELY DIFFERENT FROM SQL!
In DynamoDB, you design your table based on your ACCESS PATTERNS first.
Then you choose your keys, GSIs, and LSIs to serve those patterns.

KEY CONCEPTS:
  - Partition Key: Determines WHICH partition your item goes to.
    Items with the same partition key are on the same partition.
    GOTCHA: If all your items have the same partition key → HOT PARTITION
    (all traffic to one server = bottleneck and throttling)
  
  - Sort Key: Within a partition, items are sorted by sort key.
    Allows range queries: between, begins_with, >, <
  
  - GSI (Global Secondary Index): New partition + sort key.
    Eventual consistency. Can project attributes. Costs extra WCUs/RCUs.
    You can add GSIs after table creation.
  
  - LSI (Local Secondary Index): Same partition key, different sort key.
    Strong consistency (reads from same shard). Must be created at table creation.
    Shares throughput with main table. Use sparingly.
  
  - Read Capacity Units (RCU): 1 RCU = 1 strongly consistent read of 4KB/second
    OR 2 eventually consistent reads of 4KB/second
  - Write Capacity Units (WCU): 1 WCU = 1 write of 1KB/second

INTERVIEW QUESTION 07-A (Data Modeling):
  "Design a DynamoDB table for a multi-tenant SaaS application where you need to:
   1. Get all orders for a tenant
   2. Get a specific order by ID
   3. Get all orders for a tenant in the last 30 days
   4. Get all orders with status 'PENDING'"
  
  ANSWER PATTERN (Single Table Design):
  PK            | SK               | GSI1-PK      | GSI1-SK      | Attributes
  TENANT#t1     | ORDER#o1         | STATUS#PENDING| 2024-01-15   | amount, ...
  TENANT#t1     | ORDER#o2         | STATUS#SHIPPED| 2024-01-16   | amount, ...
  
  Access patterns:
  1. PK = TENANT#t1, SK begins_with ORDER# → All orders for tenant
  2. PK = TENANT#t1, SK = ORDER#o1 → Specific order
  3. PK = TENANT#t1, SK between ORDER#2024-01-01 and ORDER#2024-01-31 → Date range
     (Sort key must encode date for this to work!)
  4. GSI1: PK = STATUS#PENDING, SK = date → All pending orders by date

INTERVIEW QUESTION 07-B (Throughput):
  "Your DynamoDB table is getting ProvisionedThroughputExceededException errors.
   Your DBA says to increase RCUs. But your table has 10,000 RCUs and traffic
   is only 1,000 RCUs. What's wrong?"
  ANSWER: HOT PARTITION. If 80% of your traffic goes to one partition key,
  that partition is getting 800 RCU/second while others get 20 each.
  DynamoDB distributes throughput EVENLY across partitions.
  
  FIX: Add a random suffix (1-10) to partition key, then do 10 queries in parallel.
  Or use DAX for caching. Or redesign the key schema.

INTERVIEW QUESTION 07-C (DynamoDB Streams):
  "What can you do with DynamoDB Streams that you can't do with regular polling?"
  ANSWER: DynamoDB Streams give you a time-ordered sequence of item-level changes.
  You see the BEFORE and AFTER image of each change. This enables:
  - Event-driven architectures (trigger Lambda on change)
  - Replication to other systems (Elasticsearch, S3 data lake)
  - Audit trails and change data capture
  - Cross-region replication (this is what Global Tables uses internally!)
  
  GOTCHA: Streams have a 24-hour retention. Lambda reads in batches.
  If Lambda fails, it retries the SAME batch until it succeeds or the record expires.
  Use DLQ and bisect-on-error to handle poison pill records.
"""


def dynamodb_deep_dive():
    """
    DynamoDB patterns: single-table design, GSIs, transactions, streams.
    """
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    dynamodb_resource = boto3.resource('dynamodb', region_name='us-east-1')
    
    # --- Single Table Design Example ---
    
    table_definition = {
        'TableName': 'SaaSApplication',
        
        # Key schema — the MOST IMPORTANT decision
        'KeySchema': [
            {'AttributeName': 'PK', 'KeyType': 'HASH'},    # Partition key
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}    # Sort key
        ],
        
        'AttributeDefinitions': [
            {'AttributeName': 'PK', 'AttributeType': 'S'},    # String
            {'AttributeName': 'SK', 'AttributeType': 'S'},
            {'AttributeName': 'GSI1PK', 'AttributeType': 'S'},
            {'AttributeName': 'GSI1SK', 'AttributeType': 'S'},
            {'AttributeName': 'GSI2PK', 'AttributeType': 'S'},
            {'AttributeName': 'GSI2SK', 'AttributeType': 'S'}
        ],
        
        # Global Secondary Indexes
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'GSI1',
                'KeySchema': [
                    {'AttributeName': 'GSI1PK', 'KeyType': 'HASH'},
                    {'AttributeName': 'GSI1SK', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},  # ALL, KEYS_ONLY, or INCLUDE
                'BillingMode': 'PAY_PER_REQUEST'  # Matches table mode
            },
            {
                'IndexName': 'GSI2',
                'KeySchema': [
                    {'AttributeName': 'GSI2PK', 'KeyType': 'HASH'},
                    {'AttributeName': 'GSI2SK', 'KeyType': 'RANGE'}
                ],
                'Projection': {
                    'ProjectionType': 'INCLUDE',
                    'NonKeyAttributes': ['status', 'amount', 'created_at']
                    # GOTCHA: Projecting ALL doubles your storage cost and GSI write cost.
                    # Only project what your access patterns need.
                }
            }
        ],
        
        # Capacity mode
        'BillingMode': 'PAY_PER_REQUEST',  # On-demand. No capacity planning.
        # Alternative: 'PROVISIONED' with ProvisionedThroughput
        # PAY_PER_REQUEST: Better for unpredictable/bursty traffic
        # PROVISIONED: Better for predictable traffic (can use Auto Scaling + Reserved Capacity)
        
        # Encryption at rest
        'SSESpecification': {
            'Enabled': True,
            'SSEType': 'KMS',
            'KMSMasterKeyId': 'alias/dynamodb-key'
        },
        
        # Streams — capture change data
        'StreamSpecification': {
            'StreamEnabled': True,
            'StreamViewType': 'NEW_AND_OLD_IMAGES'  # Get both before and after
            # Options: KEYS_ONLY, NEW_IMAGE, OLD_IMAGE, NEW_AND_OLD_IMAGES
        },
        
        # Point-in-time recovery — ALWAYS enable for production
        # Allows restore to any second in the last 35 days
        # No performance impact. Low cost.
        
        'Tags': [
            {'Key': 'Environment', 'Value': 'production'},
            {'Key': 'Team', 'Value': 'backend'}
        ]
    }
    
    print("DYNAMODB SINGLE TABLE DESIGN:")
    print(json.dumps(table_definition, indent=2))
    
    # --- DynamoDB Transactions ---
    def transfer_credits(from_user_id: str, to_user_id: str, 
                         amount: int, table_name: str):
        """
        Transfer credits between users atomically using DynamoDB Transactions.
        
        INTERVIEW QUESTION: What are DynamoDB Transactions and what are their limits?
        ANSWER: TransactWriteItems allows up to 100 items across 1-25 tables 
        in a single atomic operation. Either ALL succeed or ALL fail.
        
        COST GOTCHA: Transactional reads/writes cost 2x the normal RCU/WCU!
        Each item in the transaction costs double capacity units.
        
        ISOLATION: Serializable. Transactions are isolated from each other.
        GOTCHA: Two concurrent transactions touching the same item will fail
        one of them with TransactionCanceledException (ConditionalCheckFailed).
        You MUST handle this and retry!
        """
        dynamodb_client = boto3.client('dynamodb')
        
        try:
            response = dynamodb_client.transact_write_items(
                TransactItems=[
                    {
                        # Deduct from sender — conditional check prevents negative balance
                        'Update': {
                            'TableName': table_name,
                            'Key': {
                                'PK': {'S': f'USER#{from_user_id}'},
                                'SK': {'S': 'PROFILE'}
                            },
                            'UpdateExpression': 'SET credits = credits - :amount',
                            'ConditionExpression': 'credits >= :amount',  # Prevent overdraft
                            'ExpressionAttributeValues': {
                                ':amount': {'N': str(amount)}
                            }
                        }
                    },
                    {
                        # Add to receiver
                        'Update': {
                            'TableName': table_name,
                            'Key': {
                                'PK': {'S': f'USER#{to_user_id}'},
                                'SK': {'S': 'PROFILE'}
                            },
                            'UpdateExpression': 'SET credits = credits + :amount',
                            'ConditionExpression': 'attribute_exists(PK)',  # Receiver must exist
                            'ExpressionAttributeValues': {
                                ':amount': {'N': str(amount)}
                            }
                        }
                    },
                    {
                        # Write an audit log record
                        'Put': {
                            'TableName': table_name,
                            'Item': {
                                'PK': {'S': f'TRANSFER#{from_user_id}'},
                                'SK': {'S': f'TS#{int(time.time())}#TO#{to_user_id}'},
                                'from_user': {'S': from_user_id},
                                'to_user': {'S': to_user_id},
                                'amount': {'N': str(amount)},
                                'timestamp': {'N': str(int(time.time()))}
                            },
                            'ConditionExpression': 'attribute_not_exists(PK)'
                            # Idempotency check — don't duplicate the audit record
                        }
                    }
                ],
                # Client request token for IDEMPOTENCY
                # If you retry with the same token within 10 minutes,
                # DynamoDB returns the result of the FIRST successful transaction
                ClientRequestToken=hashlib.md5(
                    f"{from_user_id}{to_user_id}{amount}{int(time.time()//10)}".encode()
                ).hexdigest()
            )
            print(f"✅ Transfer successful: {amount} credits from {from_user_id} to {to_user_id}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'TransactionCanceledException':
                reasons = e.response.get('CancellationReasons', [])
                print(f"❌ Transaction failed. Reasons: {reasons}")
                # Check which item caused the failure and handle appropriately
            raise
    
    print("\nDYNAMODB TRANSACTION PATTERN:")
    print("Credit transfer with atomic debit + credit + audit log")


# ================================================================================
# SECTION 08 — LAMBDA: SERVERLESS COMPUTE
# ================================================================================
"""
CONCEPT: Lambda runs your code without managing servers. You pay ONLY for:
  - Number of invocations ($0.20 per 1M requests)
  - Duration × Memory (GB-seconds)
  
  But "serverless" doesn't mean "simple". Lambda has deep complexity around:
  - Cold starts (critical for latency-sensitive apps)
  - Concurrency limits (global and reserved)
  - Memory and CPU relationship
  - VPC vs non-VPC
  - Execution environment lifecycle

LAMBDA EXECUTION MODEL:
  1. Lambda downloads your code/container
  2. Starts the execution environment (cold start time)
  3. Runs INIT code (outside handler) — once per container instance
  4. Runs your HANDLER — on every invocation
  5. Execution environment stays "warm" for ~15 minutes
  6. If another request comes while frozen: WARM start (no cold start!)
  7. If concurrent requests → new execution environment (another cold start)

COLD START ANATOMY:
  - Download code: 10-200ms (depends on package size)
  - Initialize runtime (Python, Node, etc.): 50-200ms
  - Run your INIT code (imports, DB connections, etc.): your code's init time
  Total: often 200ms-2+ seconds for Python/Node, 1-10 seconds for Java

INTERVIEW QUESTION 08-A (Concurrency):
  "What is Lambda Reserved Concurrency vs Provisioned Concurrency?"
  ANSWER:
  Reserved Concurrency: CAPS the max concurrent executions for a function.
    - Prevents one function from consuming all 1000 account-wide concurrency
    - Setting to 0 throttles the function (useful for emergency stop)
    - Creates a "pool" of concurrency reserved for this function
  
  Provisioned Concurrency: PRE-WARMS execution environments.
    - Eliminates cold starts — environments are always warm and ready
    - Costs money even when not invoked (pay for pre-warmed envs)
    - Use with Auto Scaling to scale provisioned concurrency based on schedule/metrics
    - CRITICAL: Only works with published versions or aliases (NOT $LATEST)

INTERVIEW QUESTION 08-B (Failure Modes):
  "Your Lambda function is invoked asynchronously (from S3 event notification).
   It fails. What happens?"
  ANSWER: Lambda retries 2 MORE times (total 3 attempts) with random delays.
  If all 3 fail, the event is discarded (no more retries).
  CONFIGURE: 
  - DestinationConfig.OnFailure → send to SQS/SNS/Lambda/EventBridge on final failure
  - (SQS Dead-Letter Queue is the legacy way — still works)
  - MaximumRetryAttempts: 0, 1, or 2
  - MaximumEventAgeInSeconds: Discard events older than N seconds (6h max, 60 min min)

INTERVIEW QUESTION 08-C (Performance):
  "Your Lambda function processes images and takes 10 seconds on 128MB.
   How do you optimize it?"
  ANSWER:
  1. INCREASE MEMORY — Lambda CPU scales linearly with memory.
     512MB → 2x CPU → might finish in 5s at SAME or LOWER cost (less duration × more RAM)
     Use AWS Lambda Power Tuning tool to find optimal memory.
  2. Use /tmp for temporary files (512MB to 10GB)
  3. Initialize heavy objects OUTSIDE handler (runs once, reused across warm invocations)
  4. Consider Lambda Layers for shared libraries (cache between deployments)
  5. For very large images: use parallel processing with multiple Lambdas

CROSS QUESTION 08-D:
  "You have a Lambda in a VPC. It's taking 5+ seconds to start (cold start).
   Normal Lambda in same account takes 200ms. Why?"
  ANSWER: VPC Lambdas used to require creating an ENI at cold start (+10 seconds!).
  As of 2019/2020, AWS uses Hyperplane to pre-allocate ENIs per subnet/SG combination.
  Now VPC cold starts are similar to non-VPC (~200ms extra typically).
  BUT: If you see slow VPC cold starts, check:
  1. Subnet has enough IPs (each Lambda needs an IP from the subnet CIDR)
  2. Your code is doing slow VPC operations (DNS resolution, connection establishment)
  3. Security group rules are blocking initialization calls
"""


def lambda_deep_dive():
    """
    Lambda architecture patterns, concurrency, and optimization.
    """
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # --- Lambda Function Configuration with all best practices ---
    
    lambda_config = {
        'FunctionName': 'my-production-function',
        'Runtime': 'python3.12',   # Always use latest stable runtime
        'Role': 'arn:aws:iam::123456789:role/my-lambda-role',
        'Handler': 'app.handler',
        
        # Memory — also determines CPU. 1769MB = 1 vCPU
        'MemorySize': 512,   # Start at 512MB, tune with Power Tuning tool
        
        'Timeout': 30,       # 30 seconds. Max is 900 (15 min).
                             # Set to the MINIMUM needed + buffer.
        
        # Environment variables — for config, not secrets!
        'Environment': {
            'Variables': {
                'ENVIRONMENT': 'production',
                'LOG_LEVEL': 'INFO',
                'DB_SECRET_ARN': 'arn:aws:secretsmanager:us-east-1:123:secret:db-secret',
                # NEVER put actual credentials here — they're visible in console/API
                # Use Secrets Manager or SSM Parameter Store for sensitive values
            }
        },
        
        # VPC configuration (only if needed for private resource access)
        # GUIDELINE: Don't put Lambda in VPC unless it needs to access VPC resources.
        # Non-VPC Lambda has simpler networking and no subnet IP exhaustion risk.
        'VpcConfig': {
            'SubnetIds': ['subnet-private-1', 'subnet-private-2'],
            'SecurityGroupIds': ['sg-lambda']
        },
        
        # Ephemeral storage for /tmp — configurable 512MB to 10GB
        'EphemeralStorage': {'Size': 1024},  # 1GB /tmp
        
        # Dead-letter queue for async invocation failures
        'DeadLetterConfig': {
            'TargetArn': 'arn:aws:sqs:us-east-1:123:my-dlq'
        },
        
        # Tracing — X-Ray integration
        'TracingConfig': {'Mode': 'Active'},  # vs 'PassThrough'
        
        # Layers — shared code/dependencies
        'Layers': [
            'arn:aws:lambda:us-east-1:123:layer:my-common-utils:5',
            'arn:aws:lambda:us-east-1:580247275435:layer:LambdaInsightsExtension:38'
            # Lambda Insights layer for enhanced monitoring
        ],
        
        # Code signing — for supply chain security
        # 'CodeSigningConfigArn': 'arn:aws:lambda:...:code-signing-config/...'
        
        'Tags': {
            'Environment': 'production',
            'Team': 'platform',
            'CostCenter': 'engineering'
        },
        
        # Architectures — Graviton2 (arm64) is 20% cheaper + better perf
        'Architectures': ['arm64']  # or ['x86_64']
    }
    
    print("LAMBDA FUNCTION CONFIGURATION:")
    print(json.dumps(lambda_config, indent=2))
    
    # --- Lambda Handler Best Practices ---
    lambda_handler_template = '''
import json
import os
import boto3
import logging
from functools import lru_cache
from typing import Any, Dict

# BEST PRACTICE 1: Configure logging ONCE at module level
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# BEST PRACTICE 2: Initialize clients OUTSIDE the handler
# These are reused across warm invocations — no cold start penalty for subsequent calls
@lru_cache(maxsize=None)
def get_secrets_manager():
    return boto3.client('secretsmanager')

# BEST PRACTICE 3: Cache expensive config lookups
@lru_cache(maxsize=1)
def get_database_config():
    """Called once per execution environment — cached afterward."""
    sm = get_secrets_manager()
    secret = sm.get_secret_value(
        SecretId=os.environ['DB_SECRET_ARN']
    )
    return json.loads(secret['SecretString'])

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler following best practices.
    
    IMPORTANT: context object has:
    - context.function_name, context.function_version
    - context.invoked_function_arn
    - context.memory_limit_in_mb
    - context.aws_request_id (unique per invocation — use for idempotency!)
    - context.get_remaining_time_in_millis() — check this before long ops!
    """
    
    # BEST PRACTICE 4: Structured logging with correlation ID
    request_id = context.aws_request_id
    logger.info(json.dumps({
        "event": "handler_start",
        "request_id": request_id,
        "remaining_ms": context.get_remaining_time_in_millis()
    }))
    
    try:
        # BEST PRACTICE 5: Validate input early
        if 'body' not in event:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing body"})}
        
        # BEST PRACTICE 6: Check remaining time before expensive operations
        if context.get_remaining_time_in_millis() < 5000:  # Less than 5 seconds left
            logger.warning("Low time remaining, returning early")
            return {"statusCode": 503, "body": json.dumps({"error": "Timeout imminent"})}
        
        # Your business logic here
        db_config = get_database_config()  # Cached!
        
        result = {"status": "success", "request_id": request_id}
        
        logger.info(json.dumps({
            "event": "handler_complete",
            "request_id": request_id,
            "result": result
        }))
        
        return {"statusCode": 200, "body": json.dumps(result)}
        
    except Exception as e:
        # BEST PRACTICE 7: Log full exception with context
        logger.exception(json.dumps({
            "event": "handler_error",
            "request_id": request_id,
            "error": str(e)
        }))
        raise  # Re-raise for Lambda to handle retries / DLQ
'''
    
    print("\nLAMBDA HANDLER BEST PRACTICES:")
    print(lambda_handler_template)


# ================================================================================
# SECTION 09 — SQS, SNS & EVENTBRIDGE: MESSAGING & EVENTS
# ================================================================================
"""
CONCEPT: Messaging decouples producers and consumers. This is fundamental to:
  - Resilience: Producer doesn't fail if consumer is slow/down
  - Scale: Consumers can scale independently of producers
  - Retry: Failed messages can be retried without impacting producers
  - Fan-out: One message → multiple independent consumers

THE THREE SERVICES COMPARED:
  
  SQS (Simple Queue Service):
  - Queue: One message → ONE consumer (competing consumers pattern)
  - Standard: At-least-once delivery, best-effort ordering. Very high throughput.
  - FIFO: Exactly-once delivery, strict ordering. 3,000 msg/s (30,000 with batching).
  - Pull-based: Consumers poll for messages
  - Visibility Timeout: Message hidden during processing. If not deleted → redelivered.
  - Dead Letter Queue (DLQ): Moves messages that fail N times to a separate queue.
  
  SNS (Simple Notification Service):
  - Topic: One message → MANY subscribers (fan-out pattern)
  - Push-based: SNS pushes to subscribers
  - Subscribers: SQS, Lambda, HTTP/HTTPS, Email, SMS, Kinesis Data Firehose
  - Message filtering: Subscribers can filter messages by attributes
  
  EventBridge:
  - Event bus: Route events based on content rules (more powerful than SNS filtering)
  - Schema registry: Discover and document event schemas
  - Cross-account and cross-region event routing
  - 90+ AWS service sources, 100+ partner sources
  - Event replay and archiving

INTERVIEW QUESTION 09-A (SQS Mechanics):
  "A message is in your SQS queue. Your Lambda reads it and starts processing.
   After 5 seconds, the Lambda crashes (not a graceful failure — the process dies).
   What happens to the message?"
  ANSWER: Nothing happens immediately. After the Visibility Timeout expires
  (default 30s, you should set it to your expected processing time + buffer),
  the message becomes visible again in the queue and can be picked up by
  another consumer. It's NOT lost.
  
  CRITICAL GOTCHA: If Visibility Timeout < your processing time, the message
  will become visible WHILE you're still processing it. Another consumer picks it up.
  Now you have TWO consumers processing the SAME message! 
  → Set Visibility Timeout = 6x Lambda timeout (AWS recommendation)

INTERVIEW QUESTION 09-B (Ordering):
  "You need to process user events in strict order (user signs up → activates → buys).
   Would you use SQS Standard or FIFO?"
  ANSWER: FIFO. BUT: FIFO ordering is per Message Group ID.
  Use user_id as the Message Group ID → all events for a user are ordered.
  Events from DIFFERENT users are processed in parallel (different groups).
  GOTCHA: FIFO has throughput limits. With 10,000 users × 1 msg/s = 10,000 msg/s.
  Standard FIFO: 3,000 msg/s. With high-throughput mode: 30,000 msg/s.
  Above that? Split into multiple FIFO queues or use Kinesis (ordered per shard).

INTERVIEW QUESTION 09-C (SNS + SQS Fan-Out):
  "How do you ensure the same S3 upload event is processed by THREE different
   systems (billing, analytics, notifications) independently?"
  ANSWER: SNS Fan-Out pattern.
  S3 → SNS Topic → [SQS Queue A (billing)] + [SQS Queue B (analytics)] + [SQS Queue C (notifications)]
  
  Each SQS queue has its own consumer (Lambda or EC2).
  If billing Lambda fails, analytics and notifications are unaffected.
  Each queue has its own DLQ for failed messages.
  
  WHY SNS+SQS instead of S3 directly to 3 queues?
  S3 event notifications to SQS: 1 destination per S3 event type.
  SNS: 1 notification → unlimited subscribers.

CROSS QUESTION 09-D (EventBridge vs SNS):
  "When would you use EventBridge instead of SNS for routing events?"
  ANSWER:
  Use SNS when: Simple fan-out to known subscribers. Low latency is critical.
  Use EventBridge when:
  - Complex routing rules based on event CONTENT (not just topic)
  - Cross-account event routing needed
  - Events from AWS services (CloudTrail, CodePipeline, etc.)
  - Event replay (archive and replay events for debugging/reprocessing)
  - Schema registry and governance
  - 3rd party SaaS integration (Datadog, PagerDuty, etc.)
  
  EventBridge is slightly higher latency than SNS but much more powerful routing.
"""


def messaging_deep_dive():
    """
    SQS, SNS, and EventBridge patterns for production microservices.
    """
    sqs = boto3.client('sqs', region_name='us-east-1')
    sns = boto3.client('sns', region_name='us-east-1')
    events = boto3.client('events', region_name='us-east-1')
    
    # --- SQS FIFO Queue with DLQ ---
    
    def setup_sqs_with_dlq(queue_name: str, visibility_timeout: int = 300):
        """
        Create a FIFO queue with a Dead Letter Queue for handling failures.
        
        BEST PRACTICE: Always create a DLQ.
        Messages in DLQ can be: inspected, redriven, or manually processed.
        Without DLQ: failed messages loop forever in the queue or are lost.
        
        VISIBILITY TIMEOUT FORMULA:
        visibility_timeout = Lambda_timeout × 6
        (If Lambda is 30s, set visibility timeout to 180s)
        """
        
        # First create the DLQ
        dlq_config = {
            'QueueName': f'{queue_name}-dlq.fifo',
            'Attributes': {
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'false',  # We'll use explicit dedup IDs
                'MessageRetentionPeriod': '1209600',   # 14 days (max) — time to investigate
                'ReceiveMessageWaitTimeSeconds': '20', # Long polling — reduces API calls
            },
            'tags': {'Purpose': 'dead-letter-queue', 'ParentQueue': queue_name}
        }
        
        # Main FIFO queue
        main_queue_config = {
            'QueueName': f'{queue_name}.fifo',
            'Attributes': {
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'false',
                'VisibilityTimeout': str(visibility_timeout),
                'MessageRetentionPeriod': '86400',     # 1 day (adjust to your needs)
                'ReceiveMessageWaitTimeSeconds': '20', # Long polling ALWAYS for SQS
                                                       # Reduces cost + latency vs short poll
                
                # Redrive policy: After 3 failures, send to DLQ
                'RedrivePolicy': json.dumps({
                    'deadLetterTargetArn': f'arn:aws:sqs:us-east-1:123:{{queue_name}}-dlq.fifo',
                    'maxReceiveCount': 3  # Fail 3 times → DLQ
                })
            }
        }
        
        print("SQS FIFO QUEUE WITH DLQ CONFIGURATION:")
        print(json.dumps({'dlq': dlq_config, 'main_queue': main_queue_config}, indent=2))
    
    setup_sqs_with_dlq('order-processing', visibility_timeout=300)
    
    # --- SNS Fan-Out Pattern ---
    
    fan_out_architecture = {
        "pattern": "SNS Fan-Out",
        "description": "Single S3 upload event processed by multiple independent consumers",
        "components": {
            "source": "S3 Bucket (order-uploads)",
            "event_type": "s3:ObjectCreated:*",
            "sns_topic": "arn:aws:sns:us-east-1:123:new-order-topic",
            "subscribers": [
                {
                    "name": "Order Processing Queue",
                    "type": "SQS",
                    "filter_policy": {"order_type": ["standard", "express"]},
                    "dlq": "order-processing-dlq"
                },
                {
                    "name": "Analytics Queue",
                    "type": "SQS",
                    "filter_policy": {},  # No filter = receives all messages
                    "dlq": "analytics-dlq"
                },
                {
                    "name": "Notification Lambda",
                    "type": "Lambda",
                    "filter_policy": {"priority": ["high", "urgent"]},
                    "note": "Only notifies for high-priority orders"
                }
            ]
        },
        "benefits": [
            "Each subscriber fails independently",
            "Easy to add new consumers without changing S3/SNS config",
            "SNS message filtering reduces processing in each consumer"
        ]
    }
    
    print("\nSNS FAN-OUT ARCHITECTURE:")
    print(json.dumps(fan_out_architecture, indent=2))
    
    # --- EventBridge Rule Example ---
    
    def create_eventbridge_rule_for_failed_orders():
        """
        Route failed order events to operations team with rich routing.
        
        EventBridge rule: Route any ORDER event where status = FAILED
        to both PagerDuty (via HTTP) and ops SQS queue.
        """
        rule_pattern = {
            "source": ["my-app.orders"],
            "detail-type": ["OrderStatusChanged"],
            "detail": {
                "status": ["FAILED"],
                "amount": [{"numeric": [">", 1000]}]  # Only alert for orders > $1000
            }
        }
        
        print("\nEVENTBRIDGE RULE PATTERN:")
        print(json.dumps(rule_pattern, indent=2))
        print("\nThis rule would route: ORDER_FAILED events where amount > $1000")
        print("To: PagerDuty (HTTP endpoint) + Ops SQS queue")


# ================================================================================
# SECTION 10 — EKS & ECS: CONTAINER ORCHESTRATION
# ================================================================================
"""
CONCEPT: Containers (Docker) package apps and dependencies together.
Orchestration manages WHERE and HOW containers run at scale.

ECS (Elastic Container Service):
  - AWS-native container orchestrator
  - Simpler than Kubernetes. AWS manages the control plane entirely.
  - Two launch types: EC2 (you manage nodes) or Fargate (serverless)
  - Task Definition: Blueprint for your container (image, CPU, memory, env vars)
  - Service: Maintains desired count of tasks. Integrates with ALB.
  - Fargate: No EC2 management. Pay per vCPU/memory per second. Higher per-unit cost.

EKS (Elastic Kubernetes Service):
  - Managed Kubernetes. You get vanilla K8s + AWS integrations.
  - Control plane managed by AWS (API server, etcd, scheduler)
  - Worker nodes: EC2 (managed node groups) or Fargate profiles
  - Much more complex than ECS. Use when you need:
    * Kubernetes-specific features (CRDs, Helm, Operators)
    * Multi-cloud portability (same K8s manifests on EKS/GKE/AKS)
    * Large ecosystem (Istio, ArgoCD, Karpenter, etc.)
    * Complex scheduling requirements

INTERVIEW QUESTION 10-A (ECS vs EKS):
  "When do you choose ECS Fargate vs EKS Fargate vs EKS EC2?"
  ANSWER:
  ECS Fargate: Simple containerized workloads. No K8s complexity. Great for 
  teams that don't have K8s expertise. Managed entirely by AWS.
  
  EKS Fargate: Want K8s API but no node management. But: NO DaemonSets, 
  no privileged containers, no stateful workloads easily, limited addons.
  
  EKS EC2: Full K8s capabilities. You want: DaemonSets, privileged containers,
  GPU workloads, cost optimization (Spot instances with Karpenter),
  stateful workloads with persistent volumes.

INTERVIEW QUESTION 10-B (Karpenter):
  "What is Karpenter and how does it improve on Cluster Autoscaler?"
  ANSWER:
  Cluster Autoscaler: Scales existing node groups. Slow (2+ minutes).
  Node group must be pre-defined. Can't consider pod requirements optimally.
  
  Karpenter: Directly creates EC2 instances based on pending pod requirements.
  Much faster (30-60 seconds). Picks optimal instance type for the workload.
  Consolidates nodes when underutilized (removes empty nodes automatically).
  Works natively with Spot and handles diversification automatically.

INTERVIEW QUESTION 10-C (Networking):
  "What is the AWS VPC CNI plugin for EKS and what problem does it solve?"
  ANSWER: CNI (Container Network Interface) assigns network addresses to pods.
  AWS VPC CNI gives EACH POD a REAL VPC IP address (from your subnet).
  
  Benefits: Pods are first-class VPC citizens. Can apply Security Groups to pods!
  Can use VPC routing for inter-pod traffic.
  
  GOTCHA: Pods consume your subnet IPs! A /24 subnet has 251 usable IPs.
  If you have 200 pods, that's 200 IPs from the subnet.
  Mitigation: Use /prefix/ delegation (each ENI gets a /28 block = 16 IPs per ENI).

CROSS QUESTION 10-D:
  "How does ECS Service Connect differ from AWS App Mesh?"
  ANSWER:
  App Mesh: Full service mesh using Envoy proxy sidecars. Complex to operate.
  Requires injection of Envoy into every task/pod. Full mTLS between services.
  
  Service Connect: Simpler service discovery using ECS-managed Envoy proxy.
  Automatic service registration and discovery. Built-in metrics.
  No separate control plane to manage. Less powerful than App Mesh but much simpler.
  
  Choose Service Connect for most ECS workloads.
  Choose App Mesh for complex scenarios needing circuit breakers, retries, traffic shifting.
"""


def container_orchestration_deep_dive():
    """
    ECS and EKS production patterns.
    """
    ecs = boto3.client('ecs', region_name='us-east-1')
    
    # --- ECS Task Definition with Fargate ---
    
    task_definition = {
        'family': 'my-app-task',
        'networkMode': 'awsvpc',   # Required for Fargate. Each task gets its own ENI.
        
        # Task-level resources (split between containers in the task)
        'cpu': '1024',     # 1 vCPU (valid: 256, 512, 1024, 2048, 4096)
        'memory': '2048',  # 2 GB (valid depends on CPU choice)
        
        # IAM roles
        'taskRoleArn': 'arn:aws:iam::123:role/my-task-role',
        # ^ Permissions FOR your application code (e.g., S3 access)
        
        'executionRoleArn': 'arn:aws:iam::123:role/ecsTaskExecutionRole',
        # ^ Permissions for ECS AGENT to pull image from ECR, get secrets, write logs
        
        'requiresCompatibilities': ['FARGATE'],
        
        'containerDefinitions': [
            {
                'name': 'app',
                'image': '123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.2.3',
                # ALWAYS use specific image tags — NEVER :latest in production!
                # :latest makes rollbacks impossible and debugging a nightmare.
                
                'essential': True,  # If this container dies, the task stops
                
                # CPU and memory limits for this specific container
                'cpu': 896,       # Leave 128 for sidecar containers
                'memory': 1792,   # Hard limit
                'memoryReservation': 1024,  # Soft limit (guaranteed)
                
                'portMappings': [
                    {
                        'containerPort': 8080,
                        'protocol': 'tcp',
                        'appProtocol': 'http'  # For Service Connect
                    }
                ],
                
                # Environment variables — non-sensitive config only!
                'environment': [
                    {'name': 'ENV', 'value': 'production'},
                    {'name': 'LOG_LEVEL', 'value': 'info'}
                ],
                
                # Secrets from Secrets Manager or SSM — value injected at runtime
                'secrets': [
                    {
                        'name': 'DATABASE_URL',
                        'valueFrom': 'arn:aws:secretsmanager:us-east-1:123:secret:db-url:url::'
                        # Can reference specific JSON key with :key::
                    },
                    {
                        'name': 'API_KEY',
                        'valueFrom': 'arn:aws:ssm:us-east-1:123:parameter/prod/api-key'
                        # SSM Parameter Store — good for non-secret config too
                    }
                ],
                
                # CloudWatch Logs — structured logging
                'logConfiguration': {
                    'logDriver': 'awslogs',
                    'options': {
                        'awslogs-group': '/ecs/my-app',
                        'awslogs-region': 'us-east-1',
                        'awslogs-stream-prefix': 'ecs',
                        'awslogs-create-group': 'true',
                        'mode': 'non-blocking',  # Don't block app if CloudWatch is slow!
                        'max-buffer-size': '25m'
                    }
                },
                
                # Health check — ECS will restart container if this fails
                'healthCheck': {
                    'command': ['CMD', '/usr/local/bin/healthcheck.sh'],
                    # Or: ['CMD-SHELL', 'curl -f http://localhost:8080/health || exit 1']
                    'interval': 30,
                    'timeout': 5,
                    'retries': 3,
                    'startPeriod': 60  # Grace period for slow-starting apps
                },
                
                # Read-only root filesystem — security hardening
                'readonlyRootFilesystem': True,
                
                # Mount points (for writable locations)
                'mountPoints': [
                    {'containerPath': '/tmp', 'sourceVolume': 'tmp-volume'}
                ]
            }
        ],
        
        'volumes': [
            {
                'name': 'tmp-volume',
                'host': {}  # Ephemeral storage
            }
        ]
    }
    
    print("ECS FARGATE TASK DEFINITION:")
    print(json.dumps(task_definition, indent=2))


# ================================================================================
# SECTION 11 — CLOUDFORMATION & CDK: INFRASTRUCTURE AS CODE
# ================================================================================
"""
CONCEPT: Infrastructure as Code (IaC) means your infrastructure is:
  - VERSION CONTROLLED: Tracked in Git like application code
  - REPRODUCIBLE: Create identical environments reliably
  - TESTABLE: Lint, validate, unit test your infrastructure
  - AUDITABLE: History of every change with who/when/why

CLOUDFORMATION vs CDK:
  CloudFormation: JSON/YAML templates. Declarative. Verbose. No programming logic.
  CDK: Your language (Python, TypeScript, Java). Generates CloudFormation underneath.
  
  CDK Constructs hierarchy:
  - L1 (Cfn*): 1:1 mapping to CloudFormation resources. Verbose but full control.
  - L2: Smart defaults, methods, strong types. Most commonly used.
  - L3 (Patterns): Multi-resource patterns (e.g., ApplicationLoadBalancedFargateService)

INTERVIEW QUESTION 11-A (Stack Operations):
  "CloudFormation UPDATE_ROLLBACK_FAILED — what is it and how do you fix it?"
  ANSWER: Happens when an update fails AND the rollback also fails.
  Stack is stuck. You can't update or delete normally.
  
  Fix: ContinueUpdateRollback API → specify resources to skip during rollback.
  Then fix the underlying resource issues manually.
  
  Prevention: Use Change Sets to preview changes before applying.
  Use drift detection to catch manual changes that break CloudFormation.

INTERVIEW QUESTION 11-B (Nested vs StackSets):
  "When do you use CloudFormation Nested Stacks vs StackSets?"
  ANSWER:
  Nested Stacks: Decompose ONE large template into modules.
  Used within ONE account/region. Hierarchical deployment.
  
  StackSets: Deploy the SAME template to MULTIPLE accounts/regions.
  Used for Organization-wide policies (e.g., baseline security config).
  Supports drift detection across all accounts.

INTERVIEW QUESTION 11-C (CDK Best Practice):
  "What is a CDK Context and CDK Aspect? How are they different?"
  ANSWER:
  Context: Key-value store for CDK app configuration.
  Passed via cdk.json, CDK_DEFAULT_ACCOUNT/REGION, or --context flag.
  Also used to cache environment lookups (VPC IDs, AMIs, etc.)
  
  Aspect: Visitor pattern that traverses your CDK construct tree.
  Used for: Adding tags to ALL resources, enforcing policies (require encryption,
  block public access), custom validation.
  Example: Aspects.of(app).add(new RequireEncryptionAspect())

CROSS QUESTION 11-D:
  "Your CloudFormation stack has a DynamoDB table with DeletionPolicy=Retain
   and you delete the stack. What happens to the table?"
  ANSWER: The table is RETAINED — it stays in your account, unchanged.
  The CloudFormation stack is deleted but the table lives on.
  You'd need to manually delete the table.
  
  UpdateReplacePolicy: Separate concept — what happens if CF needs to REPLACE a resource
  (e.g., changing a property that requires replacement). Retain = keep old resource.
"""


def cloudformation_deep_dive():
    """
    CloudFormation and CDK patterns for production IaC.
    """
    cfn = boto3.client('cloudformation', region_name='us-east-1')
    
    # Example CloudFormation template in Python dict form
    cfn_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Production-ready ECS service with all best practices",
        
        "Parameters": {
            "Environment": {
                "Type": "String",
                "AllowedValues": ["development", "staging", "production"],
                "Description": "Deployment environment"
            },
            "ImageTag": {
                "Type": "String",
                "Description": "Docker image tag to deploy"
            }
        },
        
        "Conditions": {
            "IsProduction": {
                "Fn::Equals": [{"Ref": "Environment"}, "production"]
            }
        },
        
        "Resources": {
            "ECSService": {
                "Type": "AWS::ECS::Service",
                "DependsOn": ["ListenerRule"],  # Ensure ALB rule exists before service
                "Properties": {
                    "Cluster": {"Ref": "ECSCluster"},
                    "TaskDefinition": {"Ref": "TaskDefinition"},
                    "DesiredCount": {
                        "Fn::If": ["IsProduction", 3, 1]  # 3 in prod, 1 otherwise
                    },
                    "DeploymentConfiguration": {
                        "MaximumPercent": 200,        # Allow double capacity during deploy
                        "MinimumHealthyPercent": 100, # Never take service below 100%
                        "DeploymentCircuitBreaker": {
                            "Enable": True,
                            "Rollback": True
                            # Auto-rollback if X% of tasks fail to start!
                            # Prevents bad deployments from fully rolling out.
                        }
                    }
                },
                "UpdatePolicy": {
                    "AutoScalingRollingUpdate": {  # For rolling deployments
                        "MaxBatchSize": 1,
                        "MinSuccessfulInstancesPercent": 100
                    }
                }
            }
        },
        
        "Outputs": {
            "ServiceArn": {
                "Value": {"Ref": "ECSService"},
                "Export": {
                    "Name": {"Fn::Sub": "${AWS::StackName}-service-arn"}
                    # Export allows cross-stack references
                }
            }
        }
    }
    
    print("CLOUDFORMATION TEMPLATE STRUCTURE:")
    print(json.dumps(cfn_template, indent=2))
    
    # CDK equivalent in Python pseudocode
    cdk_example = '''
# CDK Python example (requires aws-cdk-lib installed)
from aws_cdk import (
    Stack, aws_ecs as ecs, aws_ecs_patterns as patterns,
    aws_ec2 as ec2, aws_ecr as ecr, CfnOutput, RemovalPolicy
)

class ProductionEcsStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # L2 Construct: VPC with sensible defaults
        vpc = ec2.Vpc(self, "Vpc",
            max_azs=3,
            nat_gateways=1  # Cost optimization: 1 NAT GW vs 3 for non-prod
        )
        
        # L2 Construct: ECS Cluster
        cluster = ecs.Cluster(self, "Cluster",
            vpc=vpc,
            container_insights=True,  # CloudWatch Container Insights
            cluster_name=f"my-app-{self.node.try_get_context('environment')}"
        )
        
        # L3 Pattern: ALB + Fargate Service in one construct
        service = patterns.ApplicationLoadBalancedFargateService(
            self, "Service",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=2,
            task_image_options=patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(
                    ecr.Repository.from_repository_name(self, "Repo", "my-app"),
                    tag=self.node.try_get_context("image_tag") or "latest"
                ),
                container_port=8080,
            ),
            public_load_balancer=True
        )
        
        # Configure health check
        service.target_group.configure_health_check(
            path="/health",
            healthy_threshold_count=2,
            unhealthy_threshold_count=3
        )
        
        # Output the ALB URL
        CfnOutput(self, "AlbUrl",
            value=service.load_balancer.load_balancer_dns_name,
            export_name="AlbDnsName"
        )
'''
    
    print("\nCDK EQUIVALENT:")
    print(cdk_example)


# ================================================================================
# SECTION 12 — CLOUDWATCH, X-RAY & OBSERVABILITY
# ================================================================================
"""
CONCEPT: Observability = Metrics + Logs + Traces. You CANNOT reliably operate
a production system without all three.

CLOUDWATCH COMPONENTS:
  - Metrics: Numerical time-series data (CPU%, request count, latency)
  - Logs: Text log streams from apps and AWS services
  - Log Insights: Query language for logs (like SQL for your logs)
  - Alarms: Alert when metrics cross thresholds
  - Dashboards: Visualize metrics and logs
  - Synthetics: Canary scripts that test your endpoints proactively
  - Container Insights: ECS/EKS cluster metrics + logs
  - Lambda Insights: Lambda-specific enhanced metrics

X-RAY:
  - Distributed tracing: Track requests as they flow through microservices
  - Service map: Visual graph of your service dependencies
  - Trace analysis: Find slow services, errors, throttling
  - Sampling: Don't trace every request (too expensive). Sample 5% + all errors.

INTERVIEW QUESTION 12-A (Metrics Math):
  "How do you calculate the 99th percentile latency from CloudWatch?
   Is CloudWatch Average sufficient for monitoring latency?"
  ANSWER: NO! Average is deeply misleading for latency.
  If 99% of requests take 10ms and 1% take 10,000ms, average is ~109ms.
  That 1% (99th percentile) represents users having terrible experiences.
  
  Use: p50 (median), p90, p95, p99, p99.9
  CloudWatch Percentile Statistics: use p(X) in alarm configurations.
  
  Extended Statistics: CloudWatch supports p0.1 through p99.9 on custom metrics.
  Use percentile statistics in your alarms and dashboards.

INTERVIEW QUESTION 12-B (Log Insights Query):
  "Write a CloudWatch Logs Insights query to find the top 10 slowest Lambda
   invocations in the last hour."
  ANSWER:
  fields @timestamp, @duration, @requestId
  | filter @type = "REPORT"
  | sort @duration desc
  | limit 10

INTERVIEW QUESTION 12-C (Alarm Types):
  "What is a CloudWatch Composite Alarm and when would you use it?"
  ANSWER: Composite Alarm = combination of multiple alarms using AND/OR logic.
  Use when: A single metric being in ALARM state is a false positive.
  Example: Alert ONLY when CPU > 80% AND error rate > 5% AND latency > 2s
  (not just when CPU is high because a batch job runs).
  Reduces alert fatigue.

CROSS QUESTION 12-D:
  "Your microservices architecture has 20 services. A user reports an error.
   How do you trace the request through all 20 services?"
  ANSWER: X-Ray Distributed Tracing.
  Each service adds the X-Ray trace header (X-Amzb-Trace-Id).
  X-Ray SDK captures segments and subsegments from each service.
  Service Map shows the path a request took through all services.
  
  IMPLEMENTATION: In Python Lambda: pip install aws-xray-sdk
  from aws_xray_sdk.core import xray_recorder, patch_all
  patch_all()  # Auto-instruments boto3, requests, psycopg2, etc.
"""


def observability_deep_dive():
    """
    CloudWatch and X-Ray patterns for production observability.
    """
    cloudwatch = boto3.client('cloudwatch', region_name='us-east-1')
    logs = boto3.client('logs', region_name='us-east-1')
    
    # --- Custom Metrics ---
    def emit_business_metric(metric_name: str, value: float, 
                             unit: str = 'Count', dimensions: dict = None):
        """
        Emit a custom business metric to CloudWatch.
        
        INTERVIEW: What are the limits for custom metrics?
        - Standard resolution: 1-minute granularity (cheaper)
        - High-resolution: 1-second granularity (more expensive)
        - Retention: Based on resolution (60s data → 15 days, 1-min → 63 days, etc.)
        - Dimensions: Up to 30 per metric. Each unique dimension combination = separate metric.
        
        GOTCHA: Each unique combination of dimension values creates a SEPARATE metric.
        If you add "UserID" as a dimension for 1M users → 1M separate metrics!
        This is called "cardinality explosion" and will cost a fortune.
        Use low-cardinality dimensions (environment, region, service-name).
        """
        
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.datetime.utcnow(),
            'Dimensions': [
                {'Name': k, 'Value': v} 
                for k, v in (dimensions or {}).items()
            ],
            'StorageResolution': 1  # 1=high-resolution (1 sec), 60=standard (1 min)
        }
        
        try:
            cloudwatch.put_metric_data(
                Namespace='MyApp/BusinessMetrics',
                MetricData=[metric_data]
            )
        except ClientError as e:
            print(f"Failed to emit metric: {e}")
    
    # --- CloudWatch Alarm with Actions ---
    
    alarm_config = {
        'AlarmName': 'HighErrorRate-Production',
        'AlarmDescription': 'Alert when API error rate exceeds 1% for 5 minutes',
        
        # Metric configuration
        'MetricName': 'HTTPCode_Target_5XX_Count',
        'Namespace': 'AWS/ApplicationELB',
        'Statistic': 'Sum',
        'Period': 60,              # 1 minute evaluation period
        'EvaluationPeriods': 5,    # Need 5 consecutive violations
        'DatapointsToAlarm': 3,    # But only 3 out of 5 need to breach (M of N)
        # This reduces false positives from momentary spikes
        
        'Threshold': 100.0,
        'ComparisonOperator': 'GreaterThanThreshold',
        'TreatMissingData': 'notBreaching',
        # Options: breaching, notBreaching, ignore, missing
        # 'notBreaching': If no data, consider metric healthy. Good for counting metrics.
        # 'breaching': If no data, alarm! Good for heartbeat/health metrics.
        
        'Dimensions': [
            {'Name': 'LoadBalancer', 'Value': 'app/my-alb/1234567890'}
        ],
        
        # Actions
        'AlarmActions': [
            'arn:aws:sns:us-east-1:123:ops-alerts-topic'
        ],
        'OKActions': [
            'arn:aws:sns:us-east-1:123:ops-alerts-topic'  # Notify when recovered too
        ],
        'InsufficientDataActions': []
    }
    
    print("CLOUDWATCH ALARM CONFIGURATION:")
    print(json.dumps(alarm_config, default=str, indent=2))
    
    # --- Log Insights Query Examples ---
    log_insights_queries = {
        "find_slowest_lambda_invocations": """
fields @timestamp, @duration, @requestId, @memorySize
| filter @type = "REPORT"
| sort @duration desc
| limit 20
        """,
        
        "find_errors_with_context": """
fields @timestamp, @message, @requestId
| filter @message like /ERROR/
| parse @message "error=*" as errorType
| stats count(*) as errorCount by errorType
| sort errorCount desc
        """,
        
        "api_latency_percentiles": """
fields @timestamp, responseTime
| filter ispresent(responseTime)
| stats 
    pct(responseTime, 50) as p50,
    pct(responseTime, 90) as p90,
    pct(responseTime, 95) as p95,
    pct(responseTime, 99) as p99,
    count(*) as requestCount
by bin(5m)
| sort @timestamp asc
        """,
        
        "cold_start_analysis": """
filter @type = "REPORT"
| filter @initDuration > 0
| stats 
    count(*) as coldStarts,
    avg(@initDuration) as avgInitMs,
    max(@initDuration) as maxInitMs,
    pct(@initDuration, 95) as p95InitMs
        """
    }
    
    print("\nCLOUDWATCH LOGS INSIGHTS QUERIES:")
    for name, query in log_insights_queries.items():
        print(f"\n{name}:{query}")


# ================================================================================
# SECTION 13 — SECURITY: KMS, SECRETS MANAGER & GUARDUTY
# ================================================================================
"""
CONCEPT: AWS Security is a shared responsibility model.
  AWS secures: Physical data centers, hypervisors, managed service infrastructure.
  YOU secure: Your data, OS configs, IAM policies, encryption keys, app code.

KEY SECURITY SERVICES:
  - KMS (Key Management Service): Create and manage encryption keys. FIPS 140-2 validated.
  - Secrets Manager: Store and rotate credentials/API keys/passwords.
  - GuardDuty: Threat detection using ML + threat intelligence.
  - Security Hub: Aggregates findings from GuardDuty, Inspector, Macie, Config.
  - Macie: ML-powered PII detection in S3.
  - Inspector: Vulnerability scanning for EC2, Lambda, ECR images.
  - AWS Config: Audit and record AWS resource configurations over time.
  - CloudTrail: API audit log (who did what, when, from where).

KMS KEY TYPES:
  - AWS Managed Keys: AWS creates and manages. Rotated every year. Free.
    You can't change rotation schedule or key policies. Key ID: aws/s3, aws/rds, etc.
  - Customer Managed Keys (CMK): You create, you control policies.
    Can rotate annually (automatic) or manually. $1/month per key + API call costs.
  - Data Keys: Generated by KMS, used to encrypt DATA (not in KMS — envelope encryption).
  - CloudHSM: Dedicated Hardware Security Module. FIPS 140-2 Level 3. Very expensive.
    Use for: PKI, digital signing, regulatory requirements for dedicated HSM.

INTERVIEW QUESTION 13-A (Envelope Encryption):
  "Explain envelope encryption and why AWS uses it."
  ANSWER:
  Direct encryption: KMS encrypts your data. Problem: Large data (GBs) is slow,
  expensive (KMS has throughput limits), and data must transit to KMS.
  
  Envelope encryption:
  1. KMS generates a Data Key (plaintext + encrypted copy)
  2. Your code uses PLAINTEXT data key to encrypt data locally (fast, no KMS calls)
  3. You store ONLY the encrypted data key alongside the encrypted data
  4. Discard the plaintext data key from memory
  5. To decrypt: Send encrypted data key to KMS → get plaintext key → decrypt data
  
  Benefits: Data never leaves your system. Only the small data key transits to KMS.
  KMS only sees the key (not your data). Scales well.

INTERVIEW QUESTION 13-B (KMS Key Policy):
  "What makes KMS Key Policies different from IAM policies?"
  ANSWER: CRITICAL DIFFERENCE — KMS uses a KEY POLICY that must exist.
  
  Unlike IAM: If you have an IAM policy granting kms:Decrypt but the KEY POLICY
  doesn't allow it → ACCESS DENIED. Key policy is REQUIRED.
  
  The default key policy MUST include the account's IAM for IAM to work at all.
  Without the IAM delegation statement in the key policy, even root can't access it!
  
  GOTCHA: If you delete the key policy's IAM delegation statement and lock yourself
  out → contact AWS Support for a KMS key recovery procedure (3-7 day process).

INTERVIEW QUESTION 13-C (Secrets Rotation):
  "Secrets Manager can auto-rotate. How does the rotation work?"
  ANSWER: Rotation is done by a Lambda function that:
  1. Creates a new secret version (AWSPENDING stage)
  2. Sets the new secret in the target system (e.g., database password change)
  3. Tests the new credentials
  4. Marks the new version as AWSCURRENT
  5. Marks the old version as AWSPREVIOUS (kept briefly for rollback)
  
  The AWSPREVIOUS stage stays for 24+ hours for apps still using old credentials.
  During rotation, both current and previous credentials work.

CROSS QUESTION 13-D:
  "GuardDuty finds that an EC2 instance is making DNS requests to a domain
   associated with cryptocurrency mining. What are your next steps?"
  ANSWER:
  1. Isolate immediately: Move instance to quarantine Security Group (no outbound, no inbound)
  2. Snapshot the instance (preserve forensic evidence)
  3. Check CloudTrail for recent actions from this instance's IAM role
  4. Check VPC Flow Logs for network connections
  5. Check if IAM credentials were exfiltrated (check sts:GetCallerIdentity calls from unknown IPs)
  6. Revoke IAM role temporary credentials (--revoke-sessions on the role)
  7. Investigate: how did attacker get in? (Check SSM session history, app logs, SSH logs)
  8. Terminate the compromised instance, launch clean replacement
"""


def security_deep_dive():
    """
    KMS, Secrets Manager, and security patterns.
    """
    kms = boto3.client('kms', region_name='us-east-1')
    secrets = boto3.client('secretsmanager', region_name='us-east-1')
    
    # --- KMS Key with Proper Policy ---
    
    kms_key_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                # CRITICAL: This statement must exist or NO ONE can use the key!
                # Delegates KMS authorization to IAM policies
                "Sid": "EnableIAMUserPermissions",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::123456789012:root"
                    # Root = the AWS account itself (enables IAM-based access)
                },
                "Action": "kms:*",
                "Resource": "*"
            },
            {
                "Sid": "AllowKeyAdminToManage",
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "arn:aws:iam::123456789012:role/KeyAdminRole"
                    ]
                },
                "Action": [
                    "kms:Create*", "kms:Describe*", "kms:Enable*",
                    "kms:List*", "kms:Put*", "kms:Update*", "kms:Revoke*",
                    "kms:Disable*", "kms:Get*", "kms:Delete*",
                    "kms:TagResource", "kms:UntagResource",
                    "kms:ScheduleKeyDeletion", "kms:CancelKeyDeletion"
                    # NOTE: Admin can manage key but NOT use it for crypto!
                    # This separates key management from key usage (least privilege)
                ],
                "Resource": "*"
            },
            {
                "Sid": "AllowLambdaToUseKey",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::123456789012:role/LambdaExecutionRole"
                },
                "Action": [
                    "kms:Decrypt",
                    "kms:GenerateDataKey"  # For envelope encryption
                ],
                "Resource": "*",
                "Condition": {
                    # Encryption context — additional authentication for KMS
                    # The same context must be provided for Decrypt as was used for Encrypt
                    # Prevents misuse of the encrypted data in different contexts
                    "StringEquals": {
                        "kms:EncryptionContext:application": "my-lambda-function",
                        "kms:EncryptionContext:environment": "production"
                    }
                }
            }
        ]
    }
    
    print("KMS KEY POLICY:")
    print(json.dumps(kms_key_policy, indent=2))
    
    # --- Secrets Manager with Rotation ---
    
    def store_database_credentials(secret_name: str, credentials: dict):
        """
        Store database credentials with automatic rotation configured.
        
        SECRET STRUCTURE (for RDS auto-rotation):
        {
            "engine": "postgres",
            "host": "mydb.cluster-xyz.us-east-1.rds.amazonaws.com",
            "username": "app_user",
            "password": "initial-password-will-be-rotated",
            "dbname": "myapp",
            "port": 5432
        }
        
        Rotation Lambda will: generate new password → change it in RDS → update secret.
        """
        try:
            # Create the secret
            response = secrets.create_secret(
                Name=secret_name,
                Description='Production database credentials',
                SecretString=json.dumps(credentials),
                KmsKeyId='alias/my-secrets-key',  # Encrypt with your KMS key
                Tags=[
                    {'Key': 'Environment', 'Value': 'production'},
                    {'Key': 'Rotation', 'Value': 'enabled'}
                ]
            )
            
            # Enable automatic rotation
            secrets.rotate_secret(
                SecretId=secret_name,
                RotationLambdaARN='arn:aws:lambda:us-east-1:123:function:SecretsRotation',
                RotationRules={
                    'AutomaticallyAfterDays': 30,  # Rotate every 30 days
                    # BEST PRACTICE: Rotate more frequently for high-security systems
                }
            )
            
            print(f"✅ Secret created and rotation enabled: {secret_name}")
            
        except ClientError as e:
            print(f"Error: {e.response['Error']['Code']}")
    
    def get_secret_with_caching(secret_arn: str):
        """
        Retrieve a secret with proper caching.
        
        INTERVIEW: Why should you cache secrets instead of fetching every request?
        ANSWER: 
        1. COST: Secrets Manager charges $0.05 per 10,000 API calls
        2. LATENCY: Each API call adds latency to your request
        3. THROTTLING: Secrets Manager has request rate limits
        
        USE: AWS Secrets Manager Client-Side Caching Library
        Or: Cache in your Lambda execution environment global scope
        
        GOTCHA: Cache too long → old credentials used after rotation.
        Secrets Manager rotation keeps AWSPREVIOUS for ~1 day.
        Cache TTL should be < 1 day, typically 5-60 minutes.
        """
        # This is a simple in-memory cache (per Lambda execution environment)
        # In production: use aws_secretsmanager_caching library
        
        cache = {}  # In real code: module-level variable, not local
        
        cache_key = secret_arn
        if cache_key in cache:
            cached_time = cache[cache_key]['timestamp']
            if time.time() - cached_time < 300:  # 5-minute TTL
                return cache[cache_key]['value']
        
        secret_value = secrets.get_secret_value(SecretId=secret_arn)
        result = json.loads(secret_value['SecretString'])
        
        cache[cache_key] = {
            'value': result,
            'timestamp': time.time()
        }
        
        return result
    
    print("\nSECRETS MANAGER PATTERN:")
    print("Rotate secrets automatically. Cache on client side. Use KMS encryption.")


# ================================================================================
# SECTION 14 — COST OPTIMIZATION PATTERNS
# ================================================================================
"""
CONCEPT: Cost optimization is a first-class engineering concern at scale.
A "well-architected" system is cost-efficient. AWS Well-Architected has a
dedicated Cost Optimization pillar.

THE COST OPTIMIZATION FRAMEWORK:
  1. Right-sizing: Match instance types to actual usage
  2. Pricing model: Reserved/Savings Plans for steady-state, Spot for flexible
  3. Storage optimization: Right storage class, lifecycle policies
  4. Data transfer: Minimize cross-AZ, cross-region, internet-bound transfers
  5. Turn off unused: Stop dev/test resources after hours

COMMON COST MISTAKES:
  1. Unused Elastic IPs: $0.005/hour when not attached (~$3.60/month each)
  2. Idle NAT Gateways: $0.045/hour + $0.045/GB processed
  3. Unattached EBS volumes: Pay even when no instance uses them
  4. Old EBS snapshots: Pay for storage. Automate cleanup with Data Lifecycle Manager.
  5. Cross-AZ data transfer: $0.01/GB each way. Huge at scale.
     (e.g., EC2 in AZ-a reading from EBS in AZ-b — always keep data in same AZ)
  6. CloudWatch Logs retention: Default = never expire. Set retention!
  7. GuardDuty: Charged by data analyzed. Can be expensive in data-heavy accounts.

INTERVIEW QUESTION 14-A (Data Transfer Costs):
  "Your EKS cluster has services in multiple AZs. What are the network cost
   implications of east-west traffic (pod-to-pod in different AZs)?"
  ANSWER: $0.01/GB each direction = $0.02/GB for round trip.
  At 10TB/month of cross-AZ traffic: $200/month just in data transfer!
  
  Solutions:
  1. Topology Aware Routing: K8s routes to pods in SAME AZ when possible
  2. Service mesh with locality-aware load balancing (Istio/App Mesh)
  3. Co-locate services that talk frequently in the same AZ
  4. Rearchitect to reduce chatty cross-service calls

INTERVIEW QUESTION 14-B (Reserved vs Savings Plans):
  "Standard Reserved Instance vs Convertible Reserved Instance vs Savings Plans — 
   when do you use each?"
  ANSWER:
  Standard RI: Highest discount (up to 72%). Locked to specific instance type,
  region, OS. Cannot change. Best for stable, predictable workloads.
  
  Convertible RI: Lower discount (up to 54%). Can change instance type, OS,
  tenancy. Best for uncertain future requirements.
  
  Compute Savings Plans: Flexible (EC2, Lambda, Fargate). 
  Discount is for $/hour commitment, not specific instances.
  Good for mixed workloads. Slightly less discount than Standard RI.
  EC2 Savings Plans: Like Compute but locked to instance family + region.
  
  Modern recommendation: Use Compute Savings Plans for flexibility.
  Supplement with Standard RIs only for truly fixed, long-term workloads.

CROSS QUESTION 14-C:
  "Your team develops in AWS. How do you prevent cost overruns in developer
   sandboxes?"
  ANSWER (Multiple layers):
  1. AWS Budgets: Alert + auto-action when spending exceeds threshold
  2. SCPs: Block expensive services/regions for dev accounts
  3. AWS Cost Anomaly Detection: ML-based detection of unexpected cost spikes
  4. Instance Scheduler: Auto-stop EC2/RDS after hours
  5. Service Quotas: Limit max EC2 instances in dev account
  6. Separate dev AWS accounts (AWS Organizations): Isolate dev spend from prod
"""


def cost_optimization_patterns():
    """
    Cost optimization strategies and implementation.
    """
    pricing = boto3.client('pricing', region_name='us-east-1')
    cost_explorer = boto3.client('ce', region_name='us-east-1')
    budgets = boto3.client('budgets', region_name='us-east-1')
    
    # --- AWS Budget with Automatic Action ---
    
    def create_cost_budget_with_action(account_id: str, monthly_budget_usd: float):
        """
        Create a budget that alerts AND automatically applies an SCP
        when spending exceeds threshold.
        
        This prevents accidental cost overruns by STOPPING new resource creation
        when budget is exceeded.
        """
        
        budget_config = {
            'AccountId': account_id,
            'Budget': {
                'BudgetName': 'monthly-cost-limit',
                'BudgetType': 'COST',
                'BudgetLimit': {
                    'Amount': str(monthly_budget_usd),
                    'Unit': 'USD'
                },
                'TimeUnit': 'MONTHLY',
                'CostTypes': {
                    'IncludeTax': True,
                    'IncludeSubscription': True,
                    'UseBlended': False
                }
            },
            'NotificationsWithSubscribers': [
                {
                    'Notification': {
                        'NotificationType': 'ACTUAL',     # Actual vs Forecasted
                        'ComparisonOperator': 'GREATER_THAN',
                        'Threshold': 80,                  # Alert at 80% of budget
                        'ThresholdType': 'PERCENTAGE'
                    },
                    'Subscribers': [
                        {'SubscriptionType': 'EMAIL', 'Address': 'team@company.com'},
                        {'SubscriptionType': 'SNS', 'Address': 'arn:aws:sns:us-east-1:123:budget-alerts'}
                    ]
                },
                {
                    'Notification': {
                        'NotificationType': 'FORECASTED',  # Alert on forecasted overrun
                        'ComparisonOperator': 'GREATER_THAN',
                        'Threshold': 100,
                        'ThresholdType': 'PERCENTAGE'
                    },
                    'Subscribers': [
                        {'SubscriptionType': 'EMAIL', 'Address': 'cto@company.com'}
                    ]
                }
            ]
        }
        
        print("AWS BUDGET CONFIGURATION:")
        print(json.dumps(budget_config, indent=2))
    
    create_cost_budget_with_action('123456789012', 5000.0)
    
    # --- Cost Anomaly Detection ---
    
    anomaly_monitor = {
        "MonitorName": "service-level-anomaly-monitor",
        "MonitorType": "DIMENSIONAL",
        "MonitorDimension": "SERVICE",  # Monitor per AWS service
        "CreationDate": str(datetime.date.today()),
        "AlertSubscriptions": [
            {
                "Threshold": 100,  # Alert if anomaly > $100
                "Frequency": "DAILY",
                "MonitorArnList": ["arn:aws:ce::123:anomalymonitor/xxxxxxxx"],
                "Subscribers": [
                    {
                        "Address": "arn:aws:sns:us-east-1:123:cost-anomaly-alerts",
                        "Type": "SNS"
                    }
                ]
            }
        ]
    }
    
    print("\nCOST ANOMALY DETECTION CONFIGURATION:")
    print(json.dumps(anomaly_monitor, indent=2))
    
    # --- Savings Plans Analysis ---
    
    def analyze_savings_plan_coverage():
        """
        Analyze current compute usage and recommend Savings Plans commitment.
        
        STRATEGY:
        1. Look at last 3 months of EC2/Lambda/Fargate spend
        2. Identify the MINIMUM consistent usage (this is your baseline)
        3. Buy Savings Plans for the baseline (guaranteed commitment)
        4. Cover the rest with On-Demand or Spot
        
        GOTCHA: Don't over-commit to Savings Plans.
        If you commit $1000/hr but only use $800/hr, you pay $200/hr for nothing.
        Better to commit to 80% of expected usage and cover the rest with On-Demand.
        """
        try:
            # Get 3 months of EC2 + Fargate spend
            response = cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': '2024-01-01',
                    'End': '2024-04-01'
                },
                Granularity='MONTHLY',
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Elastic Compute Cloud - Compute',
                                   'AWS Fargate', 'AWS Lambda']
                    }
                },
                Metrics=['UnblendedCost']
            )
            
            print("\nCOST ANALYSIS FOR SAVINGS PLANS RECOMMENDATION:")
            for result in response.get('ResultsByTime', []):
                period = result['TimePeriod']['Start']
                total_cost = result['Total']['UnblendedCost']['Amount']
                print(f"  {period}: ${float(total_cost):.2f}")
                
        except ClientError as e:
            print(f"Cost Explorer Error: {e.response['Error']['Message']}")
            print("Note: Cost Explorer requires activation (free, but 12-24h delay)")


# ================================================================================
# SECTION 15 — ADVANCED ARCHITECTURE PATTERNS & SYSTEM DESIGN
# ================================================================================
"""
CONCEPT: System Design interviews test your ability to architect complete solutions.
AWS-specific system design requires knowing:
  1. Which services to use (and WHY)
  2. How they interact (event-driven vs request/response)
  3. Where the failure points are (and how you handle them)
  4. How it scales (horizontally? what are the bottlenecks?)
  5. How much it costs (rough order of magnitude)

CLASSIC AWS ARCHITECTURE PATTERNS:

PATTERN 1: SYNCHRONOUS WEB APPLICATION
  Internet → Route53 → CloudFront → ALB → EC2/EKS/ECS → 
  RDS Aurora (writes) / ElastiCache Redis (cache) / DynamoDB (sessions)
  
PATTERN 2: ASYNC EVENT-DRIVEN
  API Gateway → Lambda → SQS/SNS → Lambda → DynamoDB/S3/RDS
  
PATTERN 3: DATA LAKE
  Sources → Kinesis Firehose → S3 (raw) → Glue ETL → S3 (curated) → 
  Athena (ad-hoc query) / Redshift (DW) / QuickSight (BI)
  
PATTERN 4: REAL-TIME STREAMING
  Sources → Kinesis Data Streams → Lambda/Flink → DynamoDB/ElasticSearch
  
PATTERN 5: MULTI-REGION ACTIVE-ACTIVE
  Route53 latency-based routing → Regional ALBs → Regional EKS clusters →
  Aurora Global Database (writes to primary, reads from local replica)
  DynamoDB Global Tables (multi-region writes)

INTERVIEW QUESTION 15-A (SYSTEM DESIGN):
  "Design a URL shortener (like bit.ly) on AWS that handles 100M requests/day."
  
  COMPONENTS:
  - Write path: API Gateway → Lambda → DynamoDB (write short→long mapping)
  - Read path (hot path): CloudFront → Lambda@Edge → ElastiCache → DynamoDB
  - Analytics: Kinesis Data Streams → Lambda → S3 → Athena
  
  SCALE: 100M requests/day = ~1157 req/sec average. Peak might be 10x = 11,570 req/sec.
  - CloudFront handles: unlimited (CDN, cached redirects are free-ish)
  - Lambda@Edge: Check ElastiCache first (cache hit = no backend call)
  - ElastiCache Redis: ~100k req/sec per node in cluster mode
  - DynamoDB: Unlimited with on-demand mode
  
  KEY INSIGHT: For a URL shortener, 80% of clicks go to 20% of URLs.
  Cache the hot URLs in ElastiCache. Cache hit rate ~80% means DynamoDB only
  sees 20% of traffic. DynamoDB at 1157 × 20% = 231 req/sec → trivial.

INTERVIEW QUESTION 15-B (SYSTEM DESIGN):
  "Design a real-time leaderboard for a gaming application with 10M players."
  
  REQUIREMENT: Show top 100 players. Show user's rank. Update in real-time.
  
  SOLUTION: Redis Sorted Sets!
  - ZADD leaderboard <score> <user_id>  → O(log N)
  - ZRANK leaderboard <user_id>          → O(log N) — user's rank
  - ZREVRANGE leaderboard 0 99           → O(log N + 100) — top 100
  
  AWS: ElastiCache Redis (cluster mode for horizontal scale)
  Write path: API → Lambda → ElastiCache (update score) + DynamoDB (persist)
  Read path: API → Lambda → ElastiCache (read rank/leaderboard)
  
  SCALE: 10M players × 1 update/minute = 166,667 writes/sec.
  Redis can handle ~1M ops/sec. Need sharding: partition by game_id.

INTERVIEW QUESTION 15-C (DISASTER RECOVERY):
  "Define RTO and RPO. How would you architect for RTO=1min and RPO=5sec?"
  
  RTO (Recovery Time Objective): How long until service is restored after failure.
  RPO (Recovery Point Objective): How much data can we afford to lose.
  
  RTO=1min, RPO=5sec is VERY aggressive. Requirements:
  
  - Multi-Region Active-Active (not Active-Passive!)
  - Aurora Global Database: <1 second replication lag → RPO <5sec
  - DynamoDB Global Tables: Multi-master writes in every region
  - Route 53 health checks: Failover in 60 seconds
  - No data migration needed (active-active means data is in all regions)
  
  Cost: Very expensive! Active-active means running FULL capacity in every region.
  Typical: 2 regions = 2x compute cost + cross-region data transfer cost.
  
  For RTO=5min, RPO=1min: Active-Passive with hot standby. 
  Much cheaper. Standby has reduced capacity (can scale up during failover).

INTERVIEW QUESTION 15-D (ARCHITECTURE TRADEOFFS):
  "When would you choose Kinesis Data Streams vs SQS for stream processing?"
  
  KINESIS DATA STREAMS:
  - Ordered within a shard
  - Multiple consumers can read the SAME data independently
  - Data retained for 24 hours (up to 365 days with extended retention)
  - Consumers can replay data
  - Shards: capacity planning required (1MB/s in, 2MB/s out per shard)
  - KCL (Kinesis Client Library) handles complex consumer scenarios
  
  SQS:
  - NOT ordered (Standard). FIFO ordered per message group.
  - One consumer per message (competing consumers)
  - No replay after deletion
  - Effectively unlimited throughput (Standard)
  - Simpler: just poll and process
  
  CHOOSE KINESIS: Multiple teams need to independently process the same events.
  Event replay is needed. Strict ordering matters. Long retention needed.
  
  CHOOSE SQS: Simple work queue. One consumer. Higher throughput needed.
  Fire-and-forget processing. No replay needed. FIFO for simple ordering.
"""


def advanced_architecture_patterns():
    """
    Production architecture patterns with cross-service integration.
    """
    
    # --- PATTERN: Event-Driven Microservices ---
    
    event_driven_architecture = {
        "pattern": "Event-Driven Order Processing System",
        "components": {
            "api_layer": {
                "service": "API Gateway REST API",
                "auth": "Cognito User Pools JWT",
                "throttling": "10,000 req/s burst, 2,000 req/s steady"
            },
            "order_service": {
                "compute": "Lambda (Node.js, 512MB, 30s timeout)",
                "store": "DynamoDB (single-table design, on-demand)",
                "events_out": "EventBridge custom bus"
            },
            "notification_service": {
                "trigger": "EventBridge rule: order_placed",
                "compute": "Lambda",
                "channels": ["SES (email)", "SNS SMS", "Pinpoint (push)"]
            },
            "inventory_service": {
                "trigger": "EventBridge rule: order_placed",
                "compute": "ECS Fargate",
                "store": "Aurora PostgreSQL"
            },
            "analytics_service": {
                "trigger": "DynamoDB Streams → Kinesis Firehose",
                "destination": "S3 → Glue → Redshift",
                "query": "Athena for ad-hoc, QuickSight for dashboards"
            }
        },
        "failure_handling": {
            "eventbridge_retry": "Automatic retry with exponential backoff",
            "dlq": "All SQS queues have DLQ + CloudWatch alarm on DLQ depth",
            "idempotency": "Idempotency key on DynamoDB PutItem with ConditionExpression",
            "circuit_breaker": "Step Functions for sagas with compensation logic"
        },
        "scaling": {
            "lambda": "Auto scales to account concurrency limit (1000 default)",
            "dynamodb": "On-demand mode, no capacity planning",
            "eventbridge": "Virtually unlimited events",
            "aurora": "Serverless v2, 0.5-128 ACU"
        }
    }
    
    print("EVENT-DRIVEN ARCHITECTURE DESIGN:")
    print(json.dumps(event_driven_architecture, indent=2))
    
    # --- PATTERN: Multi-Region Active-Active ---
    
    multi_region_pattern = {
        "pattern": "Multi-Region Active-Active for e-commerce",
        "regions": ["us-east-1 (primary)", "eu-west-1 (secondary)", "ap-southeast-1 (tertiary)"],
        
        "routing": {
            "service": "Route 53",
            "policy": "Latency-based routing",
            "health_checks": "Every 10s from multiple locations",
            "failover_time": "< 60 seconds"
        },
        
        "data_layer": {
            "user_sessions": {
                "service": "DynamoDB Global Tables",
                "replication": "Multi-master, asynchronous",
                "conflict_resolution": "Last-write-wins (timestamp)"
            },
            "product_catalog": {
                "service": "Aurora Global Database (PostgreSQL)",
                "replication": "1 primary (us-east-1), 2 replicas (eu, apac)",
                "lag": "< 1 second",
                "writes": "Only to primary",
                "reads": "From local replica"
            },
            "session_cache": {
                "service": "ElastiCache Redis (Global Datastore)",
                "replication": "Primary with replicas in each region"
            }
        },
        
        "write_path_for_orders": [
            "1. Request hits regional ALB",
            "2. Order service writes to DynamoDB Global Tables (local region)",
            "3. DynamoDB replicates asynchronously to all regions",
            "4. Order confirmed to user (eventual consistency acceptable)",
            "Note: For strict consistency (inventory), route writes to primary region"
        ],
        
        "estimated_cost_vs_single_region": "2.5-3x (3 regions = 3x compute + cross-region transfer)"
    }
    
    print("\nMULTI-REGION ACTIVE-ACTIVE PATTERN:")
    print(json.dumps(multi_region_pattern, indent=2))


# ================================================================================
# ADVANCED CROSS-CUTTING INTERVIEW QUESTIONS
# ================================================================================
"""
These questions span multiple AWS services and test SYSTEM-LEVEL thinking.
These are the questions that separate senior from staff-level candidates.

MEGA QUESTION 1: "EXPLAIN AWS BOOT SEQUENCE"
  When an EC2 instance launches:
  1. VPC: DHCP assigns IP from subnet CIDR
  2. IAM: Instance profile credentials are made available via IMDS
  3. EBS: Root volume is attached
  4. Hypervisor: Boots the OS
  5. cloud-init: Reads instance metadata, sets hostname, SSH keys
  6. User Data: Runs your bootstrap script
  7. EC2 Health Check: Instance status checks (System + Instance checks pass)
  8. ASG: If in Auto Scaling Group, lifecycle hook WAIT may fire
  9. ELB: Instance registered with target group, health checks begin
  10. Ready: Traffic flows

MEGA QUESTION 2: "REQUEST FLOW THROUGH AWS"
  User types https://myapp.com → what happens?

  1. Browser: DNS lookup for myapp.com
  2. Route 53 Resolver: Returns IP (CloudFront or ALB IP)
  3. CloudFront: Check edge cache. Hit → return immediately.
  4. CloudFront → ALB: If cache miss, forward to ALB in origin region
  5. ALB: TLS termination, host-based routing, chooses target
  6. Target Group: Round-robin to ECS task IP
  7. ECS Task: App code runs, needs data
  8. App → RDS Proxy: Connection pooled request to Aurora
  9. Aurora: Query executed, result returned
  10. App → ElastiCache: Cache hit for frequently accessed data
  11. App → S3: Get static assets, pre-signed URL generation
  12. Response: Travels back through the stack
  
  Each hop has: latency implications, failure modes, scaling characteristics.

MEGA QUESTION 3: "HOW DOES AWS ACHIEVE 11 NINES DURABILITY FOR S3?"
  - Data stored across minimum 3 AZs
  - Each AZ has multiple storage nodes
  - Data is erasure-coded (Reed-Solomon) — can reconstruct data from partial nodes
  - Continuous integrity checks (CRC32 on write, periodic background scrubbing)
  - Data is never just 3 copies — it's distributed fragments
  - 11 nines = 99.999999999% durability
  - What does this mean? For 10 million objects, expect to lose 1 object every 10,000 years!

MEGA QUESTION 4: "AURORA STORAGE ARCHITECTURE"
  - No EBS. Storage is a distributed shared log system.
  - Data stored as 10GB segments across 6 storage nodes (2 per AZ, 3 AZs)
  - Only REDO LOG is sent from DB instance to storage layer (not pages!)
  - Storage applies log records to materialize pages on demand
  - Read replicas share SAME storage layer — no replication of data!
    Read replicas just cache pages from the shared storage.
  - This is why Aurora is 5x faster than MySQL for read replicas:
    Traditional MySQL replicates ALL changes to replica.
    Aurora replica just refreshes its cache from shared storage.
  - Backup: Continuous, no performance impact, point-in-time down to 1 second.

MEGA QUESTION 5: "LAMBDA COLD START UNDER THE HOOD"
  When Lambda needs a new execution environment:
  1. AWS allocates a micro-VM (Firecracker — MicroVM, not Docker!)
  2. Downloads your deployment package from S3 (or uses pre-warmed Provisioned Concurrency)
  3. Bootstraps the Lambda runtime (Python/Node/Java process starts)
  4. Runs your INIT phase (module-level code: imports, global vars, DB connections)
  5. Calls your handler
  
  Firecracker: AWS's open-source MicroVM. Boots in 125ms. More secure than traditional VMs.
  Isolation between customers: Each Lambda uses its own MicroVM.
  
  WHY COLD STARTS MATTER: API serving latency = max(app latency, cold start latency).
  A p95 API at 50ms + cold start at 2000ms = p95 2050ms (terrible UX).
  Solutions: Provisioned Concurrency, warm-up requests, architecture changes.
"""


def run_all_sections():
    """
    Master runner that demonstrates all AWS learning sections.
    NOTE: Most code examples are for educational reference.
    Run in an AWS account with appropriate permissions.
    """
    print("=" * 80)
    print("AWS DEEP LEARNING PATH — Advanced Interview Preparation")
    print("=" * 80)
    
    sections = [
        ("01 — GLOBAL INFRASTRUCTURE", list_aws_regions_and_az),
        ("02 — IAM CONCEPTS", demonstrate_iam_concepts),
        ("02b— IAM ROLES", demonstrate_iam_roles_programmatic),
        ("03 — EC2 DEEP DIVE", ec2_deep_dive),
        ("03b— AUTO SCALING", ec2_auto_scaling_deep_dive),
        ("04 — S3 DEEP DIVE", s3_deep_dive),
        ("04b— S3 MULTIPART", s3_multipart_upload_pattern),
        ("05 — VPC NETWORKING", vpc_deep_dive),
        ("06 — RDS & AURORA", rds_deep_dive),
        ("07 — DYNAMODB", dynamodb_deep_dive),
        ("08 — LAMBDA", lambda_deep_dive),
        ("09 — MESSAGING", messaging_deep_dive),
        ("10 — CONTAINERS", container_orchestration_deep_dive),
        ("11 — IaC (CFN+CDK)", cloudformation_deep_dive),
        ("12 — OBSERVABILITY", observability_deep_dive),
        ("13 — SECURITY", security_deep_dive),
        ("14 — COST OPTIMIZATION", cost_optimization_patterns),
        ("15 — ARCHITECTURE", advanced_architecture_patterns),
    ]
    
    for section_name, func in sections:
        print(f"\n{'='*80}")
        print(f"SECTION: {section_name}")
        print(f"{'='*80}")
        try:
            func()
        except Exception as e:
            print(f"[Demo mode — would need AWS credentials to run: {type(e).__name__}]")
        print()


# ================================================================================
# QUICK REFERENCE: MOST CRITICAL INTERVIEW ANSWERS
# ================================================================================

CRITICAL_FACTS = {
    "S3 Consistency": "Strongly consistent since December 2020",
    "S3 Durability": "11 9s (99.999999999%) across minimum 3 AZs",
    "S3 Request Rate": "3,500 PUT/s and 5,500 GET/s per prefix (partition by prefix to scale)",
    "Lambda Max Timeout": "900 seconds (15 minutes)",
    "Lambda Max Memory": "10,240 MB (10 GB)",
    "Lambda Concurrency Default": "1,000 per region (soft limit, can increase)",
    "DynamoDB Item Size Limit": "400 KB per item",
    "DynamoDB Consistency": "Eventually consistent by default. Strongly consistent reads available at 2x cost",
    "SQS Max Message Size": "256 KB (use S3 + SQS pointer for larger payloads)",
    "SQS Max Retention": "14 days",
    "SQS Visibility Timeout": "Default 30s, Max 12 hours. Set to 6x Lambda timeout.",
    "SNS Max Message Size": "256 KB",
    "RDS Multi-AZ Failover": "~60-120 seconds (synchronous standby)",
    "Aurora Failover": "~30 seconds (typically faster than RDS Multi-AZ)",
    "Aurora Replicas": "Up to 15 read replicas (vs 5 for standard RDS)",
    "CloudFront Origins": "S3, ALB, EC2, MediaStore, HTTP custom origins",
    "CloudFront Price Classes": "All, 100 (NA+EU), 200 (NA+EU+Asia+Africa+ME)",
    "Route53 Health Check": "Every 10s (fast) or 30s (standard). 18+ global health checkers.",
    "KMS Key Rotation": "Annual automatic rotation for CMKs (cannot change rotation period for AWS Managed Keys)",
    "Secrets Manager Max Secret Size": "65,536 bytes",
    "IAM Policy Max Size": "2,048 characters for inline, 6,144 for managed",
    "VPC Limits": "5 VPCs per region (default), 200 subnets per VPC",
    "EC2 Spot Interruption Notice": "2 minutes before termination",
    "EBS GP3 vs GP2": "GP3: 3,000 IOPS baseline (free), configurable. GP2: 3 IOPS/GB, bursts to 3,000.",
    "EBS Max IOPS": "256,000 IOPS (io2 Block Express)",
    "EKS Control Plane Cost": "$0.10/hour per cluster",
    "Fargate Pricing": "Per vCPU-second and GB-second",
}

def print_quick_reference():
    """Print all critical facts for last-minute interview review."""
    print("\n" + "=" * 80)
    print("QUICK REFERENCE — CRITICAL FACTS FOR INTERVIEWS")
    print("=" * 80)
    
    for fact, value in CRITICAL_FACTS.items():
        print(f"\n📌 {fact}:")
        print(f"   {value}")


# ================================================================================
# STUDY SCHEDULE RECOMMENDATION
# ================================================================================

STUDY_SCHEDULE = """
RECOMMENDED 30-DAY STUDY SCHEDULE FOR SENIOR AWS INTERVIEWS:

WEEK 1 — CORE SERVICES FOUNDATION:
  Day 01: IAM (trust policies, SCPs, permission boundaries, evaluation order)
  Day 02: VPC (subnets, routing, security groups, NACLs, endpoints)
  Day 03: EC2 (instance types, purchasing, Auto Scaling, user data)
  Day 04: S3 (storage classes, security, performance, events)
  Day 05: RDS & Aurora (Multi-AZ, read replicas, Aurora architecture)
  Day 06: DynamoDB (data modeling, GSIs, transactions, streams)
  Day 07: Practice SYSTEM DESIGN with above services

WEEK 2 — COMPUTE & INTEGRATION:
  Day 08: Lambda (concurrency, cold starts, invocation models, VPC)
  Day 09: ECS & Fargate (task definitions, services, deployment)
  Day 10: EKS (node groups, Fargate profiles, networking, Karpenter)
  Day 11: SQS & SNS (patterns, visibility timeout, FIFO, fan-out)
  Day 12: EventBridge (rules, schemas, cross-account, replay)
  Day 13: API Gateway (REST vs HTTP, Lambda integration, caching)
  Day 14: Practice microservices SYSTEM DESIGN

WEEK 3 — OPERATIONS & SECURITY:
  Day 15: CloudFormation (stacks, nested stacks, drift, rollback)
  Day 16: CDK (constructs, aspects, context, testing)
  Day 17: CloudWatch (metrics, logs, alarms, Insights, Synthetics)
  Day 18: X-Ray (tracing, service maps, sampling rules)
  Day 19: KMS (key types, policies, envelope encryption, rotation)
  Day 20: Secrets Manager (rotation, caching, cross-region)
  Day 21: GuardDuty, Security Hub, Config, CloudTrail (security operations)

WEEK 4 — ADVANCED & ARCHITECTURE:
  Day 22: Cost Optimization (Savings Plans, Spot, Right-sizing, Budgets)
  Day 23: Multi-Region architecture (Global Tables, Aurora Global, Route 53)
  Day 24: Kinesis (Data Streams vs Firehose, shards, KCL)
  Day 25: Data & Analytics (Glue, Athena, Redshift, QuickSight)
  Day 26: Machine Learning services (SageMaker basics, Bedrock, Rekognition)
  Day 27: Step Functions (workflows, error handling, patterns)
  Day 28: Full SYSTEM DESIGN practice (design Instagram at scale)
  Day 29: Mock interview — answer all questions in this file aloud
  Day 30: Review critical facts, relax, you're ready!
"""

print(STUDY_SCHEDULE)


# ================================================================================
# ENTRY POINT
# ================================================================================

if __name__ == "__main__":
    print(__doc__)
    print_quick_reference()
    
    print("\n" + "=" * 80)
    print("To run all sections: call run_all_sections()")
    print("Note: Requires AWS credentials (aws configure) to execute live code")
    print("=" * 80)
    
    # Uncomment to run all sections:
    # run_all_sections()
    
    print("\n✅ AWS Deep Learning Path loaded successfully!")
    print("📚 Start with Section 01 and work through sequentially.")
    print("❓ Answer every INTERVIEW QUESTION before reading the HINT.")
    print("🔗 Pay special attention to CROSS QUESTIONS — they're the hardest.")
