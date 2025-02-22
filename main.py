import streamlit as st
import asyncio
from home import show_home
from reset_database import show_reset_database
from memory_graph import show_memory_graph
from chat import show_chat_interface

class MultiPageApp:
    def __init__(self):
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Home"

    async def run(self):
        st.sidebar.title("Navigation")
        
        # Create main menu items
        main_options = {
            "Home": show_home,
            "End-to-End Chat": show_chat_interface,
            "Memory Graph": show_memory_graph,
            "Reset Database": show_reset_database,
        }

        selection = st.sidebar.selectbox(
            "Go to",
            list(main_options.keys())
        )

        page_func = main_options[selection]

        if page_func:
            if asyncio.iscoroutinefunction(page_func):
                await page_func()
            else:
                page_func()

async def main():
    st.set_page_config(
        page_title="RecallrAI Hackathon Prototype",
        page_icon="🧠",
        layout="wide"
    )

    app = MultiPageApp()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
