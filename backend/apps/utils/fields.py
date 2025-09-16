import re

from drf_extra_fields.fields import Base64FileField

class FileBase64Field(Base64FileField):
    ALLOWED_TYPES = ['']
    
    def get_file_extension(self, filename, decoded_file):

        return ''