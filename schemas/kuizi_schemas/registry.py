"""Small client for the schema registry REST API (Redpanda locally, the same API in the cloud, T021).

Standard library only. The registry URL comes from SCHEMA_REGISTRY_URL, read from the environment
or from the repository's .env file (ADR 0006: the same variable names locally and in the cloud).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONTENT_TYPE = "application/vnd.schemaregistry.v1+json"


class RegistryError(Exception):
    """The registry answered with an error, or could not be reached."""

    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


class IncompatibleSchema(RegistryError):
    """The registry refused a schema because it breaks the subject's compatibility level (HTTP 409)."""


def registry_url(env_file: Path | None = None) -> str:
    """SCHEMA_REGISTRY_URL from the environment, else from .env; raises RegistryError when unset."""
    url = os.environ.get("SCHEMA_REGISTRY_URL")
    if not url and env_file and env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.partition("=")
            if sep and key.strip() == "SCHEMA_REGISTRY_URL":
                url = value.strip().strip("'\"")
    if not url:
        raise RegistryError("SCHEMA_REGISTRY_URL is not set (copy .env.example to .env, or export it)")
    return url.rstrip("/")


@dataclass
class Registry:
    url: str
    timeout: float = 10.0

    def _call(self, method: str, path: str, body: Any = None, query: dict | None = None) -> Any:
        url = f"{self.url}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            url, data=data, method=method, headers={"Content-Type": CONTENT_TYPE, "Accept": CONTENT_TYPE}
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                text = response.read().decode()
                return json.loads(text) if text else None
        except urllib.error.HTTPError as error:
            text = error.read().decode(errors="replace")
            try:
                message = json.loads(text).get("message", text)
            except (json.JSONDecodeError, AttributeError):
                message = text
            if error.code == 409:
                raise IncompatibleSchema(message, 409) from None
            raise RegistryError(f"{method} {path}: HTTP {error.code}: {message}", error.code) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            raise RegistryError(
                f"cannot reach the schema registry at {self.url} ({error}); is the stack up (make up)?"
            ) from None

    @staticmethod
    def _subject(subject: str) -> str:
        return urllib.parse.quote(subject, safe="")

    def reachable(self) -> bool:
        try:
            self.subjects()
            return True
        except RegistryError:
            return False

    def subjects(self) -> list[str]:
        return self._call("GET", "/subjects")

    def versions(self, subject: str) -> list[int]:
        try:
            return self._call("GET", f"/subjects/{self._subject(subject)}/versions")
        except RegistryError as error:
            if error.status == 404:
                return []
            raise

    def get_version(self, subject: str, version: int | str = "latest") -> dict:
        return self._call("GET", f"/subjects/{self._subject(subject)}/versions/{version}")

    def lookup(self, subject: str, schema: str) -> dict | None:
        """The registered version of exactly this schema under `subject`, or None."""
        try:
            return self._call("POST", f"/subjects/{self._subject(subject)}", {"schema": schema})
        except RegistryError as error:
            if error.status == 404:
                return None
            raise

    def compatibility_level(self, subject: str) -> str | None:
        try:
            config = self._call("GET", f"/config/{self._subject(subject)}")
        except RegistryError as error:
            if error.status == 404:
                return None
            raise
        return config.get("compatibilityLevel") or config.get("compatibility")

    def set_compatibility(self, subject: str, level: str) -> None:
        self._call("PUT", f"/config/{self._subject(subject)}", {"compatibility": level})

    def check(self, subject: str, schema: str, version: int | str = "latest") -> tuple[bool, list[str]]:
        """Would `schema` be accepted? Redpanda applies the subject's level, transitive included."""
        result = self._call(
            "POST",
            f"/compatibility/subjects/{self._subject(subject)}/versions/{version}",
            {"schema": schema},
            query={"verbose": "true"},
        )
        return bool(result.get("is_compatible")), list(result.get("messages", []))

    def register(self, subject: str, schema: str) -> int:
        """Register `schema`; returns its global ID. Raises IncompatibleSchema when refused."""
        return self._call("POST", f"/subjects/{self._subject(subject)}/versions", {"schema": schema})["id"]

    def schema_by_id(self, schema_id: int) -> str:
        return self._call("GET", f"/schemas/ids/{schema_id}")["schema"]

    def delete_subject(self, subject: str) -> None:
        """Soft then permanent delete, then the subject's own config. For test subjects only."""
        for query in (None, {"permanent": "true"}):
            try:
                self._call("DELETE", f"/subjects/{self._subject(subject)}", query=query)
            except RegistryError as error:
                if error.status != 404:
                    raise
        try:
            self._call("DELETE", f"/config/{self._subject(subject)}")
        except RegistryError as error:
            if error.status not in (404, 405):
                raise
