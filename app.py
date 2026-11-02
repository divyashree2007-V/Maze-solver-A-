
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
from collections import deque
import time

from astar import astar_search
from maze import generate_maze


st.set_page_config(
    page_title="Maze Intelligence",
    page_icon="🧩",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background-color: #080f1f;
    color: #ffffff;
}

h1, h2, h3, h4, p, label {
    color: #ffffff !important;
}

[data-testid="stSidebar"] {
    background-color: #14243b !important;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

[data-testid="stSidebar"] label {
    font-weight: 600 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #263c59 !important;
    border: 1px solid #18bde8 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #ffffff !important;
}

[data-baseweb="popover"] [role="option"] {
    background-color: #14243b !important;
    color: #ffffff !important;
}

[data-baseweb="popover"] [role="option"]:hover {
    background-color: #087ea4 !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] button {
    background-color: #087ea4 !important;
    color: #ffffff !important;
    border: none !important;
}

.stButton button {
    background-color: #087ea4 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    border: none !important;
    min-height: 45px;
}

.stButton button:hover {
    background-color: #06a6d1 !important;
    color: #ffffff !important;
}

div[data-testid="stMetric"] {
    background-color: #14243b;
    padding: 16px;
    border-radius: 10px;
    border: 1px solid #263c59;
}

div[data-testid="stMetricLabel"] {
    color: #c4d2e5 !important;
}

div[data-testid="stMetricValue"] {
    color: #ffffff !important;
}

[data-testid="stAlert"] {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


if "grid" not in st.session_state:
    st.session_state.grid, st.session_state.start, st.session_state.goal = (
        generate_maze(21, 21)
    )

if "result" not in st.session_state:
    st.session_state.result = None

if "bfs_result" not in st.session_state:
    st.session_state.bfs_result = None


def bfs_search(grid, start, goal):
    start_time = time.perf_counter()

    queue = deque([start])
    visited = {start}
    parent = {}

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    while queue:
        current = queue.popleft()

        if current == goal:
            path = [goal]

            while path[-1] in parent:
                path.append(parent[path[-1]])

            path.reverse()

            return {
                "path": path,
                "visited_count": len(visited),
                "path_length": len(path) - 1,
                "execution_time": (
                    time.perf_counter() - start_time
                ) * 1000,
                "status": "Path Found"
            }

        for dr, dc in directions:
            nr = current[0] + dr
            nc = current[1] + dc
            neighbor = (nr, nc)

            if (
                0 <= nr < len(grid)
                and 0 <= nc < len(grid[0])
                and grid[nr][nc] == 0
                and neighbor not in visited
            ):
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)

    return {
        "path": [],
        "visited_count": len(visited),
        "path_length": 0,
        "execution_time": (
            time.perf_counter() - start_time
        ) * 1000,
        "status": "No Path Found"
    }


def create_matrix(grid, explored=None, path=None):
    explored = set(explored or [])
    path = set(path or [])

    matrix = []

    for r in range(len(grid)):
        row = []

        for c in range(len(grid[0])):
            position = (r, c)

            if grid[r][c] == 1:
                value = 0
            elif position in path:
                value = 3
            elif position in explored:
                value = 2
            else:
                value = 1

            row.append(value)

        matrix.append(row)

    return matrix


def get_colorscale():
    return [
        [0.00, "#101a2b"],
        [0.249, "#101a2b"],
        [0.25, "#e7edf5"],
        [0.499, "#e7edf5"],
        [0.50, "#18bde8"],
        [0.749, "#18bde8"],
        [0.75, "#ffd43b"],
        [1.00, "#ffd43b"]
    ]


def create_figure(grid, start, goal, explored=None, path=None):
    matrix = create_matrix(grid, explored, path)

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            z=matrix,
            zmin=0,
            zmax=3,
            colorscale=get_colorscale(),
            showscale=False,
            xgap=2,
            ygap=2,
            hoverinfo="skip"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[start[1]],
            y=[start[0]],
            mode="markers+text",
            marker=dict(size=13, color="#22c55e"),
            text=["START"],
            textposition="top center",
            textfont=dict(color="white", size=10),
            name="Start"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[goal[1]],
            y=[goal[0]],
            mode="markers+text",
            marker=dict(size=13, color="#ef4444"),
            text=["GOAL"],
            textposition="top center",
            textfont=dict(color="white", size=10),
            name="Goal"
        )
    )

    fig.update_layout(
        height=460,
        paper_bgcolor="#080f1f",
        plot_bgcolor="#080f1f",
        margin=dict(l=5, r=5, t=15, b=15),
        xaxis=dict(
            visible=False,
            scaleanchor="y",
            scaleratio=1
        ),
        yaxis=dict(
            visible=False,
            autorange="reversed"
        ),
        showlegend=False
    )

    return fig


def create_animated_figure(
    grid,
    start,
    goal,
    positions,
    animation_type
):
    fig = create_figure(grid, start, goal)

    if not positions:
        return fig

    batch_size = 3 if animation_type == "explored" else 1

    frames = []
    current_positions = []

    for index in range(0, len(positions), batch_size):
        current_positions.extend(
            positions[index:index + batch_size]
        )

        if animation_type == "explored":
            matrix = create_matrix(
                grid,
                explored=current_positions
            )
        else:
            matrix = create_matrix(
                grid,
                path=current_positions
            )

        frames.append(
            go.Frame(
                data=[
                    go.Heatmap(
                        z=matrix,
                        zmin=0,
                        zmax=3,
                        colorscale=get_colorscale(),
                        showscale=False,
                        xgap=2,
                        ygap=2,
                        hoverinfo="skip"
                    )
                ],
                traces=[0]
            )
        )

    fig.frames = frames

    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.5,
                y=-0.10,
                xanchor="center",
                yanchor="top",
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {
                                    "duration": 110,
                                    "redraw": True
                                },
                                "transition": {
                                    "duration": 0
                                },
                                "fromcurrent": True,
                                "mode": "immediate"
                            }
                        ]
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": True
                                },
                                "transition": {
                                    "duration": 0
                                },
                                "mode": "immediate"
                            }
                        ]
                    )
                ]
            )
        ],
        margin=dict(l=5, r=5, t=15, b=65)
    )

    return fig


