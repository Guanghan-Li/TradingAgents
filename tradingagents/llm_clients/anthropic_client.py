import os
import time
from functools import cached_property
from typing import Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_anthropic.chat_models import _USER_AGENT
from pydantic import Field, SecretStr
from langchain_core.utils.utils import secret_from_env

from .base_client import BaseLLMClient, normalize_content
from .request_tracker import log_llm_request, record_llm_request
from .validators import validate_model

_PASSTHROUGH_KWARGS = (
    "timeout", "max_retries", "api_key", "max_tokens",
    "callbacks", "http_client", "http_async_client", "effort", "default_headers",
    "streaming",
)


class NormalizedChatAnthropic(ChatAnthropic):
    """ChatAnthropic with normalized content output.

    Claude models with extended thinking or tool use return content as a
    list of typed blocks. This normalizes to string for consistent
    downstream handling.
    """

    anthropic_auth_token: SecretStr | None = Field(
        alias="auth_token",
        default_factory=secret_from_env(
            ["ANTHROPIC_AUTH_TOKEN"],
            default=None,
        ),
    )

    @cached_property
    def _client_params(self) -> dict[str, Any]:
        default_headers = {"User-Agent": _USER_AGENT}
        if self.default_headers:
            default_headers.update(self.default_headers)

        client_params: dict[str, Any] = {
            "base_url": self.anthropic_api_url,
            "max_retries": self.max_retries,
            "default_headers": default_headers,
        }

        auth_token = (
            self.anthropic_auth_token.get_secret_value()
            if self.anthropic_auth_token is not None
            else ""
        )
        if auth_token:
            client_params["auth_token"] = auth_token
        else:
            client_params["api_key"] = self.anthropic_api_key.get_secret_value()

        if self.default_request_timeout is None or self.default_request_timeout > 0:
            client_params["timeout"] = self.default_request_timeout

        return client_params

    def invoke(self, input, config=None, **kwargs):
        return normalize_content(super().invoke(input, config, **kwargs))

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        record_llm_request("anthropic")
        start = time.time()
        error: Optional[str] = None
        try:
            return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)
        except BaseException as exc:
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            log_llm_request(
                "anthropic",
                model=getattr(self, "model", None),
                messages=messages,
                run_manager=run_manager,
                duration_s=time.time() - start,
                error=error,
            )

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        record_llm_request("anthropic")
        start = time.time()
        error: Optional[str] = None
        try:
            return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)
        except BaseException as exc:
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            log_llm_request(
                "anthropic",
                model=getattr(self, "model", None),
                messages=messages,
                run_manager=run_manager,
                duration_s=time.time() - start,
                error=error,
            )

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        record_llm_request("anthropic")
        start = time.time()
        error: Optional[str] = None
        try:
            yield from super()._stream(messages, stop=stop, run_manager=run_manager, **kwargs)
        except BaseException as exc:
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            log_llm_request(
                "anthropic",
                model=getattr(self, "model", None),
                messages=messages,
                run_manager=run_manager,
                duration_s=time.time() - start,
                error=error,
            )

    async def _astream(self, messages, stop=None, run_manager=None, **kwargs):
        record_llm_request("anthropic")
        start = time.time()
        error: Optional[str] = None
        try:
            async for chunk in super()._astream(messages, stop=stop, run_manager=run_manager, **kwargs):
                yield chunk
        except BaseException as exc:
            error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            log_llm_request(
                "anthropic",
                model=getattr(self, "model", None),
                messages=messages,
                run_manager=run_manager,
                duration_s=time.time() - start,
                error=error,
            )


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude models."""

    def __init__(self, model: str, base_url: Optional[str] = None, **kwargs):
        super().__init__(model, base_url, **kwargs)

    def get_llm(self) -> Any:
        """Return configured ChatAnthropic instance."""
        llm_kwargs = {"model": self.model}
        if self.base_url:
            llm_kwargs["anthropic_api_url"] = self.base_url
        auth_token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
        if auth_token:
            llm_kwargs["auth_token"] = auth_token

        for key in _PASSTHROUGH_KWARGS:
            if key in self.kwargs:
                llm_kwargs[key] = self.kwargs[key]

        return NormalizedChatAnthropic(**llm_kwargs)

    def validate_model(self) -> bool:
        """Validate model for Anthropic."""
        return validate_model("anthropic", self.model)
