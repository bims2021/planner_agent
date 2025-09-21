from pymongo import MongoClient 
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

load_dotenv()

class MongoDBClient:
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        logger.info(f"Connecting to MongoDB: {self.connection_string}")
        
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client["task_planner_db"]
            self.plans_collection = self.db["plans"]
            self.workflows_collection = self.db["workflows"]
            logger.info("MongoDB connection established successfully")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    def save_plan(self, goal: str, plan: Dict, workflow_history: List[Dict] = None) -> str:
        logger.info(f"Saving plan to database: {goal[:50]}...")
        document = {
            "goal": goal,
            "plan": plan,
            "workflow_history": workflow_history or [],
            "timestamp": datetime.now(),
            "status": "completed"
        }
        try:
            result = self.plans_collection.insert_one(document)
            logger.info(f"Plan saved with ID: {result.inserted_id}")
            
            # Also save to workflows collection for tracking
            workflow_doc = {
                "plan_id": result.inserted_id,
                "goal": goal,
                "history": workflow_history or [],
                "timestamp": datetime.now()
            }
            self.workflows_collection.insert_one(workflow_doc)
            
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
            raise
    
    def save_workflow_state(self, plan_id: str, state: str, metadata: Dict = None):
        """Save workflow state for monitoring"""
        document = {
            "plan_id": plan_id,
            "state": state,
            "metadata": metadata or {},
            "timestamp": datetime.now()
        }
        self.workflows_collection.insert_one(document)
    
    def get_workflow_history(self, plan_id: str) -> List[Dict]:
        """Get workflow history for a specific plan"""
        from bson import ObjectId
        try:
            workflow = self.workflows_collection.find_one({"plan_id": ObjectId(plan_id)})
            return workflow.get("history", []) if workflow else []
        except Exception as e:
            logger.error(f"Failed to get workflow history: {e}")
            return []
    def get_all_plans(self):
        return list(self.collection.find())
    