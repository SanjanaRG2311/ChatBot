# frontend.py - Government Schemes Chatbot Frontend (Updated)
import streamlit as st
import requests
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Government Schemes Assistant",
    page_icon="🇮🇳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# API Configuration
API_BASE_URL = "http://localhost:8001"

# Clean CSS
st.markdown("""
<style>
    /* Hide all unnecessary elements */
    .stApp > header { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .stDeployButton { display: none; }
    
    /* Remove any sidebars completely */
    section[data-testid="stSidebar"] { display: none !important; }
    
    /* Main container */
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Chat messages */
    .user-message {
        background: #f0f8ff;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #9c27b0;
        white-space: pre-line;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: #667eea;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": ("Welcome to Government Schemes Assistant! 🇮🇳\n\n"
                          "I can help you find information about various government schemes across Southern Indian states.\n\n"
                          "Try asking:\n"
                          "• 'Health schemes in Tamil Nadu'\n"
                          "• 'Education scholarships in Kerala'\n"
                          "• 'Women welfare schemes in Karnataka'\n\n"
                          "What would you like to know?"),
                "timestamp": datetime.now().isoformat()
            }
        ]
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"session_{int(time.time())}"
    
    if "processing" not in st.session_state:
        st.session_state.processing = False
    
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message_to_backend(message: str):
    """Send message to backend API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "query": message,
                "session_id": st.session_state.session_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return {"error": "connection_failed"}
    except Exception as e:
        return {"error": str(e)}

def display_chat_messages():
    """Display all chat messages"""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f'<div class="user-message"><strong>You:</strong><br>{content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message"><strong>Assistant:</strong><br>{content}</div>', unsafe_allow_html=True)

def handle_user_input(user_input: str):
    """Handle user input and get response from backend"""
    if st.session_state.processing or not user_input.strip():
        return
    
    # Check backend connection first
    if not check_backend_connection():
        st.session_state.messages.append({
            "role": "assistant",
            "content": "🔴 **Backend Server Not Running**\n\nPlease start the backend server first:\n```bash\npython backend.py\n```\nThen refresh this page.",
            "timestamp": datetime.now().isoformat()
        })
        st.session_state.input_key += 1
        st.rerun()
        return
    
    st.session_state.processing = True
    
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get response from backend
    with st.spinner("Searching schemes..."):
        response_data = send_message_to_backend(user_input)
        
        if response_data and "error" not in response_data:
            assistant_response = response_data["response"]
        elif response_data and response_data.get("error") == "connection_failed":
            assistant_response = "🔴 **Connection Lost**\n\nThe backend server has stopped running. Please:\n1. Start the backend: `python backend.py`\n2. Refresh this page"
        else:
            assistant_response = "Sorry, I encountered an error while processing your request. Please try again."
        
        # Add assistant response to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": datetime.now().isoformat()
        })
    
    st.session_state.processing = False
    st.session_state.input_key += 1
    st.rerun()

def main():
    """Main application function"""
    # Hide sidebar completely
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🇮🇳 Government Schemes Assistant</h1>
        <p>Find schemes, scholarships, and welfare programs</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display connection status
    if not check_backend_connection():
        st.error("🔴 **Backend Server Not Running**\n\nPlease start the backend server first:\n```bash\npython backend.py\n```\nThen refresh this page.")
        
        # Show restart instructions
        with st.expander("Troubleshooting Steps"):
            st.markdown("""
            1. **Open a new terminal/command prompt**
            2. **Navigate to your project folder**
            3. **Run the backend server:**
               ```bash
               python backend.py
               ```
            4. **Wait for the server to start** (you should see: `Uvicorn running on http://0.0.0.0:8001`)
            5. **Refresh this page**
            
            If you're still having issues, check:
            - The backend file is named `backend.py`
            - Python is installed correctly
            - Port 8001 is not being used by another application
            """)
        
        st.stop()
    
    # Display chat messages
    display_chat_messages()
    
    # Quick action buttons
    st.markdown("### Quick Options:")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏥 Health", use_container_width=True, key="health_btn"):
            handle_user_input("Health schemes")
    
    with col2:
        if st.button("🎓 Education", use_container_width=True, key="edu_btn"):
            handle_user_input("Education schemes")
    
    with col3:
        if st.button("👩 Women", use_container_width=True, key="women_btn"):
            handle_user_input("Women welfare schemes")
    
    with col4:
        if st.button("🌾 Agriculture", use_container_width=True, key="agri_btn"):
            handle_user_input("Agriculture schemes")
    
    # Input area
    st.markdown("---")
    
    # Use form to prevent multiple submissions
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Ask about schemes:",
                placeholder="e.g., 'Health schemes in Tamil Nadu'",
                label_visibility="collapsed",
                key=f"user_input_{st.session_state.input_key}"
            )
        
        with col2:
            submitted = st.form_submit_button("Send", use_container_width=True)
    
    # Handle form submission
    if submitted and user_input and user_input.strip():
        handle_user_input(user_input.strip())
    
    # Show backend status
    st.markdown("---")
    if check_backend_connection():
        st.success("✅ Backend server is running")
    else:
        st.error("🔴 Backend server is not running")

if __name__ == "__main__":
    main()