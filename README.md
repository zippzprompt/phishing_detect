# Sistem Deteksi Phishing Website (Interface Flask)

Interface web untuk model Random Forest + SHAP dari skripsi _"Model
Interpretabilitas Deteksi Phishing Website Menggunakan Kombinasi Random
Forest dan TreeSHAP"_. User memasukkan URL, sistem mengambil halaman
webnya, menghitung fitur, memprediksi Phishing/Legitimate, dan
menampilkan penjelasan SHAP waterfall plot.

## Kenapa modelnya beda dari yang di skripsi?

Model asli skripsi memakai **70 fitur**, sebagian di antaranya (mis.
`TLDLegitimateProb`, `URLCharProb`) dihitung dari statistik seluruh
dataset training, dan `URLSimilarityIndex` memakai algoritma khusus dari
paper PhiUSIIL yang tidak dipublikasikan detail rumusnya — sulit
direplikasi persis untuk prediksi real-time satu URL.

Untuk interface ini, model **dilatih ulang dengan hyperparameter yang
sama** (`n_estimators=10, max_depth=5, criterion='gini', random_state=0`)
tapi hanya memakai **15 fitur** dengan **Mean |SHAP Value|** tertinggi
dari hasil analisis skripsi, yang dipilih karena semuanya bisa dihitung
langsung dari URL + HTML halaman tanpa butuh tabel statistik training:

| #   | Fitur              | Mean \|SHAP\| (skripsi) |
| --- | ------------------ | ----------------------- |
| 1   | URLSimilarityIndex | 0.1642                  |
| 2   | NoOfExternalRef    | 0.0730                  |
| 3   | LineOfCode         | 0.0515                  |
| 4   | NoOfSelfRef        | 0.0405                  |
| 5   | NoOfImage          | 0.0344                  |
| 6   | HasSubmitButton    | 0.0188                  |
| 7   | NoOfJS             | 0.0184                  |
| 8   | HasCopyrightInfo   | 0.0175                  |
| 9   | URLTitleMatchScore | 0.0151                  |
| 10  | HasSocialNet       | 0.0141                  |
| 11  | NoOfCSS            | 0.0134                  |
| 12  | IsResponsive       | 0.0121                  |
| 13  | URLLength          | 0.0099                  |
| 14  | HasFavicon         | 0.0085                  |
| 15  | IsHTTPS            | 0.0083                  |

Hasil retrain (lihat `model/metrics.json`, dihasilkan otomatis oleh
`model/train_lightweight_model.py`): akurasi test-set ~99.98%, hampir
identik dengan model 70-fitur di skripsi (99.94%). Ini poin bagus untuk
dijelaskan di sidang revisi: subset fitur dominan sudah cukup untuk
mempertahankan performa, sekaligus membuat sistem bisa berjalan
real-time.

**Catatan penting soal `URLSimilarityIndex`:** karena rumus asli di
paper PhiUSIIL tidak dipublikasikan detail, versi di aplikasi ini adalah
**pendekatan** memakai TF-IDF character n-gram + cosine similarity
terhadap daftar domain legitimate populer (lihat
`feature_extraction/legit_domains.py`) — konsepnya sama (menangkap
typosquatting/homograph), tapi bukan implementasi identik dari paper.
Sebutkan ini secara eksplisit di laporan/sidang sebagai batasan.

## Struktur proyek

```
phishing_app/
├── app.py                          # Flask app utama
├── requirements.txt
├── model/
│   ├── train_lightweight_model.py  # skrip retrain (sudah dijalankan)
│   ├── phishing_rf_lite.joblib     # model hasil retrain
│   ├── feature_names.json          # urutan 15 fitur (harus sama persis)
│   ├── metrics.json                # hasil evaluasi
│   └── train_subset.csv            # subset data (15 fitur) dari dataset training
├── feature_extraction/
│   ├── extract.py                  # ekstraksi 15 fitur dari URL + HTML
│   └── legit_domains.py            # referensi domain untuk URLSimilarityIndex
├── templates/
│   ├── base.html, index.html, result.html
└── static/
    └── style.css
```

## Cara menjalankan

1. (Opsional tapi disarankan) buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi:
   ```bash
   python app.py
   ```
4. Buka `http://127.0.0.1:5000` di browser, masukkan URL, klik **Periksa**.

Model sudah terlatih dan tersimpan di `model/phishing_rf_lite.joblib` —
tidak perlu training ulang untuk menjalankan aplikasi. Kalau mau
melatih ulang (misalnya ganti subset fitur), jalankan:

```bash
cd model
python train_lightweight_model.py
```

## Keterbatasan yang perlu disebutkan di laporan

- Fitur berbasis konten (HTML) butuh koneksi internet untuk fetch
  halaman target secara live; kalau halaman gagal diakses (timeout,
  diblokir, dll), fitur tersebut diisi nilai default 0 dan sistem tetap
  memberi prediksi (dengan peringatan di halaman hasil).
- `URLSimilarityIndex` dan `URLTitleMatchScore` adalah pendekatan
  (approximation), bukan replikasi rumus asli dataset PhiUSIIL.
- Model dilatih ulang dengan 15 dari 70 fitur asli — trade-off yang
  disengaja untuk kebutuhan deployment real-time (dijelaskan di atas).

# Phishing Website Detection using Random Forest and TreeSHAP

Proyek ini merupakan aplikasi berbasis web untuk mendeteksi potensi phishing pada website menggunakan algoritma **Random Forest**. Aplikasi dikembangkan menggunakan Python dan framework Flask, dengan Playwright untuk membantu proses ekstraksi informasi dari URL website.

Untuk meningkatkan transparansi hasil klasifikasi, proyek ini menggunakan **TreeSHAP** sebagai metode Explainable AI (XAI) yang membantu menjelaskan kontribusi fitur terhadap hasil prediksi model. Dengan demikian, pengguna tidak hanya memperoleh hasil deteksi, tetapi juga dapat memahami faktor-faktor yang memengaruhi keputusan model.

### Teknologi yang Digunakan

- **Python** — Bahasa pemrograman utama.
- **Flask** — Framework untuk membangun aplikasi web.
- **Playwright** — Otomatisasi browser untuk membantu ekstraksi informasi website.
- **Random Forest** — Algoritma machine learning untuk klasifikasi website phishing dan legitimate.
- **TreeSHAP** — Metode interpretabilitas model untuk menganalisis kontribusi fitur terhadap hasil prediksi.

### Tujuan Proyek

- Mengembangkan aplikasi deteksi phishing website berbasis machine learning.
- Mengklasifikasikan URL website berdasarkan karakteristik fiturnya.
- Mengintegrasikan interpretabilitas model menggunakan TreeSHAP.
- Menyediakan antarmuka web untuk mempermudah proses pemeriksaan URL.

### Catatan

Hasil deteksi merupakan prediksi berdasarkan model dan fitur yang digunakan, sehingga tidak menjamin bahwa suatu website sepenuhnya aman atau berbahaya.
