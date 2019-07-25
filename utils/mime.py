from enum import Enum

from rest_framework.exceptions import UnsupportedMediaType


SUMMARY_FORMAT = 'application/json'
FULL_FORMAT = 'application/json'


class MimeV3Type(Enum):
    full_json = FULL_FORMAT
    summary_json = SUMMARY_FORMAT


def get_full_mime_type(meta: dict) -> MimeV3Type:
    mime = meta.get('HTTP_ACCEPT_TYPE', SUMMARY_FORMAT)
    try:
        return MimeV3Type(mime)
    except ValueError:
        raise UnsupportedMediaType(mime)

