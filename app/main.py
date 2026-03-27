import streamlit as st
from api_client import get_projects

st.set_page_config(
    page_title = "Internal AI Platform",
    page_icon = "🤖",
    layout = "wide"
)

if "selected_project" not in st.session_state:
    st.session_state.selected_project = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
with st.sidebar:
    st.title("AI Platform")
    st.divider()
    
    try:
        projects = get_projects()
    except Exception:
        st.error("Unable to connect to the backend. Is it running on localhost:8000?")
        projects = []
        
    if projects:
        project_titles = {p["title"]: p for p in projects}
        selected_title = st.selectbox(
            "Active project",
            options = list(project_titles.keys()),
            index = 0
        )
        selected = project_titles[selected_title]
        
        if st.session_state.selected_project != selected["id"]:
            st.session_state.selected_project = selected["id"]
            st.session_state.chat_history = []
            st.session_state.selected_project_data = selected
            
    else:
        st.info("There are no projects. Create one in the Project section.")
        st.session_state.selected_project = None
        
    st.divider()
    st.caption("Navigate using the page menu ->")
    
st.title("Welcome to the platform")

if st.session_state.selected_project:
    project = st.session_state.get("selected_project_data", {})
    st.success(f"Active project: **{project.get('title', '')}**")
    st.markdown("Use the lateral menu to navigate between **Chat**, **Documents** & **Projects**.")
else:
    st.warning("Select or create a project to start.")