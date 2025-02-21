import streamlit as st

def show_home():
   st.title("Welcome to RecallrAI")
   
   st.markdown("""
## Enhance Your AI's Memory and Reasoning

RecallrAI is a cutting-edge platform designed to revolutionize AI memory management, reasoning, and decision-making capabilities. Our advanced system empowers AI to create, store, and utilize memories effectively, leading to more contextual and intelligent interactions.

### Prototype: Test Our Intelligent Chat System

Here, you can interact with our chat system and observe how it processes and stores memories. As you chat, important details from your conversation will be saved at the end of the session. These stored memories will later provide context for future queries, in new chat sessions.

**What happens during the session?**
- When you send a message, a classifier first determines whether any stored memory is needed to answer your query.
- If memories are not required, the assistant answers directly.
- If memories are needed, the system generates relevant queries and keywords, required for searching.
- The search retrieves related facts to provide contextual responses.

**What happens when the session ends?**
- Key information is extracted from the conversation.
- Memories are created based on this extracted information.
- A decision-making process determines whether to insert new memories, delete outdated ones, or update existing ones.

This prototype showcases the fundamental mechanics of our AI memory system in action.

### Under the Hood: Key Subroutines

Our chat functionality is powered by a suite of sophisticated subroutines. Each of these components plays a crucial role in the memory generation, management, and retrieval process:

1. **Memory Generation**
   - Reasoning LLMs: Creates nuanced, context-rich memories using advanced reasoning.
   - Non-Reasoning LLMs: Efficiently generates memories from conversation without reasoning.

2. **Decision Making**
   - Decision Prompt: Determines what to do with extracted memories.

3. **Query and Retrieval**
   - Classifier Interface: Determines whether stored memories are needed.
   - Query & Keyword Generation: Generates relevant queries and keywords.
   - Relevant Memory Search: Retrieves the most relevant stored memories.

4. **Visualization and Debugging**
   - Memory Graph: Displays a Graphical visualization of stored memories.

5. **Memory Deletion**
   - Danger Zone: Allows you to delete stored memories along with their relationships.

Explore these powerful components to understand the intricate workings of RecallrAI!
""")

   st.markdown("""
   ---

   ### Getting Started

   1. Start with our Intelligent Chat Interface to experience the full capabilities of RecallrAI.
   2. Dive into individual subroutines to understand the memory processes.
   """)
