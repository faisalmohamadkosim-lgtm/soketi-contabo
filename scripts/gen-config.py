#!/usr/bin/env python3
"""Buat config/soketi.json dengan key & secret acak untuk tiap aplikasi.

Pemakaian (dari folder repo):
    python3 scripts/gen-config.py                      # call2go cscallpro cscallbasic
    python3 scripts/gen-config.py call2go parkirhub    # daftar sendiri

Menolak menimpa config yang sudah ada (supaya key production tidak hilang tanpa sengaja);
hapus config/soketi.json dulu kalau memang mau membuat ulang.
Hasilnya dicetak sekali: salin ke includes/soketi.local.php tiap aplikasi.
"""
import json
import os
import secrets
import sys

DEFAULT_APPS = ["call2go", "cscallpro", "cscallbasic"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "soketi.json")


def main():
    apps = sys.argv[1:] or DEFAULT_APPS
    if os.path.exists(OUT):
        sys.exit("config/soketi.json sudah ada -- tidak ditimpa. Hapus dulu kalau memang mau dibuat ulang.")

    entries = [{
        "id": a,
        "key": secrets.token_hex(16),
        "secret": secrets.token_hex(24),
        "maxConnections": -1,
        "enableClientMessages": False,
        "enabled": True,
        "maxBackendEventsPerSecond": -1,
        "maxClientEventsPerSecond": -1,
        "maxReadRequestsPerSecond": -1,
        "webhooks": [],
    } for a in apps]

    with open(OUT, "w") as f:
        json.dump({"appManager.driver": "array", "appManager.array.apps": entries}, f, indent=2)
    os.chmod(OUT, 0o600)

    print("config/soketi.json dibuat. Simpan kredensial ini (hanya dicetak sekali):\n")
    for e in entries:
        print("%-14s key=%s  secret=%s" % (e["id"], e["key"], e["secret"]))


if __name__ == "__main__":
    main()
