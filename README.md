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
