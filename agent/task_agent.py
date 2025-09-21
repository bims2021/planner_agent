from langchain.agents import Tool, AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from utils.tools import WebSearchTool, WeatherTool
import json
import os
import re
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class TaskPlanningAgent:
    def __init__(self):
        logger.info("Initializing TaskPlanningAgent")
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize the tools
        self.web_search_tool = WebSearchTool()
        self.weather_tool = WeatherTool()
        
        # Define the two fixed tools
        self.tools = [
            Tool(
                name="WebSearch",
                func=self.web_search_tool.search,
                description="Useful for searching the web for information about places, restaurants, attractions, events, etc."
            ),
            Tool(
                name="Weather",
                func=self.weather_tool_func,
                description="Useful for getting weather information for a specific location. Input should be a location name."
            )
        ]
        
        # Initialize the agent with the two fixed tools
        logger.info("Initializing LangChain agent with tools")
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
        
        logger.info("TaskPlanningAgent initialized successfully")
    
    def weather_tool_func(self, location_input):
        """Wrapper function for weather tool with location extraction"""
        logger.info(f"Weather information requested: {location_input}")
        
        # Extract location from input
        location = self._extract_location(location_input)
        if not location:
            logger.warning("Could not extract location from input")
            return "Please provide a valid location name."
        
        return str(self.weather_tool.get_weather(location))
    
    def _extract_location(self, text):
        """Simple location extraction from text"""
        # Remove common prefixes
        text = re.sub(r'(weather|forecast|temperature|in|for|at)\s+', '', text.lower())
        return text.strip()
    
    def generate_plan(self, goal):
        """Generate a plan using the agent with the two fixed tools"""
        logger.info(f"Starting plan generation for goal: {goal}")
        
        prompt = f"""
        You are a helpful planning assistant. Please help me create a detailed plan for the following goal:
        
        Goal: {goal}
        
        Use your available tools to gather necessary information and create a structured, day-by-day plan.
        The plan should be practical, detailed, and include specific recommendations where possible.
        
        After gathering information, output your final plan in JSON format with days as keys and activities as values.
        """
        
        try:
            logger.info("Executing agent with tools")
            result = self.agent.run(prompt)
            logger.info("Agent execution completed")
            
            # Try to extract JSON from the result
            try:
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    plan = json.loads(json_match.group())
                    logger.info("Successfully parsed JSON plan from agent response")
                    return plan
                else:
                    logger.warning("No JSON found in agent response, returning raw text")
                    # If no JSON found, return the text as is
                    return {"plan": result}
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed: {e}")
                return {"plan": result, "error": "JSON parsing failed"}
                
        except Exception as e:
            logger.exception(f"Plan generation failed: {e}")
            return {"error": f"Failed to generate plan: {str(e)}"}
        