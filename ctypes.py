from config import settings, AWS_S3_CUSTOM_DOMAIN
import sqlalchemy.types as types
from cls import Upload

class File(types.TypeDecorator):
    impl = types.String

    def __init__(self,  *args, upload_to, size=None, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.upload_to = upload_to
        self.size = size

    def process_bind_param(self, value, dialect):
        file = Upload(value, upload_to=self.upload_to, size=self.size)
        url = file.save()
        return url

    def process_result_value(self, value, dialect):
        if value:
            if value[:3]=='S3:':
                return AWS_S3_CUSTOM_DOMAIN+value[3:]
            return settings.BASE_URL+value[3:]
        else:
            return None