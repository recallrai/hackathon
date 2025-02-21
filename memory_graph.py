import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from config import get_settings
from utils import mongodb, postgres

settings = get_settings()
DOC_ID = "32f7543c-cf51-49f1-8163-93652e26a695"

def create_color_palette(color_scheme):
    """Generate color palette based on selected scheme"""
    palettes = {
        "Blue to Purple": [(100, 149, 237), (147, 112, 219)],
        "Ocean": [(0, 119, 190), (0, 180, 216)],
        "Forest": [(34, 139, 34), (154, 205, 50)],
        "Sunset": [(255, 127, 80), (255, 99, 71)],
        "Neon": [(0, 255, 255), (255, 0, 255)]
    }
    return palettes.get(color_scheme, palettes["Blue to Purple"])

def get_color_for_node(connections, max_connections, color_scheme):
    """Generate color based on number of connections and selected color scheme"""
    start_color, end_color = create_color_palette(color_scheme)
    ratio = connections / max_connections if max_connections > 0 else 0
    
    r = start_color[0] + (end_color[0] - start_color[0]) * ratio
    g = start_color[1] + (end_color[1] - start_color[1]) * ratio
    b = start_color[2] + (end_color[2] - start_color[2]) * ratio
    
    return f'rgba({int(r)}, {int(g)}, {int(b)}, 0.9)'

def wrap_text(text, node_size):
    """
    Dynamically wrap text based on node size and content length.
    Shows complete text without truncation.
    """
    char_width = max(10, int(node_size / 8))
    words = text.split()
    
    processed_words = []
    for word in words:
        if len(word) > char_width:
            parts = [word[i:i + char_width] for i in range(0, len(word), char_width)]
            processed_words.extend(parts)
        else:
            processed_words.append(word)
    
    lines = []
    current_line = []
    current_length = 0
    
    for word in processed_words:
        if current_length + len(word) + 1 <= char_width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '<br>'.join(lines)

def calculate_node_size(text, min_size=60, max_size=400):
    """Calculate optimal node size based on text content"""
    text_length = len(text)
    num_words = len(text.split())
    
    base_size = min_size + (text_length * 1.2) + (num_words * 3)
    estimated_lines = text_length / 15
    line_padding = estimated_lines * 10
    
    final_size = base_size + line_padding
    return max(min_size, min(final_size, max_size))

