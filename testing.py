import boto3
import cv2

rekognition = boto3.client('rekognition', region_name='ap-southeast-1')
dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1')


def recognize(image_binary):
    try:
        response = rekognition.search_faces_by_image(
            CollectionId='face-collection-<YourInitials>',
            Image={'Bytes': image_binary},
            FaceMatchThreshold=80
        )
    except rekognition.exceptions.InvalidParameterException:
        # Raised when no face is detected in the frame
        return None

    for match in response['FaceMatches']:
        face_id = match['Face']['FaceId']
        similarity = match['Similarity']

        face = dynamodb.get_item(
            TableName='face-table-<YourInitials>',
            Key={'RekognitionId': {'S': face_id}}
        )

        if 'Item' in face:
            person_name = face['Item']['FullName']['S']
            print(f"Faceprint: {face_id}")
            print(f"Similarity: {similarity}")
            print(f"Found Person: {person_name}\n")
            return f"{person_name} ({similarity:.1f}%)"

    print("Person cannot be recognized\n")
    return "Person cannot be recognized"


camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise SystemExit("Could not open camera")

label = "Press SPACE to recognize, Q to quit"

while True:
    ok, frame = camera.read()
    if not ok:
        print("Failed to read from camera")
        break

    display = frame.copy()
    cv2.putText(display, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Face Recognition", display)

    key = cv2.waitKey(1) & 0xFF
    if key == ord(' '):
        _, buffer = cv2.imencode('.jpg', frame)
        result = recognize(buffer.tobytes())
        if result is None:
            print("No face detected\n")
            label = "No face detected"
        else:
            label = result
    elif key == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
