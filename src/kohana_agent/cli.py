"""Offline-first project bootstrap CLI."""

import argparse
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import xml.etree.ElementTree as ET

from .memory import MemoryStore
from .profile import create_profile


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Кохана: профіль Hermes і локальні нотатки")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Створити окремий профіль Hermes")
    init.add_argument("--home", type=Path, required=True)
    init.add_argument("--persona", type=Path, required=True)
    sub.add_parser("doctor", help="Перевірити локальні залежності без мережі")
    memory = sub.add_parser("memory", help="Локальне сховище; ще не підключене до Hermes")
    memory.add_argument("--db", type=Path, required=True)
    actions = memory.add_subparsers(dest="action", required=True)
    add = actions.add_parser("add")
    add.add_argument("content")
    add.add_argument("--project", required=True)
    add.add_argument("--source", required=True)
    search = actions.add_parser("search")
    search.add_argument("query")
    search.add_argument("--project")
    search.add_argument("--limit", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            for path in create_profile(args.home, args.persona):
                print(path)
        elif args.command == "doctor":
            print(json.dumps({"python": sys.version.split()[0],
                              "sqlite": sqlite3.sqlite_version,
                              "hermes_executable": shutil.which("hermes"),
                              "hermes_integration_tested": False}, indent=2))
        else:
            store = MemoryStore(args.db)
            if args.action == "add":
                print(json.dumps({"id": store.add(args.content, project=args.project, source=args.source)}))
            else:
                print(json.dumps(store.search(args.query, project=args.project, limit=args.limit),
                                 ensure_ascii=False, indent=2))
    except (OSError, ValueError, ET.ParseError, sqlite3.Error) as error:
        print(f"Помилка: {error}", file=sys.stderr)
        return 1
    return 0
