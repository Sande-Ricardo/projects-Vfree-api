import streamlit as st
from api_client import get_documents, upload_document, delete_document

st.set_page_config(page_title="Documents", layout="wide")
st.title("Documents")

if "upload_reset_counter" not in st.session_state:
    st.session_state.upload_reset_counter = 0

if not st.session_state.get("selected_project"):
    st.warning("Select a project from side menu to start.")
    st.stop()

project_id = st.session_state.selected_project
project_data = st.session_state.get("selected_project_data", {})
st.caption(f"Project: **{project_data.get('title', '')}**")

# --- Subir documento ---
with st.expander("Upload document", expanded=False):
    with st.form("upload_form"):
        form_suffix = st.session_state.upload_reset_counter
        
        uploaded_file = st.file_uploader(
            "Select a file",
            type=["pdf", "txt", "md"],
            key=f"file_uploader_{form_suffix}"
        )
        doc_title = st.text_input(
            "Document title", 
            key=f"doc_title_{form_suffix}"
        )
        submit_upload = st.form_submit_button("Upload")

        if submit_upload:
            if not uploaded_file:
                st.error("Select a file.")
            elif not doc_title.strip():
                st.error("Title couldn't be empty.")
            else:
                with st.spinner("Processing..."):
                    try:
                        result = upload_document(
                            project_id=project_id,
                            title=doc_title.strip(),
                            file_bytes=uploaded_file.read(),
                            file_name=uploaded_file.name
                        )
                        st.success(
                            f"Document processed: {result['chunk_count']} indexed fragments."
                        )
                        
                        st.session_state.upload_reset_counter += 1
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error uploading file: {e}")

st.divider()

try:
    documents = get_documents(project_id)
except Exception:
    st.error("Document couldn't be uploaded.")
    documents = []

if not documents:
    st.info("There are no documents in this project yet.")
else:
    st.subheader(f"{len(documents)} indexed documents")

    for doc in documents:
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            status_icon = "✅" if doc["status"] == "ready" else "⚠️"
            st.markdown(f"{status_icon} **{doc['title']}**")
            st.caption(f"{doc['file_name']} · {doc.get('file_size', 0) // 1024} KB")

        with col2:
            st.caption(doc["created_at"][:10])

        with col3:
            if st.button("🗑️", key=f"del_doc_{doc['id']}"):
                try:
                    delete_document(doc["id"])
                    st.success("Document deleted.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")