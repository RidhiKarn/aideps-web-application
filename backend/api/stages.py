from fastapi import APIRouter, HTTPException
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from typing import Dict, List, Optional
import json
import os
from services.database import db_service
from services.cleansing import CleansingService
from services.analysis import AnalysisService
from services.statistics import StatisticsService
from services.file_manager import FileManager

router = APIRouter()

# Initialize services
cleansing_service = CleansingService()
analysis_service = AnalysisService()
statistics_service = StatisticsService()

@router.post("/cleansing/analyze")
async def analyze_data_quality(workflow_id: str, document_id: str):
    """Stage 2: Analyze data for cleaning requirements"""
    
    # Get document
    document = await db_service.get_document(document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    # Load data from stage 1 folder
    data_path = FileManager.get_instance_path(document_id, 1) + "/data.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path, low_memory=False)
    else:
        # Fallback to original file path
        df = pd.read_csv(document['file_path'], low_memory=False) if document['file_type'] == '.csv' else pd.read_excel(document['file_path'])
    
    # Analyze data quality
    quality_report = {
        "missing_data": {},
        "outliers": {},
        "data_types": {},
        "suggested_actions": []
    }
    
    # Missing data analysis
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        
        quality_report["missing_data"][col] = {
            "count": int(missing_count),
            "percentage": round(missing_pct, 2),
            "pattern": "MCAR" if missing_pct < 5 else "MAR" if missing_pct < 20 else "MNAR"
        }
        
        if missing_pct > 0:
            if df[col].dtype in ['float64', 'int64']:
                quality_report["suggested_actions"].append({
                    "column": col,
                    "issue": "missing_values",
                    "suggestion": "mean" if missing_pct < 10 else "median"
                })
            else:
                quality_report["suggested_actions"].append({
                    "column": col,
                    "issue": "missing_values",
                    "suggestion": "mode"
                })
    
    # Outlier detection for numeric columns
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
        
        if len(outliers) > 0:
            quality_report["outliers"][col] = {
                "count": len(outliers),
                "percentage": round((len(outliers) / len(df)) * 100, 2),
                "lower_bound": round(lower_bound, 2),
                "upper_bound": round(upper_bound, 2),
                "outlier_values": outliers.head(10).tolist()
            }
    
    # Data types
    quality_report["data_types"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
    
    # Save quality report to stage 2 folder
    FileManager.save_stage_metadata(document_id, 2, quality_report)
    FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=2,
        filename="quality_report.json",
        data=json.dumps(quality_report, indent=2).encode()
    )
    
    return quality_report

@router.post("/cleansing/impute")
async def impute_missing_values(workflow_id: str, document_id: str, imputation_config: Dict):
    """Apply imputation strategies for missing values"""
    
    document = await db_service.get_document(document_id)
    if not document:
        raise HTTPException(404, "Document not found")
    
    # Load data from stage 1 folder
    data_path = FileManager.get_instance_path(document_id, 1) + "/data.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path, low_memory=False)
    else:
        # Fallback to original file path
        df = pd.read_csv(document['file_path'], low_memory=False) if document['file_type'] == '.csv' else pd.read_excel(document['file_path'])
    
    results = {
        "imputed_columns": [],
        "errors": []
    }
    
    # Apply imputation based on config
    for col, strategy in imputation_config.items():
        if col not in df.columns:
            results["errors"].append(f"Column {col} not found")
            continue
        
        try:
            if strategy == "mean":
                df[col].fillna(df[col].mean(), inplace=True)
            elif strategy == "median":
                df[col].fillna(df[col].median(), inplace=True)
            elif strategy == "mode":
                df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else np.nan, inplace=True)
            elif strategy == "forward_fill":
                df[col] = df[col].ffill()
            elif strategy == "backward_fill":
                df[col] = df[col].bfill()
            elif strategy == "knn":
                # Use KNN imputation for numeric columns
                if df[col].dtype in ['float64', 'int64']:
                    imputer = KNNImputer(n_neighbors=5)
                    df[col] = imputer.fit_transform(df[[col]])
            elif isinstance(strategy, (int, float, str)):
                # Custom value
                df[col].fillna(strategy, inplace=True)
            
            results["imputed_columns"].append({
                "column": col,
                "strategy": strategy,
                "remaining_missing": int(df[col].isnull().sum())
            })
        except Exception as e:
            results["errors"].append(f"Failed to impute {col}: {str(e)}")
    
    # Save cleaned data to stage 2 folder
    cleaned_csv = df.to_csv(index=False)
    cleaned_path = FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=2,
        filename="cleaned_data.csv",
        data=cleaned_csv.encode()
    )
    
    # Save imputation results
    FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=2,
        filename="imputation_results.json",
        data=json.dumps(results, indent=2).encode()
    )
    
    # Update stage status
    await db_service.update_stage_status(
        workflow_id, 2, 'in_progress',
        data={'output_data': {'cleaned_file': cleaned_path, 'imputation_results': results}}
    )
    
    return results

