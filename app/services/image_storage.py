import os
import uuid
import httpx
from PIL import Image
from io import BytesIO

from app.config import get_settings


class ImageStorageError(Exception):
    """Raised when image download or storage fails."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


async def download_and_save(
    image_url: str,
    client: httpx.AsyncClient | None = None,
    filename_prefix: str = "",
) -> tuple[str, str]:
    """Download an image from a URL and save it locally with a thumbnail.

    Args:
        image_url: The URL of the image to download.
        client: Optional httpx.AsyncClient.
        filename_prefix: Optional prefix for the filename.

    Returns:
        Tuple of (local_path, thumbnail_path) relative to the static directory.

    Raises:
        ImageStorageError: On download or save failure.
    """
    settings = get_settings()

    # Generate unique filename
    file_id = str(uuid.uuid4())[:12]
    filename = f"{filename_prefix}{file_id}.png"
    thumb_filename = f"{filename_prefix}{file_id}_thumb.png"

    base_dir = settings.generated_images_dir
    thumb_dir = os.path.join(base_dir, "thumbnails")

    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)

    full_path = os.path.join(base_dir, filename)
    thumb_path = os.path.join(thumb_dir, thumb_filename)

    should_close = client is None
    if client is None:
        client = httpx.AsyncClient(timeout=60.0)

    try:
        # Download the image
        response = await client.get(image_url, follow_redirects=True)
        if response.status_code != 200:
            raise ImageStorageError(
                f"下载图片失败 (HTTP {response.status_code}): {image_url[:100]}..."
            )

        image_data = response.content

        # Save full-resolution image
        with open(full_path, "wb") as f:
            f.write(image_data)

        # Generate and save thumbnail
        image = Image.open(BytesIO(image_data))
        image.thumbnail((400, 400), Image.LANCZOS)
        image.save(thumb_path, format="PNG")

        # Return paths relative to static directory
        local_rel = f"generated/{filename}"
        thumb_rel = f"generated/thumbnails/{thumb_filename}"

        return local_rel, thumb_rel

    except httpx.RequestError as e:
        raise ImageStorageError(f"下载图片时网络错误: {str(e)}")
    except OSError as e:
        raise ImageStorageError(f"保存图片时文件系统错误: {str(e)}")
    finally:
        if should_close and client:
            await client.aclose()


def delete_image_files(local_path: str, thumbnail_path: str) -> None:
    """Delete image files from disk.

    Args:
        local_path: Relative path to the full image (e.g. 'generated/abc.png').
        thumbnail_path: Relative path to the thumbnail.
    """
    settings = get_settings()

    full = os.path.join(settings.generated_images_dir, os.path.basename(local_path))
    thumb = os.path.join(
        settings.generated_images_dir, "thumbnails", os.path.basename(thumbnail_path)
    )

    for path in [full, thumb]:
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass  # Best-effort cleanup
