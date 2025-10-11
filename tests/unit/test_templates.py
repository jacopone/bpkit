"""Unit tests for templates module - download and placeholder replacement."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from bpkit_cli.core.templates import (
    TemplateDownloadError,
    download_template,
    replace_placeholders,
)


class TestDownloadTemplate:
    """Test the download_template function with retry logic."""

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_success(self, mock_client_class):
        """Test successful template download on first attempt."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = "# Template content\n[PROJECT_NAME]"
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(return_value=mock_response)

        mock_client_class.return_value = mock_client

        # Download
        result = download_template("https://example.com/template.md")

        assert result == "# Template content\n[PROJECT_NAME]"
        mock_client.get.assert_called_once_with("https://example.com/template.md")

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_timeout_error(self, mock_client_class):
        """Test timeout error with user-friendly message."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(side_effect=httpx.TimeoutException("Timeout"))

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError) as exc_info:
            download_template("https://example.com/template.md")

        assert "Request timed out after 10 seconds" in exc_info.value.reason
        assert "internet connection" in exc_info.value.reason

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_network_error(self, mock_client_class):
        """Test network error with user-friendly message."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(side_effect=httpx.NetworkError("Connection failed"))

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError) as exc_info:
            download_template("https://example.com/template.md")

        assert "Network error occurred" in exc_info.value.reason
        assert "firewall" in exc_info.value.reason

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_404_error(self, mock_client_class):
        """Test 404 error with user-friendly message."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.reason_phrase = "Not Found"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=mock_response
            )
        )

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError) as exc_info:
            download_template("https://example.com/template.md")

        assert "404" in exc_info.value.reason
        assert "not found" in exc_info.value.reason.lower()

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_403_error(self, mock_client_class):
        """Test 403 error with rate limit message."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.reason_phrase = "Forbidden"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "403 Forbidden", request=MagicMock(), response=mock_response
            )
        )

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError) as exc_info:
            download_template("https://example.com/template.md")

        assert "403" in exc_info.value.reason
        assert "rate-limited" in exc_info.value.reason.lower()

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_500_error(self, mock_client_class):
        """Test 500 server error with retry-later message."""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.reason_phrase = "Service Unavailable"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "503 Service Unavailable", request=MagicMock(), response=mock_response
            )
        )

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError) as exc_info:
            download_template("https://example.com/template.md")

        assert "503" in exc_info.value.reason
        assert "try again later" in exc_info.value.reason.lower()

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_generic_http_error(self, mock_client_class):
        """Test generic HTTP error."""
        mock_response = MagicMock()
        mock_response.status_code = 418
        mock_response.reason_phrase = "I'm a teapot"

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(
            side_effect=httpx.HTTPStatusError(
                "418 I'm a teapot", request=MagicMock(), response=mock_response
            )
        )

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError) as exc_info:
            download_template("https://example.com/template.md")

        assert "418" in exc_info.value.reason
        assert "I'm a teapot" in exc_info.value.reason

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_unexpected_error(self, mock_client_class):
        """Test unexpected error handling."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(side_effect=ValueError("Unexpected issue"))

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError) as exc_info:
            download_template("https://example.com/template.md")

        assert "Unexpected error" in exc_info.value.reason
        assert "ValueError" in exc_info.value.reason

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_retry_logic(self, mock_client_class):
        """Test that download retries 3 times with exponential backoff."""
        # First two attempts fail, third succeeds
        mock_response = MagicMock()
        mock_response.text = "Success content"
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(
            side_effect=[
                httpx.NetworkError("First failure"),
                httpx.NetworkError("Second failure"),
                mock_response,  # Third attempt succeeds
            ]
        )

        mock_client_class.return_value = mock_client

        result = download_template("https://example.com/template.md")

        assert result == "Success content"
        assert mock_client.get.call_count == 3

    @patch("bpkit_cli.core.templates.httpx.Client")
    def test_download_retry_exhaustion(self, mock_client_class):
        """Test that download fails after 3 retry attempts."""
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=None)
        mock_client.get = MagicMock(side_effect=httpx.NetworkError("Persistent failure"))

        mock_client_class.return_value = mock_client

        with pytest.raises(TemplateDownloadError):
            download_template("https://example.com/template.md")

        # Should have attempted 3 times
        assert mock_client.get.call_count == 3


class TestReplacePlaceholders:
    """Test the replace_placeholders function."""

    def test_replace_project_name(self):
        """Test replacing [PROJECT_NAME] placeholder."""
        template = "# [PROJECT_NAME]\n\nWelcome to [PROJECT_NAME]!"
        result = replace_placeholders(template, "my-startup")

        assert result == "# my-startup\n\nWelcome to my-startup!"

    def test_no_replacement_when_none(self):
        """Test that no replacement happens when project_name is None."""
        template = "# [PROJECT_NAME]\n\nWelcome to [PROJECT_NAME]!"
        result = replace_placeholders(template, None)

        assert result == template  # Unchanged

    def test_replace_multiple_occurrences(self):
        """Test replacing multiple occurrences."""
        template = "[PROJECT_NAME] [PROJECT_NAME] [PROJECT_NAME]"
        result = replace_placeholders(template, "test")

        assert result == "test test test"

    def test_replace_case_sensitive(self):
        """Test that replacement is case-sensitive."""
        template = "[PROJECT_NAME] [project_name] [Project_Name]"
        result = replace_placeholders(template, "test")

        # Only exact match should be replaced
        assert result == "test [project_name] [Project_Name]"

    def test_replace_empty_string(self):
        """Test replacing with empty string."""
        template = "Project: [PROJECT_NAME]"
        result = replace_placeholders(template, "")

        assert result == "Project: "

    def test_no_placeholders(self):
        """Test template with no placeholders."""
        template = "# Template\n\nNo placeholders here."
        result = replace_placeholders(template, "my-project")

        assert result == template  # Unchanged

    def test_partial_placeholder_not_replaced(self):
        """Test that partial matches are not replaced."""
        template = "PROJECT_NAME [PROJECT_NAME] [PROJECT_NAME]_SUFFIX"
        result = replace_placeholders(template, "test")

        assert result == "PROJECT_NAME test [PROJECT_NAME]_SUFFIX"


class TestTemplateDownloadError:
    """Test the TemplateDownloadError exception."""

    def test_error_attributes(self):
        """Test that error has url and reason attributes."""
        url = "https://example.com/template.md"
        reason = "Network timeout"

        error = TemplateDownloadError(url, reason)

        assert error.url == url
        assert error.reason == reason
        assert url in str(error)
        assert reason in str(error)

    def test_error_message_format(self):
        """Test error message format."""
        error = TemplateDownloadError(
            "https://example.com/file.md", "Connection failed"
        )

        message = str(error)
        assert "Failed to download template from" in message
        assert "https://example.com/file.md" in message
        assert "Connection failed" in message
