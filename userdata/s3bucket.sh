
# copies contents of S3 bucket & puts bucket name as an environment variable
# jq is required for this operation
yum install jq -y
BUCKET_NAME=$(aws ssm get-parameter --name /cdk-deploy-ec2/s3bucketname --region eu-west-1 | jq -r '.Parameter.Value')
echo "export BUCKET_NAME=${BUCKET_NAME}" >> /home/ec2-user/.bashrc 
mkdir /home/ec2-user/data && aws s3 cp --recursive s3://${BUCKET_NAME} /home/ec2-user/data && chown -R ec2-user:ec2-user /home/ec2-user/*

