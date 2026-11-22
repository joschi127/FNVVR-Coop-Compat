# FNVVR-Coop-Compat (https://github.com/joschi127/FNVVR-Coop-Compat), an addition to New Vegas Co-op by Zyrcxies.
# Licence: see LICENSE (the same as New Vegas Co-op).
"""Co-op test helper: host in the real game, a fakefriend joins (FNVVR-Coop-Compat).

Runs a co-op session without a second person or game copy: the game hosts automatically
(NVCoop.ini Mode=host, AutoApproveJoins=1) as soon as a save past the intro is loaded, and
fakefriend joins it by IP on this PC. Works with the flat game and with FNVVR (headset or
emulator); it does not need FNVVR or FNVVR-Test-Bridge.

    python -I tools/coop_test.py ini-host  --game <game folder>   NVCoop.ini for the test (keeps a backup)
    python -I tools/coop_test.py ini-restore --game <game folder> back to the backup, checked byte for byte
    python -I tools/coop_test.py wait-host --game <game folder> [--timeout 300]
    python -I tools/coop_test.py friend --exe <fakefriend.exe> --log <file> [fakefriend options ...]
    python -I tools/coop_test.py wait-join --game <game folder> [--name FakeFriend] [--timeout 60]

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
        """Sets the [Coop] keys for automatic hosting; keeps the original next to it (once)."""
        values = dict(HOST_VALUES, **(values or {}))
        if os.path.exists(self.backup):
            raise RuntimeError(f"a backup exists already ({self.backup}): restore first")
        shutil.copy2(self.ini, self.backup)
        with open(self.ini, encoding="utf-8", newline="") as f:
            lines = f.read().splitlines(keepends=True)
        seen = set()
        for i, line in enumerate(lines):
            m = re.match(r"^(\s*)([A-Za-z]+)(\s*=\s*)([^\r\n]*)(\r?\n?)$", line)
            if m and m.group(2) in values:
                lines[i] = f"{m.group(1)}{m.group(2)}{m.group(3)}{values[m.group(2)]}{m.group(5)}"
                seen.add(m.group(2))
        missing = [k for k in values if k not in seen]
        if missing:
            idx = next((i + 1 for i, l in enumerate(lines) if l.strip().lower() == "[coop]"), None)
            if idx is None:
                raise RuntimeError("no [Coop] section in NVCoop.ini")
            nl = "\r\n" if lines and lines[0].endswith("\r\n") else "\n"
            for k in missing:
                lines.insert(idx, f"{k}={values[k]}{nl}")
        with open(self.ini, "w", encoding="utf-8", newline="") as f:
            f.write("".join(lines))

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

    def wait_log(self, pattern, timeout, since=0, poll=0.5):
        """Waits for a line matching pattern in NVCoop.log after byte offset since; returns the line."""
        rx = re.compile(pattern)
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if os.path.exists(self.log):
                with open(self.log, "rb") as f:
                    if os.path.getsize(self.log) < since:
                        since = 0  # a new log (game restarted)
                    f.seek(since)
                    for raw in f.read().decode("utf-8", "replace").splitlines():
                        if rx.search(raw):
                            return raw
            time.sleep(poll)
        raise TimeoutError(f"no line /{pattern}/ in {self.log} within {timeout} s")

    def wait_host(self, timeout=300, since=0):
        return self.wait_log(r"Hosting (on port|as)", timeout, since)

    def wait_join(self, name="FakeFriend", timeout=60, since=0):
        return self.wait_log(re.escape(name) + r" joined as player", timeout, since)

    # fakefriend

    def start_friend(self, exe, options=(), log_path=None, address="127.0.0.1", port=27960, name="FakeFriend"):
        """Starts fakefriend joining this PC; its output goes to log_path (or is dropped)."""
        if self.friend and self.friend.poll() is None:
            raise RuntimeError("fakefriend runs already")
        out = open(log_path, "w", encoding="utf-8") if log_path else subprocess.DEVNULL
        self.friend = subprocess.Popen([exe, "join", address, str(port), name, *options],
                                       stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
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
    args, rest = p.parse_known_args()
    t = CoopTest(args.game or ".")
    if args.command == "ini-host":
        t.ini_host()
    elif args.command == "ini-restore":
        t.ini_restore()
    elif args.command == "wait-host":
        print(t.wait_host(args.timeout or 300))
    elif args.command == "wait-join":
        print(t.wait_join(args.name, args.timeout or 60))
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
