import streamlit as st
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
from utils.models import Memory, ConflictingMemory, QuestionAnswer
from utils.normalize_uuid import normalize_memories
from .models import (
    AdditionToExistingMemoryAction, 
    DecisionOutputType, 
    GenerationOutputType, 
    IgnoreAction, 
    InsertAction, 
    MergeConflictAction, 
    ModelResponseDecision, 
    ModelResponseGeneration, 
    ResolveTemporalConflictAction,
    ModelResponseAddition,
    ModelResponseInsertion,
)
from .constants import DEFAULT_CONFIGS, MONTHS
from config import get_settings
from utils.llm import LLMFactory, LLMProvider
from utils.embeddings import EmbeddingsFactory, EmbeddingsProvider
from prompts.ingestion.decision import get_decision_prompt_reasoning
from prompts.ingestion.insertion import get_insertion_reasoning_prompt
from prompts.ingestion.merge_conflict import (
    get_merge_conflict_generate_questions_prompt, 
    get_merge_conflict_generate_new_memories_prompt,
)
from .utils import process_thinking_response
from prompts.ingestion.generation import get_memory_generation_prompt_reasoning
from tools import get_calendar_for_any_month
from utils import postgres, milvus, mongodb

settings = get_settings()

async def show_memory_extraction():
    # clear generated memories if user goes back to chat
    if st.session_state.current_step == 0:
        del st.session_state.generated_memories
        st.session_state.current_step = 1

    st.title("Update Assistant's Knowledge")

    if st.session_state.current_step >= 1:
        st.header("Step 1: Generate Memories")

    with st.spinner("Generating memories..."):
        generate_memories_prompt = get_memory_generation_prompt_reasoning(
            day=datetime.now(timezone.utc).strftime("%A"),
            date=datetime.now(timezone.utc).strftime("%dth %B %Y"),
            time=datetime.now(timezone.utc).strftime("%H:%M:%S"),
            conversation=st.session_state.messages,
        )

        model_config = settings.get_llm_config(DEFAULT_CONFIGS["memory_generation"]["model"])
        provider: LLMProvider = LLMFactory.create_provider(model_config)

        call_count = 0
        max_recursive_calls = 2
        messages = [{"role": "user", "content": generate_memories_prompt}]

        while call_count <= max_recursive_calls:
            # generate memories
            memories_response = ""
            async for chunk in provider.stream_completion(
                messages, DEFAULT_CONFIGS["memory_generation"]["temperature"]
            ):
                memories_response += chunk

            # add that to messages dict
            messages.append({"role": "assistant", "content": memories_response})

            # process the response
            thinking, memories = await process_thinking_response(memories_response, ModelResponseGeneration)

            st.subheader(f"**Thinking (Step {call_count + 1}):**")
            st.text(thinking)

            if memories.type == GenerationOutputType.FINAL_RESULT:
                st.subheader(f"**Final Result (Step {call_count + 1}):**")
                st.json(memories.data.model_dump_json())
                st.session_state.generated_memories = memories.data.memories
                st.session_state.current_step = 2
                break

            if memories.type == GenerationOutputType.FUNCTION_CALL:
                st.subheader(f"**Function Call (Step {call_count + 1}):**")
                st.json(memories.data.model_dump_json())

            if memories.data.name == "get_calendar_for_any_month":
                month = memories.data.arguments["month"]
                year = memories.data.arguments["year"]
                result = get_calendar_for_any_month(month=month, year=year)
                
                st.subheader(f"**Function Result:**")
                st.text(result)

                content = f"""Function Result:
Below is the calendar for the month of {MONTHS[month - 1]} and year {year} in CSV format:
{result}"""
                messages.append({"role": "user", "content": content})
                call_count += 1
                continue

            else:
                raise ValueError(f"Unknown function: {memories.data.name}")

        if call_count > max_recursive_calls:
            st.warning(f"Max recursive calls ({max_recursive_calls}) reached without final result")

        if st.session_state.generated_memories:
            st.success(f"Generated {len(st.session_state.generated_memories)} memories")
        else:
            st.warning("No memories generated")

    if st.session_state.current_step >= 2 and st.session_state.generated_memories:
        st.markdown("---")
        st.header("Step 2: Decision Making")

        async def handle_decision(
            new_memory_text: str,
        ) -> Dict[str, Any]:
            """Process a single memory through the decision making pipeline"""
            # Get embeddings for new memory
            provider = EmbeddingsFactory.create_provider(settings.embedding_model)
            embeddings = provider.get_embeddings(new_memory_text)

            # Get relevant memories
            # {'node_123': 0.8, 'node_456': 0.7, 'node_789': 0.6}
            # print("embeddings: ", embeddings)
            similar_nodes = milvus.search_relevent_nodes_by_embeddings(
                embeddings=embeddings,
                min_top_k=10,
                # max_top_k=max_top_k,
                threshold=0.75
            )
            print(similar_nodes)

            # TODO: abhi ke liye mai bas symantic similarity ke basis pe hi dekh raha hoon
            # yahan pe reranker aur connected graph vala logic bhi lagana hai
            # Get memory objects for similar nodes
            relevant_memories: List[Memory] = []
            for node_id, similarity in similar_nodes.items():
                memory = postgres.get_memory_details(node_id)
                relevant_memories.append(memory)
            
            # Normalize memory IDs
            normalized_memories, uuid_mapping = normalize_memories(relevant_memories)
            
            # Create decision prompt with normalized memories
            decision_prompt = get_decision_prompt_reasoning(
                date=datetime.now(timezone.utc).strftime("%dth %B %Y"),
                time=datetime.now(timezone.utc).strftime("%H:%M:%S"),
                existing_memories=normalized_memories,
                new_memory=new_memory_text
            )
            
            # Get model and provider
            model_config = settings.get_llm_config(DEFAULT_CONFIGS["decision"]["model"])
            provider = LLMFactory.create_provider(model_config)
            
            messages = [{"role": "user", "content": decision_prompt}]
            
            # Get full response
            full_response = ""
            async for chunk in provider.stream_completion(messages, DEFAULT_CONFIGS["decision"]["temperature"]):
                full_response += chunk
            
            # Parse response into ModelResponseDecision
            thinking, decision = await process_thinking_response(full_response, ModelResponseDecision)
            
            # Convert normalized IDs back to UUIDs
            if decision.action == DecisionOutputType.INSERT:
                pass
                # decision.data.content = new_memory_text
                # decision.data.related_memory_ids = [
                #     uuid_mapping[id] for id in decision.data.related_memory_ids
                #     if id in uuid_mapping
                # ]
            elif decision.action == DecisionOutputType.MERGE_CONFLICT:
                decision.data.conflicting_memories = [
                    memory for memory in decision.data.conflicting_memories 
                    if memory.memory_id in uuid_mapping
                ]
                for memory in decision.data.conflicting_memories:
                    memory.memory_id = uuid_mapping[memory.memory_id]
            elif decision.action == DecisionOutputType.RESOLVE_TEMPORAL_CONFLICT:
                decision.data.memory_ids = [
                    uuid_mapping[id] for id in decision.data.memory_ids
                    if id in uuid_mapping 
                ]
            elif decision.action == DecisionOutputType.ADDITION_TO_EXISTING_MEMORY:
                decision.data.updated_memories = [
                    memory for memory in decision.data.updated_memories
                    if memory.memory_id in uuid_mapping
                ]
                for memory in decision.data.updated_memories:
                    memory.memory_id = uuid_mapping[memory.memory_id]
            elif decision.action == DecisionOutputType.IGNORE:
                pass
            else:
                raise ValueError(f"Unknown action type: {decision.action}")


            return {
                "thinking": thinking,
                "response": decision,
                "relevant_memories": relevant_memories,
            }

        with st.spinner("Making decisions..."):
            # Process multiple memories in parallel
            tasks = [
                handle_decision(
                    new_memory_text=memory,
                )
                for memory in st.session_state.generated_memories
            ]
            results = await asyncio.gather(*tasks)

            # Display results
            for idx, (memory, result) in enumerate(zip(st.session_state.generated_memories, results)):
                with st.expander(f"Memory {idx + 1}: {memory}...", expanded=True):
                    st.write("**Relevant Memories:**")
                    for rel_mem in result["relevant_memories"]:
                        st.write(f"- {rel_mem.content}")
                    st.write("**Model Reasoning:**")
                    st.text(result["thinking"])
                    st.write("**Decision Output:**")
                    st.json(result['response'].model_dump_json())

            st.session_state.decision_results = results
            st.session_state.current_step = 3

    if st.session_state.current_step >= 3 and st.session_state.decision_results:
        # Algo to do whatever with the results
        st.markdown("---")
        st.header("Step 3: Database operations")

        with st.spinner("Performing database operations..."):
            decisions: List[ModelResponseDecision] = [resp["response"] for resp in st.session_state.decision_results]
            for idx, dec in enumerate(decisions, 1):
                st.subheader(f"Processing Memory {idx}")
                st.write(f"**Action Type:** {dec.action}")
                
                if dec.action == DecisionOutputType.INSERT:
                    data: InsertAction = dec.data
                    st.write("**Processing Insert Action**")
                    st.write("**Getting related memories...**")

                    # Get related memories
                    provider: EmbeddingsProvider = EmbeddingsFactory.create_provider(settings.embedding_model)
                    embeddings = provider.get_embeddings(data.content)
                    rel_memories_ids = milvus.search_relevent_nodes_by_embeddings(embeddings)
                    rel_memories: List[Memory] = []
                    for id in rel_memories_ids.keys():
                        memory = postgres.get_memory_details(id)
                        rel_memories.append(memory)
                        st.write(f"✓ Found related memory: {memory.content}")
                    st.success(f"Found {len(rel_memories)} related memories")

                    st.write("**Processing memories...**")
                    prompt = ""
                    if len(rel_memories) > 0:
                        # Convert uuid to int
                        rel_memories, uuid_mapping = normalize_memories(rel_memories)
                        
                        # Get prompt
                        prompt = get_insertion_reasoning_prompt(
                            existing_memories=rel_memories,
                            new_memory=data.content
                        )
                    else:
                        # Create prompt for case with no related memories
                        prompt = get_insertion_reasoning_prompt(
                            existing_memories=[],
                            new_memory=data.content
                        )
                        st.warning("No related memories found")

                    st.write("**Getting LLM response...**")
                    # Get response from llm
                    llm_provider: LLMProvider = LLMFactory.create_provider(
                        settings.get_llm_config(DEFAULT_CONFIGS["insertion"]["model"])
                    )
                    messages = [{"role": "user", "content": prompt}]
                    full_resp = ""
                    async for chunk in llm_provider.stream_completion(
                        messages, 
                        DEFAULT_CONFIGS["insertion"]["temperature"]
                    ):
                        full_resp += chunk
                    thinking_resp, json_resp = await process_thinking_response(full_resp, ModelResponseInsertion)

                    st.write("**Model Thinking:**")
                    st.text(thinking_resp)
                    st.write("**Final Action:**")
                    st.json(json_resp.model_dump_json())

                    st.write("**Saving to databases...**")
                    # Convert int back to uuid using mappings if we have related memories
                    if len(rel_memories) > 0:
                        json_resp.related_memory_ids = [
                            uuid_mapping[id] for id in json_resp.related_memory_ids
                            if id in uuid_mapping
                        ]

                    # Insert node in postgres
                    new_mem_id = postgres.insert_memory(data.content)
                    st.write("✓ Saved to PostgreSQL")

                    # Insert node in milvus
                    milvus.insert_node(new_mem_id, embeddings)
                    st.write("✓ Saved to Milvus")

                    # Update mongodb adjacency list
                    for id in json_resp.related_memory_ids:
                        mongodb.make_edge(id, new_mem_id)
                    st.write(f"✓ Created {len(json_resp.related_memory_ids)} edges in MongoDB")
                    
                    st.success("Insert action completed successfully")

                elif dec.action == DecisionOutputType.MERGE_CONFLICT:
                    data: MergeConflictAction = dec.data
                    # TODO: P1 - do this
                    # generate questions
                    # ask user to resolve conflict
                    # generate new memories
                    # insert that memories in database
                    st.info("Merge conflict detected - This will be handled in future updates")

                elif dec.action == DecisionOutputType.RESOLVE_TEMPORAL_CONFLICT:
                    data: ResolveTemporalConflictAction = dec.data
                    # TODO: P1 - do this
                    st.info("Temporal conflict detected - This will be handled in future updates")

                elif dec.action == DecisionOutputType.ADDITION_TO_EXISTING_MEMORY:
                    data: AdditionToExistingMemoryAction = dec.data
                    st.write("**Processing Addition to Existing Memory Action**")
                    
                    for updated_memory in data.updated_memories:
                        st.write(f"**Updating Memory {updated_memory.memory_id}**")
                        st.write("**Getting related memories...**")

                        # Get embeddings for updated content
                        provider: EmbeddingsProvider = EmbeddingsFactory.create_provider(settings.embedding_model)
                        embeddings = provider.get_embeddings(updated_memory.content)
                        rel_memories_ids = milvus.search_relevent_nodes_by_embeddings(embeddings)
                        rel_memories: List[Memory] = []
                        for id in rel_memories_ids.keys():
                            memory = postgres.get_memory_details(id)
                            rel_memories.append(memory)
                            st.write(f"✓ Found related memory: {memory.content}")

                        st.success(f"Found {len(rel_memories)} related memories")

                        st.write("**Processing memories...**")
                        prompt = ""
                        if len(rel_memories) > 0:
                            # Normalize memories for insertion prompt
                            normalized_memories, uuid_mapping = normalize_memories(rel_memories)
                            # Create prompt with normalized memories
                            prompt = get_insertion_reasoning_prompt(
                                new_memory=updated_memory.content,
                                existing_memories=normalized_memories
                            )
                        else:
                            prompt = get_insertion_reasoning_prompt(
                                new_memory=updated_memory.content,
                                existing_memories=[]
                            )

                        st.write("**Getting LLM response...**")
                        # Get response from llm
                        llm_provider: LLMProvider = LLMFactory.create_provider(
                            settings.get_llm_config(DEFAULT_CONFIGS["addition"]["model"])
                        )
                        messages = [{"role": "user", "content": prompt}]
                        full_resp = ""
                        async for chunk in llm_provider.stream_completion(
                            messages,
                            DEFAULT_CONFIGS["addition"]["temperature"]
                        ):
                            full_resp += chunk
                        thinking_resp, json_resp = await process_thinking_response(full_resp, ModelResponseAddition)

                        st.write("**Model Thinking:**")
                        st.text(thinking_resp)
                        st.write("**Final Action:**")
                        st.json(json_resp.model_dump_json())

                        st.write("**Updating databases...**")
                        # Convert int back to uuid using mappings if we have related memories
                        if len(rel_memories) > 0:
                            json_resp.related_memory_ids = [
                                uuid_mapping[id] for id in json_resp.related_memory_ids
                                if id in uuid_mapping
                            ]

                        # Update memory in postgres
                        postgres.update_memory(updated_memory.memory_id, updated_memory.content)
                        st.write("✓ Updated in PostgreSQL")

                        # Update embeddings in milvus
                        milvus.update_embeddings(updated_memory.memory_id, embeddings)
                        st.write("✓ Updated in Milvus")

                        # Update mongodb adjacency list
                        # Add new edges
                        for id in json_resp.related_memory_ids:
                            mongodb.make_edge(updated_memory.memory_id, id)
                        st.write(f"✓ Updated {len(json_resp.related_memory_ids)} edges in MongoDB")

                        st.success(f"Memory {updated_memory.memory_id} updated successfully")

                elif dec.action == DecisionOutputType.IGNORE:
                    data: IgnoreAction = dec.data
                    st.info("Memory ignored - No action needed")

                else:
                    st.error(f"Unknown action type - {dec.action}")

            st.success("All memories processed successfully")
