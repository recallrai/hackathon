import streamlit as st

def show_welcome():
    st.title("Chat with Memory Assistant")
    st.markdown("""
    ### Welcome to the Memory Assistant!
    
    Here, you can interact with our chat system and observe how it processes and stores memories. As you chat, important details from your conversation will be saved at the end of the session. These stored memories will later provide context for future queries, in new chat sessions.
    
    Click 'Continue' to start chatting.
    """)
    return st.button("Continue")