@router.post("/cleansing/outliers")
async def handle_outliers(workflow_id: str, document_id: str, outlier_config: Dict):
    """Handle outliers based on user configuration"""
    
    document = await db_service.get_document(document_id)
    # Load data from stage 1 or 2 folder
    cleansed_path = FileManager.get_instance_path(document_id, 2) + "/cleaned_data.csv"
    data_path = FileManager.get_instance_path(document_id, 1) + "/data.csv"
    
    if os.path.exists(cleansed_path):
        df = pd.read_csv(cleansed_path, low_memory=False)
    elif os.path.exists(data_path):
        df = pd.read_csv(data_path, low_memory=False)
    else:
        df = pd.read_csv(document['file_path'], low_memory=False) if document['file_type'] == '.csv' else pd.read_excel(document['file_path'])
    
    results = {
        "processed_columns": [],
        "errors": []
    }
    
    for col, method in outlier_config.items():
        if col not in df.columns:
            results["errors"].append(f"Column {col} not found")
            continue
        
        if df[col].dtype not in ['float64', 'int64']:
            results["errors"].append(f"Column {col} is not numeric")
            continue
        
        try:
            if method == "remove":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                df = df[~((df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR))]
            elif method == "cap":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                df[col] = df[col].clip(lower=lower, upper=upper)
            elif method == "zscore":
                from scipy import stats
                df = df[(np.abs(stats.zscore(df[col])) < 3)]
            
            results["processed_columns"].append({
                "column": col,
                "method": method,
                "rows_after": len(df)
            })
        except Exception as e:
            results["errors"].append(f"Failed to process outliers in {col}: {str(e)}")
    
    # Save processed data to stage 2 folder
    processed_csv = df.to_csv(index=False)
    processed_path = FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=2,
        filename="outliers_processed.csv",
        data=processed_csv.encode()
    )
    
    # Save outlier processing results
    FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=2,
        filename="outlier_results.json",
        data=json.dumps(results, indent=2).encode()
    )
    
    return results

@router.post("/analysis/discover")
async def discover_patterns(workflow_id: str, document_id: str):
    """Stage 3: Analyze and discover patterns in data"""
    
    document = await db_service.get_document(document_id)
    # Load data from stage 1 or 2 folder
    cleansed_path = FileManager.get_instance_path(document_id, 2) + "/cleaned_data.csv"
    data_path = FileManager.get_instance_path(document_id, 1) + "/data.csv"
    
    if os.path.exists(cleansed_path):
        df = pd.read_csv(cleansed_path, low_memory=False)
    elif os.path.exists(data_path):
        df = pd.read_csv(data_path, low_memory=False)
    else:
        df = pd.read_csv(document['file_path'], low_memory=False) if document['file_type'] == '.csv' else pd.read_excel(document['file_path'])
    
    analysis_results = {
        "variable_types": {},
        "key_statistics": {},
        "correlations": {},
        "distributions": {}
    }
    
    # Classify variables
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio < 0.05:
                analysis_results["variable_types"][col] = "categorical"
            else:
                analysis_results["variable_types"][col] = "continuous"
        else:
            analysis_results["variable_types"][col] = "categorical"
    
    # Key statistics for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        analysis_results["key_statistics"][col] = {
            "mean": round(df[col].mean(), 2),
            "median": round(df[col].median(), 2),
            "std": round(df[col].std(), 2),
            "min": round(df[col].min(), 2),
            "max": round(df[col].max(), 2),
            "q1": round(df[col].quantile(0.25), 2),
            "q3": round(df[col].quantile(0.75), 2)
        }
    
    # Correlation matrix for numeric columns
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        # Find high correlations
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    high_corr.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": round(corr_matrix.iloc[i, j], 3)
                    })
        analysis_results["correlations"]["high_correlations"] = high_corr
    
    # Save analysis results to stage 3 folder
    FileManager.save_stage_metadata(document_id, 3, analysis_results)
    FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=3,
        filename="analysis_results.json",
        data=json.dumps(analysis_results, indent=2).encode()
    )
    
    # Save key statistics as CSV for easier viewing
    if analysis_results["key_statistics"]:
        stats_df = pd.DataFrame(analysis_results["key_statistics"]).T
        FileManager.save_stage_data(
            instance_id=document_id,
            stage_num=3,
            filename="key_statistics.csv",
            data=stats_df.to_csv().encode()
        )
    
    return analysis_results

