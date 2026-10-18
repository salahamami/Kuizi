"""A tiny in-process stand-in for the schema registry REST API, so the client and the `register`
command are tested in CI, where no registry runs. It decides compatibility with the offline checker;
the tests in test_registry_live.py prove the real registry's behaviour."""

from __future__ import annotations

import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from kuizi_schemas.compat import Version as HistoryVersion
from kuizi_schemas.compat import check_subject


class FakeRegistry:
    def __init__(self) -> None:
        self.subjects: dict[str, list[tuple[int, str]]] = {}
        self.config: dict[str, str] = {}
        self.schemas: dict[int, str] = {}
        self.requests: list[tuple[str, str]] = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args: object) -> None:  # keep test output quiet
                pass

            def _reply(self, status: int, body: object) -> None:
                data = json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/vnd.schemaregistry.v1+json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def _body(self) -> dict:
                length = int(self.headers.get("Content-Length", 0))
                return json.loads(self.rfile.read(length) or b"{}")

            def _route(self, method: str) -> None:
                path = urlparse(self.path).path
                fake.requests.append((method, path))
                status, body = fake.handle(method, path, self._body() if method in ("POST", "PUT") else {})
                self._reply(status, body)

            def do_GET(self) -> None:
                self._route("GET")

            def do_POST(self) -> None:
                self._route("POST")

            def do_PUT(self) -> None:
                self._route("PUT")

            def do_DELETE(self) -> None:
                self._route("DELETE")

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self) -> FakeRegistry:
        self.thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.server.shutdown()
        self.server.server_close()

    def _problems(self, subject: str, schema: str) -> list[str]:
        level = self.config.get(subject, "BACKWARD")
        history = [HistoryVersion(str(i), json.loads(s)) for i, s in self.subjects.get(subject, [])]
        return check_subject(subject, json.loads(schema), history, level)

    def handle(self, method: str, path: str, body: dict) -> tuple[int, object]:
        not_found = (404, {"error_code": 40401, "message": "Subject not found."})
        if method == "GET" and path == "/subjects":
            return 200, sorted(self.subjects)
        if m := re.fullmatch(r"/config/([^/]+)", path):
            subject = unquote(m.group(1))
            if method == "PUT":
                self.config[subject] = body["compatibility"]
                return 200, {"compatibility": body["compatibility"]}
            if method == "GET":
                return (200, {"compatibilityLevel": self.config[subject]}) if subject in self.config else not_found
            if method == "DELETE":
                return (200, {"compatibilityLevel": self.config.pop(subject)}) if subject in self.config else not_found
        if m := re.fullmatch(r"/subjects/([^/]+)", path):
            subject = unquote(m.group(1))
            if method == "POST":
                for version, (schema_id, schema) in enumerate(self.subjects.get(subject, []), start=1):
                    if schema == body["schema"]:
                        return 200, {"subject": subject, "version": version, "id": schema_id, "schema": schema}
                return not_found
            if method == "DELETE":
                versions = self.subjects.pop(subject, None)
                return (200, list(range(1, len(versions) + 1))) if versions is not None else not_found
        if m := re.fullmatch(r"/subjects/([^/]+)/versions", path):
            subject = unquote(m.group(1))
            if method == "GET":
                versions = self.subjects.get(subject)
                return (200, list(range(1, len(versions) + 1))) if versions else not_found
            if method == "POST":
                problems = self._problems(subject, body["schema"])
                if problems:
                    return 409, {"error_code": 409, "message": "incompatible: " + "; ".join(problems)}
                schema_id = len(self.schemas) + 1
                self.schemas[schema_id] = body["schema"]
                self.subjects.setdefault(subject, []).append((schema_id, body["schema"]))
                return 200, {"id": schema_id}
        if (m := re.fullmatch(r"/subjects/([^/]+)/versions/(\d+)", path)) and method == "GET":
            versions = self.subjects.get(unquote(m.group(1)), [])
            number = int(m.group(2))
            if not 1 <= number <= len(versions):
                return not_found
            schema_id, schema = versions[number - 1]
            return 200, {"subject": unquote(m.group(1)), "version": number, "id": schema_id, "schema": schema}
        if (m := re.fullmatch(r"/compatibility/subjects/([^/]+)/versions/latest", path)) and method == "POST":
            problems = self._problems(unquote(m.group(1)), body["schema"])
            return 200, {"is_compatible": not problems, "messages": problems}
        if (m := re.fullmatch(r"/schemas/ids/(\d+)", path)) and method == "GET":
            schema_id = int(m.group(1))
            return (200, {"schema": self.schemas[schema_id]}) if schema_id in self.schemas else not_found
        return 404, {"message": "Not found"}
