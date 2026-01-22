import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

st.set_page_config(page_title="Drive Selector", layout="centered")

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

st.title("📂 Google Drive File Selector")

# Session state
if "creds" not in st.session_state:
    st.session_state.creds = None

if "files" not in st.session_state:
    st.session_state.files = []

# Step 1: Login
if st.session_state.creds is None:
    st.info("Login with Google to access your Drive")

    if st.button("Login with Google"):
        flow = InstalledAppFlow.from_client_secrets_file(
            "client2.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)
        st.session_state.creds = creds
        st.success("✅ Logged in successfully")
        st.rerun()

else:
    # Step 2: Build Drive service
    service = build("drive", "v3", credentials=st.session_state.creds)

    # Step 3: Fetch files
    if not st.session_state.files:
        results = service.files().list(
            pageSize=20,
            fields="files(id, name, mimeType)"
        ).execute()
        st.session_state.files = results.get("files", [])

    st.subheader("Your Google Drive Files")

    if not st.session_state.files:
        st.warning("No files found")
    else:
        file_names = [f["name"] for f in st.session_state.files]
        selected_name = st.selectbox("Select a file", file_names)

        selected_file = next(
            f for f in st.session_state.files if f["name"] == selected_name
        )

        st.write("**File ID:**", selected_file["id"])
        st.write("**Type:**", selected_file["mimeType"])

        # Step 4: Download test
        if st.button("Download selected file"):
            request = service.files().get_media(
                fileId=selected_file["id"]
            )

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while not done:
                status, done = downloader.next_chunk()

            st.success("✅ File downloaded in memory")
            st.write("Size:", len(fh.getvalue()), "bytes")

        st.divider()
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
