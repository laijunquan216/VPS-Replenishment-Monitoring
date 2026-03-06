from __future__ import annotations

import smtplib
from email.message import EmailMessage
from dataclasses import dataclass


@dataclass
class SmtpConfig:
    host: str
    port: int
    username: str
    password: str
    from_email: str
    to_email: str
    use_tls: bool = True


class EmailNotifier:
    def __init__(self, config: SmtpConfig):
        self.config = config

    def send_restock_alert(self, site_name: str, product_name: str, url: str, reason: str) -> None:
        msg = EmailMessage()
        msg["Subject"] = f"[VPS补货通知] {site_name} - {product_name}"
        msg["From"] = self.config.from_email
        msg["To"] = self.config.to_email
        msg.set_content(
            "\n".join(
                [
                    "检测到 VPS 可能已补货。",
                    f"站点: {site_name}",
                    f"产品: {product_name}",
                    f"页面: {url}",
                    f"依据: {reason}",
                ]
            )
        )

        with smtplib.SMTP(self.config.host, self.config.port, timeout=20) as smtp:
            if self.config.use_tls:
                smtp.starttls()
            smtp.login(self.config.username, self.config.password)
            smtp.send_message(msg)
