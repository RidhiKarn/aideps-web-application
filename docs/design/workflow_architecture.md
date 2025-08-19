# AI-Enhanced Data Preparation System - Workflow Architecture

## System Overview

The system implements a **document-centric workflow** where each survey dataset (document instance) progresses through defined stages with user review and confirmation at each step.

## Core Workflow Stages

### Workflow Pipeline
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  1. Upload   │────▶│ 2. Cleansing │────▶│ 3. Analysis  │────▶│4. Statistics │
│  Raw Data    │     │   & Prep     │     │ & Discovery  │     │  & Weights   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                         │
                                                                         ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ 7. Generate  │◀────│6. Confirmation│◀────│  5. Propose  │◀────┘
│Final Report  │     │   & Review   │     │   Reports    │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Detailed Workflow Stages

### Stage 1: Raw Data Upload
**Purpose**: Ingest and validate survey data files

**Automated Actions**:
- File format detection (CSV, Excel)
- Initial validation (file integrity, size limits)
- Schema inference
- Data profiling (rows, columns, data types)
- Create document instance in database

**User Review Points**:
- Confirm detected schema
- Map column names to standard fields
- Set data types if incorrectly inferred
- Define primary keys/identifiers

**Output**: Validated raw dataset with metadata

---

### Stage 2: Data Cleansing
**Purpose**: Clean and prepare data for analysis

**Automated Actions**:
- **Missing Data Detection**:
  - Identify missing patterns (MCAR, MAR, MNAR)
  - Calculate missing percentages per column
  - Suggest imputation strategies

- **Outlier Detection**:
  - Statistical methods (IQR, Z-score)
  - Domain-specific rules
  - Visual outlier identification

- **Data Validation**:
  - Consistency checks
  - Range validations
  - Pattern matching
  - Skip-logic validation

**User Review Points**:
- Select imputation method per column:
  - Mean/Median/Mode
  - Forward/Backward fill
  - KNN imputation
  - Multiple imputation
  - Custom value
- Review and confirm outliers
- Approve/modify validation rules
- Accept/reject suggested corrections

**Output**: Cleaned dataset with transformation log

---

### Stage 3: Analysis & Discovery
**Purpose**: Identify key characteristics and patterns

**Automated Actions**:
- Variable categorization (numerical, categorical, ordinal)
- Distribution analysis
- Correlation detection
- Key variable identification
- Pattern discovery
- Demographic profiling

**User Review Points**:
- Confirm variable categories
- Select variables of interest
- Define analysis groups
- Set stratification variables
- Approve discovered patterns

**Output**: Analysis summary with key findings

---

### Stage 4: Statistics & Weights
**Purpose**: Calculate population estimates with design weights

**Automated Actions**:
- Apply survey weights
- Calculate weighted estimates
- Compute standard errors
- Generate confidence intervals
- Perform significance tests
- Create cross-tabulations

**User Review Points**:
- Confirm weight variables
- Select estimation methods
- Define subpopulations
- Choose statistical tests
- Review preliminary results

**Output**: Statistical summaries with weighted estimates

---

### Stage 5: Propose Reports
**Purpose**: Generate report templates based on analysis

**Automated Actions**:
- Select appropriate templates
- Generate visualizations
- Create summary tables
- Prepare narrative insights
- Format according to standards

**User Review Points**:
- Choose report sections
- Select visualizations
- Customize templates
- Add interpretations
- Define export formats

**Output**: Draft reports in multiple formats

---

### Stage 6: User Confirmation
**Purpose**: Final review before report generation

**User Actions**:
- Review complete workflow
- Verify all transformations
- Check statistical accuracy
- Approve report content
- Sign-off on results

**Output**: Approved report specification

---

### Stage 7: Final Report Generation
**Purpose**: Generate official reports

**Automated Actions**:
- Generate final PDF/HTML reports
- Create metadata documentation
- Archive workflow history
- Generate audit trail

