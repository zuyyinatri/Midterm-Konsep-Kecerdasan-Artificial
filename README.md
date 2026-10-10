# Tower of Hanoi: Perbandingan BFS, DFS, Greedy Best-First Search, dan A*

Proyek Midterm mata kuliah **Konsep Kecerdasan Artificial**, Teknik Informatika ITS (2026).

Repositori ini berisi implementasi Python untuk memecahkan permasalahan **Tower of Hanoi** dengan beberapa algoritma pencarian, lalu membandingkan solusi dan kinerjanya. Laporan lengkap (formulasi masalah, heuristik, tree pemilihan state, dan pembahasan) ada pada berkas `midterm_KKA.pdf`.

**Anggota kelompok**

| Nama | NRP |
|---|---|
| Chairunnisa' Tsabitah | 5025251023 |
| Elba Galuh Hardiyanti | 5025251025 |
| Muhammad Adinata Parikesit | 5025251041 |
| Tri Zuyyina Rohmah | 5025251043 |

---

## Fitur

- Empat algoritma pencarian: **BFS, DFS, Greedy Best-First Search, A\***.
- Jumlah tiang **3 sampai 5** dan jumlah cakram **1 sampai 7** dapat diatur.
- Mode **command line**: tabel teks tiap langkah solusi dan ringkasan metrik.
- Mode **GUI (Tkinter)**: animasi solusi (play, pause, step, lompat awal/akhir, atur kecepatan) dan tabel perbandingan keempat algoritma.
- Pemeriksaan optimalitas terhadap jumlah langkah referensi **Frame-Stewart** (untuk 3 tiang sama dengan 2^n − 1).
- Tanpa pustaka eksternal. Hanya Python 3 dan pustaka standar.

## Struktur Folder

```
midterm_kka/
├── hanoi_common.py   # definisi masalah, heuristik, input parameter, tampilan tabel
├── bfs.py            # Breadth-First Search
├── dfs.py            # Depth-First Search
├── greedy.py         # Greedy Best-First Search
├── astar.py          # A* Search
└── hanoi_app.py      # aplikasi GUI (Tkinter)
```

## Prasyarat

- Python 3.8 atau lebih baru (diuji pada Python 3.12).
- Untuk GUI: Tkinter. Biasanya sudah bawaan Python di Windows dan macOS. Pada Linux (Debian/Ubuntu) pasang dengan:

  ```bash
  sudo apt install python3-tk
  ```

## Cara Menjalankan

Masuk ke folder kode terlebih dahulu. Semua berkas harus berada dalam satu folder yang sama.

```bash
cd midterm_kka
```

### 1. Mode command line

Tiap algoritma dijalankan sebagai skrip tersendiri:

```bash
python bfs.py
python dfs.py
python greedy.py
python astar.py
```

Jika tanpa argumen, program meminta jumlah tiang dan cakram lewat input. Parameter juga dapat diberikan langsung:

```bash
python astar.py -k 3 -n 5
```

| Argumen | Keterangan | Nilai |
|---|---|---|
| `-k`, `--pegs` | jumlah tiang | 3 sampai 5 |
| `-n`, `--disks` | jumlah cakram | 1 sampai 7 |
| `--steps` | tampilan tabel tiap langkah | `auto` (default, tampil jika solusi ≤ 60 langkah), `all`, `none` |

Contoh untuk instans pada laporan (5 cakram, 3 tiang), tanpa mencetak tabel tiap langkah:

```bash
python astar.py -k 3 -n 5 --steps none
```

### 2. Mode GUI

```bash
python hanoi_app.py
```

1. Pilih jumlah tiang dan cakram.
2. Pilih algoritma, lalu klik **Solve (algoritma terpilih)**, atau klik **Bandingkan semua algoritma**.
3. Gunakan tombol animasi (⏮ ◀ ▶ ▶| ⏭) dan slider kecepatan.
4. Klik salah satu baris pada tabel perbandingan untuk memutar solusi algoritma tersebut.

## Formulasi Masalah

Sesuai Bab 2 laporan, dengan satu perbedaan representasi pada kode (lihat di bawah):

| Komponen | Definisi |
|---|---|
| State | Penempatan semua cakram pada tiang. Cakram 1 adalah yang terkecil. |
| State awal | Semua cakram di tiang A. |
| Uji tujuan | Semua cakram di tiang terakhir (C untuk 3 tiang). |
| Aksi | Pindahkan cakram teratas suatu tiang ke tiang lain yang kosong atau yang puncaknya lebih besar. |
| Biaya | 1 per langkah, sehingga g(n) adalah jumlah langkah dari state awal. |
| Ruang state | k^n state (243 untuk 3 tiang dan 5 cakram). |

