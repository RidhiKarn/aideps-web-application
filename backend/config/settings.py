from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "AIDEPS"
    debug: bool = True
    
    # ClickHouse Database
    clickhouse_host: str = "localhost"
    clickhouse_port: int = 9000
    clickhouse_user: str = "default"
    clickhouse_password: str = "clickhouse"
    clickhouse_database: str = "aideps"
    
    # File Storage
    data_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    upload_dir: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: list = [".csv", ".xlsx", ".xls"]
    
    # Stage folders
    stage_folders: dict = {
        1: "01_upload",
        2: "02_cleansing", 
        3: "03_analysis",
        4: "04_statistics",
        5: "05_reports_proposed",
        6: "06_confirmation",
        7: "07_final_reports"
    }
    
    # Processing
    batch_size: int = 1000
    max_workers: int = 4
    
    # Workflow
    total_stages: int = 7
    stage_names: dict = {
        1: "Raw Data Upload",
        2: "Data Cleansing",
        3: "Analysis & Discovery",
        4: "Statistics & Weights",
        5: "Propose Reports",
        6: "User Confirmation",
        7: "Final Report Generation"
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Create directories if they don't exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)