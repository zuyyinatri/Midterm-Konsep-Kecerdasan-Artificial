# Weighted Tower of Hanoi: BFS, UCS, Greedy Best-First, dan A*

Proyek Midterm mata kuliah **Konsep Kecerdasan Artificial**, Teknik Informatika ITS (2026).

**Anggota kelompok**

| Nama | NRP |
|---|---|
| Chairunnisa' Tsabitah | 5025251023 |
| Elba Galuh Hardiyanti | 5025251025 |
| Muhammad Adinata Parikesit | 5025251041 |
| Tri Zuyyina Rohmah | 5025251043 |

---

Aplikasi ini membandingkan empat algoritma pencarian pada masalah **Tower of Hanoi berbobot** dengan 3 sampai 5 tiang dan 3 sampai 7 cakram. Proyek ini dibuat untuk mata kuliah Konsep Kecerdasan Artificial (Teknik Informatika ITS). Tujuannya bukan sekadar menyelesaikan puzzle, tetapi memperlihatkan **mengapa tiap algoritma ada**: masing-masing menjawab pertanyaan yang berbeda tentang "solusi mana yang dianggap terbaik" dan "berapa banyak usaha pencarian yang rela dikeluarkan".

## Masalah yang dipecahkan

Cakram dengan ukuran berbeda berada di beberapa tiang. Tujuannya memindahkan semua cakram dari tiang A ke tiang terakhir. Aturannya: satu cakram teratas per langkah, dan cakram besar tidak boleh di atas cakram yang lebih kecil.

Versi ini diberi **biaya berbobot**, meniru rumus usaha `W = F x s`:

```
biaya langkah = ukuran cakram x jarak antar tiang
```

Memindahkan cakram 5 dari A ke D berbiaya 5 x 3 = 15, sedangkan cakram 1 dari A ke B berbiaya 1 x 1 = 1. Karena biaya tidak seragam, **solusi dengan langkah paling sedikit belum tentu solusi termurah**. Inilah yang membuat keempat algoritma menjadi berbeda satu sama lain.

## Untuk apa tiap algoritma ada

| Algoritma | Berkas | Pertanyaan yang dijawab | Kelebihan | Kekurangan |
|---|---|---|---|---|
| **BFS** | `bfs.py` | Berapa jumlah langkah paling sedikit? | Menjamin langkah minimum; sederhana | Mengabaikan biaya, sehingga bisa mahal |
| **UCS** | `ucs.py` | Berapa biaya total paling murah? | Menjamin biaya minimum; dipakai sebagai pembanding "optimal" | Menjelajah banyak state karena tidak punya arah |
| **Greedy Best-First** | `greedy.py` | Mana state yang tampak paling dekat tujuan sekarang? | Cepat dan hemat ekspansi | Tidak menjamin optimal; bisa sangat mahal |
| **A\*** | `astar.py` | Bagaimana mendapat biaya minimum tanpa menjelajah semuanya? | Optimal dan jauh lebih hemat ekspansi daripada UCS | Butuh heuristik yang baik; frontier bisa besar |

Cara masing-masing memilih state berikutnya dari frontier:

- **BFS:** urutan masuk antrean (FIFO), tanpa melihat biaya.
- **UCS:** `g(n)` terkecil, yaitu biaya yang sudah dikeluarkan dari state awal.
- **Greedy:** `h(n)` terkecil, yaitu perkiraan sisa biaya ke tujuan.
- **A\*:** `f(n) = g(n) + h(n)` terkecil, yaitu gabungan biaya yang sudah dikeluarkan dan perkiraan sisanya.

### Heuristik

```
h(n) = jumlah dari (ukuran cakram x jarak tiangnya ke tiang tujuan), untuk semua cakram
```

Heuristik ini **admissible** (tidak pernah melebihi biaya sebenarnya, karena tiap cakram minimal harus menempuh jarak itu) dan **consistent** (satu langkah menurunkan `h` paling banyak sebesar biaya langkah itu). Karena itu A\* menjamin solusi optimal. Heuristik ini belum memperhitungkan bahwa cakram kecil harus menyingkir lebih dulu, sehingga masih lemah.

