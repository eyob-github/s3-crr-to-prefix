# SOP: Custom S3 Bucket Replication to Specific Prefix Using Lambda and EventBridge

## Objective  
To replicate objects from the source S3 bucket `<SOURCE_BUCKET>` in account `<SOURCE_ACCOUNT_ID>` to the destination S3 bucket `<DESTINATION_BUCKET>` in another region/account using a scheduled Lambda function triggered by EventBridge.  
Since AWS native S3 replication does not support replication to a specific prefix (folder), this functionality is achieved through a Lambda function, enabling replication at the folder level.

---

## Prerequisites  
- AWS CLI access to relevant accounts  
- IAM permissions to create/update Lambda functions, roles, policies, and EventBridge rules  
- Source and destination S3 buckets created  

---

## Components  

| Component            | Description                                         |
|---------------------|-----------------------------------------------------|
| Lambda Function     | Copies new or modified files from source to destination bucket.  |
| IAM Role for Lambda | Grants Lambda permissions to list/read source bucket and write destination bucket. |
| EventBridge Rule    | Scheduled trigger that invokes Lambda at defined intervals.      |
| Destination Bucket Policy | Allows Lambda role from source account to put objects.       |

---

## Procedure  

### 1. Configure IAM Role for Lambda (Source Account)  
- Attach bucket policy with permissions to allow Lambda to put objects in the destination bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowLambdaPutObject",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<SOURCE_ACCOUNT_ID>:role/<LAMBDA_EXECUTION_ROLE>"
      },
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::<DESTINATION_BUCKET>/*"
    }
  ]
}
```
### 2. Configure Destination Bucket Policy (Destination Account)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowLambdaPutObject",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<SOURCE_ACCOUNT_ID>:role/<LAMBDA_EXECUTION_ROLE>"
      },
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::<DESTINATION_BUCKET>/*"
    }
  ]
}
```
### 3 Deploy Lambda Function
- Set the following environment variable in the Lambda function
| Variab              | Value                                         |
|---------------------|-----------------------------------------------------|
| DESTINATION_BUCKET    | <DESTINATION_BUCKET>  |
| DESTINATION_REGION  | (destination bucket region) |
| DESTINATION_PREFIX    | <DESTINATION_PREFIX>      |
| PREFIX_FILTER       | (optional, e.g., folder1/)       |
- Ensure Lambda execution role is set to <LAMBDA_EXECUTION_ROLE>.
- Deploy the latest Lambda code that lists source objects and copies recent files based on the prefix filter.

### 4. Create EventBridge Rule
- Schedule Lambda Invocation (e.g., event hour)
  - Go to EventBridge → Rules → Create rule → Schedule → Fixed rate or Cron.
  - Set the target as the Lambda Function <LAMBDA_FUNCTION_NAME>.
- Add permission to Lambda for EventBridge invocation if required:
```bash
  aws lambda add-permission \
  --function-name <LAMBDA_FUNCTION_NAME> \
  --statement-id eventbridge-invoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:<REGION>:<SOURCE_ACCOUNT_ID>:rule/<RULE_NAME>
```
### 5 Testing and Verification
- Upload test files to the source bucket under the specified prefix.
- Check Lambda log in CloudWatch for successful copy operations
- Verify that the files appear in the destination bucket with the correct prefix
### 6 Maintenance
- Monitor Lambda CloudWatch metrics for error and duration
- Adjust the Lambda schedule, memory, or timeout setting based on workload requirements
- Periodically review IAM policies to ensure the list privilege compliance

```pgsql

---

Just replace the placeholders (e.g., `<SOURCE_ACCOUNT_ID>`, `<DESTINATION_BUCKET>`, etc.) with your actual values only in your secure internal copy; never commit real sensitive data to public repos.  

```
