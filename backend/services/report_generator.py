import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

class ReportGenerator:
    """Service for generating reports (Stages 5-7)"""
    
    def __init__(self):
        self.templates = {
            "standard_survey": {
                "name": "Standard Survey Report",
                "sections": ["summary", "demographics", "key_indicators", "statistics", "appendix"]
            },
            "health_survey": {
                "name": "Health Survey Report",
                "sections": ["summary", "demographics", "health_indicators", "risk_factors", "coverage", "appendix"]
            },
            "executive_summary": {
                "name": "Executive Summary",
                "sections": ["key_findings", "recommendations"]
            }
        }
    
    def propose_reports(self, data_type: str, variables: List[str], 
                       analysis_results: Dict) -> Dict:
        """Propose appropriate report templates based on data"""
        
        proposals = []
        
        # Always propose standard survey report
        proposals.append({
            "template": "standard_survey",
            "name": "Standard Survey Report",
            "description": "Comprehensive report with all statistics and visualizations",
            "sections": self.templates["standard_survey"]["sections"],
            "recommended": True
        })
        
        # Propose health survey if health-related variables detected
        health_keywords = ["health", "disease", "medical", "hospital", "vaccine", "bmi", "blood"]
        if any(keyword in str(variables).lower() for keyword in health_keywords):
            proposals.append({
                "template": "health_survey",
                "name": "Health Survey Report",
                "description": "Specialized report for health and demographic surveys",
                "sections": self.templates["health_survey"]["sections"],
                "recommended": True
            })
        
        # Always offer executive summary
        proposals.append({
            "template": "executive_summary",
            "name": "Executive Summary",
            "description": "Concise summary of key findings",
            "sections": self.templates["executive_summary"]["sections"],
            "recommended": False
        })
        
        return {
            "proposals": proposals,
            "default_template": "standard_survey",
            "customization_available": True
        }
    
    def generate_html_report(self, df: pd.DataFrame, document_id: str, 
                           workflow_id: str) -> str:
        """Generate HTML report"""
        
        # Calculate basic statistics
        stats = self._calculate_basic_stats(df)
        
        # Generate visualizations
        charts = self._generate_charts(df)
        
        # Build HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Survey Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #3498db; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .summary-box {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .chart {{ margin: 20px 0; text-align: center; }}
                .metadata {{ color: #7f8c8d; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <h1>Survey Data Analysis Report</h1>
            
            <div class="metadata">
                <p><strong>Document ID:</strong> {document_id}</p>
                <p><strong>Workflow ID:</strong> {workflow_id}</p>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary-box">
                <h2>Executive Summary</h2>
                <ul>
                    <li><strong>Total Records:</strong> {len(df):,}</li>
                    <li><strong>Total Variables:</strong> {len(df.columns)}</li>
                    <li><strong>Numeric Variables:</strong> {len(df.select_dtypes(include=[np.number]).columns)}</li>
                    <li><strong>Categorical Variables:</strong> {len(df.select_dtypes(include=['object']).columns)}</li>
                </ul>
            </div>
            
            <h2>Data Quality Summary</h2>
            <table>
                <tr>
                    <th>Variable</th>
                    <th>Type</th>
                    <th>Missing Count</th>
                    <th>Missing %</th>
                    <th>Unique Values</th>
                </tr>
        """
        
        # Add data quality rows
        for col in df.columns[:20]:  # First 20 columns
            missing_count = df[col].isnull().sum()
            missing_pct = (missing_count / len(df)) * 100
            unique_count = df[col].nunique()
            dtype = str(df[col].dtype)
            
            html += f"""
                <tr>
                    <td>{col}</td>
                    <td>{dtype}</td>
                    <td>{missing_count}</td>
                    <td>{missing_pct:.1f}%</td>
                    <td>{unique_count}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Descriptive Statistics</h2>
            <table>
                <tr>
                    <th>Variable</th>
                    <th>Mean</th>
                    <th>Std Dev</th>
                    <th>Min</th>
                    <th>25%</th>
                    <th>50%</th>
                    <th>75%</th>
                    <th>Max</th>
                </tr>
        """
        
        # Add statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:15]
        for col in numeric_cols:
            desc = df[col].describe()
            html += f"""
                <tr>
                    <td>{col}</td>
                    <td>{desc['mean']:.2f}</td>
                    <td>{desc['std']:.2f}</td>
                    <td>{desc['min']:.2f}</td>
                    <td>{desc['25%']:.2f}</td>
                    <td>{desc['50%']:.2f}</td>
                    <td>{desc['75%']:.2f}</td>
                    <td>{desc['max']:.2f}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Key Findings</h2>
            <div class="summary-box">
                <ul>
        """
        
        # Add key findings
        findings = self._generate_key_findings(df)
        for finding in findings:
            html += f"<li>{finding}</li>"
        
        html += """
                </ul>
            </div>
            
            <h2>Visualizations</h2>
        """
        
        # Add charts
        for chart in charts:
            html += f"""
            <div class="chart">
                <h3>{chart['title']}</h3>
                <img src="data:image/png;base64,{chart['data']}" style="max-width: 800px;">
            </div>
            """
        
        html += """
            <h2>Appendix</h2>
            <p>This report was automatically generated using the AI-Enhanced Data Preparation System (AIDEPS).</p>
            <p>For detailed analysis and raw data, please refer to the source files in the instance folder.</p>
        </body>
        </html>
        """
        
        return html
    
    def generate_excel_report(self, df: pd.DataFrame, output_path: str):
        """Generate Excel report with multiple sheets"""
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary Statistics
            summary_stats = df.describe()
            summary_stats.to_excel(writer, sheet_name='Summary Statistics')
            
            # Sheet 2: Data Quality
            quality_df = pd.DataFrame({
                'Column': df.columns,
                'Type': [str(df[col].dtype) for col in df.columns],
                'Missing Count': [df[col].isnull().sum() for col in df.columns],
                'Missing %': [(df[col].isnull().sum() / len(df)) * 100 for col in df.columns],
                'Unique Values': [df[col].nunique() for col in df.columns]
            })
            quality_df.to_excel(writer, sheet_name='Data Quality', index=False)
            
            # Sheet 3: Sample Data
            df.head(100).to_excel(writer, sheet_name='Sample Data', index=False)
            
            # Sheet 4: Correlations (if applicable)
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                corr_matrix = numeric_df.corr()
                corr_matrix.to_excel(writer, sheet_name='Correlations')
    
    def generate_summary_json(self, df: pd.DataFrame) -> str:
        """Generate JSON summary of the analysis"""
        
        summary = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_records": len(df),
                "total_columns": len(df.columns)
            },
            "data_types": {
                "numeric": df.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical": df.select_dtypes(include=['object']).columns.tolist()
            },
            "missing_data": {
                col: {
                    "count": int(df[col].isnull().sum()),
                    "percentage": round((df[col].isnull().sum() / len(df)) * 100, 2)
                }
                for col in df.columns
            },
            "basic_statistics": {}
        }
        
        # Add basic statistics for numeric columns
        for col in df.select_dtypes(include=[np.number]).columns:
            summary["basic_statistics"][col] = {
                "mean": round(df[col].mean(), 2),
                "std": round(df[col].std(), 2),
                "min": round(df[col].min(), 2),
                "max": round(df[col].max(), 2)
            }
        
        return json.dumps(summary, indent=2)
    
    def _calculate_basic_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate basic statistics for the report"""
        return {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
            "categorical_columns": len(df.select_dtypes(include=['object']).columns),
            "missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
    
    def _generate_charts(self, df: pd.DataFrame) -> List[Dict]:
        """Generate charts for the report"""
        charts = []
        
        # Only generate charts for small datasets to avoid memory issues
        if len(df) > 10000:
            df_sample = df.sample(n=10000)
        else:
            df_sample = df
        
        # Chart 1: Missing data heatmap
        try:
            plt.figure(figsize=(10, 6))
            missing_data = df_sample.isnull().sum()
            missing_data = missing_data[missing_data > 0][:20]  # Top 20 columns with missing data
            
            if len(missing_data) > 0:
                missing_data.plot(kind='bar')
                plt.title('Missing Data by Column')
                plt.xlabel('Column')
                plt.ylabel('Missing Count')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                chart_data = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                charts.append({
                    "title": "Missing Data Analysis",
                    "data": chart_data
                })
        except Exception as e:
            print(f"Error generating missing data chart: {e}")
        
        # Chart 2: Distribution of a numeric variable
        try:
            numeric_cols = df_sample.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                plt.figure(figsize=(10, 6))
                df_sample[numeric_cols[0]].hist(bins=30)
                plt.title(f'Distribution of {numeric_cols[0]}')
                plt.xlabel(numeric_cols[0])
                plt.ylabel('Frequency')
                plt.tight_layout()
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                chart_data = base64.b64encode(buffer.read()).decode()
                plt.close()
                
                charts.append({
                    "title": f"Distribution of {numeric_cols[0]}",
                    "data": chart_data
                })
        except Exception as e:
            print(f"Error generating distribution chart: {e}")
        
        return charts
    
    def _generate_key_findings(self, df: pd.DataFrame) -> List[str]:
        """Generate key findings from the data"""
        findings = []
        
        # Finding 1: Data completeness
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        findings.append(f"Overall data completeness: {100 - missing_pct:.1f}%")
        
        # Finding 2: Most complete variables
        complete_cols = df.columns[df.isnull().sum() == 0].tolist()[:5]
        if complete_cols:
            findings.append(f"Completely filled variables: {', '.join(complete_cols)}")
        
        # Finding 3: Numeric variable ranges
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            findings.append(
                f"{col} ranges from {df[col].min():.2f} to {df[col].max():.2f} "
                f"with mean {df[col].mean():.2f}"
            )
        
        # Finding 4: Categorical distribution
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            col = cat_cols[0]
            mode_value = df[col].mode()[0] if not df[col].mode().empty else "N/A"
            findings.append(f"Most common value in {col}: {mode_value}")
        
        return findings
    
    def get_available_templates(self) -> List[Dict]:
        """Get list of available report templates"""
        return [
            {
                "id": key,
                "name": value["name"],
                "sections": value["sections"]
            }
            for key, value in self.templates.items()
        ]