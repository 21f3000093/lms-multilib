import logging
import os
import re
from functools import lru_cache
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger(__name__)


class StorageConfigurationError(RuntimeError):
    pass


def _required_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise StorageConfigurationError(f"{name} is not configured")
    return value


@lru_cache(maxsize=1)
def _get_r2_client():
    account_id = _required_env("R2_ACCOUNT_ID")
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=_required_env("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=_required_env("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
    )


def _get_bucket_name() -> str:
    return _required_env("R2_BUCKET_NAME")


def _get_public_url_base() -> str:
    return _required_env("R2_PUBLIC_URL").rstrip("/")


def _sanitize_object_key(filename: str) -> str:
    parts = []
    for raw_part in filename.replace("\\", "/").split("/"):
        part = raw_part.strip()
        if not part or part in {".", ".."}:
            continue
        safe_part = re.sub(r"[^A-Za-z0-9._-]", "_", part).strip("._")
        parts.append((safe_part or "file")[:140])

    if not parts:
        raise ValueError("Invalid file name")
    return "/".join(parts)


def _object_key_from_url(photo_url: str) -> str | None:
    public_base = _get_public_url_base()
    normalized_url = (photo_url or "").strip()
    if not normalized_url.startswith(public_base + "/"):
        return None

    parsed = urlparse(normalized_url)
    parsed_base = urlparse(public_base)
    if parsed.scheme != parsed_base.scheme or parsed.netloc != parsed_base.netloc:
        return None

    base_path = parsed_base.path.rstrip("/")
    object_path = parsed.path
    if base_path and object_path.startswith(base_path + "/"):
        object_path = object_path[len(base_path):]

    return object_path.lstrip("/") or None


def upload_student_photo(file_bytes: bytes, filename: str, content_type: str = "image/webp") -> str:
    object_key = _sanitize_object_key(filename)

    try:
        _get_r2_client().put_object(
            Bucket=_get_bucket_name(),
            Key=object_key,
            Body=file_bytes,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Cloudflare R2 upload failed")
        raise RuntimeError("Cloudflare upload failed") from exc

    return f"{_get_public_url_base()}/{object_key}"


def delete_student_photo(photo_url: str) -> bool:
    object_key = _object_key_from_url(photo_url)
    if not object_key:
        return False

    try:
        _get_r2_client().delete_object(Bucket=_get_bucket_name(), Key=object_key)
        return True
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Cloudflare R2 delete failed")
        raise RuntimeError("Cloudflare delete failed") from exc


def get_student_photo_key(photo_url: str) -> str | None:
    return _object_key_from_url(photo_url)
