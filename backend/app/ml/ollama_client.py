"""Optional local LLM for drop parsing and trip copy. Fails closed to rules."""

from __future__ import annotations

import json
import re

import httpx

from app.config import Settings
from app.models.schemas import DropZone, ParsedDrop


def _match_rules(text: str, zones: list[DropZone]) -> ParsedDrop | None:
    haystack = text.lower().strip()
    best: DropZone | None = None
    score = 0.0
    for zone in zones:
        names = [zone.name.lower(), zone.id.replace("-", " "), *zone.aliases]
        for name in names:
            if name and name in haystack:
                hit = 0.92 if name == haystack else 0.8
                if hit > score:
                    best = zone
                    score = hit
    if not best:
        return None
    return ParsedDrop(
        zone_id=best.id,
        zone_name=best.name,
        lat=best.lat,
        lng=best.lng,
        confidence=score,
        source="rules",
    )


def _fallback_zone(zones: list[DropZone]) -> ParsedDrop:
    zone = zones[0]
    return ParsedDrop(
        zone_id=zone.id,
        zone_name=zone.name,
        lat=zone.lat,
        lng=zone.lng,
        confidence=0.35,
        source="rules",
    )


def parse_drop(text: str, zones: list[DropZone], settings: Settings) -> ParsedDrop:
    ruled = _match_rules(text, zones)
    prompt = (
        "You convert a metro rider drop request in Gandhinagar into JSON. "
        f"Allowed zone ids: {[z.id for z in zones]}. "
        'Reply with JSON only: {"zone_id": "...", "confidence": 0.0}. '
        f"Request: {text}"
    )
    try:
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1},
        }
        with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
            response = client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
        response.raise_for_status()
        raw = response.json().get("response", "")
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return ruled or _fallback_zone(zones)
        data = json.loads(match.group(0))
        zone = next((z for z in zones if z.id == data.get("zone_id")), None)
        if not zone:
            return ruled or _fallback_zone(zones)
        return ParsedDrop(
            zone_id=zone.id,
            zone_name=zone.name,
            lat=zone.lat,
            lng=zone.lng,
            confidence=float(data.get("confidence", 0.7)),
            source="ollama",
        )
    except (httpx.HTTPError, json.JSONDecodeError, ValueError, KeyError):
        return ruled or _fallback_zone(zones)


def write_summary(
    station_name: str,
    drop_name: str,
    bay: int,
    slot_label: str,
    vehicle_type: str,
    fare_inr: int,
    settings: Settings,
) -> str:
    fallback = (
        f"You leave {station_name} for {drop_name}. "
        f"Pickup is bay {bay} at {slot_label} in a shared {vehicle_type}. "
        f"Fare is {fare_inr} rupees, paid in one tap."
    )
    prompt = (
        "Write two calm sentences for a metro rider. No exclamation marks. "
        f"Station {station_name}, drop {drop_name}, bay {bay}, "
        f"slot {slot_label}, vehicle {vehicle_type}, fare {fare_inr} INR."
    )
    try:
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.4},
        }
        with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
            response = client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
        response.raise_for_status()
        text = str(response.json().get("response", "")).strip()
        if not text or "!" in text:
            return fallback
        return text
    except httpx.HTTPError:
        return fallback
