from botocore.exceptions import ClientError
from config import settings
import boto3, logging, os

def s3():
    return boto3.client(
        service_name='s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

def s3_upload(file, bucket=settings.AWS_STORAGE_BUCKET_NAME, object_name=None, aws_location=None):
    """Upload a file to an S3 bucket

    :param file: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file is used
    :return: True if file was uploaded, else False
    """


    # If S3 object_name was not specified, use file
    if object_name is None:
        object_name = os.path.basename(file.filename)

        # print(object_name)

    # return

    # Upload the file
    s3_client = s3()
    # print(s3_client.upload_file.__annotations__)
    # return
    try:
        # response = s3_client.upload_file(Fileobj=file, bucket_name=bucket)
        f = file.file.read()
        # response = s3_client.upload_fileobj(f, bucket, object_name)
        with open(file.file.read(), "rb") as f:
            response = s3_client.upload_fileobj(f, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True

    # Fileobj=obj, Key=file_path,ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})

# async def s3_upload(file, aws_location):
#     '''
#     upload file to specified bucket location and return url
#     '''
#     pass


# def upload_file_to_bucket(s3_client, file_obj, bucket, folder, object_name=None):
#     """Upload a file to an S3 bucket

#     :param s3_client: S3 Client
#     :param file_obj: File to upload
#     :param bucket: Bucket to upload to
#     :param folder: Folder to upload to
#     :param object_name: S3 object name. If not specified then file is used
#     :return: True if file was uploaded, else False
#     """
#     # If S3 object_name was not specified, use file
#     if object_name is None:
#         object_name = file_obj

#     # Upload the file
#     try:
#         # with open("files", "rb") as f:
#         s3_client.upload_fileobj(file_obj, bucket, f"{folder}/{object_name}")
#     except ClientError as e:
#         logging.error(e)
#         return False
#     return True


# content_type = mimetypes.guess_type(fpath)[0]
# s3.Bucket(bucket_name).upload_fileobj(Fileobj=file, Key=file_path,
#                                           ExtraArgs={"ACL": "public-read",
#                                                      "ContentType": content_type})

# def s3_upload(self, file, file_path, bucket_name, width=None, height=None, make_thumb=False, make_cover=False):
#     s3 = boto3.resource(service_name='s3')
#     obj = BytesIO(self.image_optimize_from_buffer(file, width, height, make_thumb, make_cover))
#     s3.Bucket(bucket_name).upload_fileobj(Fileobj=obj, Key=file_path,
#                                           ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})
#     return f'https://{bucket_name}.s3.amazonaws.com/{file_path}'

