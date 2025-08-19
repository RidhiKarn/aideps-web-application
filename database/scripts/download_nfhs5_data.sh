#!/bin/bash

# Download NFHS-5 Sample Data
# National Family Health Survey (NFHS-5) 2019-21 India

echo "========================================="
echo "NFHS-5 Sample Data Download"
echo "========================================="

# Create data directory
DATA_DIR="../seed_data/nfhs5"
mkdir -p ${DATA_DIR}

echo "Creating sample NFHS-5 data structure..."

# Since actual NFHS-5 data requires registration and is large,
# we'll create a representative sample dataset with similar structure

# Create sample NFHS-5 CSV with typical survey variables
cat > ${DATA_DIR}/nfhs5_sample_data.csv << 'EOF'
household_id,state_code,district_code,urban_rural,cluster_number,wealth_index,household_size,respondent_age,respondent_gender,education_level,marital_status,children_ever_born,children_surviving,contraceptive_use,anemia_level,bmi,blood_pressure_systolic,blood_pressure_diastolic,diabetes_tested,hiv_tested,insurance_coverage,toilet_facility,drinking_water_source,electricity,survey_weight,state_name,district_name
HH001,28,1,1,101,3,4,28,F,3,1,2,2,1,2,22.5,120,80,1,0,1,1,1,1,1.234,Andhra Pradesh,Anantapur
HH002,28,1,2,102,2,5,35,F,2,1,3,3,0,1,24.1,118,78,0,0,0,2,2,1,1.156,Andhra Pradesh,Anantapur
HH003,28,2,1,103,4,3,42,F,4,1,1,1,1,0,23.8,125,82,1,1,1,1,1,1,1.345,Andhra Pradesh,Chittoor
HH004,28,2,2,104,1,6,25,F,1,1,4,3,0,3,19.2,115,75,0,0,0,3,3,0,1.089,Andhra Pradesh,Chittoor
HH005,36,3,1,201,5,4,30,F,5,1,0,0,1,1,25.6,122,81,1,1,1,1,1,1,1.456,Telangana,Adilabad
HH006,36,3,2,202,3,5,38,F,3,1,2,2,1,2,26.3,130,85,0,0,1,2,1,1,1.234,Telangana,Adilabad
HH007,36,4,1,203,2,7,45,F,2,1,5,4,0,0,28.1,135,88,1,0,0,1,2,1,1.123,Telangana,Hyderabad
HH008,19,5,1,301,4,3,33,F,4,1,1,1,1,1,21.9,118,76,0,1,1,1,1,1,1.567,Karnataka,Bagalkot
HH009,19,5,2,302,1,8,29,F,1,1,3,2,0,2,20.5,116,74,0,0,0,3,3,0,1.098,Karnataka,Bagalkot
HH010,19,6,1,303,5,4,31,F,5,0,0,0,NA,0,24.7,121,79,1,1,1,1,1,1,1.432,Karnataka,Bangalore Urban
HH011,27,7,1,401,3,5,27,F,3,1,2,2,1,1,23.2,119,77,0,0,1,2,2,1,1.321,Maharashtra,Ahmednagar
HH012,27,7,2,402,2,6,36,F,2,1,4,3,0,3,27.5,128,84,1,0,0,3,2,1,1.211,Maharashtra,Ahmednagar
HH013,27,8,1,403,4,4,40,F,4,1,1,1,1,0,22.8,124,80,1,1,1,1,1,1,1.478,Maharashtra,Mumbai
HH014,33,9,1,501,5,3,34,F,5,1,0,0,1,1,25.1,120,78,0,1,1,1,1,1,1.556,Tamil Nadu,Chennai
HH015,33,9,2,502,1,7,26,F,1,1,3,3,0,2,18.9,114,72,0,0,0,3,3,0,1.067,Tamil Nadu,Chennai
HH016,33,10,1,503,3,5,32,F,3,1,2,2,1,0,24.3,122,81,1,0,1,2,1,1,1.289,Tamil Nadu,Coimbatore
HH017,09,11,2,601,2,6,37,F,2,1,4,4,0,1,26.8,132,86,0,0,0,2,2,1,1.145,Uttar Pradesh,Agra
HH018,09,11,1,602,4,4,41,F,4,1,1,1,1,0,23.5,126,82,1,1,1,1,1,1,1.398,Uttar Pradesh,Agra
HH019,09,12,2,603,1,8,24,F,1,1,5,4,0,3,19.8,112,70,0,0,0,3,3,0,1.023,Uttar Pradesh,Allahabad
HH020,09,12,1,604,5,3,30,F,5,1,0,0,1,1,24.9,121,79,1,1,1,1,1,1,1.512,Uttar Pradesh,Allahabad
HH021,10,13,1,701,3,5,35,F,3,1,2,2,1,2,25.7,123,80,0,0,1,2,2,1,1.267,Bihar,Araria
HH022,10,13,2,702,2,6,28,F,2,1,3,2,0,1,21.3,117,75,0,0,0,3,2,1,1.178,Bihar,Araria
HH023,10,14,1,703,4,4,39,F,4,1,1,1,1,0,23.9,125,81,1,1,1,1,1,1,1.423,Bihar,Patna
HH024,22,15,2,801,1,7,25,F,1,1,4,3,0,3,20.1,113,71,0,0,0,3,3,0,1.089,Chhattisgarh,Bastar
HH025,22,15,1,802,5,3,31,F,5,0,0,0,NA,1,25.3,122,80,1,1,1,1,1,1,1.489,Chhattisgarh,Bastar
EOF

