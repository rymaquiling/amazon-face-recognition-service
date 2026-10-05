from __future__ import print_function

import boto3
import json
import urllib.parse

print('Loading function')

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')


# --------------- Helper Functions ------------------

def index_faces(bucket, key):
    response = rekognition.index_faces(
        Image={
            "S3Object": {
                "Bucket": bucket,
                "Name": key
            }
        },
        CollectionId="face_collection_<YourInitials>"
    )
    return response


def update_index(tableName, faceId, fullName):
    response = dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FullName': {'S': fullName}
        }
    )
    return response


# --------------- Main Handler ------------------

def lambda_handler(event, context):
    # Extract Bucket and Key from event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # URL-decode the key (e.g. converts 'index%2Fimage1.jpg' to 'index/image1.jpg')
    key = urllib.parse.unquote_plus(key)

    print("Records:", event['Records'])
    print("Processing Key:", key)

    try:
        # Index faces in Rekognition
        response = index_faces(bucket, key)

        # Verify indexing succeeded and a face was found
        if response['ResponseMetadata']['HTTPStatusCode'] == 200 and len(response['FaceRecords']) > 0:
            faceId = response['FaceRecords'][0]['Face']['FaceId']

            # Get metadata from S3 object
            ret = s3.head_object(Bucket=bucket, Key=key)
            personFullName = ret['Metadata'].get('fullname') or ret['Metadata'].get('FullName') or 'Unknown'

            # Store in DynamoDB
            update_index('face_table_<YourInitials>', faceId, personFullName)
            print("Successfully saved to DynamoDB:", faceId, "->", personFullName)

        print(response)
        return response

    except Exception as e:
        print(e)
        print("Error processing object {} from bucket {}.".format(key, bucket))
        raise e