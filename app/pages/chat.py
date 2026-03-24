import streamlit as st
from api_client import send_message, clear_history, get_memory, clear_memory

st.set_page_config(page_title = "Chat", layout = "wide")
st.title("Chat")

if not st.session_state.get("selected_project"):
    st.warning("Select a project from the side menu to start.")
    st.stop()
    
project_id = st.session_state.selected_project
project_data = st.session_state.get("selected_project_data", {})

chat_col, info_col = st.columns([3,1])

with info_col:
    st.subheader("Memory")
    try:
        memory = get_memory(project_id)
        if memory:
            for item in memory:
                st.markdown(f"**{item['key']}**: {item['value']}")
        else:
            st.caption("No information stored yet.")
    except Exception:
        st.exception("Memory couldn't be loaded.")
        
    st.divider()
    
    if st.button("Clear memory"):
        try:
            clear_memory(project_id)
            st.success("Memory cleaned.")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
            
    if st.button("New conversation"):
        try:
            clear_history(project_id)
            st.session_state.chat_history = []
            st.success("History cleaned")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
            
with chat_col:
    st.caption(f"Project: **{project_data.get('title', '')}**")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander(f"{len(msg['sources'])} sources", expanded = False):
                for source in msg["sources"]:
                    st.markdown(f"**Similarity:** {source['similarity']: .0%}")
                    st.caption(source["content"][:300] + "..." if len(source["content"]) > 300 else source["content"])
                    st.divider()
    user_input = st.chat_input("Write your message...")
    
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = send_message(project_id, user_input)
                    answer = result["answer"]
                    sources = result.get("sources", [])
                    st.markdown(answer)
                    
                    if sources:
                        with st.expander(f" {len(sources)} sources", expanded = False):
                            for source in sources:
                                st.markdown(f"**Similarity:** {source['similarity']:.0%}")
                                st.caption(source["content"][:300] + "..." if len(source["content"]) > 300 else source["content"])
                                st.divider()
                                
                except Exception as e:
                    answer = f"Error contacting to backend: {e}"
                    sources = []
                    st.error(answer)
                    
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })