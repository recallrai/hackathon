import streamlit as st
from datetime import datetime
from prompts.chat import (
    get_chat_prompt,
    get_classifier_prompt_reasoning,
    get_queries_keywords_generator_prompt_reasoning
)
from .constants import DEFAULT_CONFIGS
from config import get_settings
from utils.llm import LLMFactory, LLMProvider
from utils import postgres, mongodb, milvus
from .models import ClassifierOutput, QueryKeywordsGeneratorOutput
from .utils import process_thinking_response

settings = get_settings()

async def show_chat(selected_model, temperature):
    # Show existing messages
    for message in st.session_state.messages:

        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])

        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                with st.status("Analyzing memory needs...", expanded=False):
                    st.write("**Model Reasoning:**")
                    st.text(message["classification"]["thinking"])
                    st.write("**Classification Result:**")
                    st.json(message["classification"]["classification"].model_dump_json())
                
                if "memory_queries" in message:
                    with st.status("Generating Memory Queries...", expanded=False):
                        st.write("**Query Generation Reasoning:**")
                        st.text(message["memory_queries"]["thinking"])
                        st.write("**Generated Queries:**")
                        st.write("Vector Search Queries:")
                        for q in message["memory_queries"]["queries"].data.vector_search_queries:
                            st.write(f"- {q}")
                        st.write("Keyword Search Terms:")
                        for k in message["memory_queries"]["queries"].data.bm25_keywords:
                            st.write(f"- {k}")
                st.write(message["content"])

    user_input = st.chat_input("What's on your mind?", key="chat_input")
    if user_input:
        system_prompt = get_chat_prompt(
            day=datetime.now().strftime("%A"),
            date=datetime.now().strftime("%dth %B %Y"),
            time=datetime.now().strftime("%I:%M %p"),
            memories=st.session_state.assistant_context_memories
        )

        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Show user message in chat interface
        with st.chat_message("user"):
            st.write(user_input)

        # Assistant response
        with st.chat_message("assistant"):
            # Use classifier-specific model
            classifier_config = settings.get_llm_config(DEFAULT_CONFIGS["classifier"]["model"])
            classifier_provider = LLMFactory.create_provider(classifier_config)

            # Run classifier before showing chat response
            # classifier_prompt = get_classifier_prompt_reasoning(conversation=st.session_state.messages)
            # classifier_messages = [{"role": "user", "content": classifier_prompt}]

            # classifier_response = ""
            # async for chunk in classifier_provider.stream_completion(
            #     classifier_messages, 
            #     DEFAULT_CONFIGS["classifier"]["temperature"]
            # ):
            #     classifier_response += chunk

            # thinking, classification = await process_thinking_response(classifier_response, ClassifierOutput)
            # with st.status("Analyzing memory needs...", expanded=False):
            #     st.write("**Model Reasoning:**")
            #     st.text(thinking)
            #     st.write("**Classification Result:**")
            #     st.json(classification.model_dump_json())

            # Generate subqueries and keywords if memory_usage is True
            # if classification.memory_usage:
            if True:
                # Use queries_keywords_generator-specific model
                query_keywords_generator_config = settings.get_llm_config(DEFAULT_CONFIGS["query_keywords_generator"]["model"])
                query_keywords_generator_provider = LLMFactory.create_provider(query_keywords_generator_config)

                # Run queries_keywords_generator before showing chat response
                queries_keywords_generator_prompt = get_queries_keywords_generator_prompt_reasoning(
                    day=datetime.now().strftime("%A"),
                    date=datetime.now().strftime("%dth %B %Y"),
                    time=datetime.now().strftime("%I:%M %p"),
                    conversation=st.session_state.messages
                )
                queries_keywords_generator_messages = [{"role": "user", "content": queries_keywords_generator_prompt}]

                queries_keywords_generator_response = ""
                async for chunk in query_keywords_generator_provider.stream_completion(
                    queries_keywords_generator_messages, 
                    DEFAULT_CONFIGS["query_keywords_generator"]["temperature"]
                ):
                    queries_keywords_generator_response += chunk

                queries_keywords_generator_thinking, queries_keywords_generator_result = await process_thinking_response(queries_keywords_generator_response, QueryKeywordsGeneratorOutput)
                with st.status("Generating Memory Queries...", expanded=False):
                    st.write("**Query Generation Reasoning:**")
                    st.text(queries_keywords_generator_thinking)
                    st.write("**Generated Queries:**")
                    st.write("Vector Search Queries:")
                    for q in queries_keywords_generator_result.data.vector_search_queries:
                        st.write(f"- {q}")
                    st.write("Keyword Search Terms:")
                    for k in queries_keywords_generator_result.data.bm25_keywords:
                        st.write(f"- {k}")

            # TODO: P1 - update the model context based on new generated queries and keywords
            # currenly i'm just putting all available memories in the context
            st.session_state.assistant_context_memories = [node.text for node in await postgres.get_all_nodes()]

            # Stream the assistant response directly to the chat interface
            model_config = settings.get_llm_config(selected_model)
            provider: LLMProvider = LLMFactory.create_provider(model_config)

            # add system message to the messages list
            messages = [
                {"role": "system", "content": system_prompt},
                *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            ]

            assistant_response_container = st.empty()
            assistant_response_text = ""
            async for chunk in provider.stream_completion(messages, temperature):
                assistant_response_text += chunk
                assistant_response_container.markdown(assistant_response_text + "▌")
            assistant_response_container.markdown(assistant_response_text)

        # Store assistant response in session state
        message_data = {
            "role": "assistant", 
            "content": assistant_response_text,
            "classification": {
                "thinking": thinking,
                "classification": classification,
            }
        }

        if classification.memory_usage:
            message_data["queries_and_keywords"] = {
                "thinking": queries_keywords_generator_thinking,
                "data": queries_keywords_generator_result
            }
        st.session_state.messages.append(message_data)

        # rerun after 1st chat as we need to force reload to enable "Extract and Save Memories" button
        if len(st.session_state.messages) == 2:
            st.rerun()
