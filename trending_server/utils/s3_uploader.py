import os
from datetime import datetime
from io import BytesIO
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


class S3Uploader:
    """Handles uploading files to S3-compatible storage (AWS S3, Digital Ocean Spaces, etc.)."""

    def __init__(self, bucket_name: str = None, cdn_base_url: str = None, endpoint_url: str = None):
        self.bucket_name = bucket_name or os.getenv('SPACES_BUCKET')
        if not self.bucket_name:
            raise ValueError("Bucket name must be provided or set via SPACES_BUCKET environment variable")

        self.cdn_base_url = cdn_base_url or os.getenv('SPACES_CDN_BASE_URL')
        self.endpoint_url = endpoint_url or os.getenv('SPACES_ENDPOINT_URL')

        client_config = {}

        if self.endpoint_url:
            client_config['endpoint_url'] = self.endpoint_url

        access_key = os.getenv('SPACES_KEY') or os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('SPACES_SECRET') or os.getenv('AWS_SECRET_ACCESS_KEY')

        if access_key and secret_key:
            client_config['aws_access_key_id'] = access_key
            client_config['aws_secret_access_key'] = secret_key

        self.s3_client = boto3.client('s3', **client_config)

    def upload_file(
        self,
        file_data: BytesIO,
        key: str = None,
        content_type: str = 'application/pdf',
        metadata: dict = None
    ) -> str:
        # Generate key unless provided
        if not key:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            key = f"trending-news/{timestamp}.pdf"

        # Ensure key doesn't start with /
        key = key.lstrip('/')

        # Prepare upload arguments
        extra_args = {
            'ContentType': content_type,
            'ACL': 'public-read'
        }

        if metadata:
            extra_args['Metadata'] = metadata

        try:
            # Upload file
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )

            # Generate URL - prefer CDN if configured, otherwise direct URL
            if self.cdn_base_url:
                cdn_base = self.cdn_base_url.rstrip('/')
                url = f"{cdn_base}/{key}"
            elif self.endpoint_url:
                endpoint_clean = self.endpoint_url.replace('https://', '').replace('http://', '')
                url = f"https://{self.bucket_name}.{endpoint_clean}/{key}"
            else:
                # Default AWS S3 URL
                url = f"https://{self.bucket_name}.s3.amazonaws.com/{key}"

            return url

        except NoCredentialsError:
            raise NoCredentialsError(fmt=
                "Credentials not found. Please configure credentials via "
                "environment variables (SPACES_KEY/SPACES_SECRET for Digital Ocean, "
                "or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY for AWS S3)."
            )
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            raise ClientError(
                {'Error': {'Code': error_code, 'Message': f"Failed to upload: {error_message}"}},
                'upload_fileobj'
            )

    def upload_pdf(
        self,
        pdf_data: BytesIO,
        filename: str = None,
        metadata: dict = None
    ) -> str:
        """
        Returns:
            str: The CDN URL (if configured) or direct storage URL of the uploaded PDF
        """
        if filename:
            key = f"{filename}"
        else:
            key = None

        return self.upload_file(
            pdf_data,
            key=key,
            content_type='application/pdf',
            metadata=metadata
        )
