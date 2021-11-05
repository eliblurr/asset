import sqlalchemy.types as types
from cls import Upload

class File(types.TypeDecorator):
    impl = types.String

    def __init__(self,  *args, upload_to, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.upload_to = upload_to

    def process_bind_param(self, value, dialect):
        file = Upload(value, upload_to=self.upload_to)
        url = file.save()
        return url

    def process_result_value(self, value, dialect):
        return value[3:]
        # add app url prefix here
