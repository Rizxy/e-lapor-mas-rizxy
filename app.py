import streamlit as st
import os
import json
from datetime import datetime
from PIL import Image
import uuid
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request


# Set up page configuration
st.set_page_config(page_title="E-Lapor Mas Rizxy", layout="centered")

# Google API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

# Fungsi untuk autentikasi dan mengakses Google API
def authenticate_google_api():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

# Fungsi untuk simpan data ke Google Sheets
def save_to_google_sheets(data):
    creds = authenticate_google_api()
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_id = 'YOUR_SPREADSHEET_ID'  # Ganti dengan ID Spreadsheet Anda
    range_ = 'Sheet1!A1:F1'  # Sesuaikan dengan range di Google Sheets Anda

    values = [[data['nama'], data['lokasi'], data['laporan'], data['kategori'], data['waktu'], data['gambar']]]
    body = {'values': values}

    service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                            valueInputOption='RAW', body=body).execute()

# Fungsi untuk upload gambar ke Google Drive
def upload_to_google_drive(image_path):
    creds = authenticate_google_api()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(image_path), 'mimeType': 'image/jpeg'}
    media = MediaFileUpload(image_path, mimetype='image/jpeg')

    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')  # Mendapatkan file ID setelah diupload

# Fungsi klasifikasi otomatis
def klasifikasi_laporan(teks):
    teks = teks.lower()
    if any(k in teks for k in ["jalan", "jembatan", "lampu", "infrastruktur"]):
        return "Infrastruktur"
    elif any(k in teks for k in ["sakit", "puskesmas", "rumah sakit", "obat", "kesehatan"]):
        return "Kesehatan"
    elif any(k in teks for k in ["sekolah", "pendidikan", "guru", "murid", "siswa"]):
        return "Pendidikan"
    elif any(k in teks for k in ["bencana", "banjir", "sampah", "lingkungan"]):
        return "Lingkungan"
    elif any(k in teks for k in ["maling", "keamanan", "kriminal", "begal", "polisi"]):
        return "Keamanan"
    elif any(k in teks for k in ["ktp", "kk", "bansos", "dukcapil", "sosial", "akta"]):
        return "Sosial/kependudukan"
    else:
        return "Lainnya"

# Sidebar navigasi
page = st.sidebar.selectbox("Pilih halaman", ["Kirim Laporan", "Laporan Masuk"])

if page == "Kirim Laporan":
    st.title("📮 E-Lapor Mas Rizxy")
    st.subheader("Kirim laporan dari daerahmu!")

    nama = st.text_input("Nama")
    lokasi = st.text_input("Lokasi Kejadian")
    laporan = st.text_area("Isi laporan")
    gambar = st.file_uploader("Upload Gambar Bukti (Opsional)", type=["jpg", "jpeg", "png"])

    if st.button("Kirim Laporan"):
        if nama and lokasi and laporan:
            image_filename = None

            # Simpan gambar jika ada
            if gambar:
                image_id = str(uuid.uuid4())
                ext = gambar.name.split('.')[-1]
                image_filename = f"{image_id}.{ext}"
                image_path = os.path.join("data", "images", image_filename)
                with open(image_path, "wb") as f:
                    f.write(gambar.getbuffer())

                # Upload gambar ke Google Drive
                drive_file_id = upload_to_google_drive(image_path)

            kategori = klasifikasi_laporan(laporan)

            new_entry = {
                "nama": nama,
                "lokasi": lokasi,
                "laporan": laporan,
                "kategori": kategori,
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "gambar": drive_file_id if gambar else None
            }

            # Simpan data ke Google Sheets
            save_to_google_sheets(new_entry)

            st.success(f"Laporan berhasil dikirim! ✅\nKategori: **{kategori}**")
        else:
            st.warning("Nama, lokasi dan isi laporan harus diisi.")

elif page == "Laporan Masuk":
    st.title("📋 Laporan Masuk")

    creds = authenticate_google_api()
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet_id = 'YOUR_SPREADSHEET_ID'  # Ganti dengan ID Spreadsheet Anda
    range_ = 'Sheet1!A2:F'  # Sesuaikan dengan range di Google Sheets Anda
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_).execute()
    data = result.get('values', [])

    if data:
        for i, laporan in enumerate(data[::-1], 1):  # terbaru dulu
            st.markdown(f"### 📋 Laporan #{i}")
            st.write(f"**Nama:** {laporan[0]}")
            st.write(f"**Lokasi:** {laporan[1]}")
            st.write(f"**Laporan:** {laporan[2]}")
            st.write(f"**Kategori:** {laporan[3]}")
            st.write(f"🕒 **Waktu:** {laporan[4]}")

            # Tampilkan gambar jika ada
            if len(laporan) > 5 and laporan[5]:
                image_url = f"https://drive.google.com/uc?id={laporan[5]}"
                st.image(image_url, width=400, caption="Bukti Foto")

            st.markdown("---")
    else:
        st.info("Belum ada laporan masuk.")
