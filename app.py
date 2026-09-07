import streamlit as st
import agent

# Configure page settings
st.set_page_config(
    page_title="Self-Learning AI Travel Concierge", 
    page_icon="🌍", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inject Premium Custom CSS
st.markdown("""
<style>
    /* General app background */
    .stApp {
        background-color: #0b0f19;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Gradient and Animation */
    .premium-header {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.2em;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
        animation: fadeInDown 1s cubic-bezier(0.1, 0.8, 0.1, 1);
    }
    
    .premium-subheader {
        text-align: center;
        color: #8a96a8;
        font-size: 1.1em;
        margin-bottom: 40px;
        font-weight: 400;
        animation: fadeIn 1.5s ease-in-out;
    }
    
    /* Hide Streamlit default branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: transparent !important;}
    
    /* Animations */
    @keyframes fadeInDown {
        0% { opacity: 0; transform: translateY(-30px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    
    /* Input box styling */
    .stChatInputContainer {
        border-radius: 20px !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

# Render Headers
st.markdown('<div class="premium-header">🌍 AI Travel Concierge</div>', unsafe_allow_html=True)
st.markdown('<div class="premium-subheader">I remember your preferences across sessions. Tell me your dream destination, budget, or dietary needs!</div>', unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Optional greeting
    st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your personalized travel concierge. Where would you like to go next? Let me know if you have any specific preferences like 'I only fly Delta' or 'I am vegetarian'!"})

# Display chat messages from history
for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("E.g., I'm planning a trip to Japan next month..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Call agent and display response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing preferences and formulating a plan..."):
            try:
                # Run the deterministic Observe-Think-Act loop
                response_content = agent.run_agent_loop(st.session_state.messages)
                st.markdown(response_content)
                # Save assistant response
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            except Exception as e:
                st.error(f"System Error: {str(e)}\n\nPlease ensure your GROQ_API_KEY is set in the `.env` file.")
