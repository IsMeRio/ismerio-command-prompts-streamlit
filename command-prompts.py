# main.py
import streamlit as st
import requests

st.set_page_config(page_title="Command Prompt GUI", layout="wide")

# Styling
st.markdown("""
    <style>
    .terminal {
        background-color: black;
        color: #00FF00;
        font-family: monospace;
        padding: 10px;
        border-radius: 10px;
        height: 400px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    .directory-info {
        background-color: #222;
        color: #00FF00;
        font-family: monospace;
        padding: 5px 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🖥️ Command Prompt GUI")

# Session State
if "connected" not in st.session_state:
    st.session_state.connected = False
if "terminal_history" not in st.session_state:
    st.session_state.terminal_history = ""
if "current_directory" not in st.session_state:
    st.session_state.current_directory = "Unknown"

# Inputs
ip_address = st.text_input("Enter Server IP (e.g., http://abc123.ngrok.io)")

# Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Connect"):
        if ip_address:
            try:
                response = requests.post(f"{ip_address}/connect", json={"command": "connect"})
                data = response.json()
                st.session_state.connected = True
                st.session_state.current_directory = data.get("current_directory", "Unknown")
                st.session_state.terminal_history += "Connected to server.\n"
                st.success("Connected!")
            except Exception as e:
                st.error(f"Connection error: {e}")
        else:
            st.warning("Please enter the server IP.")

with col2:
    if st.button("Disconnect"):
        if ip_address:
            try:
                response = requests.post(f"{ip_address}/connect", json={"command": "disconnect"})
                st.session_state.connected = False
                st.success("Disconnected!")
                st.session_state.terminal_history += "Disconnected from server.\n"
            except Exception as e:
                st.error(f"Disconnection error: {e}")
        else:
            st.warning("Please enter the server IP.")

# Show Current Directory from Server
st.markdown(f'<div class="directory-info">Current Directory: {st.session_state.current_directory}</div>', unsafe_allow_html=True)

# Terminal output
st.markdown(f'<div class="terminal">{st.session_state.terminal_history}</div>', unsafe_allow_html=True)

# Command Input
if st.session_state.connected:
    command = st.text_input("Enter your command")

    if st.button("Execute Command"):
        if command:
            try:
                cmd = command.strip()

                response = requests.post(f"{ip_address}/command", json={"command": cmd})
                data = response.json()

                output = data.get("output", "No output")
                new_dir = data.get("current_directory", st.session_state.current_directory)

                # Update server directory
                st.session_state.current_directory = new_dir

                # Update terminal history
                st.session_state.terminal_history += f"> {command}\n{output}\n"
                st.rerun()

            except Exception as e:
                st.session_state.terminal_history += f"Error executing command: {e}\n"
                st.rerun()
else:
    st.warning("Please connect to a server first.")

# Footer
st.markdown("---")
st.caption("Version 0.6 (Alpha) | Report bugs to ismerio on Discord")
