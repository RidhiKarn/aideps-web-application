import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Optional

class AnalysisService:
    """Service for data analysis and discovery (Stage 3)"""
    
    def identify_variable_types(self, df: pd.DataFrame) -> Dict:
        """Identify and classify variable types"""
        variable_types = {}
        
        for column in df.columns:
            dtype = df[column].dtype
            unique_count = df[column].nunique()
            total_count = len(df[column].dropna())
            unique_ratio = unique_count / total_count if total_count > 0 else 0
            
            # Determine variable type
            if dtype in ['object', 'string']:
                if unique_count == 2:
                    variable_types[column] = {
                        "type": "binary",
                        "values": df[column].unique().tolist()
                    }
                elif unique_count < 10:
                    variable_types[column] = {
                        "type": "categorical",
                        "unique_values": unique_count,
                        "values": df[column].value_counts().to_dict()
                    }
                else:
                    variable_types[column] = {
                        "type": "text",
                        "unique_values": unique_count
                    }
            
            elif dtype in ['int64', 'float64']:
                if unique_count == 2:
                    variable_types[column] = {
                        "type": "binary_numeric",
                        "values": df[column].unique().tolist()
                    }
                elif unique_count < 10 and unique_ratio < 0.05:
                    variable_types[column] = {
                        "type": "ordinal",
                        "unique_values": unique_count,
                        "values": sorted(df[column].unique().tolist())
                    }
                else:
                    variable_types[column] = {
                        "type": "continuous",
                        "range": [float(df[column].min()), float(df[column].max())]
                    }
            
            elif dtype in ['datetime64', 'datetime64[ns]']:
                variable_types[column] = {
                    "type": "datetime",
                    "min": str(df[column].min()),
                    "max": str(df[column].max())
                }
            
            else:
                variable_types[column] = {
                    "type": "unknown",
                    "dtype": str(dtype)
                }
        
        return variable_types
    
    def calculate_descriptive_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate descriptive statistics for all numeric columns"""
        stats_dict = {}
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            col_data = df[column].dropna()
            
            if len(col_data) > 0:
                stats_dict[column] = {
                    "count": int(len(col_data)),
                    "mean": float(col_data.mean()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "25%": float(col_data.quantile(0.25)),
                    "50%": float(col_data.quantile(0.50)),
                    "75%": float(col_data.quantile(0.75)),
                    "max": float(col_data.max()),
                    "skewness": float(col_data.skew()),
                    "kurtosis": float(col_data.kurtosis())
                }
        
        return stats_dict
    
    def find_correlations(self, df: pd.DataFrame, threshold: float = 0.7) -> Dict:
        """Find correlations between numeric variables"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if numeric_df.shape[1] < 2:
            return {"message": "Not enough numeric columns for correlation analysis"}
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()
        
        # Find high correlations
        high_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold:
                    high_correlations.append({
                        "variable1": corr_matrix.columns[i],
                        "variable2": corr_matrix.columns[j],
                        "correlation": round(corr_value, 3),
                        "strength": "strong" if abs(corr_value) > 0.8 else "moderate"
                    })
        
        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "high_correlations": high_correlations,
            "threshold_used": threshold
        }
    
    def identify_key_variables(self, df: pd.DataFrame, target: Optional[str] = None) -> List[Dict]:
        """Identify potentially important variables"""
        key_variables = []
        
        # Variables with high completeness
        for column in df.columns:
            missing_pct = (df[column].isnull().sum() / len(df)) * 100
            
            if missing_pct < 5:  # Less than 5% missing
                key_variables.append({
                    "variable": column,
                    "reason": "high_completeness",
                    "missing_percentage": round(missing_pct, 2)
                })
        
        # If target is specified, find variables correlated with target
        if target and target in df.columns and df[target].dtype in ['int64', 'float64']:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                if col != target:
                    correlation = df[col].corr(df[target])
                    if abs(correlation) > 0.3:
                        key_variables.append({
                            "variable": col,
                            "reason": "correlated_with_target",
                            "correlation": round(correlation, 3)
                        })
        
        # Remove duplicates
        seen = set()
        unique_key_vars = []
        for var in key_variables:
            if var["variable"] not in seen:
                seen.add(var["variable"])
                unique_key_vars.append(var)
        
        return unique_key_vars
    
    def detect_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect patterns in the data"""
        patterns = {
            "missing_patterns": {},
            "value_patterns": {},
            "temporal_patterns": {}
        }
        
        # Missing data patterns
        missing_cols = df.columns[df.isnull().any()].tolist()
        if len(missing_cols) > 1:
            # Check if missing values occur together
            missing_together = []
            for i in range(len(missing_cols)):
                for j in range(i + 1, len(missing_cols)):
                    col1, col2 = missing_cols[i], missing_cols[j]
                    both_missing = df[col1].isnull() & df[col2].isnull()
                    if both_missing.sum() > 0:
                        missing_together.append({
                            "columns": [col1, col2],
                            "count": int(both_missing.sum()),
                            "percentage": round((both_missing.sum() / len(df)) * 100, 2)
                        })
            
            patterns["missing_patterns"]["co_occurring"] = missing_together
        
        # Value patterns (for categorical variables)
        for column in df.select_dtypes(include=['object']).columns:
            value_counts = df[column].value_counts()
            if len(value_counts) < 20:  # Only for low-cardinality columns
                patterns["value_patterns"][column] = {
                    "distribution": value_counts.to_dict(),
                    "mode": value_counts.index[0] if len(value_counts) > 0 else None,
                    "entropy": stats.entropy(value_counts)
                }
        
        return patterns
    
    def create_summary_report(self, df: pd.DataFrame) -> Dict:
        """Create a comprehensive summary report"""
        return {
            "dataset_info": {
                "rows": len(df),
                "columns": len(df.columns),
                "memory_usage": df.memory_usage(deep=True).sum() / 1024**2,  # MB
                "column_names": df.columns.tolist()
            },
            "variable_types": self.identify_variable_types(df),
            "descriptive_stats": self.calculate_descriptive_stats(df),
            "correlations": self.find_correlations(df),
            "key_variables": self.identify_key_variables(df),
            "patterns": self.detect_patterns(df)
        }