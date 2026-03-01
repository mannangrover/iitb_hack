# InsightX - Conversational AI for Digital Payment Analytics

A sophisticated natural language interface that democratizes access to complex payment transaction data, enabling business leaders to extract meaningful insights without writing SQL.

## 🎯 Project Overview

InsightX is a hackathon solution for analyzing 250,000+ digital payment transactions. The system interprets diverse business questions, performs real-time statistical analysis, and delivers clear, actionable insights with full explainability.

### Key Capabilities

- **Intent Recognition**: Understands diverse business questions (descriptive, comparative, segmentation, risk analysis)
- **Real-time Analysis**: Performs complex aggregations and statistical computations on large datasets
- **Explainable Results**: Provides clear reasoning with supporting statistics and trends
- **Context-Aware Responses**: Handles follow-up questions and ambiguous queries gracefully
- **Multi-dimensional Analysis**: Navigates transaction patterns, user behavior, and operational metrics

## 🏗️ Architecture

```
InsightX/
├── src/
│   ├── database/              # Database layer
│   │   ├── database.py        # SQLAlchemy configuration
│   │   ├── models.py          # ORM models
│   │   └── data_loader.py     # Data import utilities
│   ├── nlp/                   # Natural Language Processing
│   │   └── intent_recognizer.py  # Intent classification
│   ├── analysis/              # Data Analysis
│   │   └── query_builder.py   # Query execution engine
│   ├── api/                   # API Layer
│   │   ├── routes.py          # FastAPI routes
│   │   └── response_generator.py  # LLM-based response generation
│   └── __init__.py
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration
└── README.md                 # This file
```

## 🛠️ Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite with SQLAlchemy ORM (serverless, lightweight)
- **NLP**: Custom intent recognition with pattern matching
- **LLM Integration**: OpenAI API (optional, with fallback templates)
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Python**: 3.8+

## 📋 Prerequisites

- Python 3.8 or higher
- pip or conda package manager
- OpenAI API key (optional, for enhanced responses)
- ✅ **No database server installation needed!**

## 🚀 Installation & Setup

### 1. Clone and Navigate to Project

```bash
cd d:\Dhiraj\insightx_ai
```

### 2. Create Virtual Environment

```bash
# Using Python venv
python -m venv venv
venv\Scripts\activate

# Or using conda
conda create -n insightx python=3.10
conda activate insightx
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

You can optionally edit `.env` to set your OpenAI API key:

```
DATABASE_URL=sqlite:///./insightx_db.db

OPENAI_API_KEY=your_openai_api_key (optional)
FASTAPI_PORT=8000
FASTAPI_HOST=0.0.0.0
```

**Note**: SQLite database file (`insightx_db.db`) will be created automatically on first run.

### 5. Load Data

**Option A: Generate Synthetic Data**

```bash
python -m src.database.data_loader
```

This generates 250,000 realistic synthetic transactions with varied patterns.

**Option B: Load Your Own Dataset**

Prepare a CSV with these columns:
- user_id, amount, category, timestamp
- device_type, network_type, state, age_group
- status, fraud_flag, merchant_id, latitude, longitude

```bash
python -m src.database.data_loader your_data.csv
```

## 🎮 Running the Application

### Start the FastAPI Server (Backend)

```bash
python main.py
```

The API server will start at `http://localhost:8000`

### Start the Streamlit UI (Frontend)

In a **new terminal**:

```bash
streamlit run app.py
```

The UI will open at `http://localhost:8501`

### Quick Start (Both Services)

**Terminal 1 - Start API:**
```bash
python main.py
```

**Terminal 2 - Start UI:**
```bash
streamlit run app.py
```

Then open your browser to **http://localhost:8501**

## 🌐 User Interface Features

### Query Input
- Natural language question input with examples
- Real-time API health check
- Quick example query buttons

### Results Display
- **Confidence Score**: How confident the system is
- **Intent Type**: What kind of analysis was performed
- **Analysis Explanation**: Natural language explanation of results
- **Key Insights**: Bullet-point summary of findings
- **Detailed Data**: Expandable JSON view of raw analysis

### Query History
- View all previous queries
- Track intent types and timestamps
- Reference past analyses

### API Integration
- Configurable API endpoint (default: localhost:8000)
- Automatic health checks
- Error handling and user feedback

## 📊 Example Scenarios

**Scenario 1: Descriptive Analysis**
```
Query: "What's the average transaction amount for Food category?"
Result: Average amount, total transactions, success rate, sample data
```

**Scenario 2: Comparative Analysis**
```
Query: "Compare transaction amounts between iOS and Android"
Result: Side-by-side comparison, best performer, transaction counts
```

**Scenario 3: User Segmentation**
```
Query: "Show transaction patterns by state"
Result: Top segments, unique users per segment, transaction volumes
```

**Scenario 4: Risk Analysis**
```
Query: "What's the fraud rate for Shopping?"
Result: Fraud count, fraud rate %, failure rate, risk level recommendations
```

## 📝 API Usage

