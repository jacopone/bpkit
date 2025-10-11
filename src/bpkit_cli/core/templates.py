"""Template download and management utilities."""

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class TemplateDownloadError(Exception):
    """Raised when template download fails after retries."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to download template from {url}: {reason}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def download_template(url: str) -> str:
    """Download template content from GitHub raw URL with retry logic.

    Retries up to 3 times with exponential backoff on failures.

    Args:
        url: GitHub raw content URL

    Returns:
        Template content as string

    Raises:
        TemplateDownloadError: If download fails after retries with user-friendly message

    Example:
        >>> content = download_template(
        ...     "https://raw.githubusercontent.com/user/repo/main/template.md"
        ... )
        >>> assert "[PROJECT_NAME]" in content
    """
    try:
        with httpx.Client(timeout=10.0, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.TimeoutException as e:
        raise TemplateDownloadError(
            url,
            "Request timed out after 10 seconds. Please check your internet connection."
        ) from e
    except httpx.NetworkError as e:
        raise TemplateDownloadError(
            url,
            "Network error occurred. Please check your internet connection and firewall settings."
        ) from e
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise TemplateDownloadError(
                url,
                "Template not found (404). The repository may have moved or been deleted."
            ) from e
        elif e.response.status_code == 403:
            raise TemplateDownloadError(
                url,
                "Access forbidden (403). GitHub may have rate-limited your IP address."
            ) from e
        elif e.response.status_code >= 500:
            raise TemplateDownloadError(
                url,
                f"GitHub server error ({e.response.status_code}). Please try again later."
            ) from e
        else:
            raise TemplateDownloadError(
                url,
                f"HTTP error {e.response.status_code}: {e.response.reason_phrase}"
            ) from e
    except Exception as e:
        raise TemplateDownloadError(
            url,
            f"Unexpected error: {type(e).__name__}: {e}"
        ) from e


def replace_placeholders(content: str, project_name: str | None) -> str:
    """Replace template placeholders with actual values.

    Currently supports:
    - [PROJECT_NAME]: Replaced with project_name if provided

    Args:
        content: Template content with placeholders
        project_name: Project name to substitute, or None to leave unchanged

    Returns:
        Content with placeholders replaced

    Example:
        >>> template = "# Project: [PROJECT_NAME]\\n"
        >>> result = replace_placeholders(template, "my-startup")
        >>> assert result == "# Project: my-startup\\n"
    """
    if project_name:
        content = content.replace("[PROJECT_NAME]", project_name)
    return content
