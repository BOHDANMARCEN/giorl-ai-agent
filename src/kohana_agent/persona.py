"""Deterministic rendering of the versioned persona source."""

from pathlib import Path
import xml.etree.ElementTree as ET


def render_persona(source: Path) -> str:
    with source.open("rb") as stream:
        data = stream.read(256_001)
    if len(data) > 256_000:
        raise ValueError("Persona перевищує ліміт 256 KB")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("DTD та XML entities не підтримуються")
    root = ET.fromstring(data)
    if root.tag != "ai_persona" or root.get("version") != "3.0":
        raise ValueError("Потрібна ai_persona версії 3.0")
    if root.get("language") != "uk":
        raise ValueError("Очікується language=uk")
    required = {"identity", "priority_and_boundaries", "language_and_voice",
                "technical_partner", "context_and_memory", "response_contract"}
    if not required.issubset({child.tag for child in root}):
        raise ValueError("Відсутні обов'язкові розділи Persona")
    lines = ["# Кохана — Persona 3.0", "",
             "Згенеровано з XML. Редагуй джерело та створюй новий профіль.", ""]

    def visit(element: ET.Element, depth: int) -> None:
        attributes = ", ".join(f"{key}={value}" for key, value in element.attrib.items())
        label = element.tag + (f" ({attributes})" if attributes else "")
        if len(element):
            lines.extend([f"{'#' * min(depth + 2, 6)} {label}", ""])
            if element.text and element.text.strip():
                lines.extend([" ".join(element.text.split()), ""])
            for child in element:
                visit(child, depth + 1)
        else:
            content = " ".join((element.text or "").split())
            lines.append(f"- **{label}**: {content}")
        if element.tail and element.tail.strip():
            lines.append(" ".join(element.tail.split()))

    for section in root:
        visit(section, 0)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
