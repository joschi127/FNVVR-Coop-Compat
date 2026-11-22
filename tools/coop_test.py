# FNVVR-Coop-Compat (https://github.com/joschi127/FNVVR-Coop-Compat), an addition to New Vegas Co-op by Zyrcxies.
# Licence: see LICENSE (the same as New Vegas Co-op).
"""Co-op test helper: host in the real game, a fakefriend joins (FNVVR-Coop-Compat).

Runs a co-op session without a second person or game copy: the game hosts automatically
(NVCoop.ini Mode=host, AutoApproveJoins=1) as soon as a save past the intro is loaded, and
fakefriend joins it by IP on this PC. Works with the flat game and with FNVVR (headset or
emulator); it does not need FNVVR or FNVVR-Test-Bridge.

    python -I tools/coop_test.py ini-host  --game <game folder>   NVCoop.ini for the test (keeps a backup)
    python -I tools/coop_test.py ini-restore --game <game folder> back to the backup, checked byte for byte
    python -I tools/coop_test.py wait-host --game <game folder> [--timeout 300] [--newer-than <time>]
    python -I tools/coop_test.py friend --exe <fakefriend.exe> --log <file> [fakefriend options ...]
    python -I tools/coop_test.py wait-join --game <game folder> [--name FakeFriend] [--timeout 60] [--newer-than <time>]

Pass --newer-than with the time taken just before starting the game (date +%s), so that a line of the
previous session's NVCoop.log does not count.

The same functions can be imported (CoopTest). Call ini-host before the game starts (NVCoop.ini in
Data/NVSE/Plugins is read once at start) and ini-restore after it has quit. Load a save past the intro
(left Doc Mitchell's house); co-op starts hosting within a few seconds.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import time

INI = os.path.join("Data", "NVSE", "Plugins", "NVCoop.ini")
BACKUP_SUFFIX = ".coop-test-backup"
LOG = "NVCoop.log"
HOST_VALUES = {"Mode": "host", "AutoApproveJoins": "1", "IpHosting": "1"}


class CoopTest:
    def __init__(self, game):
        self.game = game
        self.ini = os.path.join(game, INI)
        self.backup = self.ini + BACKUP_SUFFIX
        self.log = os.path.join(game, LOG)
        self.friend = None

    # NVCoop.ini

    def ini_host(self, values=None):
        """Sets the [Coop] keys for automatic hosting; keeps the original next to it (once).

        The game writes the file in the ANSI code page: it is read and written byte for byte (latin-1),
        keys are matched in [Coop] only and without case, as GetPrivateProfileString does."""
        values = dict(HOST_VALUES, **(values or {}))
        if os.path.exists(self.backup):
            raise RuntimeError(f"a backup exists already ({self.backup}): restore first")
        with open(self.ini, encoding="latin-1", newline="") as f:
            text = f.read()
        lines = text.split("\n")
        wanted = {k.lower(): k for k in values}
        seen, section, coop_line = set(), "", None
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("[") and "]" in stripped:
                section = stripped[1:stripped.index("]")].strip().lower()
                if section == "coop" and coop_line is None:
                    coop_line = i
                continue
            m = re.match(r"^(\s*)([^=;\s]+)(\s*=\s*)([^\r]*)(\r?)$", line)
            if section == "coop" and m and m.group(2).lower() in wanted:
                key = wanted[m.group(2).lower()]
                lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}{values[key]}{m.group(5)}"
                seen.add(key)
        missing = [k for k in values if k not in seen]
        if missing:
            if coop_line is None:
                raise RuntimeError("no [Coop] section in NVCoop.ini")
            cr = "\r" if lines and lines[0].endswith("\r") else ""
            for k in missing:
                lines.insert(coop_line + 1, f"{k}={values[k]}{cr}")
        result = "\n".join(lines)
        # The backup only once the new text is ready, so that a failure leaves nothing behind
        shutil.copy2(self.ini, self.backup)
        with open(self.ini, "w", encoding="latin-1", newline="") as f:
            f.write(result)

    def ini_port(self):
        """The port of [Coop] in NVCoop.ini (27960 when not set or without the file)."""
        section = ""
        if not os.path.exists(self.ini):
            return 27960
        with open(self.ini, encoding="latin-1") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("[") and "]" in stripped:
                    section = stripped[1:stripped.index("]")].strip().lower()
                elif section == "coop" and "=" in stripped and stripped.split("=", 1)[0].strip().lower() == "port":
                    try:
                        return int(stripped.split("=", 1)[1].strip())
                    except ValueError:
                        break
        return 27960

    def ini_restore(self):
        if not os.path.exists(self.backup):
            raise RuntimeError(f"no backup ({self.backup})")
        shutil.copy2(self.backup, self.ini)
        with open(self.backup, "rb") as a, open(self.ini, "rb") as b:
            if a.read() != b.read():
                raise RuntimeError("NVCoop.ini differs from the backup after restoring")
        os.remove(self.backup)

    # NVCoop.log

    def log_size(self):
        return os.path.getsize(self.log) if os.path.exists(self.log) else 0

    def wait_log(self, pattern, timeout, since=0, newer_than=None, poll=0.5):
        """Waits for a line matching pattern in NVCoop.log; returns the line.

        since: byte offset to start at in the current log. newer_than: a time (time.time()) taken before the
        game started: a log last written before it is the previous session's and is not read (the game starts
        a new NVCoop.log at each start). Without either, an old log's line counts too."""
        rx = re.compile(pattern)
        end = time.monotonic() + timeout
        while True:
            if os.path.exists(self.log) and (newer_than is None or os.path.getmtime(self.log) >= newer_than):
                with open(self.log, "rb") as f:
                    if os.path.getsize(self.log) < since:
                        since = 0  # a new log (game restarted)
                    f.seek(since)
                    for raw in f.read().decode("utf-8", "replace").splitlines():
                        if rx.search(raw):
                            return raw
            if time.monotonic() >= end:
                raise TimeoutError(f"no line /{pattern}/ in {self.log} within {timeout} s")
            time.sleep(poll)

    def wait_host(self, timeout=300, since=0, newer_than=None):
        # Hosting by IP, which fakefriend joins (Steam-only hosting logs "Hosting as" alone)
        return self.wait_log(r"Hosting on port", timeout, since, newer_than)

    def wait_join(self, name="FakeFriend", timeout=60, since=0, newer_than=None):
        return self.wait_log(re.escape(name) + r" joined as player", timeout, since, newer_than)

    # fakefriend

    def start_friend(self, exe, options=(), log_path=None, address="127.0.0.1", port=None, name="FakeFriend"):
        """Starts fakefriend joining this PC (port: NVCoop.ini's); its output goes to log_path (or is dropped)."""
        if self.friend and self.friend.poll() is None:
            raise RuntimeError("fakefriend runs already")
        port = port or self.ini_port()
        out = open(log_path, "w", encoding="utf-8") if log_path else subprocess.DEVNULL
        try:
            self.friend = subprocess.Popen([exe, "join", address, str(port), name, *options],
                                           stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        finally:
            if out is not subprocess.DEVNULL:
                out.close()  # the child has its own handle
        return self.friend

    def stop_friend(self, timeout=5):
        if self.friend and self.friend.poll() is None:
            self.friend.terminate()
            try:
                self.friend.wait(timeout)
            except subprocess.TimeoutExpired:
                self.friend.kill()
        self.friend = None


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("command", choices=["ini-host", "ini-restore", "wait-host", "friend", "wait-join"])
    p.add_argument("--game", help="game folder (with FalloutNV.exe)")
    p.add_argument("--exe", help="fakefriend.exe")
    p.add_argument("--log", help="file for fakefriend's output")
    p.add_argument("--name", default="FakeFriend")
    p.add_argument("--timeout", type=float, default=None)
    p.add_argument("--newer-than", type=float, default=None,
                   help="wait-host/wait-join: ignore a log last written before this time (seconds since 1970), "
                        "taken before the game was started")
    args, rest = p.parse_known_args()
    t = CoopTest(args.game or ".")
    if args.command == "ini-host":
        t.ini_host()
    elif args.command == "ini-restore":
        t.ini_restore()
    elif args.command == "wait-host":
        print(t.wait_host(300 if args.timeout is None else args.timeout, newer_than=args.newer_than))
    elif args.command == "wait-join":
        print(t.wait_join(args.name, 60 if args.timeout is None else args.timeout, newer_than=args.newer_than))
    elif args.command == "friend":
        if not args.exe:
            p.error("friend needs --exe")
        proc = t.start_friend(args.exe, rest, args.log, name=args.name)
        try:
            sys.exit(proc.wait())
        except KeyboardInterrupt:
            t.stop_friend()
    return 0


if __name__ == "__main__":
    sys.exit(main())
