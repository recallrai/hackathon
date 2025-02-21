import streamlit as st
from utils import mongodb, postgres, milvus

def get_database_counts():
    """Get count of items in each database"""
    pg_count = postgres.get_node_count()
    mongo_count = sum([len(mongodb.get_adjacency_list()[node_adj_list]) for node_adj_list in mongodb.get_adjacency_list().keys()])
    milvus_count = milvus.get_node_count()
    return pg_count, mongo_count, milvus_count

def show_reset_database():
    st.title("⚠️ Danger Zone ⚠️")
    st.warning("Warning: These actions are irreversible!")

    # Get current counts
    pg_count, mongo_count, milvus_count = get_database_counts()
    
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("PostgreSQL Nodes", pg_count)
        pg_confirm = st.checkbox(f"Confirm deletion of {pg_count} PostgreSQL nodes")
        if st.button("Clear PostgreSQL"):
            if pg_confirm:
                postgres.clear_all_nodes()
                st.success(f"PostgreSQL database cleared! Deleted {pg_count} nodes.")
            else:
                st.error("Please confirm deletion by checking the box")

    with col2:
        st.metric("MongoDB Edges", mongo_count)
        mongo_confirm = st.checkbox(f"Confirm deletion of {mongo_count} MongoDB edges")
        if st.button("Clear MongoDB"):
            if mongo_confirm:
                mongodb.delete_adjacency_list()
                st.success(f"MongoDB cleared! Deleted {mongo_count} edges.")
            else:
                st.error("Please confirm deletion by checking the box")

    with col3:
        st.metric("Milvus Vectors", milvus_count)
        milvus_confirm = st.checkbox(f"Confirm deletion of {milvus_count} Milvus vectors")
        if st.button("Clear Milvus"):
            if milvus_confirm:
                milvus.clear_all_nodes()
                st.success(f"Milvus database cleared! Deleted {milvus_count} vectors.")
            else:
                st.error("Please confirm deletion by checking the box")
