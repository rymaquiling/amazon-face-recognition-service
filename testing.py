import os
import platform

os.environ["OPENCV_LOG_LEVEL"] = "OFF"  # hide OpenCV warnings while we search for cameras

import boto3
import cv2

rekognition = boto3.client('rekognition', region_name='ap-southeast-1')
dynamodb = boto3.client('dynamodb', region_name='ap-southeast-1')

# Each OS has its own camera driver. Picking it ourselves avoids slow or failing defaults.
if platform.system() == 'Windows':
    BACKEND = cv2.CAP_DSHOW
elif platform.system() == 'Darwin':  # macOS
    BACKEND = cv2.CAP_AVFOUNDATION
else:  # Linux
    BACKEND = cv2.CAP_V4L2

MAX_CAMERAS = 5  # how many camera slots to check


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


def is_working(camera):
    """A real webcam gives frames that are not black and keep changing.
    Fake cameras (e.g. OBS Virtual Camera when OBS is closed) show a black or frozen image."""
    for _ in range(10):  # skip the first frames, they are dark while the camera warms up
        camera.read()
    ok1, frame1 = camera.read()
    for _ in range(5):
        camera.read()
    ok2, frame2 = camera.read()

    if not (ok1 and ok2):
        return False
    is_black = frame2.mean() < 10
    is_frozen = cv2.absdiff(frame1, frame2).mean() == 0
    return not is_black and not is_frozen


def open_camera(start_index=0):
    """Try each camera slot, starting at start_index, and return the first one that works."""
    for i in range(MAX_CAMERAS):
        index = (start_index + i) % MAX_CAMERAS
        camera = cv2.VideoCapture(index, BACKEND)
        if camera.isOpened() and is_working(camera):
            print(f"Using camera {index}")
            return camera, index
        camera.release()

    raise SystemExit(
        "No working camera found. Check that:\n"
        "- No other app is using the camera (Zoom, Teams, browser, OBS)\n"
        "- The camera privacy shutter or camera on/off key is not blocking it\n"
        "- Python is allowed to use the camera:\n"
        "    Windows: Settings > Privacy & security > Camera > allow desktop apps\n"
        "    macOS: System Settings > Privacy & Security > Camera > allow Terminal/VS Code, then restart it"
    )


camera, camera_index = open_camera()
label = "SPACE: recognize, C: switch camera, Q: quit"

try:
    while True:
        ok, frame = camera.read()
        if not ok:
            # Camera was unplugged or taken by another app: reconnect instead of quitting
            print("Lost the camera, reconnecting...")
            camera.release()
            camera, camera_index = open_camera(camera_index)
            continue

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
        elif key == ord('c'):
            # Wrong camera picked (e.g. phone or virtual camera)? Switch to the next one
            camera.release()
            camera, camera_index = open_camera(camera_index + 1)
        elif key == ord('q'):
            break
finally:
    # Always free the camera, even after an error or Ctrl+C, so it is not left locked
    camera.release()
    cv2.destroyAllWindows()
