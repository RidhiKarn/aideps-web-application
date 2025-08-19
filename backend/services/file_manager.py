import os
import shutil
import json
from typing import Dict, Optional
from datetime import datetime
from config.settings import settings

class FileManager:
    """Manages instance-based folder structure for workflows"""
    
    @staticmethod
    def create_instance_folders(instance_id: str) -> Dict[str, str]:
        """Create folder structure for a new instance"""
        instance_path = os.path.join(settings.data_dir, instance_id)
        
        # Create main instance folder
        os.makedirs(instance_path, exist_ok=True)
        
        # Create stage subfolders
        stage_paths = {}
        for stage_num, folder_name in settings.stage_folders.items():
            stage_path = os.path.join(instance_path, folder_name)
            os.makedirs(stage_path, exist_ok=True)
            stage_paths[stage_num] = stage_path
        
        # Create metadata file
        metadata = {
            "instance_id": instance_id,
            "created_at": datetime.now().isoformat(),
            "stage_folders": stage_paths,
            "status": "initialized"
        }
        
        metadata_path = os.path.join(instance_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return stage_paths
    
    @staticmethod
    def get_instance_path(instance_id: str, stage_num: Optional[int] = None) -> str:
        """Get path for instance or specific stage folder"""
        instance_path = os.path.join(settings.data_dir, instance_id)
        
        if stage_num and stage_num in settings.stage_folders:
            return os.path.join(instance_path, settings.stage_folders[stage_num])
        
        return instance_path
    
    @staticmethod
    def save_stage_data(instance_id: str, stage_num: int, filename: str, 
                       data: bytes = None, source_path: str = None) -> str:
        """Save data to a specific stage folder"""
        stage_path = FileManager.get_instance_path(instance_id, stage_num)
        file_path = os.path.join(stage_path, filename)
        
        if data:
            # Save from bytes
            with open(file_path, "wb") as f:
                f.write(data)
        elif source_path:
            # Copy from existing file
            shutil.copy2(source_path, file_path)
        else:
            raise ValueError("Either data or source_path must be provided")
        
        return file_path
    
    @staticmethod
    def save_stage_metadata(instance_id: str, stage_num: int, metadata: Dict) -> str:
        """Save metadata for a specific stage"""
        stage_path = FileManager.get_instance_path(instance_id, stage_num)
        metadata_file = os.path.join(stage_path, "stage_metadata.json")
        
        # Add timestamp
        metadata["updated_at"] = datetime.now().isoformat()
        metadata["stage_number"] = stage_num
        metadata["stage_name"] = settings.stage_names.get(stage_num)
        
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        return metadata_file
    
    @staticmethod
    def get_stage_files(instance_id: str, stage_num: int) -> Dict[str, str]:
        """Get all files in a stage folder"""
        stage_path = FileManager.get_instance_path(instance_id, stage_num)
        
        if not os.path.exists(stage_path):
            return {}
        
        files = {}
        for filename in os.listdir(stage_path):
            file_path = os.path.join(stage_path, filename)
            if os.path.isfile(file_path):
                files[filename] = file_path
        
        return files
    
    @staticmethod
    def copy_to_next_stage(instance_id: str, from_stage: int, to_stage: int, 
                          filename: str) -> str:
        """Copy a file from one stage to the next"""
        from_path = os.path.join(
            FileManager.get_instance_path(instance_id, from_stage),
            filename
        )
        
        to_path = os.path.join(
            FileManager.get_instance_path(instance_id, to_stage),
            filename
        )
        
        if os.path.exists(from_path):
            shutil.copy2(from_path, to_path)
            return to_path
        else:
            raise FileNotFoundError(f"File {filename} not found in stage {from_stage}")
    
    @staticmethod
    def create_stage_report(instance_id: str, stage_num: int) -> Dict:
        """Create a summary report for a stage"""
        stage_path = FileManager.get_instance_path(instance_id, stage_num)
        
        report = {
            "stage_number": stage_num,
            "stage_name": settings.stage_names.get(stage_num),
            "files": [],
            "total_size": 0
        }
        
        if os.path.exists(stage_path):
            for filename in os.listdir(stage_path):
                file_path = os.path.join(stage_path, filename)
                if os.path.isfile(file_path):
                    file_info = {
                        "name": filename,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(
                            os.path.getmtime(file_path)
                        ).isoformat()
                    }
                    report["files"].append(file_info)
                    report["total_size"] += file_info["size"]
        
        return report
    
    @staticmethod
    def get_instance_summary(instance_id: str) -> Dict:
        """Get summary of all stages for an instance"""
        instance_path = os.path.join(settings.data_dir, instance_id)
        
        if not os.path.exists(instance_path):
            return {"error": f"Instance {instance_id} not found"}
        
        summary = {
            "instance_id": instance_id,
            "path": instance_path,
            "stages": {}
        }
        
        # Load metadata if exists
        metadata_path = os.path.join(instance_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                summary["created_at"] = metadata.get("created_at")
        
        # Get info for each stage
        for stage_num, folder_name in settings.stage_folders.items():
            stage_report = FileManager.create_stage_report(instance_id, stage_num)
            summary["stages"][stage_num] = stage_report
        
        return summary