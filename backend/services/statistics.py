import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple

class StatisticsService:
    """Service for statistical calculations and weighting (Stage 4)"""
    
    def apply_weights(self, df: pd.DataFrame, weight_column: str) -> pd.DataFrame:
        """Apply survey weights to the dataset"""
        if weight_column not in df.columns:
            raise ValueError(f"Weight column '{weight_column}' not found in dataset")
        
        # Normalize weights to sum to sample size
        weights = df[weight_column].values
        normalized_weights = weights * (len(df) / weights.sum())
        
        df_weighted = df.copy()
        df_weighted['normalized_weight'] = normalized_weights
        
        return df_weighted
    
    def calculate_weighted_mean(self, df: pd.DataFrame, variable: str, 
                               weight_column: str = None) -> Dict:
        """Calculate weighted mean with standard error"""
        if variable not in df.columns:
            raise ValueError(f"Variable '{variable}' not found in dataset")
        
        # Remove missing values
        data = df[[variable]].copy()
        if weight_column and weight_column in df.columns:
            data[weight_column] = df[weight_column]
            data = data.dropna()
            weights = data[weight_column].values
        else:
            data = data.dropna()
            weights = np.ones(len(data))
        
        values = data[variable].values
        
        # Calculate weighted mean
        weighted_mean = np.average(values, weights=weights)
        
        # Calculate weighted variance
        variance = np.average((values - weighted_mean) ** 2, weights=weights)
        
        # Calculate standard error
        n_eff = weights.sum() ** 2 / (weights ** 2).sum()  # Effective sample size
        standard_error = np.sqrt(variance / n_eff)
        
        # Calculate 95% confidence interval
        ci_lower = weighted_mean - 1.96 * standard_error
        ci_upper = weighted_mean + 1.96 * standard_error
        
        return {
            "variable": variable,
            "mean": round(float(weighted_mean), 4),
            "standard_error": round(float(standard_error), 4),
            "confidence_interval": {
                "lower": round(float(ci_lower), 4),
                "upper": round(float(ci_upper), 4),
                "level": 0.95
            },
            "sample_size": len(values),
            "effective_sample_size": round(float(n_eff), 2)
        }
    
    def calculate_weighted_proportion(self, df: pd.DataFrame, variable: str, 
                                     category: any, weight_column: str = None) -> Dict:
        """Calculate weighted proportion for categorical variables"""
        if variable not in df.columns:
            raise ValueError(f"Variable '{variable}' not found in dataset")
        
        # Create binary indicator
        data = df[[variable]].copy()
        if weight_column and weight_column in df.columns:
            data[weight_column] = df[weight_column]
            data = data.dropna()
            weights = data[weight_column].values
        else:
            data = data.dropna()
            weights = np.ones(len(data))
        
        # Binary indicator for the category
        indicator = (data[variable] == category).astype(int).values
        
        # Calculate weighted proportion
        weighted_prop = np.average(indicator, weights=weights)
        
        # Calculate standard error (using formula for proportion)
        variance = weighted_prop * (1 - weighted_prop)
        n_eff = weights.sum() ** 2 / (weights ** 2).sum()
        standard_error = np.sqrt(variance / n_eff)
        
        # Calculate 95% confidence interval
        ci_lower = weighted_prop - 1.96 * standard_error
        ci_upper = weighted_prop + 1.96 * standard_error
        
        # Ensure CI is within [0, 1]
        ci_lower = max(0, ci_lower)
        ci_upper = min(1, ci_upper)
        
        return {
            "variable": variable,
            "category": str(category),
            "proportion": round(float(weighted_prop), 4),
            "percentage": round(float(weighted_prop * 100), 2),
            "standard_error": round(float(standard_error), 4),
            "confidence_interval": {
                "lower": round(float(ci_lower), 4),
                "upper": round(float(ci_upper), 4),
                "level": 0.95
            },
            "count": int(indicator.sum()),
            "weighted_count": round(float((indicator * weights).sum()), 2),
            "sample_size": len(indicator)
        }
    
    def calculate_crosstab(self, df: pd.DataFrame, row_var: str, col_var: str,
                          weight_column: str = None) -> Dict:
        """Calculate weighted crosstabulation"""
        if row_var not in df.columns or col_var not in df.columns:
            raise ValueError("Variables not found in dataset")
        
        if weight_column and weight_column in df.columns:
            # Weighted crosstab
            crosstab = pd.crosstab(
                df[row_var], 
                df[col_var], 
                weights=df[weight_column], 
                normalize='all'
            )
        else:
            # Unweighted crosstab
            crosstab = pd.crosstab(
                df[row_var], 
                df[col_var], 
                normalize='all'
            )
        
        # Convert to percentages
        crosstab_pct = crosstab * 100
        
        # Calculate chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(
            pd.crosstab(df[row_var], df[col_var])
        )
        
        return {
            "row_variable": row_var,
            "column_variable": col_var,
            "crosstab": crosstab.to_dict(),
            "crosstab_percentage": crosstab_pct.to_dict(),
            "chi_square": {
                "statistic": round(float(chi2), 4),
                "p_value": round(float(p_value), 4),
                "degrees_of_freedom": int(dof),
                "significant": p_value < 0.05
            }
        }
    
    def calculate_population_estimates(self, df: pd.DataFrame, variables: List[str],
                                      weight_column: str, population_size: int = None) -> Dict:
        """Calculate population-level estimates from survey data"""
        if weight_column not in df.columns:
            raise ValueError(f"Weight column '{weight_column}' not found")
        
        estimates = {}
        
        # If population size is provided, scale weights
        if population_size:
            scaling_factor = population_size / df[weight_column].sum()
        else:
            scaling_factor = 1
        
        for var in variables:
            if var not in df.columns:
                continue
            
            if df[var].dtype in ['int64', 'float64']:
                # Continuous variable - calculate total
                data = df[[var, weight_column]].dropna()
                weighted_total = (data[var] * data[weight_column] * scaling_factor).sum()
                
                estimates[var] = {
                    "type": "continuous",
                    "weighted_total": round(float(weighted_total), 2),
                    "weighted_mean": round(float(weighted_total / (data[weight_column] * scaling_factor).sum()), 2)
                }
            else:
                # Categorical variable - calculate counts
                categories = {}
                for category in df[var].unique():
                    if pd.notna(category):
                        count = ((df[var] == category) * df[weight_column] * scaling_factor).sum()
                        categories[str(category)] = round(float(count), 2)
                
                estimates[var] = {
                    "type": "categorical",
                    "weighted_counts": categories,
                    "total": round(sum(categories.values()), 2)
                }
        
        return {
            "population_size": population_size,
            "scaling_factor": round(scaling_factor, 4),
            "estimates": estimates
        }
    
    def calculate_subgroup_statistics(self, df: pd.DataFrame, target_var: str,
                                     group_var: str, weight_column: str = None) -> Dict:
        """Calculate statistics for subgroups"""
        if target_var not in df.columns or group_var not in df.columns:
            raise ValueError("Variables not found in dataset")
        
        subgroup_stats = {}
        
        for group in df[group_var].unique():
            if pd.notna(group):
                subset = df[df[group_var] == group]
                
                if df[target_var].dtype in ['int64', 'float64']:
                    # Calculate weighted mean for continuous variable
                    stats_result = self.calculate_weighted_mean(
                        subset, target_var, weight_column
                    )
                    subgroup_stats[str(group)] = stats_result
                else:
                    # Calculate distribution for categorical variable
                    value_counts = subset[target_var].value_counts()
                    if weight_column and weight_column in subset.columns:
                        weighted_counts = {}
                        for val in value_counts.index:
                            prop = self.calculate_weighted_proportion(
                                subset, target_var, val, weight_column
                            )
                            weighted_counts[str(val)] = prop["percentage"]
                    else:
                        weighted_counts = (value_counts / len(subset) * 100).to_dict()
                    
                    subgroup_stats[str(group)] = {
                        "distribution": weighted_counts,
                        "sample_size": len(subset)
                    }
        
        return {
            "target_variable": target_var,
            "grouping_variable": group_var,
            "subgroups": subgroup_stats
        }
    
    def perform_hypothesis_test(self, df: pd.DataFrame, var1: str, var2: str,
                               test_type: str = "auto") -> Dict:
        """Perform appropriate hypothesis test based on variable types"""
        if var1 not in df.columns or var2 not in df.columns:
            raise ValueError("Variables not found in dataset")
        
        # Remove missing values
        data = df[[var1, var2]].dropna()
        
        # Determine test type if auto
        if test_type == "auto":
            if df[var1].dtype in ['int64', 'float64'] and df[var2].dtype in ['int64', 'float64']:
                test_type = "correlation"
            elif df[var1].dtype in ['int64', 'float64'] and df[var2].nunique() == 2:
                test_type = "t_test"
            elif df[var1].dtype in ['int64', 'float64'] and df[var2].nunique() > 2:
                test_type = "anova"
            else:
                test_type = "chi_square"
        
        result = {
            "variable1": var1,
            "variable2": var2,
            "test_type": test_type,
            "sample_size": len(data)
        }
        
        if test_type == "correlation":
            corr, p_value = stats.pearsonr(data[var1], data[var2])
            result.update({
                "correlation": round(float(corr), 4),
                "p_value": round(float(p_value), 4),
                "significant": p_value < 0.05
            })
        
        elif test_type == "t_test":
            groups = data[var2].unique()
            if len(groups) == 2:
                group1 = data[data[var2] == groups[0]][var1]
                group2 = data[data[var2] == groups[1]][var1]
                t_stat, p_value = stats.ttest_ind(group1, group2)
                result.update({
                    "t_statistic": round(float(t_stat), 4),
                    "p_value": round(float(p_value), 4),
                    "significant": p_value < 0.05,
                    "group1_mean": round(float(group1.mean()), 4),
                    "group2_mean": round(float(group2.mean()), 4)
                })
        
        elif test_type == "anova":
            groups = [data[data[var2] == g][var1].values for g in data[var2].unique()]
            f_stat, p_value = stats.f_oneway(*groups)
            result.update({
                "f_statistic": round(float(f_stat), 4),
                "p_value": round(float(p_value), 4),
                "significant": p_value < 0.05
            })
        
        elif test_type == "chi_square":
            crosstab = pd.crosstab(data[var1], data[var2])
            chi2, p_value, dof, expected = stats.chi2_contingency(crosstab)
            result.update({
                "chi2_statistic": round(float(chi2), 4),
                "p_value": round(float(p_value), 4),
                "degrees_of_freedom": int(dof),
                "significant": p_value < 0.05
            })
        
        return result