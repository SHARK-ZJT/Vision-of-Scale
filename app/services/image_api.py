from openai import AsyncOpenAI

from app.config import get_settings


class ImageAPIError(Exception):
    """Raised when the image generation API returns an error."""

    def __init__(self, message: str, status_code: int | None = None, response_body: str = ""):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


async def generate_images(
    prompt: str,
    model: str | None = None,
    size: str = "1024x1024",
    n: int = 1,
    seed: int = -1,
    response_format: str = "url",
) -> dict:
    """Call 火山引擎 即梦AI (Seedream 4.0) via OpenAI-compatible API.

    Args:
        prompt: The text prompt for image generation.
        model: Model name. Defaults to doubao-seedream-4-0-250828.
        size: Image size — "1024x1024", "1664x936", "936x1664", "2K", "4K".
        n: Number of images to generate (1-4).
        seed: Random seed. Use -1 for random.
        response_format: 'url' for image URL or 'b64_json' for base64.

    Returns:
        Dict with 'data' key containing a list of image result dicts with 'url' keys.

    Raises:
        ImageAPIError: On API error responses.
    """
    settings = get_settings()
    model = model or settings.default_model

    client = AsyncOpenAI(
        api_key=settings.ark_api_key,
        base_url=settings.ark_base_url,
    )

    try:
        # Build extra_body for Seedream-specific options
        extra_body: dict = {}

        # Multi-image via sequential_image_generation
        if n > 1:
            extra_body["sequential_image_generation"] = "auto"
            extra_body["sequential_image_generation_options"] = {"max_images": n}

        response = await client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            n=1 if n > 1 else 1,  # OpenAI param — Seedream uses extra_body for multiple
            response_format=response_format,
            extra_body=extra_body if extra_body else None,
        )

        # Build compatible response dict
        return {
            "created": getattr(response, "created", 0),
            "data": [
                {
                    "url": img.url if hasattr(img, "url") else "",
                    "b64_json": img.b64_json if hasattr(img, "b64_json") else "",
                }
                for img in response.data
            ],
        }

    except Exception as e:
        error_msg = str(e)

        if "401" in error_msg or "Unauthorized" in error_msg or "authentication" in error_msg.lower():
            raise ImageAPIError(
                "API 认证失败，请检查 ARK_API_KEY 是否正确配置，以及是否在火山引擎控制台开通了 Seedream 4.0 模型",
                status_code=401,
                response_body=error_msg,
            )
        elif "429" in error_msg or "rate" in error_msg.lower():
            raise ImageAPIError(
                "请求过于频繁，请稍后再试",
                status_code=429,
                response_body=error_msg,
            )
        elif "400" in error_msg:
            raise ImageAPIError(
                f"请求参数错误: {error_msg}",
                status_code=400,
                response_body=error_msg,
            )
        elif "timeout" in error_msg.lower():
            raise ImageAPIError(
                "API 请求超时，请稍后重试（图片生成可能需要较长时间）",
            )
        else:
            raise ImageAPIError(
                f"API 请求失败: {error_msg[:500]}",
            )
