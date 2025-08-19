import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from typing import Dict, List, Optional
import os
from services.file_manager import FileManager

class CleansingService:
    """Service for data cleansing operations (Stage 2)"""
    
    def analyze_missing_data(self, df: pd.DataFrame) -> Dict:
        """Analyze missing data patterns"""
        analysis = {}
        
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            total_count = len(df)
            missing_pct = (missing_count / total_count) * 100
            
            analysis[column] = {
                "missing_count": int(missing_count),
                "missing_percentage": round(missing_pct, 2),
                "total_count": total_count,
                "non_missing_count": total_count - missing_count
            }
            
            # Suggest imputation strategy
            if missing_pct > 0:
                if df[column].dtype in ['float64', 'int64']:
                    if missing_pct < 5:
                        analysis[column]["suggested_strategy"] = "mean"
                    elif missing_pct < 20:
                        analysis[column]["suggested_strategy"] = "median"
                    else:
                        analysis[column]["suggested_strategy"] = "knn"
                else:
                    analysis[column]["suggested_strategy"] = "mode"
        
        return analysis
    
    def detect_outliers(self, df: pd.DataFrame) -> Dict:
        """Detect outliers using IQR method"""
        outliers = {}
        
        for column in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            if outlier_count > 0:
                outliers[column] = {
                    "count": int(outlier_count),
                    "percentage": round((outlier_count / len(df)) * 100, 2),
                    "lower_bound": round(lower_bound, 2),
                    "upper_bound": round(upper_bound, 2),
                    "outlier_indices": df[outlier_mask].index.tolist()[:10]  # First 10
                }
        
        return outliers
    
    def impute_missing_values(self, df: pd.DataFrame, strategies: Dict) -> pd.DataFrame:
        """Apply imputation strategies to handle missing values"""
        df_imputed = df.copy()
        
        for column, strategy in strategies.items():
            if column not in df_imputed.columns:
                continue
            
            if strategy == "mean" and df_imputed[column].dtype in ['float64', 'int64']:
                df_imputed[column].fillna(df_imputed[column].mean(), inplace=True)
            
            elif strategy == "median" and df_imputed[column].dtype in ['float64', 'int64']:
                df_imputed[column].fillna(df_imputed[column].median(), inplace=True)
            
            elif strategy == "mode":
                mode_value = df_imputed[column].mode()
                if not mode_value.empty:
                    df_imputed[column].fillna(mode_value[0], inplace=True)
            
            elif strategy == "forward_fill":
                df_imputed[column].fillna(method='ffill', inplace=True)
            
            elif strategy == "backward_fill":
                df_imputed[column].fillna(method='bfill', inplace=True)
            
            elif strategy == "knn" and df_imputed[column].dtype in ['float64', 'int64']:
                # Use KNN imputation
                numeric_cols = df_imputed.select_dtypes(include=[np.number]).columns
                imputer = KNNImputer(n_neighbors=5)
                df_imputed[numeric_cols] = imputer.fit_transform(df_imputed[numeric_cols])
            
            elif strategy == "drop":
                df_imputed = df_imputed.dropna(subset=[column])
            
            else:
                # Custom value
                df_imputed[column].fillna(strategy, inplace=True)
        
        return df_imputed
    
    def handle_outliers(self, df: pd.DataFrame, strategies: Dict) -> pd.DataFrame:
        """Handle outliers based on specified strategies"""
        df_processed = df.copy()
        
        for column, strategy in strategies.items():
            if column not in df_processed.columns:
                continue
            
            if df_processed[column].dtype not in ['float64', 'int64']:
                continue
            
            if strategy == "remove":
                Q1 = df_processed[column].quantile(0.25)
                Q3 = df_processed[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                df_processed = df_processed[
                    (df_processed[column] >= lower_bound) & 
                    (df_processed[column] <= upper_bound)
                ]
            
            elif strategy == "cap":
                Q1 = df_processed[column].quantile(0.25)
                Q3 = df_processed[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                df_processed[column] = df_processed[column].clip(
                    lower=lower_bound, 
                    upper=upper_bound
                )
            
            elif strategy == "winsorize":
                # Cap at 5th and 95th percentile
                lower_bound = df_processed[column].quantile(0.05)
                upper_bound = df_processed[column].quantile(0.95)
                df_processed[column] = df_processed[column].clip(
                    lower=lower_bound,
                    upper=upper_bound
                )
        
        return df_processed
    
    def validate_data(self, df: pd.DataFrame, rules: List[Dict]) -> Dict:
        """Validate data against specified rules"""
        validation_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        
        for rule in rules:
            rule_type = rule.get("type")
            column = rule.get("column")
            
            if rule_type == "range" and column in df.columns:
                min_val = rule.get("min")
                max_val = rule.get("max")
                
                if df[column].dtype in ['float64', 'int64']:
                    violations = df[(df[column] < min_val) | (df[column] > max_val)]
                    
                    if len(violations) > 0:
                        validation_results["failed"].append({
                            "rule": rule,
                            "violations": len(violations),
                            "message": f"{column} has {len(violations)} values outside range [{min_val}, {max_val}]"
                        })
                    else:
                        validation_results["passed"].append({
                            "rule": rule,
                            "message": f"{column} values are within range"
                        })
            
            elif rule_type == "unique" and column in df.columns:
                duplicates = df[df.duplicated(subset=[column])]
                
                if len(duplicates) > 0:
                    validation_results["warnings"].append({
                        "rule": rule,
                        "duplicates": len(duplicates),
                        "message": f"{column} has {len(duplicates)} duplicate values"
                    })
            
            elif rule_type == "required" and column in df.columns:
                missing = df[column].isnull().sum()
                
                if missing > 0:
                    validation_results["failed"].append({
                        "rule": rule,
                        "missing": missing,
                        "message": f"{column} has {missing} missing values but is required"
                    })
        
        return validation_results