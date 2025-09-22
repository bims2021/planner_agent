import requests
import os
from dotenv import load_dotenv
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

load_dotenv()

class WebSearchTool:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        self.base_url = "https://serpapi.com/search"
        
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")
        
        logger.info("WebSearchTool initialized")
    
    def search(self, query, num_results=3):
        logger.info(f"Web search: {query}")
        
        if self.api_key:
            return self._search_serpapi(query, num_results)
        elif self.google_api_key and self.google_cse_id:
            return self._search_google(query, num_results)
        else:
            logger.warning("No web search API keys configured, using demo data")
            return self._get_demo_search_results(query)
    
    def _search_serpapi(self, query, num_results):
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
            "num": num_results
        }
        
        try:
            logger.debug(f"SerpAPI request: {params}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()  # This will raise an HTTPError if the response status is 4xx or 5xx
            results = response.json()  # Parse JSON response
            
            # Extract organic results
            organic_results = results.get("organic_results", [])[:num_results]  # Limit to num_results
            simplified_results = []
            
            for result in organic_results:
                simplified_results.append({
                    "title": result.get("title"),
                    "snippet": result.get("snippet"),
                    "link": result.get("link")
                })
            
            logger.info(f"SerpAPI search returned {len(simplified_results)} results")
            return simplified_results
        except requests.exceptions.RequestException as e:
            logger.error(f"SerpAPI search failed due to a request error: {e}")
            return {"error": f"Error performing web search: {str(e)}"}
        except ValueError as e:
            logger.error(f"SerpAPI search failed due to JSON decoding error: {e}")
            return {"error": f"Error decoding API response: {str(e)}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred during SerpAPI search: {e}")
            return {"error": f"An unexpected error occurred: {str(e)}"}
    
    def _search_google(self, query, num_results):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": self.google_api_key,
            "cx": self.google_cse_id,
            "num": min(num_results, 10)
        }
        
        try:
            logger.debug(f"Google Custom Search request: {params}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            results = response.json()
            
            simplified_results = []
            for item in results.get("items", [])[:num_results]:
                simplified_results.append({
                    "title": item.get("title"),
                    "snippet": item.get("snippet"),
                    "link": item.get("link")
                })
            
            logger.info(f"Google Custom Search returned {len(simplified_results)} results")
            return simplified_results
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Custom Search failed due to a request error: {e}")
            return {"error": f"Error performing Google search: {str(e)}"}
        except ValueError as e:
            logger.error(f"Google Custom Search failed due to JSON decoding error: {e}")
            return {"error": f"Error decoding API response: {str(e)}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred during Google Custom Search: {e}")
            return {"error": f"An unexpected error occurred: {str(e)}"}
    
    def _get_demo_search_results(self, query):
        """Return demo data for presentation when no APIs are configured"""
        return [
            {
                "title": f"Search result for {query}",
                "snippet": "This is demonstration data shown because no web search API keys were configured. In a real deployment, this would be actual search results.",
                "link": "https://example.com/demo"
            },
            {
                "title": f"Another result for {query}",
                "snippet": "The system can use SerpAPI or Google Custom Search API when properly configured with API keys.",
                "link": "https://example.com/demo"
            }
        ]

class WeatherTool:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        logger.info("WeatherTool initialized")
    
    def get_weather(self, location):
        logger.info(f"Weather lookup: {location}")
        
        if not self.api_key:
            logger.warning("OpenWeather API key not configured, using demo data")
            return self._get_demo_weather_data(location)
        
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            logger.debug(f"OpenWeather API request: {params}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("cod") != 200:
                logger.error(f"OpenWeather API error: {data.get('message', 'Unknown error')}")
                return {"error": f"Error fetching weather: {data.get('message', 'Unknown error')}"}
            
            weather_info = {
                "location": data.get("name"),
                "temperature": data.get("main", {}).get("temp"),
                "description": data.get("weather", [{}])[0].get("description"),
                "humidity": data.get("main", {}).get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed")
            }
            
            logger.info(f"Weather lookup successful for {location}")
            return weather_info
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather lookup failed due to a request error: {e}")
            return {"error": f"Error fetching weather: {str(e)}"}
        except ValueError as e:
            logger.error(f"Weather lookup failed due to JSON decoding error: {e}")
            return {"error": f"Error decoding API response: {str(e)}"}
        except Exception as e:
            logger.error(f"An unexpected error occurred during weather lookup: {e}")
            return {"error": f"An unexpected error occurred: {str(e)}"}
    
    def _get_demo_weather_data(self, location):
        """Return demo weather data for presentation"""
        return {
            "location": location,
            "temperature": 22,
            "description": "Partly cloudy",
            "humidity": 65,
            "wind_speed": 3.5,
            "source": "demo_data"
        }