@router.post("/statistics/calculate")
async def calculate_statistics(workflow_id: str, document_id: str, config: Dict):
    """Stage 4: Calculate weighted statistics"""
    
    document = await db_service.get_document(document_id)
    # Load data from stage 1 or 2 folder
    cleansed_path = FileManager.get_instance_path(document_id, 2) + "/cleaned_data.csv"
    data_path = FileManager.get_instance_path(document_id, 1) + "/data.csv"
    
    if os.path.exists(cleansed_path):
        df = pd.read_csv(cleansed_path, low_memory=False)
    elif os.path.exists(data_path):
        df = pd.read_csv(data_path, low_memory=False)
    else:
        df = pd.read_csv(document['file_path'], low_memory=False) if document['file_type'] == '.csv' else pd.read_excel(document['file_path'])
    
    weight_col = config.get("weight_column", "survey_weight")
    variables = config.get("variables", df.select_dtypes(include=[np.number]).columns.tolist())
    
    results = {
        "weighted_means": {},
        "weighted_totals": {},
        "standard_errors": {},
        "confidence_intervals": {}
    }
    
    # Check if weight column exists
    if weight_col in df.columns:
        weights = df[weight_col]
    else:
        # Use equal weights if no weight column
        weights = np.ones(len(df))
    
    for var in variables:
        if var not in df.columns or df[var].dtype not in ['float64', 'int64']:
            continue
        
        # Weighted mean
        weighted_mean = np.average(df[var].dropna(), weights=weights[:len(df[var].dropna())])
        results["weighted_means"][var] = round(weighted_mean, 3)
        
        # Weighted total (population estimate)
        weighted_total = np.sum(df[var].dropna() * weights[:len(df[var].dropna())])
        results["weighted_totals"][var] = round(weighted_total, 0)
        
        # Standard error (simplified)
        n = len(df[var].dropna())
        se = df[var].std() / np.sqrt(n)
        results["standard_errors"][var] = round(se, 3)
        
        # 95% Confidence interval
        ci_lower = weighted_mean - 1.96 * se
        ci_upper = weighted_mean + 1.96 * se
        results["confidence_intervals"][var] = {
            "lower": round(ci_lower, 3),
            "upper": round(ci_upper, 3)
        }
    
    # Save statistics results to stage 4 folder
    FileManager.save_stage_metadata(document_id, 4, results)
    FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=4,
        filename="weighted_statistics.json",
        data=json.dumps(results, indent=2).encode()
    )
    
    # Save statistics as CSV for easier viewing
    stats_df = pd.DataFrame({
        'variable': list(results["weighted_means"].keys()),
        'weighted_mean': list(results["weighted_means"].values()),
        'weighted_total': [results["weighted_totals"].get(k, 0) for k in results["weighted_means"].keys()],
        'standard_error': [results["standard_errors"].get(k, 0) for k in results["weighted_means"].keys()],
        'ci_lower': [results["confidence_intervals"].get(k, {}).get('lower', 0) for k in results["weighted_means"].keys()],
        'ci_upper': [results["confidence_intervals"].get(k, {}).get('upper', 0) for k in results["weighted_means"].keys()]
    })
    FileManager.save_stage_data(
        instance_id=document_id,
        stage_num=4,
        filename="statistics_summary.csv",
        data=stats_df.to_csv(index=False).encode()
    )
    
    return results