### 1. Query Endpoint (Main)

**POST** `/api/query`

Request:
```json
{
  "query": "What's the average transaction amount for Food category?"
}
```

Response:
```json
{
  "query": "What's the average transaction amount for Food category?",
  "intent": "descriptive",
  "explanation": "Based on the transaction data analysis...",
  "insights": [
    "Total transactions analyzed: 25000",
    "Average transaction amount: ₹1250.50",
    "Success rate: 98.50%"
  ],
  "confidence_score": 0.92,
  "raw_data": { ... }
}
```

### 2. Supported Entities

**GET** `/api/supported-entities`

Returns all supported categories, devices, networks, states, age groups, and intent types.

### 3. Example Queries

**GET** `/api/example-queries`

Returns example queries demonstrating different intent types.

### 4. Health Check

**GET** `/api/health`

## 🔍 Example Queries

### Descriptive Analysis
- "What's the average transaction amount for Food category?"
- "How many transactions happened in Maharashtra?"
- "Peak hours for Entertainment transactions?"

### Comparative Analysis
- "Compare transaction amounts between iOS and Android users"
- "WiFi vs 4G: which has higher transaction success rates?"
- "Entertainment vs Shopping: which category has more transactions?"

### User Segmentation
- "Show me transaction patterns by age group"
- "Which state has the most active users?"
- "Compare spending across different age demographics"

### Risk Analysis
- "What's the fraud rate for Shopping category?"
- "How many failed transactions occurred in the last week?"
- "Which categories have the highest fraud flags?"

## 📊 Data Analysis Capabilities

### Descriptive Metrics
- Total/Average/Median transaction amounts
- Transaction count by category
- Success rates and failure analysis
- Distribution statistics

### Comparative Insights
- Device type performance (iOS vs Android vs Web)
- Network quality impact (5G vs 4G vs WiFi)
- Category-wise comparisons
- Geographic comparisons

### User Segmentation
- Age-based spending patterns
- State-wise transaction volumes
- Device preference analysis
- Category popularity by segment

### Risk Metrics
- Fraud detection rates by category
- Failed transaction analysis
- High-risk transaction identification
- Anomaly detection insights

## 🔧 Configuration

### Customizing Intent Recognition

Edit `src/nlp/intent_recognizer.py`:

```python
# Add custom categories
self.categories = ["Food", "Entertainment", ...]

# Add custom keywords for intent classification
descriptive_keywords = ["average", "total", ...]
```

### Adjusting Analysis Parameters

Edit `src/analysis/query_builder.py` to customize:
- Statistical calculations
- Risk thresholds
- Aggregation methods

### LLM Integration

The system works with or without OpenAI:
- **With LLM**: Generates conversational, contextual responses
- **Without LLM**: Falls back to template-based responses

Set `OPENAI_API_KEY` in `.env` to enable LLM mode.

## 📈 Database Schema

### Transactions Table

```sql
CREATE TABLE transactions (
  transaction_id INT PRIMARY KEY,
  user_id INT NOT NULL,
  amount FLOAT NOT NULL,
  category VARCHAR(50) NOT NULL,
  timestamp DATETIME NOT NULL,
  device_type VARCHAR(20) NOT NULL,
  network_type VARCHAR(20) NOT NULL,
  state VARCHAR(50) NOT NULL,
  age_group VARCHAR(20) NOT NULL,
  status VARCHAR(20) NOT NULL,
  fraud_flag BOOLEAN DEFAULT FALSE,
  merchant_id INT NOT NULL,
  latitude FLOAT,
  longitude FLOAT,
  INDEX (user_id, category, state, timestamp, fraud_flag)
);
```

## 🚦 Troubleshooting

### Database File Not Created

```bash
# SQLite database file will be auto-created on first run
# Check that you have write permissions in project directory
```

### No Transactions Found

```bash
# Load data: python -m src.database.data_loader
# Check database: python -c "from src.database.models import *; from src.database.database import SessionLocal; print(SessionLocal().query(Transaction).count())"
```

### Port Already in Use

```bash
# Change port in .env or use:
python -c "import main; import uvicorn; uvicorn.run('main:app', port=8001)"
```

### Import Errors

```bash
# Reinstall dependencies:
pip install -r requirements.txt
```

## 🎓 Project Highlights

✅ **Complete NLP Pipeline**: Intent recognition with entity extraction  
✅ **Scalable Architecture**: Handles 250K+ transactions efficiently  
✅ **Multiple Analysis Types**: Descriptive, comparative, segmentation, risk  
✅ **Explainable AI**: Clear reasoning with statistical backing  
✅ **Easy Integration**: RESTful API with comprehensive documentation  
✅ **Production Ready**: Error handling, logging, database optimization  

## 📝 License

This project is part of the InsightX hackathon by Techfest, IIT Bombay.

## 👥 Support

For questions or issues:
1. Check the example queries and API documentation
2. Review the troubleshooting section
3. Examine log output for error messages
4. Verify database connectivity and data presence

---

**Happy Analyzing! 📊**
