import pymongo
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)

load_dotenv()

class MongoDBClient:
    def __init__(self, mongo_uri, db_name, collection_name):
        # 1. Correctly initializes a single client and collection using the arguments
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        
        # This part ensures that the database connection is actually working
        try:
            self.client.admin.command('ping')
            logger.info("MongoDB connection established successfully.")
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
            # 2. Saves the document to the correct collection
            result = self.collection.insert_one(document)
            logger.info(f"Plan saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save plan: {e}")
            raise
    
    def get_all_plans(self):
        # 3. Retrieves documents from the same collection
        plans = self.collection.find().sort("timestamp", pymongo.DESCENDING)
        return [{**plan, '_id': str(plan['_id'])} for plan in plans]
    
    def delete_plan(self, plan_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(plan_id)})
            logger.info(f"Deleted {result.deleted_count} plan(s) with ID: {plan_id}")
        except Exception as e:
            logger.error(f"Failed to delete plan: {e}")
            raise