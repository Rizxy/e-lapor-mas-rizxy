import streamlit as st
import json
from datetime import datetime
from PIL import Image
import uuid
import gspread
from google.oauth2.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import tempfile


# ----------------- Autentikasi ------------------
def auth_google_services():
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    return creds, client

creds, gsheet_client = auth_google_services()

# ----------------Upload gambar ke Gdrive ---------------------
def upload_gambar_ke_drive(gambar):
    gauth = GoogleAuth()
    gauth.credentials = creds
    drive = GoogleDrive(gauth)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(gambar.getvalue())
        tmp_file.flush()
        file_drive = drive.CreateFile({
            "title" : gambar.name,
            "parents" : [{"id": st.secrets["drive_folder_id"]}]
        })
        file_drive.SetContentFile(tmp_file.name)
        file_drive.Upload()
        return f"https://drive.google.com/uc?id={file_drive['id']}"


#----------------- Simpan ke Google Sheets -------------------
def simpan_laporan_ke_sheets(data_laporan):
    sheet_id = st.secrets["sheet_id"]
    sheet = gsheet_client.open_by_key(sheet_id).sheet1
    sheet.append_row(data_laporan)

    # ---------- UI ----------
st.title("📢 E-Lapor Mas Wapres")

page = st.sidebar.selectbox("Navigasi", ["Kirim Laporan"])

if page == "Kirim Laporan":
    st.subheader("Formulir Laporan")
    
    nama = st.text_input("Nama")
    lokasi = st.text_input("Lokasi")
    isi_laporan = st.text_area("Isi Laporan")
    gambar = st.file_uploader("Upload Gambar Bukti", type=["jpg", "jpeg", "png"])

    if st.button("Kirim Laporan"):
        if not nama or not lokasi or not isi_laporan:
            st.warning("Harap lengkapi semua kolom terlebih dahulu.")
        else:
            url_gambar = ""
            if gambar:
                url_gambar = upload_gambar_ke_drive(gambar)

            # Dummy kategori (nanti bisa diganti AI)
            kategori = "Lainnya"

            data_laporan = [
                nama,
                lokasi,
                isi_laporan,
                kategori,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                url_gambar
            ]
            simpan_laporan_ke_sheets(data_laporan)
            st.success("✅ Laporan berhasil dikirim!")