"""REST client for the Flask backend. Pygame never touches the graphs or algorithms directly."""
import json
import urllib.error
import urllib.request

DEFAULT_URL = "http://127.0.0.1:5000"


class ApiError(Exception):
    """Any failure the user should read (invalid order, backend down...)."""


class HttpTransport:
    """Real network transport (standard library only)."""

    def __init__(self, base_url: str = DEFAULT_URL, timeout: float = 5.0) -> None:
        self.base, self.timeout = base_url.rstrip("/"), timeout

    def request(self, method: str, path: str, body=None) -> tuple[int, dict]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                return res.status, json.loads(res.read() or b"{}")
        except urllib.error.HTTPError as err:  # 400/409 carry a JSON explanation
            try:
                return err.code, json.loads(err.read() or b"{}")
            except ValueError:
                return err.code, {}
        except (urllib.error.URLError, OSError) as err:
            raise ApiError("No se pudo conectar con el backend. ¿Está corriendo en el puerto 5000?") from err


class ApiClient:
    """One method per endpoint; errors become ApiError with the backend's own message."""

    def __init__(self, transport=None) -> None:
        self.transport = transport or HttpTransport()

    def _call(self, method: str, path: str, body=None) -> dict:
        status, data = self.transport.request(method, "/api" + path, body)
        if status >= 400 or data.get("success") is False:
            raise ApiError(data.get("error") or f"Error del servidor ({status})")
        return data

    def health(self) -> dict:
        return self._call("GET", "/health")

    def status(self) -> dict:
        return self._call("GET", "/scenario/status")

    def current_scenario(self) -> dict:
        return self._call("GET", "/scenario/current")

    def upload_scenario(self, raw: dict) -> dict:
        return self._call("POST", "/scenario/upload", raw)

    def plan(self) -> dict:
        return self._call("GET", "/defense/plan")

    def create_plan(self) -> dict:
        return self._call("POST", "/defense/plan", {})

    def state(self) -> dict:
        return self._call("GET", "/simulation/state")

    def reset(self) -> dict:
        return self._call("POST", "/simulation/reset", {})

    def tick(self, dt: float) -> dict:
        return self._call("POST", "/simulation/tick", {"dt": dt})

    def recruit(self, kind: str, count: int = 1) -> dict:
        return self._call("POST", "/units/recruit", {"type": kind, "count": count})

    def move(self, soldier_ids: list, dest: str, mode: str) -> dict:
        return self._call("POST", "/transport/move", {"soldier_ids": soldier_ids, "dest": dest, "mode": mode})

    def fly(self, soldier_ids: list, dest: str) -> dict:
        return self._call("POST", "/transport/helicopter", {"soldier_ids": soldier_ids, "dest": dest})

    def path(self, src: str, dst: str, mode: str) -> dict:
        return self._call("GET", f"/transport/path?src={src}&dst={dst}&mode={mode}")
