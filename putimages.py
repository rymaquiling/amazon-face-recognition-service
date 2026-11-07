import io
import os

import boto3
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

s3 = boto3.resource('s3')

# Get list of objects for indexing
images=[('image1.jpg','Lebron James'),
      ('image2.png','Lebron James'),
      ('image3.png','Jungkook'),
      ('image4.jpg','Jungkook'),
      ('image5.jpg','Taylor Swift'),
      ('image6.jpg','Taylor Swift'),
      ('image7.jpg','Sabrina Carpenter'),
      ('image8.jpg','Sabrina Carpenter'),
      ('<YourPic1.jpg>','<YourName>'), # CHANGE
      ('<YourPic2.jpg>','<YourName>') # CHANGE
      ]


def read_as_jpeg(path):
    # Rekognition only accepts JPEG/PNG, so convert anything else (e.g. HEIC)
    stream = io.BytesIO()
    Image.open(path).convert('RGB').save(stream, format='JPEG')
    return stream.getvalue()


# Iterate through list to upload objects to S3
for image in images:
    key = 'index/' + os.path.splitext(image[0])[0] + '.jpg'
    # CHANGE
    object = s3.Object('face-bucket-<YourInitials>', key)
    ret = object.put(Body=read_as_jpeg(image[0]),
                    ContentType='image/jpeg',
                    Metadata={'FullName':image[1]})
