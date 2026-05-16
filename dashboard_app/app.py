from __future__ import annotations

import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    from .data_access import DashboardRepository
except ImportError:
    from data_access import DashboardRepository


BASE_DIR = Path(__file__).resolve().parent


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR / "static"), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        repository = DashboardRepository()

        if parsed.path == "/api/dashboard":
            self._send_json(repository.get_dashboard_payload())
            return

        if parsed.path == "/api/players":
            limit = self._read_limit(parsed.query)
            self._send_json({"items": repository.get_player_spotlight(limit=limit)})
            return

        if parsed.path == "/api/games":
            limit = self._read_limit(parsed.query)
            self._send_json({"items": repository.get_game_spotlight(limit=limit)})
            return

        if parsed.path == "/api/player":
            name = self._read_text_param(parsed.query, "name")
            if not name:
                self._send_json({"error": "Missing player name."}, status=HTTPStatus.BAD_REQUEST)
                return

            payload = repository.get_player_details(name)
            if not payload:
                self._send_json({"error": "Player not found."}, status=HTTPStatus.NOT_FOUND)
                return

            self._send_json(payload)
            return

        if parsed.path == "/api/game":
            title = self._read_text_param(parsed.query, "title")
            if not title:
                self._send_json({"error": "Missing game title."}, status=HTTPStatus.BAD_REQUEST)
                return

            payload = repository.get_game_details(title)
            if not payload:
                self._send_json({"error": "Game not found."}, status=HTTPStatus.NOT_FOUND)
                return

            self._send_json(payload)
            return

        if parsed.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        repository = DashboardRepository()

        try:
            payload = self._read_json_body()
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        try:
            if parsed.path == "/api/players":
                result = repository.add_player(payload.get("name", ""))
                self._send_json({"item": result}, status=HTTPStatus.CREATED)
                return

            if parsed.path == "/api/games":
                result = repository.add_game(
                    title=payload.get("title", ""),
                    min_players=int(payload.get("min_players")),
                    max_players=int(payload.get("max_players")),
                    game_theme=payload.get("game_theme", ""),
                    year_of_release=payload.get("year_of_release", ""),
                )
                self._send_json({"item": result}, status=HTTPStatus.CREATED)
                return

            if parsed.path == "/api/sessions":
                result = repository.add_session(
                    game_title=payload.get("game_title", ""),
                    session_date=payload.get("session_date", ""),
                    game_duration=int(payload.get("game_duration")),
                    players=payload.get("players", []),
                )
                self._send_json({"item": result}, status=HTTPStatus.CREATED)
                return
        except (TypeError, ValueError) as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
            return

        self._send_json({"error": "Not found."}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return

    def _read_limit(self, query: str) -> int:
        params = parse_qs(query)
        raw_limit = params.get("limit", ["5"])[0]

        try:
            return max(1, min(20, int(raw_limit)))
        except ValueError:
            return 5

    def _read_text_param(self, query: str, key: str) -> str:
        params = parse_qs(query)
        return params.get(key, [""])[0].strip()

    def _read_json_body(self) -> dict:
        raw_length = self.headers.get("Content-Length")
        if not raw_length:
            raise ValueError("Missing request body.")

        try:
            length = int(raw_length)
        except ValueError as exc:
            raise ValueError("Invalid content length.") from exc

        raw_body = self.rfile.read(length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Request body must be valid JSON.") from exc

        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")

        return payload

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), DashboardRequestHandler)
    print(f"Board game dashboard running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
