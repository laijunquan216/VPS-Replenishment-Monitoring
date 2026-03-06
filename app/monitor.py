from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path
import threading
import time
from typing import Any
from urllib.request import Request, urlopen

from .adapters import DetectorRule, build_rule_from_dict, detect_in_stock, validate_rules
from .notifier import EmailNotifier, SmtpConfig


@dataclass
class CheckResult:
    site_name: str
    product_name: str
    url: str
    in_stock: bool
    reason: str
    checked_at: str


class MonitorService:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._running = False
        self._last_state: dict[str, bool] = {}
        self._results: list[CheckResult] = []
        self._errors: list[str] = []
        self.raw_config: dict[str, Any] = {}
        self.reload_config()

    def _load_config_from_disk(self) -> dict[str, Any]:
        with self.config_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _apply_config(self, config: dict[str, Any]) -> None:
        interval = int(config.get("interval_seconds", 60))
        if interval <= 0:
            raise ValueError("interval_seconds 必须大于 0")

        rules_raw = config.get("rules", [])
        rules: list[DetectorRule] = [build_rule_from_dict(r) for r in rules_raw]
        validate_rules(rules)

        smtp = config.get("smtp")
        notifier = None
        if smtp and smtp.get("enabled"):
            notifier = EmailNotifier(
                SmtpConfig(
                    host=smtp["host"],
                    port=int(smtp.get("port", 587)),
                    username=smtp["username"],
                    password=smtp["password"],
                    from_email=smtp["from_email"],
                    to_email=smtp["to_email"],
                    use_tls=bool(smtp.get("use_tls", True)),
                )
            )

        self.interval_seconds = interval
        self.user_agent = config.get("user_agent", "Mozilla/5.0 VPS Monitor")
        self.rules = rules
        self.notifier = notifier
        self.raw_config = config

    def reload_config(self) -> None:
        self._apply_config(self._load_config_from_disk())

    def save_config(self, config: dict[str, Any]) -> None:
        self._apply_config(config)
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def get_config(self, mask_sensitive: bool = True) -> dict[str, Any]:
        config = json.loads(json.dumps(self.raw_config))
        if mask_sensitive and config.get("smtp", {}).get("password"):
            config["smtp"]["password"] = "******"
        return config

    def _fetch_html(self, url: str) -> str:
        req = Request(url, headers={"User-Agent": self.user_agent})
        with urlopen(req, timeout=25) as response:  # nosec B310
            return response.read().decode("utf-8", errors="ignore")

    def check_once(self) -> list[CheckResult]:
        batch: list[CheckResult] = []
        now = datetime.now().isoformat(timespec="seconds")

        for rule in self.rules:
            try:
                html = self._fetch_html(rule.url)
                in_stock, reason = detect_in_stock(html, rule)
                result = CheckResult(
                    site_name=rule.site_name,
                    product_name=rule.product_name,
                    url=rule.url,
                    in_stock=in_stock,
                    reason=reason,
                    checked_at=now,
                )
                batch.append(result)

                key = f"{rule.site_name}:{rule.product_name}"
                old = self._last_state.get(key)
                self._last_state[key] = in_stock
                if self.notifier and in_stock and old is False:
                    self.notifier.send_restock_alert(rule.site_name, rule.product_name, rule.url, reason)
            except Exception as exc:  # pylint: disable=broad-except
                self._errors.append(f"{now} | {rule.site_name}/{rule.product_name}: {exc}")

        with self._lock:
            self._results = batch
            self._errors = self._errors[-50:]

        return batch

    def _loop(self) -> None:
        while self._running:
            self.check_once()
            time.sleep(self.interval_seconds)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

    def status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "running": self._running,
                "interval_seconds": self.interval_seconds,
                "results": [asdict(r) for r in self._results],
                "errors": list(self._errors),
                "rules": [asdict(r) for r in self.rules],
            }
