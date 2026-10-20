"""Create a dedicated Hermes profile without changing existing profiles."""

from pathlib import Path
import os
from .persona import render_persona


USER_TEMPLATE = """# Користувач
Мова спілкування: українська.
Ім'я, технічне середовище та вподобання: уточнити в користувача.
Не вважати старі відомості про обладнання актуальними без перевірки.
"""
MEMORY_TEMPLATE = """# Пам'ять
Новий профіль. Перевірених фактів про середовище поки немає.
"""


def create_profile(home: Path, source: Path) -> list[Path]:
    soul = render_persona(source)
    home = home.expanduser().resolve()
    # A dedicated new directory avoids clobbering live config, memory or secrets.
    home.parent.mkdir(parents=True, exist_ok=True)
    home.mkdir(mode=0o700, exist_ok=False)
    outputs = {
        home / "SOUL.md": soul,
        home / "memories" / "USER.md": USER_TEMPLATE,
        home / "memories" / "MEMORY.md": MEMORY_TEMPLATE,
    }
    (home / "memories").mkdir(mode=0o700)
    for path, content in outputs.items():
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
        os.chmod(path, 0o600)
    return list(outputs)
