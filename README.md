# Self-Learning Travel Agent ✈️

A multimodal, self-learning AI Travel Assistant engineered for high reliability, deterministic execution, and seamless deployment. 

## Project Overview

This application acts as a personalized travel planner that "learns" about the user over time. By combining the official OpenAI Python SDK with a custom SQLite memory layer, the agent tracks persistent preferences across chat sessions (e.g., dietary restrictions, seating preferences, budget constraints). It utilizes an **Observe-Think-Act** loop to reason about user input, decide when to query its local knowledge tools, and save new preferences organically.

## Architecture Justification: Why Pure Python Over LangChain?

While abstraction frameworks like LangChain or LangGraph are popular for rapid prototyping, this agent is built using a **deterministic, pure Python routing loop** integrated directly with the official OpenAI API. 

This architectural decision was made to prioritize:
1. **System Observability & Debugging:** Abstraction frameworks often obscure the prompt payload and tool-calling loop, creating "black boxes" that are incredibly difficult to debug in production environments. By managing the state list and `chat.completions.create()` calls manually, every token sent to the LLM is visible, trackable, and loggable via Python's standard `logging` module.
2. **Data Integrity:** The agent interacts directly with a SQLite database wrapped in robust `try...except` blocks, transaction handling, and threading safeguards (`check_same_thread=False`). Abstracted memory classes (like `ConversationBufferMemory`) often lack the granular control required for concurrent multi-user environments or graceful degradation during database lock events.
3. **Engineering Maturity:** Standard engineering principles—explicit data structures, modular tool definitions, bounded iteration limits (to prevent infinite LLM loops), and standard execution logging—provide a more maintainable, performant, and corporate-ready codebase than reliance on heavily abstracted, fast-changing third-party libraries.

## System Features

- **Observe-Think-Act Loop:** Deterministic routing capable of continuous multi-step reasoning.
- **Robust Error Handling:** Safely handles LLM hallucinations (malformed JSON arguments) and SQLite concurrency locking.
- **Execution Logging:** Integrated Python `logging` captures state changes and execution traces (outputs to console and `agent.log`).
- **Streamlit Web UI:** A beautiful, responsive chat interface.

## Local Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your Groq API key (or OpenAI API key):
   ```
   GROQ_API_KEY=your_key_here
   ```
4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Deployment (Streamlit Community Cloud)

To deploy this live so recruiters and peers can test the UI without cloning the repository:

1. **Commit to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Production-ready Self-Learning Agent"
   git branch -M main
   # Replace with your repository URL:
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
2. **Connect to Streamlit:**
   - Go to [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
   - Click **"New app"** -> **"Deploy a public app from GitHub"**.
   - Select your repository and ensure the Main file path is set to `app.py`.
   - Click **"Advanced settings"** and add your `GROQ_API_KEY` under the Secrets section.
   - Click **Deploy!**
