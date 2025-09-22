import streamlit as st
import json
from datetime import datetime
from agent.task_agent import TaskPlanningAgent
from utils.database import MongoDBClient
import logging
from logging_config import setup_logging, logger
import os
from dotenv import load_dotenv

load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


# Initialize session state
if 'plans' not in st.session_state:
    st.session_state.plans = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'db_client' not in st.session_state:
    st.session_state.db_client = None

logger.info("Initializing Streamlit application")

# Set up page
st.set_page_config(page_title="AI Task Planning Agent", page_icon="🤖", layout="wide")
st.title("🤖 AI Task Planning Agent")

# Initialize agent and database
@st.cache_resource
def init_agent():
    logger.info("Initializing TaskPlanningAgent")
    return TaskPlanningAgent()

@st.cache_resource
def init_database():
    logger.info("Initializing MongoDB client")
    mongo_uri = os.environ.get("MONGO_DB_URI")
    db_name = os.environ.get("MONGO_DB_NAME")
    collection_name = os.environ.get("MONGO_DB_COLLECTION")
    
    if not all([mongo_uri, db_name, collection_name]):
        logger.error("Database environment variables are not set.")
        st.error("Missing database configuration. Please check your .env file.")
        return None
    
    return MongoDBClient(mongo_uri, db_name, collection_name)

if st.session_state.agent is None:
    st.session_state.agent = init_agent()
if st.session_state.db_client is None:
    st.session_state.db_client = init_database()

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Create New Plan", "View Past Plans"])

# Display tool status
st.sidebar.info("**Tools Status:**\n- Web Search: Available\n- Weather API: Available")

if page == "Create New Plan":
    st.header("Create a New Plan")
    
    # Goal input
    goal = st.text_area(
        "Enter your goal:",
        placeholder="e.g., Plan a 3-day trip to Jaipur with cultural highlights and good food",
        height=100
    )
    
    if st.button("Generate Plan", type="primary"):
        if goal:
            with st.spinner("Generating your plan using web search and weather data..."):
                if st.session_state.db_client is not None:
                    # Generate plan using agent
                    plan = st.session_state.agent.generate_plan(goal)
                    
                    if "error" in plan:
                        st.error(plan["error"])
                    else:
                        # Save to database
                        plan_id = st.session_state.db_client.save_plan(goal, plan)
                        
                        # Add to session state
                        st.session_state.plans.insert(0, {
                            "id": plan_id,
                            "goal": goal,
                            "plan": plan,
                            "timestamp": datetime.now()
                        })
                        
                        st.success("Plan generated successfully!")
                        
                        # Display the plan
                        st.subheader("Your Plan")
                        if "plan" in plan and isinstance(plan["plan"], str):
                            # Handle case where plan is a string instead of structured data
                            st.write(plan["plan"])
                        else:
                            # Structured plan
                            plan_data = plan if "plan" not in plan else plan["plan"]
                            for day, activities in plan_data.items():
                                st.markdown(f"### {day}")
                                if isinstance(activities, list):
                                    for i, activity in enumerate(activities, 1):
                                        st.markdown(f"{i}. {activity}")
                                elif isinstance(activities, dict):
                                    for time, activity in activities.items():
                                        st.markdown(f"- **{time}**: {activity}")
                                elif isinstance(activities, str):
                                    st.markdown(activities)
                                st.markdown("---")
                else:
                    st.error("Cannot generate plan: Database client not available.")
        else:
            st.warning("Please enter a goal first.")

else:  # View Past Plans
    st.header("Past Plans")
    
    if st.session_state.db_client is not None:
        # Fetch plans from database
        plans = st.session_state.db_client.get_all_plans()
        
        if not plans:
            st.info("No plans found. Create your first plan!")
        else:
            # Search and filter
            search_query = st.text_input("Search plans", placeholder="Enter keywords to search...")
            
            filtered_plans = plans
            if search_query:
                filtered_plans = [
                    p for p in plans 
                    if search_query.lower() in p['goal'].lower() or 
                    any(search_query.lower() in str(v).lower() for v in p['plan'].values() if isinstance(v, (str, list)))
                ]
            
            st.write(f"Found {len(filtered_plans)} plan(s)")
            
            # Display plans in reverse chronological order
            for plan in filtered_plans:
                with st.expander(f"{plan['goal']} - {plan['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                    st.markdown(f"**Goal:** {plan['goal']}")
                    st.markdown("**Plan:**")
                    
                    plan_data = plan['plan']
                    if isinstance(plan_data, dict):
                        for day, activities in plan_data.items():
                            st.markdown(f"### {day}")
                            if isinstance(activities, list):
                                for i, activity in enumerate(activities, 1):
                                    st.markdown(f"{i}. {activity}")
                            elif isinstance(activities, dict):
                                for time, activity in activities.items():
                                    st.markdown(f"- **{time}**: {activity}")
                            elif isinstance(activities, str):
                                st.markdown(activities)
                            st.markdown("---")
                    else:
                        st.markdown(str(plan_data))
                    
                    if st.button("Delete", key=plan['_id']):
                        st.session_state.db_client.delete_plan(plan['_id'])
                        st.rerun()
    else:
        st.error("Cannot display plans: Database client not available.")