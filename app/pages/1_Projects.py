import streamlit as st
from api_client import get_projects, create_project, delete_project, update_project

st.set_page_config(page_title = "Projects", layout = "wide")
st.title("Project Management")

# with st.expander("➕ New project", expanded = False):
#     with st.form("create_project_form"):
#         new_title = st.text_input("Project name")
#         new_instructions = st.text_area(
#             "Assistant instructions",
#             placeholder = "Ex: Always reply in english. Be concise. Use no more than 5 sentences.",
#             height = 120
#         )
#         submitted = st.form_submit_button("Create project")
        
#         if submitted:
#             if not new_title.strip():
#                 st.error("The name can't be empty.")
#             else:
#                 try:
#                     create_project(new_title.strip(), new_instructions.strip())
#                     st.success(f"'{new_title}' project created.")
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Error creating project: {e}")
    
if "create_form_key" not in st.session_state:
    st.session_state.create_form_key = 0

with st.expander("➕ New project", expanded=False):
    with st.form(key=f"create_project_form_{st.session_state.create_form_key}"):
        new_title = st.text_input("Project name")
        new_instructions = st.text_area(
            "Assistant instructions",
            placeholder="Ej: Always reply in [language]. Be concise. Use no more than 5 sentences.",
            height=120
        )
        submitted = st.form_submit_button("Create project")

        if submitted:
            if not new_title.strip():
                st.error("The name can't be empty.")
            else:
                try:
                    create_project(new_title.strip(), new_instructions.strip())
                    st.success(f"'{new_title}' project created.")
                    st.session_state.create_form_key += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating project: {e}")

st.divider()

try:
    projects = get_projects()
except Exception:
    st.info("Unable to connect to the backend.")
    projects = []
    
if not projects:
    st.info("There are no projects yet.")
else:
    for project in projects:
        with st.expander(f"{project['title']}", expanded = False):
            col1, col2 = st.columns([4,1])
            
            with col1:
                with st.form(f"edit_{project['id']}"):
                    edited_title = st.text_input(
                        "Name",
                        value=project["title"],
                        key=f"title_{project['id']}"
                    )
                    edited_instructions = st.text_area(
                        "Instructions",
                        value=project.get("instructions", ""),
                        height=100,
                        key=f"inst_{project['id']}"
                    )
                    if st.form_submit_button("Save"):
                        try:
                            update_project(
                                project["id"],
                                edited_title.strip(),
                                edited_instructions.strip()
                            )
                            st.success("Project updated.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
            with col2:
                st.write("")
                st.write("")
                if st.button("Delete", key=f"del_{project['id']}"):
                    try:
                        delete_project(project["id"])
                        if st.session_state.get("selected_project" == project["id"]):
                            st.session_state.selected_project = None
                            st.session_state.chat_history = []
                        st.success("Project deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")