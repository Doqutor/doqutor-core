import os
import logging
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
FILE_NAME = 'demo.txt'


def create_file():
    """Create a file called "demo.txt"
    """
    f = open(FILE_NAME, "w")
    f.write("Hello, I am a hacker")
    f.close()


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    try:
        response = s3.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def main_program():

    # get buckets
    response = s3.list_buckets()

    for bucket in response['Buckets']:

        # filter bucket names
        if 'frontend' in bucket["Name"]:
            print(f'Uploading {FILE_NAME} in bucket: {bucket["Name"]}')

            # creating demo file
            create_file()

            # upload file to S3
            if upload_file(FILE_NAME, bucket['Name']):
                print('File uploaded')
            break
        else:
            print('Could not find S3 BUCKET, exiting!')

    # clean up
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)


if __name__ == '__main__':
    main_program()