echo "Sample NFHS-5 data created at: ${DATA_DIR}/nfhs5_sample_data.csv"

# Create data dictionary
cat > ${DATA_DIR}/nfhs5_data_dictionary.json << 'EOF'
{
  "variables": {
    "household_id": {
      "type": "identifier",
      "description": "Unique household identifier"
    },
    "state_code": {
      "type": "categorical",
      "description": "State code as per Census"
    },
    "district_code": {
      "type": "categorical",
      "description": "District code within state"
    },
    "urban_rural": {
      "type": "binary",
      "description": "1=Urban, 2=Rural",
      "values": {"1": "Urban", "2": "Rural"}
    },
    "wealth_index": {
      "type": "ordinal",
      "description": "Wealth quintile (1=Poorest to 5=Richest)",
      "values": {"1": "Poorest", "2": "Poorer", "3": "Middle", "4": "Richer", "5": "Richest"}
    },
    "respondent_age": {
      "type": "numeric",
      "description": "Age of respondent in years",
      "range": [15, 49]
    },
    "respondent_gender": {
      "type": "categorical",
      "description": "Gender of respondent",
      "values": {"M": "Male", "F": "Female"}
    },
    "education_level": {
      "type": "ordinal",
      "description": "Highest education level",
      "values": {
        "0": "No education",
        "1": "Primary",
        "2": "Secondary",
        "3": "Higher secondary",
        "4": "Graduate",
        "5": "Post-graduate"
      }
    },
    "anemia_level": {
      "type": "ordinal",
      "description": "Anemia severity",
      "values": {
        "0": "Not anemic",
        "1": "Mild",
        "2": "Moderate",
        "3": "Severe"
      }
    },
    "survey_weight": {
      "type": "weight",
      "description": "Survey sampling weight for population estimates"
    }
  },
  "missing_codes": {
    "NA": "Not applicable",
    "DK": "Don't know",
    "NR": "No response"
  }
}
EOF

echo "Data dictionary created at: ${DATA_DIR}/nfhs5_data_dictionary.json"

# Create validation rules for NFHS-5 data
cat > ${DATA_DIR}/nfhs5_validation_rules.json << 'EOF'
{
  "rules": [
    {
      "name": "age_range",
      "column": "respondent_age",
      "type": "range",
      "min": 15,
      "max": 49,
      "severity": "error"
    },
    {
      "name": "wealth_index_values",
      "column": "wealth_index",
      "type": "values",
      "allowed": [1, 2, 3, 4, 5],
      "severity": "error"
    },
    {
      "name": "urban_rural_values",
      "column": "urban_rural",
      "type": "values",
      "allowed": [1, 2],
      "severity": "error"
    },
    {
      "name": "bmi_range",
      "column": "bmi",
      "type": "range",
      "min": 12,
      "max": 50,
      "severity": "warning"
    },
    {
      "name": "children_consistency",
      "type": "consistency",
      "condition": "children_surviving <= children_ever_born",
      "severity": "error"
    },
    {
      "name": "weight_positive",
      "column": "survey_weight",
      "type": "range",
      "min": 0,
      "severity": "error"
    }
  ]
}
EOF

echo "Validation rules created at: ${DATA_DIR}/nfhs5_validation_rules.json"

# Create report template configuration
cat > ${DATA_DIR}/nfhs5_report_template.json << 'EOF'
{
  "template_name": "NFHS-5 Standard Report",
  "sections": [
    {
      "title": "Executive Summary",
      "type": "summary",
      "content": ["key_indicators", "sample_characteristics"]
    },
    {
      "title": "Demographic Profile",
      "type": "descriptive",
      "variables": ["age", "education_level", "wealth_index"],
      "stratify_by": ["urban_rural", "state"]
    },
    {
      "title": "Health Indicators",
      "type": "analysis",
      "indicators": [
        {
          "name": "Anemia Prevalence",
          "variable": "anemia_level",
          "calculation": "proportion",
          "subgroups": ["urban_rural", "wealth_index"]
        },
        {
          "name": "BMI Distribution",
          "variable": "bmi",
          "calculation": "mean",
          "subgroups": ["age_group", "education_level"]
        }
      ]
    },
    {
      "title": "Coverage Indicators",
      "type": "weighted_estimates",
      "variables": ["insurance_coverage", "contraceptive_use"],
      "apply_weights": true
    }
  ],
  "output_formats": ["pdf", "html", "excel"]
}
EOF

echo "Report template created at: ${DATA_DIR}/nfhs5_report_template.json"

echo ""
echo "========================================="
echo "NFHS-5 sample data preparation complete!"
echo "========================================="
echo ""
echo "Files created:"
echo "  - ${DATA_DIR}/nfhs5_sample_data.csv (25 sample records)"
echo "  - ${DATA_DIR}/nfhs5_data_dictionary.json"
echo "  - ${DATA_DIR}/nfhs5_validation_rules.json"
echo "  - ${DATA_DIR}/nfhs5_report_template.json"
echo ""
echo "This sample data represents the structure of actual NFHS-5 survey"
echo "with key demographic and health indicators."