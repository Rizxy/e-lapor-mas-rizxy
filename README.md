# 📘 Rangkuman Proyek: E-Lapor Mas Wapres

## 🧠 Tujuan Proyek

Membangun aplikasi pelaporan masyarakat berbasis web menggunakan **Streamlit**, yang:

- Memudahkan masyarakat mengirim laporan ke pemerintah
- Mendukung unggahan gambar bukti
- Mengelola laporan secara terstruktur
- Akan didukung AI untuk klasifikasi otomatis dan validasi komunitas

---

## ✅ Fitur yang Sudah Selesai

### 1. **Formulir Kirim Laporan**

- Input nama, lokasi, isi laporan
- Upload gambar bukti (opsional)
- Penyimpanan ke file `laporan.json`
- Gambar disimpan di folder `data/images`

### 2. **Halaman Laporan Masuk**

- Menampilkan laporan terbaru ke terlama
- Informasi yang ditampilkan:
  - Nama pelapor
  - Lokasi
  - Isi laporan
  - Waktu
  - Gambar jika ada

---

## 🛠️ Struktur Folder Saat Ini

```
📁 app_lapor_wapres
├── 📄 app.py
├── 📄 README.md
└── 📁 data
    ├── 📄 laporan.json
    └── 📁 images
```

---

## 🗺️ Rencana Fitur Selanjutnya

### 3. **AI Klasifikasi Laporan Otomatis**

- Klasifikasi laporan ke dalam kategori:
  - Infrastruktur
  - Kesehatan
  - Pendidikan
  - Keamanan
  - Lingkungan
  - Sosial/Kependudukan
  - Lainnya
- Versi awal: berdasarkan kata kunci
- Versi lanjutan: model Naive Bayes/Text Classification

### 4. **Dashboard Statistik**

- Jumlah laporan per kategori
- Jumlah laporan per lokasi
- Timeline laporan (mingguan/bulanan)

### 5. **Sistem Validasi Komunitas (Inspirasi dari Blockchain)**

- Laporan akan tampil di "Pending"
- Masyarakat lain bisa konfirmasi validitas laporan
- Jika lolos validasi, baru dikirim ke pemerintah

---

## 💡 Teknologi yang Digunakan

- Python
- Streamlit
- JSON (penyimpanan lokal)
- Pillow (gambar)
- UUID (penamaan gambar unik)
- Rencana: Scikit-learn untuk AI, Pandas untuk statistik

---

## 👨‍💻 Status Saat Ini

- ✅ Tampilan kirim dan tampil laporan selesai
- 🔄 Dalam rencana: Klasifikasi otomatis
- 📌 Belum mulai: Statistik, validasi publik, integrasi AI

---

## 🤝 Catatan Kolaborasi

- Proyek dikembangkan bersama Rizxy dan temannya
- IDE: IntelliJ IDEA dengan virtual environment `.venv`
- Tujuan jangka panjang: Bisa diakses publik, bantu pemerintah deteksi masalah lokal

---

> "Dari laporan kecil, bisa lahir perubahan besar."
