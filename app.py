import streamlit as st
import pandas as pd
import plotly.express as px
from db import create_admin, validate_admin, save_file_info, get_user_files

st.set_page_config(page_title="CSV Explorer", layout="wide", page_icon="🚀")

# ------------------ Session State ------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "show_register" not in st.session_state:
    st.session_state["show_register"] = False
if "uploaded_df" not in st.session_state:
    st.session_state["uploaded_df"] = None

# ------------------ Login Page ------------------
def show_login_page():
    # Centered Login Title
    st.markdown(
        "<h1 style='text-align: center; color: #4CAF50;'>Login</h1>",
        unsafe_allow_html=True
    )

    # CSS to center the form and style input boxes
    st.markdown(
        """
        <style>
        /* Center the form container */
        .stForm {
            max-width: 400px;
            margin: 0 auto; /* center horizontally */
            padding: 30px;
            border: 2px solid #4CAF50;
            border-radius: 10px;
            background-color: #e8f5e9;
        }

        /* Make input boxes full width inside the form */
        .stTextInput>div>div>input {
            width: 100% !important;
        }

        /* Center the submit button */
        div.stButton > button {
            display: block;
            margin: 10px auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Streamlit form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username and password:
                user = validate_admin(username, password)
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = username
                else:
                    st.error("❌ Invalid username or password.")
            else:
                st.warning("Please enter username and password")

    # Register button centered
    st.markdown(
        """
        <div style="
            max-width: 400px;
            margin: 0 auto;  /* center */
            padding: 15px;
            background-color: #FFECB3;  /* color of the box */
            border-radius: 0 0 10px 10px;  /* rounded bottom corners */
            text-align: center;
        ">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Place the register button inside the colored box
    if st.button("New User? Register Here"):
        st.session_state["show_register"] = True
# ------------------ Register Page ------------------
def show_register_page():
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Register</h1>", unsafe_allow_html=True)

    with st.form("register_form"):
        st.markdown(
            """
            <style>
            .stForm {
                max-width: 400px;
                margin: 0 auto;
                padding: 30px;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                background-color: #FFF3E0;
            }
            .stTextInput>div>div>input {
                width: 100% !important;
            }
            div.stButton > button {
                display: block;
                margin: 10px auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        new_user = st.text_input("New Username", key="reg_user")
        new_pass = st.text_input("New Password", type="password", key="reg_pass")
        submitted = st.form_submit_button("Register")
        if submitted:
            if new_user and new_pass:
                create_admin(new_user, new_pass)
                st.success("✅ Registered Successfully! Go back to login.")
            else:
                st.warning("Please fill all fields")

    if st.button("Back to Login"):
        st.session_state["show_register"] = False
# ------------------ CSV Upload & Dashboard ------------------
def show_upload_page():
    st.markdown(f"## 👋 Welcome, {st.session_state['user']}!")

    if st.button("Logout"):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["uploaded_df"] = None

    st.sidebar.header("📂 Upload & Visualization")
    uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state["uploaded_df"] = df
        save_file_info(uploaded_file.name, st.session_state["user"])
        st.success(f"✅ File '{uploaded_file.name}' info saved in database!")

    if st.session_state["uploaded_df"] is not None:
        df = st.session_state["uploaded_df"]

        # ------------------ Metrics ------------------
        st.markdown("### 🧾 Dataset Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("Rows", df.shape[0])
        col2.metric("Columns", df.shape[1])
        col3.metric("Missing Values", df.isnull().sum().sum())

        st.write("### Preview of Dataset")
        st.dataframe(df.head())

        st.markdown("### ⚙ Data Preprocessing")
        st.write("*Null Values per Column:*")
        st.write(df.isnull().sum())
        st.write("*Basic Statistics:*")
        st.write(df.describe(include='all'))

        df_filled = df.fillna("Missing")

        # ------------------ Visualization ------------------
        st.markdown("### 📊 Interactive Visualizations")
        numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

        with st.sidebar.expander("Chart Options"):
            chart_type = st.selectbox("Select Chart Type", ["Bar", "Line", "Pie", "Scatter"])
            x_axis = st.selectbox("X-axis", df.columns)
            y_axis = None
            color_col = None
            if chart_type in ["Bar", "Line", "Scatter"]:
                y_axis = st.selectbox("Y-axis", numeric_cols if numeric_cols else df.columns)
            if chart_type in ["Bar", "Pie", "Scatter"]:
                color_col = st.selectbox("Color (optional)", categorical_cols + [None])

        fig = None
        if chart_type == "Bar":
            fig = px.bar(df, x=x_axis, y=y_axis, color=color_col,
                         title=f"Bar Chart: {y_axis} vs {x_axis}",
                         text_auto=True, template="plotly_dark")
        elif chart_type == "Line":
            fig = px.line(df, x=x_axis, y=y_axis, color=color_col,
                          title=f"Line Chart: {y_axis} vs {x_axis}",
                          template="plotly_dark", markers=True)
        elif chart_type == "Pie":
            if categorical_cols:
                pie_col = st.selectbox("Column for Pie Chart", categorical_cols, key="pie_col")
                fig = px.pie(df, names=pie_col, color=color_col,
                             title=f"Pie Chart: {pie_col}",
                             template="plotly_dark", hole=0.3)
        elif chart_type == "Scatter":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col,
                             title=f"Scatter: {y_axis} vs {x_axis}",
                             template="plotly_dark", size_max=15, hover_data=df.columns)

        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # ------------------ File Upload History ------------------
        st.markdown("### 🗂 Your Uploaded File History")
        user_files = get_user_files(st.session_state["user"])
        if user_files is not None and not user_files.empty:
            st.dataframe(user_files)
        else:
            st.info("You haven’t uploaded any files yet!")

# ------------------ App Flow ------------------
if st.session_state["logged_in"]:
    show_upload_page()
else:
    if st.session_state["show_register"]:
        show_register_page()
    else:
        show_login_page()