def display_animation(fig):
    html = pio.to_html(
        fig,
        full_html=True,
        include_plotlyjs=True,
        auto_play=True,
        animation_opts={
            "frame": {
                "duration": 110,
                "redraw": True
            },
            "transition": {
                "duration": 0
            },
            "fromcurrent": True,
            "mode": "immediate"
        }
    )

    st.components.v1.html(
        html,
        height=510,
        scrolling=False
    )


st.title("🧩 MAZE INTELLIGENCE")

st.caption(
    "AI-Powered Maze Navigation Using A* Search Algorithm"
)


st.sidebar.title("⚙️ CONTROL PANEL")

st.sidebar.markdown("### Maze Settings")

maze_size = st.sidebar.selectbox(
    "Select Maze Size",
    [11, 15, 19, 21, 25, 29],
    index=3
)

st.sidebar.markdown("---")

if st.sidebar.button(
    "🔄 GENERATE NEW MAZE",
    use_container_width=True
):
    st.session_state.grid, st.session_state.start, st.session_state.goal = (
        generate_maze(maze_size, maze_size)
    )

    st.session_state.result = None
    st.session_state.bfs_result = None

    st.rerun()


st.sidebar.markdown("---")

st.sidebar.markdown("### Algorithm Details")

st.sidebar.info(
    "A* Search Algorithm\n\n"
    "Heuristic: Manhattan Distance\n\n"
    "Path Cost: 1 per movement\n\n"
    "Comparison: BFS"
)

st.sidebar.markdown("---")

st.sidebar.markdown("### Color Guide")
st.sidebar.markdown("⬛ Walls")
st.sidebar.markdown("⬜ Open Cells")
st.sidebar.markdown("🟦 Explored Nodes")
st.sidebar.markdown("🟨 Shortest Path")
st.sidebar.markdown("🟩 Start Point")
st.sidebar.markdown("🟥 Goal Point")


grid = st.session_state.grid
start = st.session_state.start
goal = st.session_state.goal


st.markdown("### 🗺️ MAZE OVERVIEW")

if st.session_state.result is None:
    initial_fig = create_figure(
        grid,
        start,
        goal
    )

    st.plotly_chart(
        initial_fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


if st.button(
    "🔎 START A* SEARCH",
    use_container_width=True
):
    with st.spinner("A* is calculating the shortest route..."):
        st.session_state.result = astar_search(
            grid,
            start,
            goal
        )

        st.session_state.bfs_result = bfs_search(
            grid,
            start,
            goal
        )

    st.rerun()


result = st.session_state.result


if result:

    if result["status"] == "Path Found":
        st.success("Shortest Path Successfully Found!")
    else:
        st.error("No Path Found!")

    st.markdown("---")

    st.markdown("### 🔬 SEARCH VISUALIZATION COMPARISON")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 🔍 EXPLORED NODES")

        st.caption(
            "Cyan cells show all positions visited by A*."
        )

        explored_fig = create_animated_figure(
            grid,
            start,
            goal,
            result["explored_order"],
            "explored"
        )

        display_animation(explored_fig)

    with col2:
        st.markdown("### 🟡 SHORTEST PATH")

        st.caption(
            "Yellow cells show the final route from Start to Goal."
        )

        path_fig = create_animated_figure(
            grid,
            start,
            goal,
            result["path"],
            "path"
        )

        display_animation(path_fig)

    st.markdown("---")

    st.markdown("### 📊 A* PERFORMANCE ANALYSIS")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Path Length",
        result["path_length"]
    )

    col2.metric(
        "Nodes Explored",
        result["visited_count"]
    )

    col3.metric(
        "Execution Time",
        f'{result["execution_time"]:.3f} ms'
    )

    col4.metric(
        "Status",
        result["status"]
    )

    st.markdown("---")

    st.markdown("### ⚔️ A* VS BFS COMPARISON")

    bfs = st.session_state.bfs_result

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🧠 A* Search")

        st.metric("Path Length", result["path_length"])
        st.metric("Nodes Explored", result["visited_count"])

        st.metric(
            "Execution Time",
            f'{result["execution_time"]:.3f} ms'
        )

    with col2:
        st.subheader("🔍 Breadth First Search")

        st.metric("Path Length", bfs["path_length"])
        st.metric("Nodes Explored", bfs["visited_count"])

        st.metric(
            "Execution Time",
            f'{bfs["execution_time"]:.3f} ms'
        )

    st.markdown("---")

    st.markdown("### 🧠 HOW A* WORKS")

    st.write(
        "A* is an informed search algorithm that finds an optimal path "
        "by combining actual movement cost and estimated distance "
        "to the goal."
    )

    st.latex(r"f(n) = g(n) + h(n)")

    st.write("**g(n):** Actual cost from the starting point.")
    st.write("**h(n):** Estimated distance to the goal using Manhattan Distance.")
    st.write("**f(n):** Total estimated cost.")

else:
    st.info(
        "Click START A* SEARCH to explore the maze and find the shortest path."
    )
