# Discord User Scrapper

Script Python kecil yang **memantau channel Discord tertentu** secara real-time, membersihkan isi pesannya, lalu menyimpannya ke file teks dan CSV. Kalau sebuah pesan mengandung kata `BUY` / `SELL` beserta angka harga, harganya ikut diekstrak ke kolom terpisah di CSV.

Cocok untuk mencatat penawaran jual-beli di channel trading (misalnya daftar harga yang diposting penjual).

> ⚠️ **Baca bagian [Peringatan](#peringatan) sebelum menjalankan.** Script ini login memakai token akun user (bukan bot), yang melanggar Ketentuan Layanan Discord.

## Fitur

- Memantau satu atau beberapa channel sekaligus (`CHANNEL_IDS`).
- Mengabaikan pesan dari bot.
- Membersihkan pesan: menghapus emoji custom (`<:nama:123>`), format markdown (`**`, `__`, `~~`), dan spasi berlebih.
- Mengekstrak harga `BUY` dan `SELL` dengan regex.
- Menyimpan hasil ke tiga file di folder `data/`.

## Struktur Folder

```
discord-user-scrapper/
├── user_scraper.py      # script utama
├── requirements.txt     # dependensi Python
├── .env.example         # contoh konfigurasi (salin jadi .env)
├── .gitignore
├── README.md
└── data/                # hasil scrape (otomatis dibuat, di-ignore git)
    ├── scraped_messages.txt   # semua pesan yang sudah dibersihkan
    ├── scraped_messages.csv   # hanya pesan yang punya harga BUY/SELL
    ├── parsed_messages.txt    # log ringkas pesan yang masuk ke CSV
    └── user_trades.db         # database SQLite lama (belum dipakai script)
```

## Instalasi

Butuh Python 3.8 atau lebih baru (proyek ini dikembangkan dengan Python 3.13).

```bash
# 1. buat dan aktifkan virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. install dependensi
pip install -r requirements.txt
```

## Konfigurasi

1. Salin `.env.example` menjadi `.env`:

   ```bash
   cp .env.example .env        # Windows: copy .env.example .env
   ```

2. Isi `DISCORD_TOKEN` di `.env` dengan token akun Discord kamu.

3. Buka `user_scraper.py` dan ganti isi `CHANNEL_IDS` dengan ID channel yang ingin dipantau:

   ```python
   CHANNEL_IDS = [
       123456789012345678,
       234567890123456789,
   ]
   ```

   Cara mendapatkan ID channel: aktifkan **Developer Mode** di Discord (Settings → Advanced), lalu klik kanan channel → **Copy Channel ID**.

## Menjalankan

```bash
python user_scraper.py
```

Kalau berhasil, terminal menampilkan `✅ Login sebagai ...` dan daftar channel yang dipantau. Setiap pesan baru yang masuk akan dicetak dan disimpan. Hentikan dengan `Ctrl + C`.

## Format Output

**`data/scraped_messages.txt`** — satu baris per pesan:

```
[2025-08-23 14:39:36] username#0 | SELL TONS 2.050 205.000 READY ALL PAYMENT
```

**`data/scraped_messages.csv`** — hanya pesan yang mengandung harga BUY atau SELL:

| Kolom | Isi |
|-------|-----|
| `Timestamp` | waktu pesan diterima script |
| `Author` | username pengirim |
| `Buy Price` | angka pertama setelah kata `BUY` (kosong jika tidak ada) |
| `Sell Price` | angka pertama setelah kata `SELL` (kosong jika tidak ada) |
| `Full Message` | isi pesan setelah dibersihkan |

Harga diambil apa adanya sebagai teks (misalnya `1.950`), tidak dikonversi ke angka.

**`data/parsed_messages.txt`** — log ringkas untuk setiap baris yang ditulis ke CSV.

File-file ini bersifat *append*: setiap kali script dijalankan, data baru ditambahkan di bawah data lama.

## Cara Kerja Singkat

1. `discord.Client()` dari `discord.py-self` login memakai `DISCORD_TOKEN`.
2. Event `on_message` memeriksa apakah pesan berasal dari channel di `CHANNEL_IDS` dan bukan dari bot.
3. Isi pesan dibersihkan (`clean_message`), ditulis ke file mentah, lalu dicocokkan dengan regex `BUY` / `SELL`.
4. Jika ada harga, baris baru ditambahkan ke CSV dan log parsed.

## Peringatan

- **Melanggar ToS Discord.** Memakai token akun pengguna untuk mengotomatisasi akun (self-bot) tidak diizinkan oleh Discord dan **akun bisa dibanned**. Gunakan dengan risiko sendiri, sebaiknya bukan di akun utama.
- **Jaga kerahasiaan token.** Token memberi akses penuh ke akun. Jangan pernah commit file `.env`, kirim lewat chat, atau menyertakannya dalam file zip yang dibagikan. Kalau token pernah bocor, ubah password akun Discord agar token lama tidak berlaku lagi.
- **Privasi.** Hasil scrape berisi username dan pesan orang lain. Folder `data/` sudah masuk `.gitignore`; jangan dipublikasikan tanpa izin, dan patuhi aturan server tempat kamu memantau.

## Catatan

- Script hanya mencatat pesan yang masuk *selama script berjalan*; riwayat pesan lama tidak diambil.
- `user_trades.db` (tabel `trades`) adalah sisa dari versi sebelumnya dan tidak dibaca atau ditulis oleh `user_scraper.py` saat ini.
- Variabel `CHANNEL_IDS` dibaca dari `user_scraper.py`, bukan dari `.env`.