## Contoh hasil (4 tiang, 5 cakram)

| Algoritma | Langkah | Biaya | Optimal? | Diekspansi | Dibangkitkan | Frontier maks. |
|---|---|---|---|---|---|---|
| BFS | 13 | 67 | Tidak | 983 | 5745 | 283 |
| UCS | 13 | 55 | Ya | 1023 | 5949 | 249 |
| Greedy | 58 | 173 | Tidak | 389 | 2257 | 242 |
| A\* | 15 | 55 | Ya | 364 | 2114 | 413 |

Yang bisa dipelajari dari tabel ini:

- BFS menemukan 13 langkah, tetapi biayanya 67, lebih mahal daripada UCS yang juga 13 langkah dengan biaya 55.
- Greedy cepat mencapai tujuan menurut jumlah ekspansi, tetapi solusinya 58 langkah dan berbiaya 173.
- A\* mendapat biaya optimal yang sama dengan UCS dengan ekspansi sekitar 64% lebih sedikit.
- Angka frontier dihitung sebagai panjang antrean prioritas, termasuk entri usang pada UCS dan A\*.

Jumlah langkah bergantung pada pasangan tiang dan cakram. Contohnya 3 tiang dengan 3 cakram selalu 7 langkah.

## Struktur berkas

| Berkas | Isi |
|---|---|
| `hanoi_common.py` | Definisi masalah, biaya langkah, heuristik, input parameter, dan tampilan tabel |
| `bfs.py` | Breadth-First Search (uji tujuan saat state dibangkitkan) |
| `ucs.py` | Uniform-Cost Search |
| `greedy.py` | Greedy Best-First Search |
| `astar.py` | A\* Search |
| `hanoi_app.py` | Aplikasi GUI (Tkinter) dengan animasi solusi dan tabel perbandingan |

Representasi state: tuple dengan panjang `n`, dengan `state[i]` berisi indeks tiang tempat cakram ke-`i` berada. State awal berisi semua cakram di tiang A, dan state tujuan berisi semua cakram di tiang terakhir.

## Cara menjalankan

Tidak perlu menginstal apa pun. Cukup Python 3 (Tkinter sudah bawaan Python), dan semua berkas harus berada di folder yang sama.

**Aplikasi GUI:**

```bash
python hanoi_app.py
```

Pilih jumlah tiang dan cakram (default 4 tiang, 5 cakram), lalu klik **Solve** untuk satu algoritma atau **Bandingkan semua algoritma**. Klik baris pada tabel untuk memutar animasi solusi algoritma tersebut. Tombol animasi tersedia untuk play, pause, langkah mundur dan maju, serta lompat ke awal atau akhir, dengan kecepatan yang bisa diatur.

**Baris perintah (satu algoritma):**

```bash
python bfs.py    -k 4 -n 5
python ucs.py    -k 4 -n 5
python greedy.py -k 4 -n 5
python astar.py  -k 4 -n 5
```

Opsi `--steps all|auto|none` mengatur apakah tabel tiap langkah ditampilkan. Mode `auto` menampilkannya jika solusi tidak lebih dari 60 langkah. Jika `-k` dan `-n` tidak diberikan, program akan menanyakannya.

## Batasan

- Jumlah tiang 3 sampai 5 dan cakram 3 sampai 7.
- Bobot cakram sama dengan ukurannya (`disk_weight` di `hanoi_common.py` bisa diubah).
- Waktu eksekusi bergantung pada perangkat dan hanya cocok untuk perbandingan relatif.
- Hasil di atas berlaku untuk urutan pembangkitan aksi dan aturan pemutus seri yang dipakai di kode; sifat optimalitas tiap algoritma tidak berubah jika keduanya diganti, tetapi jumlah ekspansi bisa bergeser.
