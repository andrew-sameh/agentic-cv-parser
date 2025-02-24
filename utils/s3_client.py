# https://github.com/Longdh57/fastapi-minio

from utils.uuid6 import uuid7
from pydantic import BaseModel
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from datetime import datetime, timedelta


class IS3Response(BaseModel):
    bucket_name: str
    file_name: str
    url: str
    # presigned_url: str
    # exp: int | None = None
    is_public: bool


class S3Client:
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        private_bucket_name: str,
        public_bucket_name: str,
        base_folder: str,
        environment: str,
    ):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.private_bucket_name = private_bucket_name
        self.public_bucket_name = public_bucket_name
        self.base_folder = base_folder
        self.environment = environment
        # self.create_buckets(
        #     [(self.private_bucket_name, "private"), (self.public_bucket_name, "public")]
        # )

    def create_buckets(self, bucket_list):
        """
        This method checks if each bucket in the list exists and creates it with the appropriate ACL if not.
        """
        for bucket_name, bucket_type in bucket_list:
            try:
                self.s3.head_bucket(Bucket=bucket_name)
                print(f"Bucket {bucket_name} already exists.")
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    try:
                        # Create a public or private bucket
                        if bucket_type == "public":
                            self.s3.create_bucket(
                                Bucket=bucket_name,
                                CreateBucketConfiguration={
                                    "LocationConstraint": self.s3.meta.region_name
                                },
                                ACL="public-read",  # Setting the ACL to public-read for public buckets
                            )
                            print(f"Public bucket {bucket_name} created successfully.")
                        else:
                            self.s3.create_bucket(
                                Bucket=bucket_name,
                                CreateBucketConfiguration={
                                    "LocationConstraint": self.s3.meta.region_name
                                },
                            )
                            print(f"Private bucket {bucket_name} created successfully.")
                    except ClientError as create_error:
                        print(
                            f"[x] Failed to create bucket {bucket_name}: {create_error}"
                        )
                        raise create_error
                else:
                    print(f"[x] Error checking bucket {bucket_name}: {e}")
                    raise e

    def presigned_get_object(self, bucket_name, object_name):
        url = self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=timedelta(days=7).total_seconds(),
        )
        return url

    def check_file_name_exists(self, bucket_name, file_name):
        try:
            self.s3.head_object(Bucket=bucket_name, Key=file_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                raise e

    def put_object(
        self,
        file_data,
        file_name,
        content_type,
        entity: str,
        sub_entity: str = None,
        category: str = None,
        is_public: bool = False,
    ) -> IS3Response:
        """
        Uploads an object to an S3 bucket.

        Args:
            file_data: The file data to be uploaded.
            file_name: The name of the file to be uploaded.
            content_type: The content type of the file.
            entity (str): The main category that the file belongs to. For example, "blog_images".
            sub_entity (str, optional): A sub-category under the main entity. For example, if the entity is "blog_images", sub_entity could be "travel". Defaults to None.
            category (str, optional): A further classification under the sub-entity. For example, under the "travel" sub-entity, category could be "Europe". Defaults to None.
            is_public (bool, optional): Whether the file should be publicly accessible. Defaults to False.

        Returns:
            IS3Response: An instance of IS3Response containing details of the uploaded file.

        Raises:
            NoCredentialsError: If no AWS credentials are provided.
            ClientError: If there's an error with the client or during the file upload.

        Example:
            put_object( file_data=image_data, file_name="eiffel_tower.jpg", content_type="image/jpeg", entity="blog_images",sub_entity="travel", category="Europe", is_public=True)
        """
        try:
            updated_file_name = f"{uuid7()}_{file_name.replace(' ', '_')}"
            state = "public" if is_public else "private"
            bucket_name = (
                self.public_bucket_name if is_public else self.private_bucket_name
            )
            # Create object name with structure: appName/environment/entity/sub_entity/uuid_fileName
            if sub_entity and category:
                object_name = f"{self.base_folder}/{state}/{self.environment}/{entity}/{sub_entity}/{category}/{updated_file_name}"
            if sub_entity:
                object_name = f"{self.base_folder}/{state}/{self.environment}/{entity}/{sub_entity}/{updated_file_name}"
            else:
                object_name = f"{self.base_folder}/{state}/{self.environment}/{entity}/{updated_file_name}"

            extra_args = {"ContentType": content_type}
            if is_public:
                extra_args["ACL"] = "public-read"

            self.s3.upload_fileobj(
                Fileobj=file_data,
                Bucket=bucket_name,
                Key=object_name,
                ExtraArgs=extra_args,
            )
            # Set the object ACL to public-read
            # if is_public:
            #     self.s3.put_object_acl(
            #         Bucket=bucket_name,
            #         Key=object_name,
            #         ACL='public-read'
            #     )
            url = (
                self.presigned_get_object(
                    bucket_name=bucket_name, object_name=object_name
                )
                if not is_public
                else f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
            )
            # presigned_url = url if not is_public else None
            # exp = (
            #     int((datetime.now() + timedelta(days=7)).timestamp())
            #     if not is_public
            #     else None
            # )
            data_file = IS3Response(
                bucket_name=bucket_name,
                file_name=object_name,
                url=url,
                # exp=exp,
                is_public=is_public,
                # presigned_url=presigned_url,
            )
            return data_file
        except NoCredentialsError as e:
            print(f"[x] No credentials error: {e}")