**Output**: Final reports with complete documentation

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Workflow  │ │ Stage    │ │Progress  │ │ Report   │  │
│  │Navigator │ │ Views    │ │Tracker   │ │ Viewer   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   API Gateway (FastAPI)                  │
├──────────────────────────────────────────────────────────┤
│                   Workflow Engine                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │  Stage   │ │Transition│ │  State   │ │  Audit   │  │
│  │ Manager  │ │  Logic   │ │  Store   │ │  Logger  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
├──────────────────────────────────────────────────────────┤
│                  Processing Services                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Upload   │ │Cleansing │ │Analysis  │ │Statistics│  │
│  │ Service  │ │ Service  │ │ Service  │ │ Service  │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │ Report   │ │Validation│ │  Export  │               │
│  │ Service  │ │ Service  │ │ Service  │               │
│  └──────────┘ └──────────┘ └──────────┘               │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                 Data Layer (ClickHouse)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Documents │ │Workflows │ │  Stages  │ │  Audit   │  │
│  │          │ │          │ │          │ │   Log    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Database Design (ClickHouse)

### Core Tables Structure

```sql
-- Document instances (survey datasets)
documents (
    document_id UUID,
    document_name String,
    upload_date DateTime,
    file_path String,
    file_size UInt64,
    file_type String,
    user_id String,
    organization String,
    survey_type String,
    status String,
    metadata JSON
)

-- Workflow instances
workflows (
    workflow_id UUID,
    document_id UUID,
    current_stage UInt8,
    status String,
    started_at DateTime,
    completed_at Nullable(DateTime),
    created_by String,
    metadata JSON
)

-- Stage execution history
workflow_stages (
    stage_id UUID,
    workflow_id UUID,
    document_id UUID,
    stage_number UInt8,
    stage_name String,
    status String,
    started_at DateTime,
    completed_at Nullable(DateTime),
    input_data JSON,
    output_data JSON,
    user_actions JSON,
    automated_actions JSON,
    error_log Nullable(String)
)

-- Data snapshots at each stage
data_snapshots (
    snapshot_id UUID,
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    data_version String,
    row_count UInt64,
    column_count UInt16,
    snapshot_path String,
    checksum String,
    created_at DateTime
)

-- Audit trail
audit_log (
    audit_id UUID,
    document_id UUID,
    workflow_id UUID,
    stage_number UInt8,
    action_type String,
    action_details JSON,
    user_id String,
    timestamp DateTime,
    ip_address String
)

-- Processing configurations
stage_configs (
    config_id UUID,
    document_id UUID,
    stage_number UInt8,
    config_type String,
    config_data JSON,
    created_at DateTime,
    updated_at DateTime
)

-- Generated reports
reports (
    report_id UUID,
    document_id UUID,
    workflow_id UUID,
    report_type String,
    report_format String,
    file_path String,
    generated_at DateTime,
    metadata JSON
)
```

## Workflow State Management

### Stage States
```python
class StageStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_REVIEW = "awaiting_review"
    REVIEWED = "reviewed"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
```

### Workflow Navigation Rules
1. **Forward Progression**: Can only move to next stage after current stage is completed
2. **Backward Navigation**: Can revisit any completed stage
3. **Stage Modification**: Modifying a previous stage invalidates all subsequent stages
4. **Parallel Processing**: Some sub-tasks within a stage can run in parallel
5. **Checkpoint System**: Each stage completion creates a data checkpoint

## UI/UX Design

