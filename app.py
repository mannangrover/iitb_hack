import streamlit as st
import requests
import json
import os
from datetime import datetime
import pandas as pd
import altair as alt

# Page configuration
st.set_page_config(
    page_title="InsightX - Payment Analytics AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with fixed header
st.markdown("""
<style>
    /* Hide the top streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container styling */
    .main {
        padding-top: 0;
    }
    
    /* Fixed header - truly fixed to top of page */
    .header-container {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 12px 20px;
        z-index: 9999 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
        width: 100%;
        box-sizing: border-box;
        height: 50px;
    }
    
    /* Push main content down to account for fixed header */
    [data-testid="stAppViewContainer"],
    [data-testid="stMainBlockContainer"],
    .main {
        margin-top: 60px !important;
        padding-top: 0 !important;
        padding-bottom: 70px !important;
    }

    /* Ensure chat input is fully visible */
    [data-testid="stChatInput"] {
        margin-bottom: 10px !important;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 15px;
        flex: 1;
    }
    
    .header-title {
        color: white;
        font-size: 1.4em;
        font-weight: bold;
        margin: 0;
        white-space: nowrap;
    }
    
    .header-tagline {
        color: #e0e0ff;
        font-size: 0.85em;
        margin: 0;
        white-space: nowrap;
    }
    
    .header-status {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    
    .status-badge {
        color: white;
        font-size: 0.85em;
        padding: 4px 10px;
        border-radius: 4px;
        background: rgba(255,255,255,0.2);
        white-space: nowrap;
    }
    
    .status-active {
        background: rgba(76, 175, 80, 0.7) !important;
    }
    
    .status-connected {
        background: rgba(76, 175, 80, 0.7) !important;
    }
    
    .status-error {
        background: rgba(244, 67, 54, 0.6) !important;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    
    .query-input {
        border: 2px solid #667eea;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Load API URL from environment or Streamlit secrets, fall back to localhost
def get_api_url():
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        return st.secrets.get("api_url", "http://localhost:8000")
    except:
        # Fall back to environment variable
        return os.getenv("API_URL", "http://localhost:8000")

if "api_url" not in st.session_state:
    st.session_state.api_url = get_api_url()
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "api_session_status" not in st.session_state:
    st.session_state.api_session_status = "No session"
if "last_chart" not in st.session_state:
    st.session_state.last_chart = None

# Sidebar
with st.sidebar:
    st.title("💬 InsightX Chat")
    
    # Conversation Management
    st.subheader("🎯 Conversation")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶ Start New", use_container_width=True, help="Begin a new conversation"):
            try:
                response = requests.post(
                    f"{st.session_state.api_url}/api/conversation/start",
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.conversation_history = []
                    st.session_state.query_history = []
                    st.success(f"✓ Started: {data['session_id'][:12]}...")
                    st.rerun()
            except Exception as e:
                st.error(f"Failed: {e}")
    
    with col2:
        if st.button("❌ End", use_container_width=True, help="End current conversation"):
            if st.session_state.session_id:
                try:
                    requests.delete(
                        f"{st.session_state.api_url}/api/conversation/{st.session_state.session_id}",
                        timeout=5
                    )
                except:
                    pass
                st.session_state.session_id = None
                st.session_state.conversation_history = []
                st.session_state.query_history = []
                st.info("Conversation ended")
                st.rerun()
    
    # Session status
    if st.session_state.session_id:
        st.info(f"📌 Session: {st.session_state.session_id[:20]}...")
    else:
        st.warning("No active session")
    
    st.divider()
    
    st.subheader("💡 Ask Better Questions")
    st.markdown("""
    - **Start with outcomes:** total value, growth, risk, or efficiency
    - **Add a lens:** bank, category, state, age group, device, network, or time
    - **Follow-up works:** "How about X?" or "By state?"

    **Common scopes:**
    banks, categories, age groups, states, devices, networks
    
    **Example Flow:**
    1. "Total transaction value by state"
    2. "How about only Food?"
    3. "Show top 3 states"
    """)
    
    st.divider()
    
    st.subheader("📚 Example Questions")
    example_queries = [
        "Top banks by total transaction value",
        "Total transaction value by state",
        "Average transaction amount by state",
        "Compare iOS vs Android by total amount",
        "Fraud rate by state",
        "Where is failure rate highest by bank?",
        "Top 3 fraud categories in Delhi",
        "Transactions from Karnataka by receiver bank",
        "Average Food amount per state",
        "Peak hours for Food transactions",
        "Day of week pattern for Entertainment",
        "Transaction count by device type",
        "Compare UPI networks by average amount",
        "Age group trends in Maharashtra",
        "Sender vs receiver age group for failed transactions",
        "Weekend vs weekday transaction volume"
    ]
    
    for i, query in enumerate(example_queries, 1):
        if st.button(f"📌 {query}", key=f"example_{i}", use_container_width=True):
            st.session_state.pending_query = query
            st.rerun()
    
    st.divider()
    
    st.subheader("⚙️ Settings")
    
    api_url = st.text_input(
        "API Endpoint",
        value=st.session_state.api_url,
        help="Enter the FastAPI server URL"
    )
    st.session_state.api_url = api_url
    
    show_raw = st.checkbox("Show raw data", value=False)
    # Chart options
    top_n = st.slider("Top N for charts", min_value=3, max_value=20, value=10)

# Fixed Header - Render immediately after CSS
# Check API status
api_status = "not connected"
try:
    response = requests.get(f"{st.session_state.api_url}/api/health", timeout=1)
    api_status = "connected" if response.status_code == 200 else "error"
except:
    api_status = "error"

# Build header status
session_status = "🔑 Active" if st.session_state.session_id else "📋 New"
api_indicator = "✅ Connected" if api_status == "connected" else "❌ Error"

# Render fixed header using HTML - appears at top of main content
st.markdown(f"""
<div class="header-container">
    <div class="header-left">
        <div>
            <p class="header-title">💳 InsightX</p>
            <p class="header-tagline">Payment Analytics AI</p>
        </div>
    </div>
    <div class="header-status">
        <span class="status-badge status-active">{session_status}</span>
        <span class="status-badge status-connected">{api_indicator}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Function to render chart from raw_data
def render_chart(chart_data, top_n=10):
    """Render bar chart based on raw_data from API response"""
    if not chart_data:
        return
    
    try:
        if 'data' in chart_data and isinstance(chart_data['data'], list):
            rows = chart_data['data']
            df = pd.DataFrame(rows)
            metric = chart_data.get('metric') or ''
            
            # Check for total/amount FIRST (before defaulting to average)
            if metric in ('amount','total_amount','total') or (metric == '' and 'total_amount' in df.columns):
                df = df.sort_values('total_amount', ascending=False).head(top_n)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('category:N', sort='-y', title='Category'),
                    y=alt.Y('total_amount:Q', title='Total Amount')
                ).properties(width=700)
                st.subheader('📊 Comparison')
                st.altair_chart(chart, use_container_width=True)
            elif metric == 'count' or ('transaction_count' in df.columns and metric == 'count'):
                df = df.sort_values('transaction_count', ascending=False).head(top_n)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('category:N', sort='-y', title='Category'),
                    y=alt.Y('transaction_count:Q', title='Transaction Count')
                ).properties(width=700)
                st.subheader('📊 Comparison (count)')
                st.altair_chart(chart, use_container_width=True)
            elif (metric and metric.startswith('avg')) or ('average_amount' in df.columns and metric == ''):
                df = df.sort_values('average_amount', ascending=False).head(top_n)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('category:N', sort='-y', title='Category'),
                    y=alt.Y('average_amount:Q', title='Average Amount')
                ).properties(width=700)
                st.subheader('📊 Comparison (avg)')
                st.altair_chart(chart, use_container_width=True)
            elif 'transaction_count' in df.columns:
                df = df.sort_values('transaction_count', ascending=False).head(top_n)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('category:N', sort='-y', title='Category'),
                    y=alt.Y('transaction_count:Q', title='Transaction Count')
                ).properties(width=700)
                st.subheader('📊 Comparison (count)')
                st.altair_chart(chart, use_container_width=True)
        elif 'segments' in chart_data and isinstance(chart_data['segments'], list):
            rows = chart_data['segments']
            df = pd.DataFrame(rows)
            if 'transaction_count' in df.columns:
                df = df.sort_values('transaction_count', ascending=False).head(top_n)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('segment:N', sort='-y', title='Segment'),
                    y=alt.Y('transaction_count:Q', title='Transaction Count')
                ).properties(width=700)
                st.subheader('📊 Segmentation')
                st.altair_chart(chart, use_container_width=True)
            elif 'average_transaction_value' in df.columns:
                df = df.sort_values('average_transaction_value', ascending=False).head(top_n)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('segment:N', sort='-y', title='Segment'),
                    y=alt.Y('average_transaction_value:Q', title='Average Transaction Value')
                ).properties(width=700)
                st.subheader('📊 Segmentation (avg)')
                st.altair_chart(chart, use_container_width=True)
        elif 'groups' in chart_data and isinstance(chart_data['groups'], list):
            rows = chart_data['groups']
            df = pd.DataFrame(rows)
            if 'fraud_rate' in df.columns:
                df = df.sort_values('fraud_rate', ascending=False)
                measure = 'fraud_rate'
                ytitle = 'Fraud Rate (%)'
            elif 'total' in df.columns:
                df = df.sort_values('total', ascending=False)
                measure = 'total'
                ytitle = 'Total Count'
            else:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                if len(numeric_cols) > 0:
                    measure = numeric_cols[0]
                    ytitle = measure.replace('_', ' ').title()
                else:
                    measure = None
            if measure:
                df = df.head(top_n)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('group:N', sort='-y', title='Group'),
                    y=alt.Y(f'{measure}:Q', title=ytitle)
                ).properties(width=700)
                st.subheader('📊 Groups')
                st.altair_chart(chart, use_container_width=True)
        elif 'temporal' in chart_data and isinstance(chart_data['temporal'], dict):
            temporal = chart_data['temporal']
            hourly = temporal.get('hourly') or []
            if hourly:
                df = pd.DataFrame(hourly)
                if 'hour' in df.columns and 'transaction_count' in df.columns:
                    df = df.sort_values('hour')
                    chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X('hour:O', title='Hour of Day'),
                        y=alt.Y('transaction_count:Q', title='Transaction Count')
                    ).properties(width=700)
                    st.subheader('📊 Hourly Distribution')
                    st.altair_chart(chart, use_container_width=True)

            daily = temporal.get('day_of_week') or []
            if daily:
                df = pd.DataFrame(daily)
                if 'day_of_week' in df.columns and 'transaction_count' in df.columns:
                    df = df.sort_values('day_of_week')
                    chart = alt.Chart(df).mark_bar().encode(
                        x=alt.X('day_of_week:O', title='Day of Week (0=Mon)'),
                        y=alt.Y('transaction_count:Q', title='Transaction Count')
                    ).properties(width=700)
                    st.subheader('📊 Day-of-Week Distribution')
                    st.altair_chart(chart, use_container_width=True)
    except Exception:
        pass

