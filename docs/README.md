# AI Task Planning Agent

An AI-powered agent that helps with task planning by breaking down goals into actionable steps, enriching them with external information, and creating structured plans.

task-planning-agent/
├── app.py
├── requirements.txt
├── agent/
│   ├── __init__.py
│   └── task_agent.py
├── utils/
│   ├── __init__.py
│   ├── database.py
│   └── tools.py
├── logging_config.py
├── .env.example
└── README.md

## How It Works

1. **Goal Input**: User provides a natural language goal
2. **Goal Breakdown**: LLM breaks down the goal into actionable steps
3. **Information Enrichment**: 
   - Web search for research-related steps
   - Weather API for weather-related information
4. **Plan Structuring**: LLM organizes enriched steps into a day-by-day plan
5. **Storage**: Plan is saved to MongoDB for future reference
6. **Display**: User can view the plan and browse past plans

### Architecture Diagram

User Input → Streamlit UI → Task Planning Agent → LLM + Tools → Database → Results Display


## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd task-planning-agent

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
### Set up environment variables
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017/
SERPAPI_KEY=your_serpapi_key (optional)
OPENWEATHER_API_KEY=your_openweather_api_key (optional)

### Set up MongoDB

Install MongoDB locally or use MongoDB Atlas

Update the MONGODB_URI in your .env file if needed

### Run the application

streamlit run app.py

Example Goals and Generated Plans
Example 1: "Plan a 2-day vegetarian food tour in Hyderabad"

Generated Plan:
json

{
  "Day 1": [
    "Breakfast at Cafe Bahar (famous for vegetarian biryani)",
    "Visit Charminar and explore surrounding food stalls",
    "Lunch at Chutneys (popular for South Indian vegetarian dishes)",
    "Evening snacks at Niloufer Cafe (famous for tea and snacks)",
    "Dinner at Udipi Hotel (authentic vegetarian thali)"
  ],
  "Day 2": [
    "Breakfast at Minerva Coffee Shop",
    "Visit Golkonda Fort",
    "Lunch at Nanking (Chinese vegetarian options)",
    "Evening at Hussain Sagar Lake",
    "Dinner at Paradise Food Court (vegetarian options available)"
  ]
}

Example 2: "Create a weekend plan in Vizag with beach, hiking, and seafood"

Generated Plan:
json

{
  "Saturday": [
    "Morning: Visit RK Beach for sunrise and stroll",
    "Breakfast at local eatery for authentic Andhra meals",
    "Hike at Kailasagiri Hill for panoramic views",
    "Lunch at Sea Inn for fresh seafood",
    "Evening: Visit Tenneti Park and enjoy beach activities",
    "Dinner at Dharani for traditional Andhra seafood dishes"
  ],
  "Sunday": [
    "Morning: Visit Yarada Beach for relaxation",
    "Breakfast at hotel or local cafe",
    "Visit INS Kurusura Submarine Museum",
    "Lunch at Fisherman's Cove for beachside dining",
    "Evening: Shop at local markets for souvenirs",
    "Dinner at Absolute Barbecues for variety of seafood options"
  ]
}

### AI Assistance Disclosure

This project uses AI in several ways:

OpenAI's GPT models for goal breakdown and plan structuring.

AI-generated code comments and documentation assistance.

AI-assisted debugging and optimization suggestions.