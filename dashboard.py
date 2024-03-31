import streamlit as st
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json

# Function to display login page
def login(session_state):
    st.markdown(
        """
        <style>
        .login-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 2rem;
            border: 1px solid #ccc;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: #f9f9f9;
            width: 300px;
            text-align: center;
        }
        .login-container img {
            width: 80px;
            margin-bottom: 1rem;
        }
        </style>
        """
        , unsafe_allow_html=True
    )
    st.markdown("<h1>Login</h1>", unsafe_allow_html=True)
    st.image("vece_logo.webp", width=100)  # Replace with your image path
    login_id = st.text_input("Enter Login ID", key="login_id")
    password = st.text_input("Enter Password", type="password", key="password")

    # Press Enter to submit the form
    if st.button("Login") or (password and session_state.login_id and password):
        if session_state.login_id == "mihir" and password == "1234":
            st.success("Logged in successfully!")
            session_state.logged_in = True
        else:
            st.error("Invalid credentials. Please try again.")

# Function to logout
def logout(session_state):
    session_state.logged_in = False
    session_state.login_id = None
    session_state.password = None
    st.success("Logged out successfully!")

# Main function
def main():
    # Initialize session state
    session_state = st.session_state
    if not hasattr(session_state, "logged_in"):
        session_state.logged_in = False
        session_state.login_id = None
        session_state.password = None

    # Check if logged in
    if not session_state.logged_in:
        login(session_state)
        return

    # Get the greeting message
    current_time = datetime.datetime.now()
    hour = current_time.hour
    if 6 <= hour < 12:
        greeting = "Good Morning"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # Streamlit web interface
    st.title("Real-Time Sensor Data Visualization Dashboard")

    # Add user icon and greeting message to the sidebar
    st.sidebar.image("vece_logo.webp", width=100)  # Replace with your image path
    st.sidebar.write(f"## {greeting}, {session_state.login_id}!")

    # Create placeholder for the time display
    time_placeholder = st.sidebar.empty()

    # Read sensor data from the server
    try:
        response = requests.get('http://localhost:5000/receive_data', timeout=1)
        data = json.loads(response.text)
        temperature = data['temperature']
        humidity = data['humidity']
        relay_1 = data['relay_status']
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch sensor data: {e}")
        return

    # Display temperature, humidity, and relay status
    st.sidebar.write(f"**Temperature:** {temperature:.1f} °C")
    st.sidebar.write(f"**Humidity:** {humidity:.1f} %")
    st.sidebar.write(f"**Relay 1 status:** {relay_1}")

    # Add logout button
    if st.sidebar.button("Logout"):
        logout(session_state)

    # Create two columns for the line charts
    col1, col2 = st.columns(2)

    # Create the initial line chart for sensor data with initial data in the first column
    chart_temp = col1.line_chart(pd.DataFrame(columns=["Temperature"]))

    # Create the initial line chart for sensor data with initial data in the second column
    chart_humidity = col2.line_chart(pd.DataFrame(columns=["Humidity"]))

    # Add spacing between graph 2 and graph 3
    st.write("\n\n\n")

    # Create the initial pie chart
    fig_pie, ax_pie = plt.subplots()
    pie_chart = st.pyplot(fig_pie)

    # Create the initial specific line chart using an empty DataFrame
    columns = ["Timestamp", "Temperature", "Humidity"]
    chart_data = pd.DataFrame(columns=columns)
    chart_specific = st.empty()

    # Maximum number of data points to display at a time
    max_points = 100

    # Flag to track if an error has occurred
    error_occurred = False

    while True:

        try:

            response = requests.get('http://localhost:5000/receive_data', timeout=1)
            data = json.loads(response.text)

            # Read sensor data from the server
            temperature = data['temperature']
            humidity = data['humidity']
            relay_1 = data['relay_status']

            # Get current timestamp
            current_time = datetime.datetime.now()

            # Update the time display
            time_placeholder.markdown(f"**Date:** {current_time.strftime('%Y-%m-%d')}   **Time:** {current_time.strftime('%H:%M:%S')}")

            # Update the sensor data line charts with historical data
            chart_temp.add_rows(pd.DataFrame([temperature], columns=["Temperature"], index=[current_time]))
            chart_humidity.add_rows(pd.DataFrame([humidity], columns=["Humidity"], index=[current_time]))

            # Update the pie chart
            ax_pie.clear()
            ax_pie.pie([temperature, humidity], labels=['Temperature', 'Humidity'], autopct='%1.1f%%', startangle=90)
            ax_pie.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            pie_chart.pyplot(fig_pie)

            # Update the specific line chart with sensor data
            new_data = pd.DataFrame([[current_time, temperature, humidity]], columns=columns)
            chart_data = pd.concat([chart_data, new_data], ignore_index=True)

            # Limit the number of data points
            if len(chart_data) > max_points:
                chart_data = chart_data.iloc[1:]

            chart_specific.line_chart(chart_data.set_index("Timestamp"))

            # Reset the error flag
            error_occurred = False

            # Sleep for a short duration before reading again
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            if not error_occurred:
                st.error(f"Error reading sensor data: {e}")
                st.warning(f'Error {e}', icon="⚠️")
                error_occurred = True
            # Wait for a short duration before trying again
            time.sleep(1)
            continue  # Continue with the next iteration of the loop

if __name__ == "__main__":
    main()