# Display conversation history (chat-like format)
if st.session_state.conversation_history:
    st.subheader("💬 Conversation")
    
    for msg in st.session_state.conversation_history:
        if msg["type"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
                if msg.get("intent"):
                    st.caption(f"Intent: **{msg['intent']}** | Confidence: **{msg['confidence']:.0%}**")
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
                if msg.get("insights"):
                    summary = " | ".join(msg.get("insights", [])[:3])
                    if summary:
                        st.caption(f"Insight: {summary}")
                # Render chart for this response
                if msg.get("raw_data"):
                    render_chart(msg["raw_data"], st.session_state.get('top_n', 10))

st.divider()

# Main query section is now at bottom using chat_input for ChatGPT-style layout

# Process query when user submits via chat_input or clicks an example
user_query = st.chat_input("Ask a question about the transaction data...")

# If example question was clicked, use pending_query instead
if st.session_state.pending_query:
    user_query = st.session_state.pending_query
    st.session_state.pending_query = None  # Clear pending query

if user_query:
    with st.spinner("🔍 Analyzing with LLM context..."):
        try:
            api_response = requests.post(
                f"{st.session_state.api_url}/api/query",
                json={"query": user_query, "context": {"session_id": st.session_state.session_id}},
                timeout=30
            )

            if api_response.status_code == 200:
                result = api_response.json()

                # Persist session id for follow-ups
                returned_session = result.get("session_id")
                if returned_session:
                    st.session_state.session_id = returned_session

                # Store in conversation history
                st.session_state.conversation_history.append({
                    "type": "user",
                    "content": user_query,
                    "intent": result.get("intent"),
                    "confidence": result.get("confidence_score", 0)
                })

                st.session_state.conversation_history.append({
                    "type": "assistant",
                    "content": result.get("explanation", ""),
                    "insights": result.get("insights", []),
                    "raw_data": result.get("raw_data", {})
                })
                # No longer needed - chart is rendered in conversation loop
                st.session_state.last_chart = None

                # Add to legacy history
                st.session_state.query_history.append({
                    "query": user_query,
                    "intent": result.get("intent"),
                    "timestamp": datetime.now()
                })

                st.success("✓ Analysis Complete!")
                st.rerun()

            else:
                st.error(f"API Error: {api_response.status_code}")
                st.error(api_response.text)

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
            st.info("Run `python main.py` in another terminal to start the server")
        except requests.exceptions.Timeout:
            st.error("❌ Request timeout. The server is taking too long to respond.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔧 FastAPI + Streamlit")
with col2:
    st.caption(f"📅 {datetime.now().strftime('%b %d, %Y')}")
with col3:
    if st.session_state.session_id:
        st.caption(f"✅ Session Active")
    else:
        st.caption(f"⏸️ Start a conversation to begin")
