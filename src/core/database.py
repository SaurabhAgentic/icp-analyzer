from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
from bson import ObjectId
import json

class Database:
    def __init__(self):
        """Initialize MongoDB connection."""
        self.client = MongoClient(
            host=os.getenv('MONGODB_HOST', 'localhost'),
            port=int(os.getenv('MONGODB_PORT', 27017)),
            username=os.getenv('MONGODB_USER', ''),
            password=os.getenv('MONGODB_PASSWORD', '')
        )
        
        # Get database
        self.db: Database = self.client[os.getenv('MONGODB_DB', 'icp_analyzer')]
        
        # Get collections
        self.analyses: Collection = self.db.analyses
        self.reports: Collection = self.db.reports
        self.webhooks: Collection = self.db.webhooks
        self.exports: Collection = self.db.exports
        
        # Create indexes
        self._create_indexes()
    
    def _create_indexes(self):
        """Create necessary indexes for collections."""
        # Analyses collection indexes
        self.analyses.create_index([('user_id', 1)])
        self.analyses.create_index([('created_at', 1)], expireAfterSeconds=30*24*60*60)  # 30 days TTL
        
        # Reports collection indexes
        self.reports.create_index([('user_id', 1)])
        self.reports.create_index([('created_at', 1)], expireAfterSeconds=7*24*60*60)  # 7 days TTL
        
        # Webhooks collection indexes
        self.webhooks.create_index([('user_id', 1)], unique=True)
        
        # Exports collection indexes
        self.exports.create_index([('user_id', 1)])
        self.exports.create_index([('created_at', 1)], expireAfterSeconds=24*60*60)  # 24 hours TTL
    
    def save_analysis(self, user_id: str, analysis_data: Dict[str, Any]) -> str:
        """Save analysis results to database."""
        document = {
            'user_id': user_id,
            'analysis_data': analysis_data,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.analyses.insert_one(document)
        return str(result.inserted_id)
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve analysis results from database."""
        try:
            document = self.analyses.find_one({'_id': ObjectId(analysis_id)})
            if document:
                document['_id'] = str(document['_id'])
                return document
            return None
        except Exception:
            return None
    
    def save_report(self, user_id: str, report_data: Dict[str, Any]) -> str:
        """Save report to database."""
        document = {
            'user_id': user_id,
            'report_data': report_data,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.reports.insert_one(document)
        return str(result.inserted_id)
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve report from database."""
        try:
            document = self.reports.find_one({'_id': ObjectId(report_id)})
            if document:
                document['_id'] = str(document['_id'])
                return document
            return None
        except Exception:
            return None
    
    def save_webhook(self, user_id: str, webhook_url: str) -> bool:
        """Save webhook configuration."""
        try:
            self.webhooks.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'webhook_url': webhook_url,
                        'updated_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            return True
        except Exception:
            return False
    
    def get_webhook(self, user_id: str) -> Optional[str]:
        """Retrieve webhook URL for user."""
        try:
            document = self.webhooks.find_one({'user_id': user_id})
            return document['webhook_url'] if document else None
        except Exception:
            return None
    
    def save_export(self, user_id: str, export_data: Dict[str, Any]) -> str:
        """Save export data to database."""
        document = {
            'user_id': user_id,
            'export_data': export_data,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = self.exports.insert_one(document)
        return str(result.inserted_id)
    
    def get_export(self, export_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve export data from database."""
        try:
            document = self.exports.find_one({'_id': ObjectId(export_id)})
            if document:
                document['_id'] = str(document['_id'])
                return document
            return None
        except Exception:
            return None
    
    def get_user_analyses(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent analyses for a user."""
        try:
            cursor = self.analyses.find(
                {'user_id': user_id}
            ).sort('created_at', -1).limit(limit)
            
            return [{
                '_id': str(doc['_id']),
                'analysis_data': doc['analysis_data'],
                'created_at': doc['created_at']
            } for doc in cursor]
        except Exception:
            return []
    
    def cleanup_old_data(self) -> Dict[str, int]:
        """Clean up old data from collections."""
        try:
            # Delete old analyses (older than 30 days)
            analyses_deleted = self.analyses.delete_many({
                'created_at': {'$lt': datetime.utcnow() - timedelta(days=30)}
            }).deleted_count
            
            # Delete old reports (older than 7 days)
            reports_deleted = self.reports.delete_many({
                'created_at': {'$lt': datetime.utcnow() - timedelta(days=7)}
            }).deleted_count
            
            # Delete old exports (older than 24 hours)
            exports_deleted = self.exports.delete_many({
                'created_at': {'$lt': datetime.utcnow() - timedelta(hours=24)}
            }).deleted_count
            
            return {
                'analyses_deleted': analyses_deleted,
                'reports_deleted': reports_deleted,
                'exports_deleted': exports_deleted
            }
        except Exception:
            return {
                'analyses_deleted': 0,
                'reports_deleted': 0,
                'exports_deleted': 0
            }

# Initialize global database instance
db = Database() 