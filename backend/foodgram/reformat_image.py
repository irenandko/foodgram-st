import base64
import imghdr
from rest_framework import serializers
from django.core.files.base import ContentFile


class ReformattingBase64(serializers.ImageField):
    """Переформатирование фото профиля из base64."""

    def to_internal_value(self, data):
        try:
            if isinstance(data, str) and data.startswith('data:image'):
                header, img_str = data.split(';base64,')
                file_ext = imghdr.what(None, h=base64.b64decode(img_str))

                if not file_ext:
                    raise serializers.ValidationError(
                        ('Не удалось определить тип изображения.')
                    )

                image_data = base64.b64decode(img_str)
                content = ContentFile(
                    image_data,
                    name=f'temp.{file_ext}'
                )
            else:
                raise serializers.ValidationError(
                    ('Неверный формат изображения. Ожидается base64 строка.')
                )

        except (ValueError, TypeError, OSError, base64.binascii.Error) as e:
            raise serializers.ValidationError(
                ('Ошибка при обработке изображения: {error}')
                .format(error=str(e))
            )

        return super().to_internal_value(content)

    def validate_empty_values(self, data):
        if data is None:
            return True, None
        return False, data
