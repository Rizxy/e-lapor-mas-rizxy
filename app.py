import streamlit as st
import os
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
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    client = gspread.authorize(creds)
    return creds, client

creds, gsheet_client = auth_google_services()

# ----------------Upload gambar ke Gdrive ---------------------
def upload_gambar_ke_drive(gambar):
    gauth = GoogleAuth()
    gauth.credentials = creds
    drive = GoogleDrive(gauth)


    ext = os.path.splitext(gambar.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:

        tmp_file.write(gambar.getvalue())
        tmp_file.flush()
        file_drive = drive.CreateFile({
            "title": gambar.name,
            "parents": [{"id": st.secrets["drive_folder_id"]}]
        })
        file_drive.SetContentFile(tmp_file.name)
        file_drive.Upload()
        
        # Beri permission publik agar bisa ditampilkan di Streamlit
        file_drive.InsertPermission({
            'type': 'anyone',
            'value': 'anyone',
            'role': 'reader'
        })

        return f"https://drive.google.com/uc?export=view&id={file_drive['id']}"


#----------------- Simpan ke Google Sheets -------------------
def simpan_laporan_ke_sheets(data_laporan):
    sheet_id = st.secrets["sheet_id"]
    sheet = gsheet_client.open_by_key(sheet_id).sheet1
    sheet.append_row(data_laporan)

# ---------------- Ambil data dari Google Sheets --------------
def ambil_data_laporan():
    sheet_id = st.secrets["sheet_id"]
    sheet = gsheet_client.open_by_key(sheet_id).sheet1
    records = sheet.get_all_values()

    data_laporan = []
    for row in records[1:]:  # Skip header
        data_laporan.append({
            "nama": row[0],
            "lokasi": row[1],
            "isi": row[2],
            "kategori": row[3],
            "waktu": row[4],
            "gambar_url": row[5] if len(row) > 5 else ""
        })
    return data_laporan

def baca_laporan_dari_sheets():
    sheet_id = st.secrets["sheet_id"]
    sheet = gsheet_client.open_by_key(sheet_id).sheet1
    records = sheet.get_all_records()

    laporan_list = []
    for row in records:
        laporan = {
            "nama": row.get("nama") or row.get("Nama"),
            "lokasi": row.get("lokasi") or row.get("Lokasi"),
            "isi": row.get("isi_laporan") or row.get("Isi Laporan"),
            "kategori": row.get("kategori") or row.get("Kategori"),
            "waktu": row.get("waktu") or row.get("Waktu"),
            "gambar_url": row.get("url_gambar") or row.get("Url Gambar") or row.get("url")  # tergantung header di sheet
        }
        laporan_list.append(laporan)
    return laporan_list



# ---------- UI ----------
st.title("📢 E-Lapor SuaraRakyat")

page = st.sidebar.selectbox("Navigasi", ["Kirim Laporan", "Laporan Masuk"])

if page == "Kirim Laporan":
    st.subheader("Kirim laporan dari daerahmu!")
    
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

            kategori = "Lainnya"  # dummy kategori

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

elif page == "Laporan Masuk":
    st.header("📥 Laporan Masuk")

    sheet_id = st.secrets["sheet_id"]
    sheet = gsheet_client.open_by_key(sheet_id).sheet1
    records = sheet.get_all_values()

    if records and len(records) > 1:  # baris pertama biasanya header/manual
        for laporan in reversed(records[1:]):
            st.subheader(f"{laporan[3]} - {laporan[1]}")
            st.write(f"🧑 Nama: {laporan[0]}")
            st.write(f"🕒 Waktu: {laporan[4]}")
            st.write(f"📝 Laporan: {laporan[2]}")

            if len(laporan) > 5:
              url = laporan[5].strip()
              if url.startswith("http"):
                  st.image(url, width=300)
              else:
                  st.write("📎 Bukti belum tersedia atau tidak valid.")


            st.markdown("---")
    else:
        st.info("Belum ada laporan masuk.")