### Main Dashboard
```
┌────────────────────────────────────────────────────────────┐
│  Document: NFHS-5_Survey_2024.csv         Status: Stage 3  │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Progress Timeline:                                        │
│  ┌────┬────┬────┬────┬────┬────┬────┐                   │
│  │ ✓  │ ✓  │ ▶  │    │    │    │    │                   │
│  └────┴────┴────┴────┴────┴────┴────┘                   │
│   Upload Clean Analyze Stats Report Review Generate       │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Current Stage: Data Analysis & Discovery                  │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  Automated Analysis Complete                        │ │
│  │                                                     │ │
│  │  • 15 variables identified                         │ │
│  │  • 3 key demographic variables found               │ │
│  │  • 2 correlation patterns detected                 │ │
│  │                                                     │ │
│  │  [Review Variables] [View Patterns] [Modify]       │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                            │
│  [← Previous Stage]  [Save Progress]  [Continue →]        │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Stage Navigation Features
1. **Visual Progress Bar**: Shows completed, current, and pending stages
2. **Stage Cards**: Click to navigate to any accessible stage
3. **Status Indicators**:
   - ✓ Completed
   - ▶ Current/Active
   - ⏸ Awaiting Review
   - ○ Pending
   - ⚠ Has Issues
4. **Quick Actions**: Available at each stage for common tasks
5. **History View**: See all actions taken at each stage

## API Design

### Workflow Management Endpoints
```python
# Document management
POST   /api/documents/upload
GET    /api/documents/{document_id}
GET    /api/documents/list

# Workflow operations
POST   /api/workflows/create
GET    /api/workflows/{workflow_id}/status
POST   /api/workflows/{workflow_id}/stages/{stage_number}/start
POST   /api/workflows/{workflow_id}/stages/{stage_number}/complete
GET    /api/workflows/{workflow_id}/stages/{stage_number}/data
POST   /api/workflows/{workflow_id}/stages/{stage_number}/review
POST   /api/workflows/{workflow_id}/navigate/{stage_number}

# Stage-specific operations
POST   /api/stages/cleansing/impute
POST   /api/stages/cleansing/outliers
POST   /api/stages/analysis/variables
POST   /api/stages/statistics/weights
POST   /api/stages/reports/generate

# Progress tracking
GET    /api/workflows/{workflow_id}/progress
GET    /api/workflows/{workflow_id}/history
GET    /api/workflows/{workflow_id}/audit
```

## Real-time Updates

### WebSocket Events
```javascript
// Client subscribes to workflow updates
ws.subscribe(`workflow.${workflowId}`)

// Server sends stage updates
{
  "event": "stage.completed",
  "data": {
    "workflow_id": "...",
    "stage_number": 2,
    "next_stage": 3
  }
}

// Progress updates
{
  "event": "processing.progress",
  "data": {
    "stage": 2,
    "task": "imputation",
    "progress": 75
  }
}
```

## NFHS-5 Example Implementation

### Sample Data Structure
```python
# NFHS-5 typical variables
{
    "household_id": "String",
    "state_code": "Integer",
    "district_code": "Integer",
    "urban_rural": "Category",
    "wealth_index": "Ordinal",
    "education_level": "Ordinal",
    "age": "Numeric",
    "gender": "Binary",
    "weight_variable": "Numeric",
    # ... health indicators
}
```

### Workflow Configuration for NFHS-5
```yaml
nfhs5_workflow:
  stage_1_upload:
    validations:
      - required_columns: ["household_id", "state_code", "weight_variable"]
      - file_format: ["csv", "dta", "sav"]
  
  stage_2_cleansing:
    missing_data:
      age: "median"
      education_level: "mode"
      wealth_index: "forward_fill"
    outliers:
      age: 
        method: "range"
        min: 0
        max: 120
  
  stage_3_analysis:
    key_variables: ["age", "education_level", "wealth_index"]
    stratification: ["state_code", "urban_rural"]
  
  stage_4_statistics:
    weights: "weight_variable"
    estimates:
      - "prevalence"
      - "means"
      - "proportions"
  
  stage_5_reports:
    templates: ["nfhs_standard", "state_factsheet"]
    formats: ["pdf", "html", "excel"]
```

## Implementation Notes

1. **State Persistence**: All stage states are persisted in ClickHouse for recovery
2. **Idempotency**: All operations are idempotent to handle retries
3. **Versioning**: Each data modification creates a new version
4. **Rollback**: Users can revert to any previous stage state
5. **Caching**: Intermediate results are cached for performance
6. **Async Processing**: Heavy computations run asynchronously with progress tracking
7. **Validation**: Each stage has entry and exit validations
8. **Audit Trail**: Every user action and system operation is logged