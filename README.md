# Deep Property Search

An AI-powered property analysis API that provides comprehensive insights and recommendations for real estate properties using Google's Gemini AI.

## Features

- Property analysis with multiple AI personas
- Quick property summaries
- Detailed inspection checklists
- Location-based insights
- Investment potential analysis
- Chat-based interaction with AI personas

## Project Structure

```
deep_prop_search/
├── backend/
│   ├── api/
│   │   ├── models.py      # Pydantic models for API
│   │   └── routes.py      # API endpoints
│   ├── agents/
│   │   └── property.py    # Property analysis agent
│   ├── services/
│   │   └── scraper.py     # Property data scraper
│   └── utils/
│       └── locations.py   # Location utilities
├── tests/
│   └── test_property_agent.py
├── prompts/
│   ├── analysis_prompt.txt
│   ├── quick_summary_prompt.txt
│   ├── inspection_checklist.txt
│   └── analysis_template.json
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/deep_prop_search.git
cd deep_prop_search
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Usage

### Running the API

```bash
uvicorn backend.api.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `POST /chat/start`: Start a new chat session for property analysis
- `POST /chat/message`: Send a message in an existing chat session
- `GET /chat/session/{session_id}`: Get the current state of a chat session
- `GET /chat/sessions`: List all active chat sessions

### Running Tests

```bash
pytest tests/
```

## AI Personas

The system includes multiple AI personas for property analysis:

1. **Optimistic Ollie**
   - Focuses on growth opportunities and potential
   - Emphasizes positive aspects and future value

2. **Cautious Cat**
   - Specializes in risk assessment
   - Highlights potential issues and concerns

3. **Negative Nancy**
   - Provides critical analysis
   - Focuses on potential drawbacks and challenges

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 