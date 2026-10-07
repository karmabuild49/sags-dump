#!/usr/bin/env python3
"""ARKIV · sags-dump.py — pak noter til en sagsfil, inkl. database-dump."""
import os
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone


def take_u(argv):
    """Læs mål-URL enten som -u URL, --u=URL, --url=URL eller som første argument."""
    args = argv[1:]
    if not args:
        return ""
    if args[0] in ("-u", "--u", "--url") and len(args) > 1:
        return args[1]
    if args[0].startswith("--u=") or args[0].startswith("--url="):
        return args[0].split("=", 1)[1]
    return args[0]


def dump_database():
    """
    Dump en database via pg_dump eller mysqldump.
    Konfiguration via miljøvariabler:
      DB_ENGINE   = postgres | mysql  (auto-detekteret hvis tom)
      DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    Returnerer (navn, dump-tekst) eller (navn, fejlbesked).
    """
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "")
    name = os.environ.get("DB_NAME", "")
    user = os.environ.get("DB_USER", "")
    password = os.environ.get("DB_PASSWORD", "")
    engine = (os.environ.get("DB_ENGINE") or "").lower()

    if not name:
        return None, "Ingen DB_NAME angivet — database-dump sprunget over."

    if not engine:
        if shutil.which("pg_dump"):
            engine = "postgres"
        elif shutil.which("mysqldump"):
            engine = "mysql"
        else:
            return None, "Hverken pg_dump eller mysqldump fundet — dump sprunget over."

    env = dict(os.environ)
    if password:
        env["PGPASSWORD"] = password
        env["MYSQL_PWD"] = password

    if engine == "postgres":
        port = port or "5432"
        cmd = ["pg_dump", "-h", host, "-p", port]
        if user:
            cmd += ["-U", user]
        cmd += [name]
    elif engine == "mysql":
        port = port or "3306"
        cmd = ["mysqldump", f"-h{host}", f"-P{port}"]
        if user:
            cmd += [f"-u{user}"]
        cmd += [name]
    else:
        return None, f"Ukendt DB_ENGINE: {engine!r}"

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=600, env=env
        )
    except FileNotFoundError:
        return engine, f"Fejl: {cmd[0]} er ikke installeret."
    except subprocess.TimeoutExpired:
        return engine, "Fejl: database-dump fik timeout (600 s)."

    if result.returncode != 0:
        return engine, f"Fejl under dump (exit {result.returncode}):\n{result.stderr.strip()}"
    return engine, result.stdout


def main() -> None:
    target = take_u(sys.argv) or "(intet mål)"
    note = sys.stdin.read().strip()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    engine, dump = dump_database()
    dump_label = f"database-dump ({engine})" if engine else "database-dump"

    print("# Arkiv sag")
    print(f"tid\t{stamp}")
    print(f"mål\t{shlex.quote(target)}")
    print()
    print(note or "(ingen note)")
    print()
    if dump and not dump.startswith("Fejl") and not dump.startswith("Ingen") and not dump.startswith("Hverken"):
        print(f"## BEGIN {dump_label}")
        print(dump.rstrip())
        print(f"## END {dump_label}")
    else:
        print(f"({dump})")


if __name__ == "__main__":
    main()