def show_memory_graph():
    st.title("Memory Graph Visualization")
    
    # Sidebar organization
    with st.sidebar:
        st.header("Layout Settings")
        
        layout_options = {
            "Force-directed (Best for complex graphs)": nx.spring_layout,
            "Circular (Good for cycles)": nx.circular_layout,
            "Spiral (Space-efficient)": nx.spiral_layout,
            "Shell (Hierarchical)": nx.shell_layout,
            "Spectral (Pattern-based)": nx.spectral_layout
        }
        selected_layout = st.selectbox(
            "Layout Style",
            list(layout_options.keys()),
            help="Choose how nodes are arranged"
        )
        
        st.header("Visual Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            node_spacing = st.slider("Node Spacing", 1.0, 8.0, 3.0, 0.2)
        with col2:
            edge_opacity = st.slider("Connection Opacity", 0.1, 1.0, 0.7, 0.1)
        
        col3, col4 = st.columns(2)
        with col3:
            text_size = st.slider("Text Size", 8, 16, 12, 1)
        with col4:
            text_opacity = st.slider("Text Opacity", 0.5, 1.0, 0.9, 0.1)
        
        st.header("Color Settings")
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Blue to Purple", "Ocean", "Forest", "Sunset", "Neon"]
        )
        
        st.header("Interaction Settings")
        enable_animations = st.checkbox("Enable Animations", True)
        show_labels = st.checkbox("Show Node Labels", True)
        edge_style = st.selectbox(
            "Edge Style",
            ["Curved", "Straight", "Arc"]
        )
    
    try:
        # Get data and create graph
        adjacency_list = mongodb.get_adjacency_list(DOC_ID)
        G = nx.Graph()
        
        # Get all nodes from PostgreSQL database
        db_nodes = postgres.get_all_nodes()
        
        # Initialize the nodes dictionary with zero connections
        nodes_dict = {}
        
        # First pass: Count connections for each node
        for node_id, connections in adjacency_list.items():
            nodes_dict[node_id] = len(connections)
        
        # Second pass: Add all nodes to the graph
        for node in db_nodes:
            try:
                memory = postgres.get_memory_details(node.id)
                # Get connection count from dictionary, default to 0
                connection_count = nodes_dict.get(node.id, 0)
                
                G.add_node(
                    node.id,
                    text=memory.content,
                    connections=connection_count,
                    importance=connection_count
                )
            except Exception as e:
                st.error(f"Error fetching memory {node.id}: {str(e)}")
                continue
        
        # Add edges
        for node_id, connections in adjacency_list.items():
            if node_id in G:  # Only add edges if source node exists
                for target_id in connections:
                    if target_id in G:  # Only add edge if target node exists
                        weight = 1 / (len(connections) + len(adjacency_list.get(target_id, [])))
                        G.add_edge(node_id, target_id, weight=weight)
        
        if len(G.nodes()) == 0:
            st.warning("No memories found in the network")
            return
        
        # Calculate max_connections
        max_connections = max((G.nodes[node]['connections'] for node in G.nodes()), default=1)
        
        # Calculate layout
        layout_name = selected_layout.split(" ")[0].lower()
        layout_func = layout_options[selected_layout]
        
        if layout_name == "force-directed":
            pos = layout_func(G, k=node_spacing, weight='weight', iterations=50)
        else:
            pos = layout_func(G)
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            if edge_style == "Curved":
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2
                curve_factor = 0.2 if enable_animations else 0.1
                curve_x = mid_x + (y1 - y0) * curve_factor
                curve_y = mid_y - (x1 - x0) * curve_factor
                path_x = [x0, curve_x, x1]
                path_y = [y0, curve_y, y1]
                line_shape = 'spline'
            elif edge_style == "Arc":
                mid_x = (x0 + x1) / 2
                mid_y = (y0 + y1) / 2 + abs(x1 - x0) * 0.2
                path_x = [x0, mid_x, x1]
                path_y = [y0, mid_y, y1]
                line_shape = 'spline'
            else:  # Straight
                path_x = [x0, x1]
                path_y = [y0, y1]
                line_shape = 'linear'
            
            edge_trace = go.Scatter(
                x=path_x,
                y=path_y,
                mode='lines',
                line=dict(
                    width=1.5,
                    color=f'rgba(128, 128, 128, {edge_opacity})',
                    shape=line_shape
                ),
                hoverinfo='none'
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        hover_text = []
        node_sizes = []
        node_colors = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_size = calculate_node_size(G.nodes[node]['text'])
            wrapped_text = wrap_text(G.nodes[node]['text'], node_size)
            
            node_text.append(wrapped_text if show_labels else "")
            hover_text.append(
                f"Connections: {G.nodes[node]['connections']}<br>"
                f"Text: {G.nodes[node]['text']}"
            )
            node_sizes.append(node_size)
            node_colors.append(get_color_for_node(
                G.nodes[node]['connections'],
                max_connections,
                color_scheme
            ))
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text' if show_labels else 'markers',
            hoverinfo='text',
            hovertext=hover_text,
            text=node_text,
            textposition="middle center",
            textfont=dict(
                size=max(8, min(text_size, 14)),
                color='rgba(0, 0, 0, {})'.format(text_opacity),
                family='Arial'
            ),
            marker=dict(
                symbol='circle',
                size=node_sizes,
                color=node_colors,
                line=dict(
                    color='rgba(128, 128, 128, 1)',
                    width=1
                )
            )
        )
        
        # Calculate graph bounds
        x_coords = node_x.copy()
        y_coords = node_y.copy()
        x_range = [min(x_coords), max(x_coords)]
        y_range = [min(y_coords), max(y_coords)]
        
        x_padding = (x_range[1] - x_range[0]) * 0.2
        y_padding = (y_range[1] - y_range[0]) * 0.2
        x_range = [x_range[0] - x_padding, x_range[1] + x_padding]
        y_range = [y_range[0] - y_padding, y_range[1] + y_padding]
        
        # Create figure with proper ranges
        fig = go.Figure(
            data=[*edge_traces, node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(
                    range=x_range,
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    fixedrange=False
                ),
                yaxis=dict(
                    range=y_range,
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    fixedrange=False
                ),
                width=1200,
                height=900,
                plot_bgcolor='rgba(255, 255, 255, 0)',
                paper_bgcolor='rgba(255, 255, 255, 0)',
                dragmode='pan'
            )
        )
        
        # Add controls
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    showactive=False,
                    buttons=[
                        dict(
                            label="Reset View",
                            method="relayout",
                            args=[{
                                "xaxis.range": x_range,
                                "yaxis.range": y_range,
                                "xaxis.autorange": False,
                                "yaxis.autorange": False
                            }]
                        ),
                        dict(
                            label="Zoom In",
                            method="relayout",
                            args=[{
                                "xaxis.range": [
                                    (x_range[0] + x_range[1])/2 - (x_range[1] - x_range[0])/4,
                                    (x_range[0] + x_range[1])/2 + (x_range[1] - x_range[0])/4
                                ],
                                "yaxis.range": [
                                    (y_range[0] + y_range[1])/2 - (y_range[1] - y_range[0])/4,
                                    (y_range[0] + y_range[1])/2 + (y_range[1] - y_range[0])/4
                                ]
                            }]
                        )
                    ],
                    pad={"r": 10, "t": 10},
                    x=0.1,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ]
        )
        
        if enable_animations:
            fig.update_layout(
                transition={
                    'duration': 500,
                    'easing': 'cubic-in-out'
                }
            )
        
        # Display graph
        st.plotly_chart(fig, use_container_width=True, config={
            'scrollZoom': True,
            'displayModeBar': True,
            'modeBarButtonsToAdd': ['select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d'],
            'modeBarButtonsToRemove': ['autoScale2d']
        })
        
        # Display graph statistics
        with st.expander("Graph Statistics", expanded=False):
            st.write(f"Total Nodes: {len(G.nodes())}")
            st.write(f"Total Connections: {len(G.edges())}")
            if len(G.nodes()) > 0:
                avg_connections = sum(G.nodes[node]['connections'] for node in G.nodes()) / len(G.nodes())
                st.write(f"Average Connections per Node: {avg_connections:.2f}")
        
    except Exception as e:
        st.error(f"Error generating visualization: {str(e)}")

if __name__ == "__main__":
    show_memory_graph()
