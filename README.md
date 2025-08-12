# SOP: Custom S3 Bucket Replication to Specific Prefix Using Lambda and EventBridge

## Objective  
To replicate objects from the source S3 bucket `<SOURCE_BUCKET>` in account `<SOURCE_ACCOUNT_ID>` to the destination S3 bucket `<DESTINATION_BUCKET>` in another region/account using a scheduled Lambda function triggered by EventBridge.  
Since AWS native S3 replication does not support replication to a specific prefix (folder), this functionality is achieved through a Lambda function enabling replication at the folder level.

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
