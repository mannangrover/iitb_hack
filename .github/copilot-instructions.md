# InsightX Conversational AI - Project Setup & Development Guide

## Project Overview

InsightX is a hackathon solution that provides a conversational AI interface for querying digital payment transaction data. It allows business leaders to extract meaningful insights from 250,000+ transactions using natural language queries without writing SQL.

## Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Database**: SQLite with SQLAlchemy ORM (serverless, lightweight)
- **NLP**: Custom intent recognition with pattern matching
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **Python Version**: 3.8+

## Project Structure

## Project Structure

```
src/
├── database/          # Database configuration and models
│   ├── database.py   # SQLAlchemy setup and connection
│   ├── models.py     # ORM models (Transaction)
│   └── data_loader.py # Data import utilities
├── nlp/              # Natural Language Processing
│   └── intent_recognizer.py  # Intent classification engine
├── analysis/         # Analytics and Query Execution
│   └── query_builder.py # Query builder for different intents
└── api/              # FastAPI layer
    ├── routes.py     # API endpoints
    └── response_generator.py # LLM-based response generation

main.py              # FastAPI application entry point
app.py               # Streamlit UI application
requirements.txt     # Python dependencies
.env.example        # Environment configuration template
```

## Key Features

### Intent Recognition
- Recognizes 4 main intent types:
  - **Descriptive**: Average amounts, totals, distributions
  - **Comparative**: Device types, networks, categories
  - **User Segmentation**: Age groups, states, demographics
  - **Risk Analysis**: Fraud rates, failure analysis

### Entity Extraction
- Automatically extracts: categories, device types, networks, states, age groups
- Supports time reference extraction (peak hours, daily/monthly analysis)

### Analysis Capabilities
- Real-time statistical computations
- Multi-dimensional aggregations
- Risk flagging and anomaly detection
- Comparative metrics and trends

### Response Generation
- Template-based responses (always available)
- LLM-enhanced responses (with OpenAI API key)
- Confidence scoring
- Insight extraction and formatting

## Setup Instructions

### 1. Environment Configuration
Edit `.env` with optional OpenAI API key:
```
DATABASE_URL=sqlite:///./insightx_db.db
OPENAI_API_KEY=sk-...  # Optional
```

### 2. Load Transaction Data
```bash
# Generate 250K synthetic transactions:
python -m src.database.data_loader

# Or load your own CSV:
python -m src.database.data_loader your_data.csv
```

### 3. Start API Server
```bash
python main.py
# Server runs at http://localhost:8000
```

## Development Notes

### Adding Custom Intent Types
Edit `src/nlp/intent_recognizer.py`:
1. Add keywords to `_classify_intent()`
2. Add entity extraction patterns to `_extract_entities()`
3. Create corresponding query method in `src/analysis/query_builder.py`

### Adding New Entities
Update the entity lists in `IntentRecognizer`:
- `self.categories` - transaction categories
- `self.states` - geographic regions
- `self.devices` - device types
- `self.networks` - network types
- `self.age_groups` - age segments

### Database Schema Extension
New fields can be added to the `Transaction` model in `src/database/models.py`, then:
1. Update data_loader.py to handle new fields
2. Update intent_recognizer.py to recognize new entities
3. Update query_builder.py to use new fields in analysis

## API Endpoints

### Main Query Endpoint
**POST** `/api/query`
```json
{
  "query": "What's the average transaction amount for Food?"
}
```

### Utility Endpoints
- **GET** `/api/health` - Health check
- **GET** `/api/supported-entities` - Available filters
- **GET** `/api/example-queries` - Query examples

## Testing

### Manual Testing
1. Access Swagger UI: http://localhost:8000/docs
2. Try example queries from `/api/example-queries`
3. Test different intent types and entity combinations

### Example Query Patterns
- Descriptive: "average transaction amount", "total spending"
- Comparative: "iOS vs Android", "WiFi vs 4G"
- Segmentation: "by age group", "by state"
- Risk: "fraud rate", "failed transactions"

## Performance Notes

- Database uses indexes on frequently queried columns: user_id, category, state, timestamp, fraud_flag
- Batch insertion (5000 records/batch) for efficient data loading
- Query results cached for identical queries (can be implemented in routes.py)

## Deployment Considerations

For production deployment:
1. Update FASTAPI_HOST to specific IP/domain
2. Use connection pooling (already configured in SQLAlchemy)
3. Add authentication/authorization middleware
4. Implement request rate limiting
5. Add comprehensive logging
6. Use environment-specific configuration files
7. Consider database replication/backups

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Database file not created | Run server once, SQLite creates file automatically |
| No data | Run `python -m src.database.data_loader` to load transactions |
| Port already in use | Change FASTAPI_PORT in .env or use different port |
| LLM responses not working | Ensure OPENAI_API_KEY set in .env (system falls back to templates) |

## Future Enhancements

- [ ] Implement temporal analysis (hourly/daily/weekly patterns)
- [ ] Add follow-up question support with conversation context
- [ ] Enhance LLM integration with prompt engineering
- [ ] Add visualization endpoints (charts, graphs)
- [ ] Implement query caching for performance
- [ ] Add user authentication and query history
- [ ] Support for custom date ranges in queries
- [ ] Real-time fraud detection dashboard
- [ ] Export analysis results (CSV, PDF)

## Documentation References

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- MySQL Connector Python: https://dev.mysql.com/doc/connector-python/en/
- Pydantic: https://docs.pydantic.dev/
