# Soketi untuk Contabo (production)

Soketi (server WebSocket protokol Pusher) untuk production di VPS Contabo, di belakang Caddy (TLS otomatis).
Satu instance dipakai bersama oleh beberapa aplikasi (call2go, cscallpro, cscallbasic, dst.), tiap aplikasi
punya `id`/`key`/`secret` sendiri. Versi dev/lokal ada di repo `nanaaja/soketi`.

```
 browser / Android ──wss://pusher.callhub.id──▶ Caddy :443 ──▶ 127.0.0.1:6001 Soketi
 server PHP aplikasi ──(HTTP API, event)───────────────────────────▲
```

Isi repo: `docker-compose.yml` (port hanya ke 127.0.0.1), `Caddyfile`, `scripts/gen-config.py` (generator key),
`config/soketi.json.example`. `config/soketi.json` berisi key asli dan **tidak pernah di-commit**.

## Setup server (Ubuntu 24.04)

```bash
# 0. Firewall: izinkan SSH SEBELUM enable
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw enable

# 1. Docker + repo
curl -fsSL https://get.docker.com | sh
git clone https://github.com/faisalmohamadkosim-lgtm/soketi-contabo /opt/soketi && cd /opt/soketi

# 2. Key & secret baru (dicetak sekali -- simpan di password manager)
python3 scripts/gen-config.py                 # atau: python3 scripts/gen-config.py call2go parkirhub
docker compose up -d

# 3. Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install -y caddy
cp Caddyfile /etc/caddy/Caddyfile && systemctl reload caddy
```

Prasyarat: A record `pusher.callhub.id` → IP VPS (cek `nslookup pusher.callhub.id`).

## Cek

```bash
curl https://pusher.callhub.id/                     # OK
curl -s 127.0.0.1:9601/metrics | grep soketi_connected
docker logs soketi_app --tail 20
```

## Sambungkan aplikasi

Di tiap aplikasi, `includes/soketi.local.php` (di-gitignore di aplikasinya):

```php
define('SOKETI_APP_ID',     'call2go');          // sesuai id di config/soketi.json
define('SOKETI_APP_KEY',    '...');
define('SOKETI_APP_SECRET', '...');
define('SOKETI_WS_HOST', 'pusher.callhub.id');   // alamat untuk browser & Android
define('SOKETI_WS_PORT', 443);
define('SOKETI_WS_TLS',  true);
```

Aplikasi di server lain: pengiriman event dari PHP harus menjangkau Soketi lewat HTTPS
(`https://pusher.callhub.id`). Polling di aplikasi tetap menjadi cadangan kalau Soketi mati.

## Operasional

| Tugas | Perintah |
|---|---|
| Tambah/ubah app | edit `config/soketi.json` → `docker compose restart app` |
| Update image | ubah tag di `docker-compose.yml` → `docker compose pull && docker compose up -d` |
| Backup | cukup `config/soketi.json` (Soketi tidak menyimpan data) |
| Putar key | hapus `config/soketi.json`, jalankan `scripts/gen-config.py` lagi, perbarui tiap aplikasi |

Jangan membuka 6001/9601 ke internet. Kalau `curl` dari luar ke `http://IP:6001` berhasil, ada yang salah dengan
binding port di compose.
