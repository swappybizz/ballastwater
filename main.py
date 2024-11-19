import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Title and Description
st.title("Dynamic Ballast Water Exchange Simulator")
st.markdown("""
This advanced simulator models ballast water exchange operations with real-time dynamic graphs for input-output relationships.
""")

# Sidebar Inputs
st.sidebar.header("Tank Parameters")
tank_length = st.sidebar.slider("Tank Length (m)", 10.0, 200.0, 50.0)
tank_width = st.sidebar.slider("Tank Width (m)", 5.0, 50.0, 20.0)
tank_height = st.sidebar.slider("Tank Height (m)", 5.0, 20.0, 10.0)
flow_rate = st.sidebar.slider("Flow Rate (m³/s)", 0.1, 10.0, 1.0, 0.1)
exchange_efficiency = st.sidebar.slider("Exchange Efficiency (%)", 10, 100, 80)

# Initialize session state variables
if "concentration" not in st.session_state:
    st.session_state.concentration = np.ones((100, 100))
if "time_step" not in st.session_state:
    st.session_state.time_step = 0
if "efficiency_over_time" not in st.session_state:
    st.session_state.efficiency_over_time = []
if "flow_rate_impact" not in st.session_state:
    st.session_state.flow_rate_impact = []
if "tank_area_impact" not in st.session_state:
    st.session_state.tank_area_impact = []

# Simulation logic
def update_concentration(concentration, flow, efficiency):
    """
    Updates the concentration field using a simplified mixing model.
    """
    # Add random mixing effects to simulate turbulence
    noise = np.random.uniform(-0.05, 0.05, concentration.shape)
    concentration += flow * noise

    # Add exchange efficiency effects
    concentration *= (1 - efficiency / 100)
    concentration = np.clip(concentration, 0, 1)  # Keep values within bounds
    return concentration

# Function to simulate the mixing process
@st.fragment(run_every=1)
def run_simulation():
    st.session_state.time_step += 1

    # Update concentration
    st.session_state.concentration = update_concentration(
        st.session_state.concentration,
        flow_rate,
        exchange_efficiency
    )

    # Track efficiency over time
    avg_concentration = np.mean(st.session_state.concentration)
    st.session_state.efficiency_over_time.append((st.session_state.time_step, avg_concentration))

    # Track flow rate impact (avoid duplicate entries)
    if not st.session_state.flow_rate_impact or st.session_state.flow_rate_impact[-1][0] != flow_rate:
        st.session_state.flow_rate_impact.append((flow_rate, avg_concentration))

    # Track tank area impact
    tank_area = tank_length * tank_width
    st.session_state.tank_area_impact.append((tank_area, avg_concentration))

# Function to plot Efficiency vs Time
@st.fragment(run_every=1)
def plot_efficiency_over_time():
    times, efficiencies = zip(*st.session_state.efficiency_over_time)

    fig, ax = plt.subplots()
    ax.plot(times, efficiencies, marker="o", linestyle="-", color="blue")
    ax.set_title("Efficiency Over Time")
    ax.set_xlabel("Time Steps")
    ax.set_ylabel("Average Concentration")
    ax.grid(True)

    st.pyplot(fig)

# Function to plot Flow Rate Impact
@st.fragment(run_every=1)
def plot_flow_rate_impact():
    flow_rates, efficiencies = zip(*st.session_state.flow_rate_impact)

    fig, ax = plt.subplots()
    scatter = ax.scatter(flow_rates, efficiencies, c=range(len(flow_rates)), cmap="viridis")
    for i, txt in enumerate(range(len(flow_rates))):
        ax.annotate(txt, (flow_rates[i], efficiencies[i]), fontsize=8)
    ax.set_title("Flow Rate vs Efficiency")
    ax.set_xlabel("Flow Rate (m³/s)")
    ax.set_ylabel("Average Concentration")
    ax.grid(True)

    st.pyplot(fig)

# Function to plot Tank Dimension Impact
@st.fragment(run_every=1)
def plot_tank_dimension_impact():
    tank_areas, efficiencies = zip(*st.session_state.tank_area_impact)

    fig, ax = plt.subplots()
    ax.plot(tank_areas, efficiencies, marker="x", linestyle="--", color="orange")
    ax.set_title("Tank Area vs Mixing Efficiency")
    ax.set_xlabel("Tank Area (m²)")
    ax.set_ylabel("Average Concentration")
    ax.grid(True)

    st.pyplot(fig)

# Function to plot Concentration Dynamics
@st.fragment(run_every=1)
def plot_concentration_dynamics():
    fig, ax = plt.subplots()
    c = ax.imshow(
        st.session_state.concentration,
        extent=[0, tank_length, 0, tank_width],
        origin="lower",
        cmap="coolwarm",
        interpolation="nearest"
    )
    plt.colorbar(c, ax=ax, label="Concentration")
    ax.set_title(f"Ballast Water Mixing (Step {st.session_state.time_step})")
    ax.set_xlabel("Tank Length (m)")
    ax.set_ylabel("Tank Width (m)")

    st.pyplot(fig)

# Real-Time Simulation
st.subheader("Simulation Output")
run_simulation()

# Input-Output Graphs in 2x2 Grid
st.subheader("Dynamic Graphs")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Concentration Dynamics")
    plot_concentration_dynamics()

with col2:
    st.markdown("### Efficiency Over Time")
    plot_efficiency_over_time()

with col1:
    st.markdown("### Flow Rate Impact on Efficiency")
    plot_flow_rate_impact()

with col2:
    st.markdown("### Tank Dimensions Impact on Efficiency")
    plot_tank_dimension_impact()

# Notes and Additional Information
st.markdown("""
### Notes:
- **Efficiency Over Time**: Tracks the average concentration during the mixing process.
- **Flow Rate Impact**: Demonstrates how flow rate affects the average concentration.
- **Tank Dimensions Impact**: Shows the relationship between tank area and mixing efficiency.
- **Concentration Dynamics**: Displays the concentration field evolution in the tank.
- Adjust the parameters in the sidebar to observe dynamic changes in real-time.
""")
