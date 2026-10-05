import boto3

s3 = boto3.resource('s3')

# Get list of objects for indexing
images=[('image1.jpg','Elon Musk'),
      ('image2.jpg','Elon Musk'),
      ('image3.jpg','Bill Gates'),
      ('image4.jpg','Bill Gates'),
      ('image5.jpg','Taylor Swift'),
      ('image6.jpg','Taylor Swift'),
      ('mypic1.jpg','Ryan Maquiling'),
      ('mypic2.jpg','Ryan Maquiling'),
      ('<YourPic1.jpg>','<YourName>'), # OPTIONAL
      ('<YourPic2.jpg>','<YourName>') # OPTIONAL
      ]

# Iterate through list to upload objects to S3   
for image in images:
    file = open(image[0],'rb')
    object = s3.Object('face-bucket-<YourInitials>','index/'+ image[0])
    ret = object.put(Body=file,
                    Metadata={'FullName':image[1]})
