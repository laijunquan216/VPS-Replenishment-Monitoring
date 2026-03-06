from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Optional


@dataclass
class DetectorRule:
    """Generic stock detector rule that works for different VPS websites."""

    site_name: str
    url: str
    product_name: str
    # Pattern for finding the product card/section in HTML.
    product_anchor: str
    # If any unavailable token appears near the product anchor => out of stock.
    unavailable_tokens: tuple[str, ...] = (
        "out of stock",
        "sold out",
        "缺货",
        "缺货中",
        "0 available",
        "0 可用",
        "0可用",
    )
    # If available token appears near anchor => in stock.
    available_tokens: tuple[str, ...] = (
        "order now",
        "buy now",
        "available",
        "立即购买",
        "有货",
    )
    window_size: int = 1200


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower()


def extract_product_window(html: str, product_anchor: str, window_size: int = 1200) -> Optional[str]:
    normalized = _normalize(html)
    anchor = _normalize(product_anchor)
    idx = normalized.find(anchor)
    if idx < 0:
        return None
    start = max(0, idx - window_size // 3)
    end = min(len(normalized), idx + window_size)
    return normalized[start:end]


def detect_in_stock(html: str, rule: DetectorRule) -> tuple[bool, str]:
    """Return (is_in_stock, reason)."""

    window = extract_product_window(html, rule.product_anchor, rule.window_size)
    if window is None:
        return False, f"未找到产品锚点: {rule.product_anchor}"

    for token in rule.unavailable_tokens:
        if _normalize(token) in window:
            return False, f"检测到缺货关键词: {token}"

    for token in rule.available_tokens:
        if _normalize(token) in window:
            return True, f"检测到有货关键词: {token}"

    return False, "未匹配到有货关键词，默认视为缺货"


def build_rule_from_dict(raw: dict) -> DetectorRule:
    required = ["site_name", "url", "product_name", "product_anchor"]
    missing = [k for k in required if not raw.get(k)]
    if missing:
        raise ValueError(f"规则缺少字段: {', '.join(missing)}")

    return DetectorRule(
        site_name=raw["site_name"],
        url=raw["url"],
        product_name=raw["product_name"],
        product_anchor=raw["product_anchor"],
        unavailable_tokens=tuple(raw.get("unavailable_tokens") or DetectorRule.unavailable_tokens),
        available_tokens=tuple(raw.get("available_tokens") or DetectorRule.available_tokens),
        window_size=int(raw.get("window_size") or 1200),
    )


def validate_rules(rules: Iterable[DetectorRule]) -> None:
    for rule in rules:
        if not rule.url.startswith(("http://", "https://")):
            raise ValueError(f"URL 非法: {rule.url}")
