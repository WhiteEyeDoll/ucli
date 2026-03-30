import json
from functools import cache
from types import TracebackType
from typing import Optional, Self, Type

import httpx

from ucli.client.models.client import ClientOptions
from ucli.client.resources.sites import SitesResource


class APIClientV1:

    def __init__(self, options: ClientOptions):

        self.options = options

        base_url = httpx.URL(str(self.options.base_url)).join(
            "proxy/network/integration/v1/"
        )

        self._client = httpx.Client(
            base_url=base_url,
            verify=self.options.verify_tls,
            timeout=self.options.timeout,
            headers={"X-API-KEY": self.options.api_key},
        )

    def request(self, method: str, path: str, **kwargs):

        response = self._client.request(method, path, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            response_detail = self._format_response_detail(response)
            request_payload_label = "request_json"
            request_payload = kwargs.get("json")
            if request_payload is None and "content" in kwargs:
                request_payload_label = "request_content"
                request_payload = kwargs.get("content")
            if request_payload is None and "data" in kwargs:
                request_payload_label = "request_data"
                request_payload = kwargs.get("data")

            request_detail = self._format_request_detail(request_payload)
            request_detail_suffix = (
                f" {request_payload_label}={request_detail!r}" if request_detail else ""
            )
            raise httpx.HTTPStatusError(
                "HTTP request failed: "
                f"status={response.status_code} method={method} path={path} "
                f"response={response_detail!r}{request_detail_suffix}",
                request=error.request,
                response=error.response,
            ) from error

        # 204 No Content is always empty by definition
        if response.status_code == 204:
            return {}

        if not response.content:
            return {}

        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            try:
                return response.json()
            except ValueError as error:
                body = response.text
                snippet = body[:200] if body else ""
                raise ValueError(
                    "Response declared JSON but could not be decoded. "
                    f"status={response.status_code} content_type={content_type!r} "
                    f"body_snippet={snippet!r}"
                ) from error

        return {}

    @staticmethod
    def _format_response_detail(response: httpx.Response) -> str:
        if not response.content:
            return "<empty>"

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                serialized_payload = json.dumps(response.json(), ensure_ascii=False)
                return serialized_payload[:2000]
            except ValueError:
                pass

        body = response.text.strip()
        return body[:2000] if body else "<empty>"

    @staticmethod
    def _format_request_detail(payload: object) -> str:
        if payload is None:
            return ""

        try:
            serialized_payload = json.dumps(payload, ensure_ascii=False)
        except (TypeError, ValueError):
            serialized_payload = repr(payload)

        return serialized_payload[:2000]

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "APIClientV1":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:

        _ = (exc_type, exc_value, traceback)

        self.close()

    @property
    def sites(self) -> SitesResource:
        return SitesResource(self)

    @classmethod
    @cache
    def get_client(cls, options: ClientOptions) -> Self:

        return cls(options)
