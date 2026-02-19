# 🧠 AI Agent: Context & Memory Management System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-agent-sejal-01.streamlit.app/)

An AI Agent System exploring **Long-term Memory** and **Context Awareness** for AI Agents in business environments. This system acts as an intelligent auditor, making invoice approval decisions based on historical supplier performance.

## 🚀 Features

-   **Memory Lifecycle Management**:  
    Differentiates between **CRITICAL (Fresh)** memories (2025-2026) and **STALE (Old)** memories (2024).
-   **Context Prioritization**:  
    The AI prioritizes recent critical issues over older, resolved problems when making decisions.
-   **Resilient AI Logic**:  
    Powered by Google Gemini (Flash 2.0/1.5) with automatic fallback handling for API outages or quota limits.
-   **Vector Search**:  
    Uses **ChromaDB** to retrieve semantically relevant past interactions.
-   **Explainable AI**:  
    The agent cites specific dates and events to justify its APPROVE/REJECT verdicts.

## 🛠️ Tech Stack

-   **Frontend**: Streamlit
-   **AI Model**: Google Gemini 2.0 Flash / 1.5 Flash
-   **Memory Store**: ChromaDB (Vector Database)
-   **Structured Data**: SQLite
-   **Language**: Python 3.9+

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sejalkutriyar/AI_Agent_Manager.git
    cd AI_Agent_Manager
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Secrets**:
    Create a file named `.streamlit/secrets.toml` in the project root and add your API Key:
    ```toml
    GEMINI_API_KEY = "your_google_ai_studio_api_key_here"
    ```

4.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

## ☁️ Deployment (Streamlit Cloud)

This app is ready for deployment on [Streamlit Community Cloud](https://streamlit.io/cloud).

1.  Push this code to GitHub.
2.  Connect your repository in Streamlit Cloud.
3.  **Crucial**: In the "Advanced Settings" of the deployment screen, paste your `GEMINI_API_KEY` into the **Secrets** section.

## 📂 Project Structure

-   `app.py`: Main application logic and UI.
-   `memory_engine.py`: Handles ChromaDB interactons and memory weighting.
-   `database.py`: Manages SQLite connection for structured invoice data.
-   `requirements.txt`: Python dependencies.

---

## 🩺 Troubleshooting

- **API key rejected / reported as leaked (403)**: If you see messages like "Your API key was reported as leaked", revoke the current key in Google Cloud / AI Studio and create a new key. Then update `.streamlit/secrets.toml` with the new `GEMINI_API_KEY` value.

- **Model not found (404)**: A 404 during generation often means the model name is not supported for your API version. Check model names, or remove models that are not available for your account.

- **Switching from `google.generativeai` to `google.genai`**: The older `google.generativeai` package is deprecated. To prepare for newer SDKs, update your environment and code when ready:

```bash
pip install --upgrade google-genai
# or add to requirements.txt: google-genai>=0.1.0
```

Refer to the Google GenAI SDK docs for migration details. If you are not ready to migrate immediately, the app includes improved error messaging to help identify API key and model issues.
