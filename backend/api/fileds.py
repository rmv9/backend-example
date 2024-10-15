import base64

from django.core.files.base import ContentFile
from rest_framework import fields


class Base64ImageField(fields.ImageField):
    """Поле для декодировки изображений"""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            img_format, img_str = data.split(';base64,')
            ext = img_format.split('/')[-1]

            data = ContentFile(base64.b64decode(img_str), name=f'image.{ext}')

        return super().to_internal_value(data)
