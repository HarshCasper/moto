from random import randint
from unittest import SkipTest

import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws, settings
from moto.textract.models import TextractBackend

# See our Development Tips on writing tests for hints on how to write good tests:
# http://docs.getmoto.org/en/latest/docs/contributing/development_tips/tests.html


@mock_aws
def test_get_document_text_detection():
    if settings.TEST_SERVER_MODE:
        raise SkipTest("Cannot set textract backend values in server mode")

    TextractBackend.JOB_STATUS = "SUCCEEDED"
    TextractBackend.PAGES = randint(5, 500)
    TextractBackend.BLOCKS = [
        {
            "Text": "This is a test",
            "Id": "0",
            "Confidence": "100",
            "Geometry": {
                "BoundingBox": {
                    "Width": "0.5",
                    "Height": "0.5",
                    "Left": "0.5",
                    "Top": "0.5",
                },
            },
        }
    ]

    client = boto3.client("textract", region_name="us-east-1")
    job = client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": "bucket", "Name": "name"}}
    )

    resp = client.get_document_text_detection(JobId=job["JobId"])

    assert resp["Blocks"][0]["Text"] == "This is a test"
    assert resp["Blocks"][0]["Id"] == "0"
    assert resp["Blocks"][0]["Confidence"] == "100"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Width"] == "0.5"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Height"] == "0.5"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Left"] == "0.5"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Top"] == "0.5"
    assert resp["JobStatus"] == "SUCCEEDED"
    assert resp["DocumentMetadata"]["Pages"] == TextractBackend.PAGES


@mock_aws
def test_start_document_text_detection():
    client = boto3.client("textract", region_name="us-east-1")
    resp = client.start_document_text_detection(
        DocumentLocation={"S3Object": {"Bucket": "bucket", "Name": "name"}}
    )

    assert "JobId" in resp


@mock_aws
def test_get_document_text_detection_without_job_id():
    client = boto3.client("textract", region_name="us-east-1")
    with pytest.raises(ClientError) as e:
        client.get_document_text_detection(JobId="Invalid Job Id")

    assert e.value.response["Error"]["Code"] == "InvalidJobIdException"


@mock_aws
def test_detect_document_text():
    client = boto3.client("textract", region_name="us-east-1")
    result = client.detect_document_text(
        Document={
            "S3Object": {
                "Bucket": "bucket",
                "Name": "name.jpg",
            }
        }
    )
    assert isinstance(result["Blocks"], list)
    assert result["DetectDocumentTextModelVersion"] == "1.0"


@mock_aws
def test_get_document_analysis():
    if settings.TEST_SERVER_MODE:
        raise SkipTest("Cannot set textract backend values in server mode")

    TextractBackend.JOB_STATUS = "SUCCEEDED"
    TextractBackend.PAGES = randint(5, 500)
    TextractBackend.BLOCKS = [
        {
            "Text": "This is a test",
            "Id": "0",
            "Confidence": "100",
            "Geometry": {
                "BoundingBox": {
                    "Width": "0.5",
                    "Height": "0.5",
                    "Left": "0.5",
                    "Top": "0.5",
                },
            },
        }
    ]

    client = boto3.client("textract", region_name="us-east-1")
    job = client.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": "bucket", "Name": "name"}},
        FeatureTypes=["TABLES", "FORMS"],
    )

    resp = client.get_document_analysis(JobId=job["JobId"], MaxResults=1000)

    assert resp["Blocks"][0]["Text"] == "This is a test"
    assert resp["Blocks"][0]["Id"] == "0"
    assert resp["Blocks"][0]["Confidence"] == "100"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Width"] == "0.5"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Height"] == "0.5"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Left"] == "0.5"
    assert resp["Blocks"][0]["Geometry"]["BoundingBox"]["Top"] == "0.5"
    assert resp["JobStatus"] == "SUCCEEDED"
    assert resp["DocumentMetadata"]["Pages"] == TextractBackend.PAGES


@mock_aws
def test_start_document_analysis():
    client = boto3.client("textract", region_name="us-east-1")
    resp = client.start_document_analysis(
        DocumentLocation={"S3Object": {"Bucket": "bucket", "Name": "name"}},
        FeatureTypes=["TABLES", "FORMS"],
        ClientRequestToken="unique-token",
        JobTag="test-job",
        NotificationChannel={
            "SNSTopicArn": "arn:aws:sns:us-east-1:123456789012:AmazonTextractTopic",
            "RoleArn": "arn:aws:iam::123456789012:role/TextractRole",
        },
    )

    assert "JobId" in resp
