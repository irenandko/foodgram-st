import base64
import imghdr
from rest_framework import serializers
from django.core.files.base import ContentFile


class ReformattingBase64(serializers.ImageField):
    """Переформатирование фото профиля из base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, img_str = data.split(';base64,')
            ext = imghdr.what(None, h=base64.b64decode(img_str))
            content = ContentFile(
                base64.b64decode(img_str),
                name=f'temp.{ext}')

        return super().to_internal_value(content)