**Representasi di kode.** State disimpan sebagai tuple panjang `n`, di mana `state[i]` adalah indeks tiang tempat cakram ke-`i` berada. Contohnya, `(0, 0, 0, 0, 0)` adalah state awal dan `(2, 2, 2, 2, 2)` adalah state tujuan pada 3 tiang.

## Heuristik

Greedy dan A\* memakai heuristik **h1**: jumlah cakram yang belum berada di tiang tujuan.

- **Admissible**: setiap cakram yang salah tempat butuh minimal satu pemindahan.
- **Consistent**: satu langkah hanya mengubah posisi satu cakram.

## Algoritma

| Algoritma | File | Struktur frontier | Kunci prioritas | Optimal? |
|---|---|---|---|---|
| BFS | `bfs.py` | antrean FIFO | kedalaman | Ya (biaya seragam) |
| DFS | `dfs.py` | stack LIFO | urutan terakhir masuk | Tidak |
| Greedy | `greedy.py` | priority queue | h(n) | Tidak |
| A\* | `astar.py` | priority queue | f(n) = g(n) + h(n), seri dipecah dengan g terbesar | Ya (h admissible) |

Seluruh algoritma memakai graph search dengan *visited set* agar tidak berputar pada siklus.

## Metrik Keluaran

Setiap run mencetak ringkasan berikut:

- Jumlah langkah dan status optimal terhadap Frame-Stewart.
- Node di-expand dan di-generate.
- Ukuran frontier maksimum (pendekatan kebutuhan memori).
- Waktu eksekusi (detik, bersifat relatif terhadap perangkat keras).

## Contoh Hasil (3 tiang, 5 cakram)

Hasil menjalankan kode pada repositori ini (`python <algoritma>.py -k 3 -n 5 --steps none`):

| Algoritma | Langkah | Optimal? | Expanded | Generated | Frontier maks. |
|---|---|---|---|---|---|
| BFS | 31 | Ya | 206 | 616 | 26 |
| DFS | 81 | Tidak | 82 | 242 | 42 |
| Greedy (h1) | 35 | Tidak | 167 | 500 | 14 |
| A\* (h1) | 31 | Ya | 184 | 551 | 16 |

Pola utama yang konsisten dengan laporan:

- BFS dan A\* menemukan solusi optimal 31 langkah, sedangkan A\* memakai frontier lebih kecil daripada BFS.
- Greedy dengan h1 menghasilkan solusi 35 langkah (tidak optimal).
- DFS menemukan solusi dengan cepat tetapi jalurnya jauh lebih panjang dari optimum.

### Catatan perbedaan dengan angka di laporan

Angka *expanded*, *generated*, dan *frontier* pada tabel di atas **tidak sama persis** dengan Tabel 3.1 pada laporan (misalnya BFS 233/243/32 pada laporan). Penyebabnya adalah perbedaan implementasi, bukan kesalahan:

- Pada kode ini, *generated* dihitung dari setiap suksesor yang dihasilkan, termasuk yang sudah pernah dikunjungi. Pada laporan, *generated* adalah node yang benar-benar masuk frontier.
- BFS pada kode melakukan uji tujuan saat node dibangkitkan (*generate*), sedangkan algoritma pada laporan menguji saat node diambil dari frontier.
- Pemutus seri A\* pada kode memilih g terbesar, sedangkan laporan memilih h terkecil.

Panjang solusi dan sifat optimalnya tetap sama.

Hal berikut dibahas di laporan tetapi **tidak ada** di kode pada repositori ini:

- UCS (pada biaya seragam urutannya identik dengan BFS).
- Heuristik h2 (berbasis cakram terbesar yang belum di tiang tujuan).
- Visualisasi tree pemilihan state dan skrip pengukuran waktu rata-rata 200 kali eksekusi.

## Batasan

- Biaya setiap langkah adalah 1.
- State awal selalu semua cakram di tiang A, dan tujuan selalu di tiang terakhir.
- Waktu eksekusi hanya perbandingan relatif. Hasilnya bergantung pada perangkat keras.
- Pada 5 tiang dengan banyak cakram, Frame-Stewart hanya referensi pembanding. Algoritma pencarian tetap menghitung solusinya sendiri.

## Referensi

1. S. Russell dan P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed. Pearson, 2020.
2. P. E. Hart, N. J. Nilsson, dan B. Raphael, "A formal basis for the heuristic determination of minimum cost paths," *IEEE Trans. Systems Science and Cybernetics*, vol. 4, no. 2, 1968.
3. E. W. Dijkstra, "A note on two problems in connexion with graphs," *Numerische Mathematik*, vol. 1, 1959.
4. J. Pearl, *Heuristics: Intelligent Search Strategies for Computer Problem Solving*. Addison-Wesley, 1984.
5. A. M. Hinz, "The Tower of Hanoi," *L'Enseignement Mathématique*, vol. 35, 1989.
