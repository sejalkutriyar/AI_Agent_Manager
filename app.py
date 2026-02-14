import streamlit as st
import google.generativeai as genai

# Fix for ChromaDB on Streamlit Cloud (SQLite version issue)
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from memory_engine import MemoryManager
from database import init_db
import sqlite3

# SETUP & CONNECTION
init_db()
# GEMINI_API_KEY = "AIzaSyBJuQLzSQMLk5zXFrK3SA_fzsoeGQURXUQ"
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except FileNotFoundError:
    st.error("Secrets file not found. Please create .streamlit/secrets.toml")
    st.stop()
except KeyError:
    st.error("GEMINI_API_KEY not found in secrets.toml")
    st.stop()

# Robust Model Selection Logic
def get_working_model():
    # List of models to try in order of preference (lighter/cheaper first)
    candidate_models = [
        "gemini-2.0-flash-lite", 
        "gemini-2.0-flash", 
        "gemini-flash-latest",
        "gemini-1.5-flash",
        "gemini-pro"
    ]
    
    for model_name in candidate_models:
        try:
            model = genai.GenerativeModel(model_name)
            # Test connection with a dummy prompt
            # Note: We won't actually call generate_content here to save quota, 
            # but we initialize the object.
            return model, model_name
        except Exception:
            continue
            
    return None, "None"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model, active_model_name = get_working_model()
except Exception as e:
    model = None
    active_model_name = f"Error: {e}"

# Page Config
st.set_page_config(page_title="AI Agent Memory System", layout="wide")

# UI DESIGN
st.title("🧠 AI Agent: Context & Memory Manager")
st.markdown(f"Business Environment Decision Support System | **Active Model:** {active_model_name}")

# Sidebar for Input
with st.sidebar:
    st.header("New Transaction")
    supplier = st.selectbox("Select Supplier", ["Supplier XYZ", "TechCorp Inc", "Global Logistics"])
    amount = st.number_input("Invoice Amount (₹)", min_value=1000, value=250000)
    process_btn = st.button("Process with AI Memory")

# Main Display Area
col1, col2 = st.columns([1, 1])

