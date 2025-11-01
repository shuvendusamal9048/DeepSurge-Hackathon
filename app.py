import streamlit as st
import pandas as pd
import plotly.express as px
import bcrypt
from database import create_connection
import datetime

conn = create_connection()
cursor = conn.cursor(dictionary=True)

# ------------------ Signup ------------------
st.sidebar.header("📝 Sign Up")
new_user = st.sidebar.text_input("New username")
new_pass = st.sidebar.text_input("New password", type="password")

if st.sidebar.button("Register"):
    if not new_user or not new_pass:
        st.sidebar.error("Enter both username and password")
    else:
        cursor.execute("SELECT * FROM admin WHERE username=%s", (new_user,))
        if cursor.fetchone():
            st.sidebar.error("User already exists")
        else:
            hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
            cursor.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", (new_user, hashed))
            conn.commit()
            st.sidebar.success("✅ User created! Please log in above.")

# ------------------ Login ------------------
st.header("🔐 Login")
username_input = st.text_input("Username")
password_input = st.text_input("Password", type="password")

if st.button("Login"):
    cursor.execute("SELECT * FROM admin WHERE username=%s", (username_input,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password_input.encode(), user['password'].encode()):
        st.success(f"✅ Logged in as {username_input}")
        st.session_state["logged_in_user"] = username_input
    else:
        st.error("❌ Invalid username or password")

# ------------------ CSV Upload ------------------
if "logged_in_user" in st.session_state:
    username = st.session_state["logged_in_user"]

    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        # Save metadata to MySQL
        cursor.execute(
            "INSERT INTO file_info (filename, uploaded_by, rows, cols) VALUES (%s, %s, %s, %s)",
            (uploaded_file.name, username, df.shape[0], df.shape[1])
        )
        conn.commit()
        st.success(f"✅ Metadata saved for {uploaded_file.name}")

        # ---------------- Dynamic Charts ----------------
        st.subheader("📈 Charts")
        num_cols = df.select_dtypes(include='number').columns.tolist()
        cat_cols = df.select_dtypes(include='object').columns.tolist()

        chart_type = st.selectbox("Select chart type", ["Line", "Scatter", "Histogram", "Bar", "Pie"])

        if chart_type in ["Line", "Scatter"]:
            if len(num_cols) >= 2:
                x_col = st.selectbox("X-axis", num_cols)
                y_col = st.selectbox("Y-axis", [c for c in num_cols if c != x_col])
                fig = px.line(df, x=x_col, y=y_col) if chart_type == "Line" else px.scatter(df, x=x_col, y=y_col)
                st.plotly_chart(fig)

        elif chart_type == "Histogram" and num_cols:
            col = st.selectbox("Column", num_cols)
            fig = px.histogram(df, x=col)
            st.plotly_chart(fig)

        elif chart_type in ["Bar", "Pie"] and cat_cols and num_cols:
            x_col = st.selectbox("Categorical X", cat_cols)
            y_col = st.selectbox("Numeric Y", num_cols)
            data = df.groupby(x_col)[y_col].sum().reset_index()
            fig = px.bar(data, x=x_col, y=y_col) if chart_type == "Bar" else px.pie(data, names=x_col, values=y_col)
            st.plotly_chart(fig)
