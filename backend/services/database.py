from clickhouse_driver import Client
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
from config.settings import settings
import json

class DatabaseService:
    def __init__(self):
        self.client = None
        
    async def initialize(self):
        """Initialize ClickHouse connection"""
        try:
            self.client = Client(
                host=settings.clickhouse_host,
                port=settings.clickhouse_port,
                user=settings.clickhouse_user,
                password=settings.clickhouse_password,
                database=settings.clickhouse_database
            )
            # Test connection
            result = self.client.execute("SELECT 1")
            print(f"Connected to ClickHouse: {settings.clickhouse_database}")
        except Exception as e:
            print(f"Failed to connect to ClickHouse: {e}")
            raise
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.disconnect()
    
    # Document operations
    async def create_document(self, data: Dict, document_id: str = None) -> str:
        """Create a new document entry"""
        if not document_id:
            document_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO documents (
            document_id, document_name, original_filename, file_path,
            file_size, file_type, user_id, organization, survey_type,
            row_count, column_count, metadata
        ) VALUES
        """
        
        try:
            self.client.execute(
                query + " (%(document_id)s, %(document_name)s, %(original_filename)s, %(file_path)s, "
                "%(file_size)s, %(file_type)s, %(user_id)s, %(organization)s, %(survey_type)s, "
                "%(row_count)s, %(column_count)s, %(metadata)s)",
                {
                    'document_id': document_id,
                    'document_name': data.get('document_name'),
                    'original_filename': data.get('original_filename'),
                    'file_path': data.get('file_path'),
                    'file_size': data.get('file_size', 0),
                    'file_type': data.get('file_type'),
                    'user_id': data.get('user_id', 'system'),
                    'organization': data.get('organization', ''),
                    'survey_type': data.get('survey_type', ''),
                    'row_count': data.get('row_count', 0),
                    'column_count': data.get('column_count', 0),
                    'metadata': json.dumps(data.get('metadata', {}))
                }
            )
        except Exception as e:
            print(f"Database error creating document: {str(e)}")
            raise e
        
        return document_id
    
    async def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document by ID"""
        query = "SELECT * FROM documents WHERE document_id = %(document_id)s"
        result = self.client.execute(query, {'document_id': document_id})
        
        if result:
            row = result[0]
            return {
                'document_id': str(row[0]),
                'document_name': row[1],
                'original_filename': row[2],
                'upload_date': row[3],
                'file_path': row[4],
                'file_size': row[5],
                'file_type': row[6],
                'status': row[12],
                'row_count': row[13],
                'column_count': row[14],
                'metadata': json.loads(row[15]) if row[15] else {}
            }
        return None
    
    # Workflow operations
    async def create_workflow(self, document_id: str, user_id: str) -> str:
        """Create a new workflow for a document"""
        workflow_id = str(uuid.uuid4())
        query = """
        INSERT INTO workflows (
            workflow_id, document_id, workflow_name, created_by, 
            last_modified_by, configuration, metadata
        ) VALUES
        """
        
        self.client.execute(
            query + " (%(workflow_id)s, %(document_id)s, %(workflow_name)s, "
            "%(created_by)s, %(last_modified_by)s, %(configuration)s, %(metadata)s)",
            {
                'workflow_id': workflow_id,
                'document_id': document_id,
                'workflow_name': f"Workflow for {document_id[:8]}",
                'created_by': user_id,
                'last_modified_by': user_id,
                'configuration': '{}',
                'metadata': '{}'
            }
        )
        
        # Initialize workflow stages
        await self._initialize_workflow_stages(workflow_id, document_id)
        
        return workflow_id
    
    async def _initialize_workflow_stages(self, workflow_id: str, document_id: str):
        """Initialize all stages for a workflow"""
        stages = settings.stage_names
        
        for stage_num, stage_name in stages.items():
            stage_id = str(uuid.uuid4())
            query = """
            INSERT INTO workflow_stages (
                stage_id, workflow_id, document_id, stage_number,
                stage_name, stage_type, status, input_data, output_data,
                user_actions, automated_actions, validation_results
            ) VALUES
            """
            
            self.client.execute(
                query + " (%(stage_id)s, %(workflow_id)s, %(document_id)s, "
                "%(stage_number)s, %(stage_name)s, %(stage_type)s, %(status)s, "
                "%(input_data)s, %(output_data)s, %(user_actions)s, "
                "%(automated_actions)s, %(validation_results)s)",
                {
                    'stage_id': stage_id,
                    'workflow_id': workflow_id,
                    'document_id': document_id,
                    'stage_number': stage_num,
                    'stage_name': stage_name,
                    'stage_type': stage_name.lower().replace(' ', '_'),
                    'status': 'pending',
                    'input_data': '{}',
                    'output_data': '{}',
                    'user_actions': '{}',
                    'automated_actions': '{}',
                    'validation_results': '{}'
                }
            )
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow details"""
        query = "SELECT * FROM workflows WHERE workflow_id = %(workflow_id)s"
        result = self.client.execute(query, {'workflow_id': workflow_id})
        
        if result:
            row = result[0]
            return {
                'workflow_id': str(row[0]),
                'document_id': str(row[1]),
                'workflow_name': row[2],
                'current_stage': row[3],
                'total_stages': row[4],
                'status': row[5],
                'started_at': row[6],
                'completed_at': row[7]
            }
        return None
    
    async def get_workflow_stages(self, workflow_id: str) -> List[Dict]:
        """Get all stages for a workflow"""
        query = """
        SELECT stage_number, stage_name, status, started_at, completed_at
        FROM workflow_stages
        WHERE workflow_id = %(workflow_id)s
        ORDER BY stage_number
        """
        
        result = self.client.execute(query, {'workflow_id': workflow_id})
        
        stages = []
        for row in result:
            stages.append({
                'stage_number': row[0],
                'stage_name': row[1],
                'status': row[2],
                'started_at': row[3],
                'completed_at': row[4]
            })
        
        return stages
    
    async def update_stage_status(self, workflow_id: str, stage_number: int, 
                                  status: str, data: Dict = None) -> bool:
        """Update stage status and data"""
        updates = ["status = %(status)s", "started_at = now()"]
        params = {'workflow_id': workflow_id, 'stage_number': stage_number, 'status': status}
        
        if status == 'completed':
            updates.append("completed_at = now()")
        
        if data:
            if 'output_data' in data:
                updates.append("output_data = %(output_data)s")
                params['output_data'] = json.dumps(data['output_data'])
            if 'user_actions' in data:
                updates.append("user_actions = %(user_actions)s")
                params['user_actions'] = json.dumps(data['user_actions'])
        
        query = f"""
        ALTER TABLE workflow_stages
        UPDATE {', '.join(updates)}
        WHERE workflow_id = %(workflow_id)s AND stage_number = %(stage_number)s
        """
        
        self.client.execute(query, params)
        
        # Update workflow current stage
        if status == 'completed' and stage_number < settings.total_stages:
            self.client.execute(
                "ALTER TABLE workflows UPDATE current_stage = %(next_stage)s "
                "WHERE workflow_id = %(workflow_id)s",
                {'workflow_id': workflow_id, 'next_stage': stage_number + 1}
            )
        
        return True
    
    async def create_audit_log(self, data: Dict):
        """Create audit log entry"""
        audit_id = str(uuid.uuid4())
        query = """
        INSERT INTO audit_log (
            audit_id, document_id, workflow_id, stage_number,
            action_category, action_type, action_details, user_id,
            user_role, ip_address, user_agent, session_id,
            response_status, response_time_ms
        ) VALUES
        """
        
        self.client.execute(
            query + " (%(audit_id)s, %(document_id)s, %(workflow_id)s, "
            "%(stage_number)s, %(action_category)s, %(action_type)s, "
            "%(action_details)s, %(user_id)s, %(user_role)s, %(ip_address)s, "
            "%(user_agent)s, %(session_id)s, %(response_status)s, %(response_time_ms)s)",
            {
                'audit_id': audit_id,
                'document_id': data.get('document_id'),
                'workflow_id': data.get('workflow_id'),
                'stage_number': data.get('stage_number'),
                'action_category': data.get('action_category', 'workflow'),
                'action_type': data.get('action_type'),
                'action_details': json.dumps(data.get('action_details', {})),
                'user_id': data.get('user_id', 'system'),
                'user_role': data.get('user_role', 'user'),
                'ip_address': data.get('ip_address', ''),
                'user_agent': data.get('user_agent', ''),
                'session_id': data.get('session_id', ''),
                'response_status': data.get('response_status', 'success'),
                'response_time_ms': data.get('response_time_ms', 0)
            }
        )

# Singleton instance
db_service = DatabaseService()