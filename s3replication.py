import boto3
import botocore
import os
import logging
from boto3.s3.transfer import TransferConfig
from datetime import datetime, timezone, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SOURCE_BUCKET = os.environ.get('SOURCE_BUCKET')
DESTINATION_BUCKET = os.environ.get('DESTINATION_BUCKET')
DESTINATION_REGION = os.environ.get('DESTINATION_REGION')
DESTINATION_PREFIX = os.environ.get('DESTINATION_PREFIX', '')
PREFIX_FILTER = os.environ.get('PREFIX_FILTER', '')

GB = 1024 ** 3
transfer_config = TransferConfig(
    multipart_threshold=5 * GB,
    multipart_chunksize=100 * 1024 * 1024,
    max_concurrency=10,
    use_threads=True
)

s3_client_dest = boto3.client('s3', region_name=DESTINATION_REGION)
s3_client_source = boto3.client('s3')

def lambda_handler(event, context):
    logger.info("Scheduled replication started.")

    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

    paginator = s3_client_source.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=SOURCE_BUCKET)

    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            last_modified = obj['LastModified']

            if PREFIX_FILTER and not key.startswith(PREFIX_FILTER):
                continue

            if last_modified < one_hour_ago:
                continue

            destination_key = f"{DESTINATION_PREFIX}{key}"

            logger.info(f"Copying {key} to {DESTINATION_BUCKET}/{destination_key}")

            try:
                s3_client_dest.copy(
                    {'Bucket': SOURCE_BUCKET, 'Key': key},
                    DESTINATION_BUCKET,
                    destination_key,
                    Config=transfer_config
                )
                logger.info(f"Copied {key} successfully.")
            except botocore.exceptions.ClientError as e:
                logger.error(f"ClientError copying {key}: {e}")
            except botocore.exceptions.ParamValidationError as e:
                logger.error(f"ParamValidationError copying {key}: {e}")

    logger.info("Scheduled replication completed.")
    return {"status": "completed"}
