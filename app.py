
import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Titanic Analytics Dashboard",
    page_icon="🚢",
    layout="wide"
)

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("data/titanic_cleaned.csv")

df = load_data()

# Prepare additional columns
df["family_size"] = df["sibsp"] + df["parch"] + 1

df["age_group"] = pd.cut(
    df["age"],
    bins=[0, 12, 18, 60, 100],
    labels=["Child", "Teenager", "Adult", "Senior"]
)

# Dashboard title
st.title("🚢 Titanic Passenger Analytics")
st.caption("Interactive Exploratory Data Analysis Dashboard")

st.divider()

# Sidebar filters
st.sidebar.header("Dashboard Filters")

gender = st.sidebar.multiselect(
    "Select Gender",
    sorted(df["sex"].dropna().unique()),
    default=sorted(df["sex"].dropna().unique())
)

classes = st.sidebar.multiselect(
    "Select Passenger Class",
    sorted(df["class"].dropna().unique()),
    default=sorted(df["class"].dropna().unique())
)

age_groups = st.sidebar.multiselect(
    "Select Age Group",
    ["Child", "Teenager", "Adult", "Senior"],
    default=["Child", "Teenager", "Adult", "Senior"]
)

survival = st.sidebar.selectbox(
    "Survival Status",
    ["All", "Survived", "Did Not Survive"]
)

# Apply filters
filtered_df = df[
    (df["sex"].isin(gender)) &
    (df["class"].isin(classes)) &
    (df["age_group"].astype(str).isin(age_groups))
]

if survival == "Survived":
    filtered_df = filtered_df[filtered_df["survived"] == 1]
elif survival == "Did Not Survive":
    filtered_df = filtered_df[filtered_df["survived"] == 0]

# KPI calculations
total = len(filtered_df)
survivors = int(filtered_df["survived"].sum())

survival_rate = (
    filtered_df["survived"].mean() * 100 if total else 0
)

average_age = filtered_df["age"].mean() if total else 0
average_fare = filtered_df["fare"].mean() if total else 0

# KPI cards
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Passengers", f"{total:,}")
col2.metric("Total Survivors", f"{survivors:,}")
col3.metric("Survival Rate", f"{survival_rate:.2f}%")
col4.metric("Average Age", f"{average_age:.2f}" if total else "N/A")

st.metric(
    "Average Fare",
    f"{average_fare:.2f}" if total else "N/A"
)

st.divider()

if total == 0:
    st.warning("No passengers match the selected filters.")
else:
    # Gender chart
    st.subheader("Passenger Analysis")

    col1, col2 = st.columns(2)

    gender_data = (
        filtered_df.groupby(["sex", "survived"])
        .size()
        .reset_index(name="Passengers")
    )

    gender_data["Status"] = gender_data["survived"].map({
        0: "Did Not Survive",
        1: "Survived"
    })

    with col1:
        fig_gender = px.bar(
            gender_data,
            x="sex",
            y="Passengers",
            color="Status",
            barmode="group",
            title="Gender vs Survival",
            color_discrete_map={
                "Survived": "green",
                "Did Not Survive": "red"
            }
        )
        st.plotly_chart(fig_gender, use_container_width=True)

    # Class chart
    class_data = (
        filtered_df.groupby(["class", "survived"])
        .size()
        .reset_index(name="Passengers")
    )

    class_data["Status"] = class_data["survived"].map({
        0: "Did Not Survive",
        1: "Survived"
    })

    with col2:
        fig_class = px.bar(
            class_data,
            x="class",
            y="Passengers",
            color="Status",
            barmode="group",
            title="Passenger Class vs Survival",
            color_discrete_map={
                "Survived": "green",
                "Did Not Survive": "red"
            }
        )
        st.plotly_chart(fig_class, use_container_width=True)

    # Age distribution
    st.subheader("Age and Fare Analysis")

    col1, col2 = st.columns(2)

    with col1:
        fig_age = px.histogram(
            filtered_df,
            x="age",
            nbins=25,
            title="Age Distribution",
            marginal="box"
        )
        st.plotly_chart(fig_age, use_container_width=True)

    with col2:
        fig_fare = px.histogram(
            filtered_df,
            x="fare",
            nbins=30,
            title="Fare Distribution",
            marginal="box"
        )
        st.plotly_chart(fig_fare, use_container_width=True)

    # Family size chart
    family_data = (
        filtered_df.groupby("family_size")["survived"]
        .mean()
        .mul(100)
        .reset_index(name="Survival Rate")
    )

    fig_family = px.bar(
        family_data,
        x="family_size",
        y="Survival Rate",
        title="Family Size vs Survival Rate",
        labels={
            "family_size": "Family Size",
            "Survival Rate": "Survival Rate (%)"
        }
    )

    st.plotly_chart(fig_family, use_container_width=True)

    # Data table
    with st.expander("View Filtered Passenger Data"):
        st.dataframe(filtered_df, use_container_width=True)

st.divider()
st.caption("SWYNEX Internship | Task 3 - Interactive Dashboard")
