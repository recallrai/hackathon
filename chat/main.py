import streamlit as st
from .constants import DEFAULT_CONFIGS
from config import get_settings
from .chat import show_chat
from .memories_extraction import show_memory_extraction

settings = get_settings()

# TODO: when assistant is generating, disable chat input (use assistant_generating session state variable)
# TODO: in "extract and save memories", make sure the results of all previous steps are displayed while processing current step

def show_welcome():
    st.title("Chat with Memory Assistant")
    st.markdown("""
    ### Welcome to the Memory Assistant!
    
    Here, you can interact with our chat system and observe how it processes and stores memories. As you chat, important details from your conversation will be saved at the end of the session. These stored memories will later provide context for future queries, in new chat sessions.
    
    Click 'Continue' to start chatting.
    """)
    return st.button("Continue")

def show_model_settings():
    """Show model settings sidebar"""
    # Get sorted list of providers, with default provider selected if available.
    provider_list = sorted({model.provider for model in settings.ModelConfig.llms})
    default_provider = DEFAULT_CONFIGS["chat"]["provider"]
    default_provider_index = provider_list.index(default_provider) if default_provider in provider_list else 0
    selected_provider = st.selectbox(
        "Provider",
        options=provider_list,
        index=default_provider_index,
        key="chat_sidebar_provider"
    )

    # Filter models by the selected provider.
    provider_models = [
        model.name for model in settings.ModelConfig.llms 
        if model.provider == selected_provider
    ]
    default_model = DEFAULT_CONFIGS["chat"]["model"]
    default_index = provider_models.index(default_model) if default_model in provider_models else 0
    selected_model = st.selectbox(
        "Chat Model",
        options=provider_models,
        index=default_index,
        key="chat_sidebar_model"
    )
    slider_temp = st.slider(
        "Temperature",
        0.0, 1.0,
        value=DEFAULT_CONFIGS["chat"]["temperature"],
        step=0.05,
        key="chat_temperature"
    )
    return selected_model, slider_temp

async def show_chat_interface():
    """entry point for chat interface"""
    # track if welcome message is shown
    if "chat_welcome_shown" not in st.session_state:
        st.session_state.chat_welcome_shown = False
    # tracks messages in the chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # tracks current step in memory extraction process (0-chat, 1-memory extraction, 2-decision making, ...)
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    # keeps the generated memories output in session state
    if "generated_memories" not in st.session_state:
        st.session_state.generated_memories = []
    # keeps the decision results in session state
    if "decision_results" not in st.session_state:
        st.session_state.decision_results = []
    # this is the assistant context that is passed to the model
    if "assistant_context_memories" not in st.session_state:
        st.session_state.assistant_context_memories = []

    with st.sidebar:
        st.subheader("Model Settings")
        selected_model, temperature = show_model_settings()

        if st.session_state.messages:
            if st.session_state.current_step:
                if st.button("Back to Chat"):
                    st.session_state.current_step = 0
                    st.rerun()
            else:
                if st.button("Extract and Save Memories"):
                    st.session_state.current_step = 1
                    st.rerun()
        if st.button("New Chat", type="secondary"):
            # reset all session state variables
            st.session_state.messages = []
            st.session_state.current_step = 0
            st.session_state.generated_memories = []
            st.session_state.decision_results = []
            st.session_state.assistant_context_memories = []
            st.rerun()

    if not st.session_state.chat_welcome_shown:
        if show_welcome():
            st.session_state.chat_welcome_shown = True
            st.rerun()
    else:
        if st.session_state.current_step > 0:
            await show_memory_extraction()
        else:
            await show_chat(selected_model, temperature)
