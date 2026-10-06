import boto3
import io
from PIL import Image

rekognition = boto3.client('rekognition', region_name='ap-southeast-1')
dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1')

image_path = input("Enter path of the image to check: ")

image = Image.open(image_path)
stream = io.BytesIO()
image.save(stream, format="JPEG")
image_binary = stream.getvalue()

response = rekognition.search_faces_by_image(
    CollectionId='face_collection_<YourInitials>',
    Image={'Bytes': image_binary}                                       
)

found = False
for match in response['FaceMatches']:
    face_id = match['Face']['FaceId']
    confidence = match['Face']['Confidence']
        
    face = dynamodb.get_item(
        TableName='face_table_<YourInitials>',  
        Key={'RekognitionId': {'S': face_id}}
    )
    
    if 'Item' in face:
        person_name = face['Item']['FullName']['S']
        print(f"Faceprint: {face_id}")
        print(f"Confidence Level: {confidence}")
        print(f"Found Person: {person_name}")
        found = True

if not found:
    print("Person cannot be recognized")