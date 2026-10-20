# Робота з GitHub

Основний репозиторій: [BOHDANMARCEN/giorl-ai-agent](https://github.com/BOHDANMARCEN/giorl-ai-agent).

```bash
git clone https://github.com/BOHDANMARCEN/giorl-ai-agent.git
cd giorl-ai-agent
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Назва репозиторію — `giorl-ai-agent`; Python-пакет залишається `kohana-agent`, CLI — `kohana`.

Основна гілка: `main`. Для подальшої розробки створюй окремі гілки та PR. Workflow `checks` запускає unit-тести на Python 3.11, 3.12 та 3.13. Результат конкретного запуску перевіряй у вкладці Actions.

Репозиторій публічний. Профілі `.kohana/`, бази, `.env`, API-ключі та історія діалогів мають залишатися поза Git. Перед комітом перевіряй `git diff --cached`.
