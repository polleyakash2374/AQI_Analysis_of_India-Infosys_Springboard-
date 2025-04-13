import streamlit as st
from streamlit.components.v1 import html
import pandas as pd
import hashlib
import time
from io import BytesIO
import sqlite3
import os
import base64


# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()
# Helper functions for password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# Database operations
def add_user(email, password, name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', 
                  (email, hash_password(password), name))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def get_user(email):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    conn.close()
    return user

def update_password(email, new_password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('UPDATE users SET password = ? WHERE email = ?', 
              (hash_password(new_password), email))
    conn.commit()
    conn.close()

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def add_background_image(image_file):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/png;base64,{image_file});
            background-size: cover;
            
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Replace 'background.jpg' with your image file path
image_path = "raj1.webp"
if os.path.exists(image_path):
    image_base64 = get_base64_image(image_path)
    add_background_image(image_base64)
else:
    st.warning("Background image not found.")


# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "reset_password_step" not in st.session_state:
    st.session_state.reset_password_step = None
if "email_to_reset" not in st.session_state:
    st.session_state.email_to_reset = None


# Authentication Functionality
def signup():
    st.title("Sign Up")
    email = st.text_input("Email")
    name = st.text_input("Name")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("🔒Sign Up"):
        if not email or not name or not password:
            st.error("Please fill in all fields.")
        elif get_user(email):
            st.error("Email already exists.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            success = add_user(email, password, name)
            if success:
                st.success("Sign up successful. Please log in.")
                time.sleep(1)
                # st.experimental_rerun()
            else:
                st.error("Error signing up. Please try again.")

def login():
    st.title("🔒Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(email)
        if user and verify_password(password, user[1]):
            st.session_state.logged_in = True
            st.session_state.user = user[2]
            st.success("Login successful🔓")
            time.sleep(1)
            #st.experimental_rerun()
        else:
            st.error("Invalid email or password.")

    if st.button("Forgot Password"):
        st.session_state.reset_password_step = 1
        # st.experimental_rerun()

def reset_password():
    if st.session_state.reset_password_step == 1:
        st.title("Reset Password")
        email = st.text_input("Enter your registered Email")

        if st.button("Submit"):
            user = get_user(email)
            if user:
                st.session_state.email_to_reset = email
                st.session_state.reset_password_step = 2
                # st.experimental_rerun()
            else:
                st.error("Email not found. Please check and try again.")

    elif st.session_state.reset_password_step == 2:
        st.title("Set New Password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")

        if st.button("Reset Password"):
            if not new_password:
                st.error("Password cannot be empty.")
            elif new_password != confirm_new_password:
                st.error("Passwords do not match.")
            else:
                update_password(st.session_state.email_to_reset, new_password)
                st.success("Password has been reset successfully.")
                time.sleep(1)
                st.session_state.reset_password_step = None
                st.session_state.email_to_reset = None
                #st.experimental_rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    # st.experimental_rerun()

# Main App Description
def app_description():
    # st.title("🏠Home")
    import streamlit as st
    st.markdown("<h1 style='text-align: center; color: #ffffff;'>🏠Home</h1>", unsafe_allow_html=True)
    # st.image("aqio.webp") 
    st.markdown(
    """
    <style>
        button[title^=Exit]+div [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

    st.write("""
## What is AQI in India?
The Air Quality Index (AQI) is a standardized metric used to measure and communicate air quality. It indicates the level of air pollution and its potential impact on health. The AQI scale in India, developed by the Central Pollution Control Board (CPCB), considers various pollutants, including:

Particulate Matter (PM2.5 and PM10)
Nitrogen Dioxide (NO₂)
Sulfur Dioxide (SO₂)
Carbon Monoxide (CO)
Ozone (O₃)
Ammonia (NH₃)
             
AQI values are categorized into different ranges (e.g., Good, Satisfactory, Moderate, Poor, Very Poor, and Severe), each indicating the associated health implications.

## What Can We Get from the Dashboard?
             
⚫  ***The dashboard can provide insights and features such as***:

♦️***City-Wise AQI Distribution***: Identify cities with the highest and lowest AQI levels at any given time.
             
♦️***Pollutant Breakdown***: Analyze the concentration of individual pollutants (PM2.5, NO₂, etc.).
             
♦️***Historical Data***: View AQI trends over days, months, or years to observe seasonal variations or the impact of interventions.
             
♦️***Health Advisory***: Generate health warnings and recommended actions based on AQI levels.
             
♦️***Comparison Tools***: Compare AQI and pollutant data across cities or time periods.
             
♦️***Data Download***: Allow users to download filtered or raw data for deeper analysis.
             
⚫ ***Targeted Information for Stakeholders***:
             
♦️***Residents***: Take precautions against pollution.
             
♦️***Researchers***: Study pollution causes and mitigation.
             
♦️***Businesses***: Adapt operations during high pollution levels.
             
♦️***Government Agencies***: Use the data for policymaking and enforcement.
             

             
## Why Charts are Necessary for AQI Representation?
             
♦️***Clarity***: Charts simplify complex data, making it understandable at a glance.
             
♦️***Comparisons***: Bar charts or line graphs help compare AQI or pollutant levels across cities or timeframes.
             
♦️***Interactive Exploration***: Tools like pie charts, heatmaps, and dashboards provide interactive ways to delve deeper into specific data points.
             
♦️***Decision-Making***: Visual representations assist in identifying trends, anomalies, and actionable patterns efficiently.
             
In essence, an AQI dashboard app with various charts and visualization features bridges the gap between raw data and actionable insights, empowering users to make informed decisions for a healthier environment.
    """)

# Power BI Dashboard Integration
def dashboard():
    st.header("📊Dashboard")
    st.markdown("Dashboard of AQI details of INDIA")
    st.components.v1.iframe("https://app.powerbi.com/view?r=eyJrIjoiOTg5YTkxNzQtYmY2Ny00OGQxLTg1YmMtZmI0NWY0NWZhYTBhIiwidCI6ImU1MjFhY2E0LTA2NTYtNDU2Ni04OGVmLWY3ZDg3MzY0ZGExMCJ9", height=500)

def data_download():
    st.header("📥Download Filtered Data")
    st.markdown("<h2 style='color:#ffffff;'>Sample dataset</h2>",unsafe_allow_html=True)
    df="InfosysDataset.csv"
    try:
    # Load data
        data = pd.read_csv(df)
        # st.write(data.head())
        AQI_Bucket = st.multiselect("Filter by Category", options=data["AQI_Bucket"].unique())
        City = st.multiselect("Filter by City", options=data["StationId"].unique())

        filtered_data1 = data
        if AQI_Bucket:
              filtered_data1 = filtered_data1[filtered_data1["AQI_Bucket"].isin(AQI_Bucket)]
        if City:
            filtered_data1 = filtered_data1[filtered_data1["StationId"].isin(City)]
        st.write(filtered_data1)
        csv = filtered_data1.to_csv(index=False)
        st.download_button("Download Data", data=csv, file_name="filtered_data1.csv", mime="text/csv")

        
    except FileNotFoundError:
        st.error("Error loading data. Ensure the 'InfosysDataset.csv' file exists in the working directory.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

def data_about():
    st.markdown("<h1 style='color: #ffffff;'>🎯 Conclusion</h1>", unsafe_allow_html=True)
    st.write("""
        - Top AQI of India: Benglaluru,Chennai,Gurugram,Hydrabad,Kolkata
        - Avg of NO2: 28.88 
        - Avg of SO2: 11.05
        - Avg of PM2.5: 66.49
        - Avg of CO: 1.49
    """)
    st.markdown("<h2 style='color: #ffffff;'>💬 Feedback</h2>", unsafe_allow_html=True)
    with st.form(key="feedback_form"):
        st.text_area("Your Feedback", placeholder="Write your comments here...")
        rating = st.slider("Rate Us", 1, 5, 3)
        submitted = st.form_submit_button("Submit")
        if submitted:
            #st.experimental_rerun()
            st.success("Thank you for your feedback!")
    
    st.markdown("<h2 style='color: #ffffff;'>❓ Need Help</h2>", unsafe_allow_html=True)
    st.info("For issues or support, contact the administrator at polleyakash1810@gmail.com")
# # Main Logic
def main():
    # Custom CSS for Styling
    st.markdown(f"""
        <style>
        body {{ 
            background-color: #f6f6f2; 
            font-family: 'Arial', sans-serif; 
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #388087;
        }}
        .stButton>button {{
            background-color: #FFFFFF; 
            color: black; 
            border-radius: 8px; 
            padding: 10px;
        }}
        .stButton>button:hover {{
            background-color:#C5B5B8 ;
        }}
        .custom-heading {{
            font-size: 34px; /* Slightly larger font size */
            font-weight: bold;
            color: #388087;
            text-align: center;
            margin-bottom: 20px;
        }}
        .content-container {{
            padding: 20px;
            background-color: #6FB3BB; 
            border-radius: 10px;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Handle reset password step
    if st.session_state.reset_password_step:
        reset_password()
    # If not logged in, show login/signup options
    elif not st.session_state.get('logged_in', False):
        choice = st.sidebar.radio("Choose an option", ["Login", "Sign Up"])
        if choice == "Login":
            login()
            if "page" not in st.session_state  :
                st.session_state.page = "Home"
            if st.session_state.page != "Home":
                st.session_state.page = "Home"
        elif choice == "Sign Up":
            signup()
    # If logged in, redirect to Home page by default
    else:
        # Set default page to Home if not already set
        if "page" not in st.session_state  :
            st.session_state.page = "Home"


        # Sidebar for user options
        st.markdown("<h1 style='color:#ffffff;'>Air Quality Index Visualization of Indian Cities(2015-20)</h1>", unsafe_allow_html=True)
        st.sidebar.write(f"Welcome, {st.session_state.user}!")
        st.sidebar.button("Logout", on_click=logout)

        # Navigation buttons
        st.markdown("<div style='display: flex; justify-content: center; gap: 10px;'>", unsafe_allow_html=True)
        cols = st.columns(4)
        if cols[0].button("🏡 Home"):
            st.session_state.page = "Home"
        if cols[1].button("📊 Dashboard"):
            st.session_state.page = "Dashboard"
        if cols[2].button("💡 Insights"):
            st.session_state.page = "Insights"
        if cols[3].button("🗂 About"):
            st.session_state.page = "About"
        st.markdown("</div>", unsafe_allow_html=True)

        # Display the content based on the selected page
        if st.session_state.page == "Home":
            app_description()
        elif st.session_state.page == "Dashboard":
            dashboard()
        elif st.session_state.page == "Insights":
            data_download()
        elif st.session_state.page == "About":
            data_about()

if __name__ == "__main__":
    main()