if process_btn:
    mm = MemoryManager()
    
    # RETRIEVE MEMORIES
    with col1:
        st.subheader("📜 Retrieved Memories")
        memories = mm.get_weighted_memory(supplier)
        
        if not memories:
            st.info("No historical issues found for this entity.")
        else:
            for m in memories:
                color = "red" if "CRITICAL" in m['status'] else "orange" if "RELEVANT" in m['status'] else "gray"
                st.markdown(f":{color}[**{m['status']}**] ({m['date']})")
                st.write(f"Issue: {m['issue']}")
                st.divider()

    # AI DECISION
    with col2:
        st.subheader("🤖 AI Auditor Verdict")
        
        if model is None:
            st.error("AI Error: Could not connect to Gemini. Please check your internet or API key.")
        else:
            with st.spinner("AI is analyzing history..."):
                memory_summary = "\n".join([f"- {m['date']}: [{m['status']}] {m['issue']}" for m in memories])
                
                prompt = f"""
                You are a Business Auditor. Analyze this transaction based on historical context.
                
                Transaction Details:
                Supplier: {supplier} 
                Amount: ₹{amount}
                
                Historical Memories (Sorted by Importance):
                {memory_summary if memory_summary else "No past issues recorded."}
                
                Decision Rules:
                1. **Prioritize Recent History**: If recent history (2025-2026) contradicts older history (2024), trust the recent history more.
                2. **Critical Issues**: If there are CRITICAL issues in the last 6 months, lean towards HOLD or REJECT.
                3. **Redemption**: If 2024 was bad but 2025/2026 is good, consider it a redeemed supplier and lean towards APPROVE.
                
                Task: 
                1.  **Line 1**: Verdict (Exact format: "VERDICT: APPROVE", "VERDICT: REJECT", or "VERDICT: HOLD")
                2.  **Line 2**: Confidence Score (Exact format: "CONFIDENCE: X%")
                3.  **Line 3**: Key Driver Event (Exact format: "KEY_DRIVER: YYYY-MM-DD: Event Description")
                4.  **Line 4+**: Detailed Reasoning.
                """
                
                # Feature 2: Semantic Memory Summarization (Information Overload Prevention)
                if len(memories) > 5:
                    with st.spinner("⚠️ Memory Overload detected. Generating Executive Summary..."):
                        summary_prompt = f"Summarize these {len(memories)} supplier events into a concise 3-sentence executive brief focused on risks and reliability: {memory_summary}"
                        try:
                            # Use a lighter model for summarization
                            summary_model = genai.GenerativeModel("gemini-2.0-flash-lite")
                            summary_response = summary_model.generate_content(summary_prompt)
                            if summary_response.text:
                                # Replace raw list with summary in the main prompt
                                prompt = prompt.replace(f"{memory_summary if memory_summary else 'No past issues recorded.'}", 
                                                        f"Historical Executive Summary: {summary_response.text}")
                                st.info(f"ℹ️ **Context Summary**: {summary_response.text}")
                        except Exception:
                            pass # Fallback to raw data
                
                # Fallback logic for generation
                response_text = None
                
                # List of models to try if the primary one fails
                fallback_chain = [
                   active_model_name, # Try current one first
                   "gemini-2.0-flash-lite",
                   "gemini-flash-latest", 
                   "gemini-pro"
                ]
                
                # Remove duplicates while preserving order
                seen = set()
                models_to_try = [x for x in fallback_chain if not (x in seen or seen.add(x))]

                for m_name in models_to_try:
                    try:
                        # Update status
                        st.caption(f"Attempting analysis with {m_name}...")
                        current_model = genai.GenerativeModel(m_name)
                        response = current_model.generate_content(prompt)
                        
                        if response.text:
                            response_text = response.text
                            active_model_name = m_name # Update active model to show success
                            break # Success!
                            
                    except Exception as e:
                        print(f"Model {m_name} failed: {e}")
                        continue
                
                if response_text:
                    st.success(f"Decision Generated using {active_model_name}!")
                    full_response = response_text
                    
                    # Parsing Logic
                    lines = full_response.split('\n')
                    verdict_line = lines[0].upper()
                    confidence_line = "CONFIDENCE: 0%"
                    key_driver_line = "KEY_DRIVER: N/A"
                    
                    # Extract structured data
                    for line in lines[:5]: 
                        if "CONFIDENCE:" in line.upper():
                            confidence_line = line
                        if "KEY_DRIVER:" in line.upper():
                            key_driver_line = line

                    # Display Verdict Badge
                    if "APPROVE" in verdict_line:
                        st.balloons()
                        st.success(verdict_line)
                    elif "REJECT" in verdict_line:
                        st.error(verdict_line)
                    elif "HOLD" in verdict_line:
                        st.warning(verdict_line)
                    else:
                        st.warning(verdict_line if "VERDICT" in verdict_line else "VERDICT: HOLD / INSPECT")

                    # Feature 1: Confidence & Transparency Metrics
                    m_col1, m_col2 = st.columns(2)
                    
                    # Parse Confidence Int
                    try:
                        conf_val = int(''.join(filter(str.isdigit, confidence_line)))
                    except:
                        conf_val = 50
                        
                    with m_col1:
                        st.metric("AI Confidence", f"{conf_val}%")
                        st.progress(conf_val / 100)
                    
                    with m_col2:
                         st.info(f"🎯 **{key_driver_line}**")

                    st.markdown("### 📝 AI Reasoning")
                    st.write("\n".join(lines[3:])) # Print reasoning
                    
                    # Feature 3: Interactive Feedback Loop
                    st.divider()
                    st.subheader("📢 Process Feedback")
                    
                    feedback_col1, feedback_col2 = st.columns([3, 1])
                    with feedback_col1:
                        feedback_text = st.text_input("Disagree? Add correction:", placeholder="E.g., 'Override: Weather delay, not supplier fault.'")
                    with feedback_col2:
                        st.write("") 
                        st.write("") 
                        if st.button("💾 Save Feedback"):
                            if feedback_text:
                                mm = MemoryManager()
                                from datetime import datetime
                                today_str = datetime.now().strftime("%Y-%m-%d")
                                mm.add_event(supplier, f"HUMAN_OVERRIDE: {feedback_text}", today_str)
                                st.success("Feedback saved! Agent will remember this.")
                            else:
                                st.error("Enter feedback text.")
                else:
                    st.error("All AI models failed. Please try again later (Quota Exceeded).")
                        


else:
    st.info("👈 Enter transaction details in the sidebar to start analysis.")

st.divider()
st.caption("Sejal's AI_Agent_Memory")