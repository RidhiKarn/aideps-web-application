# AIDEPS Frontend - World-Class Data Preparation Interface

## Overview
A modern, responsive React application for the AI-Enhanced Data Preparation System (AIDEPS), designed specifically for MoSPI's survey data processing needs.

## Key Features

### 🎯 7-Stage Workflow Pipeline
1. **Raw Data Upload** - Drag & drop with instant preview
2. **Data Cleansing** - AI-powered cleaning suggestions
3. **Analysis & Discovery** - Pattern detection and insights
4. **Statistics & Weights** - Weighted calculations
5. **Propose Reports** - AI-suggested templates
6. **User Confirmation** - Review and approve
7. **Final Report Generation** - Multi-format exports

### 🎨 World-Class UI/UX
- **Material Design 3** - Modern, clean interface
- **Dark/Light Mode** - User preference support
- **Responsive Design** - Works on all devices
- **Real-time Updates** - Live progress tracking
- **Interactive Visualizations** - D3.js and Recharts
- **Drag & Drop** - Intuitive file handling
- **Smart Defaults** - AI-powered suggestions

### 📊 Data Visualization
- Interactive charts and graphs
- Missing data heatmaps
- Distribution plots
- Correlation matrices
- Quality score dashboards
- Before/after comparisons

### 🔧 Technical Stack
- **React 18** with TypeScript
- **Material-UI v5** for components
- **D3.js** for custom visualizations
- **Recharts** for standard charts
- **AG-Grid** for data tables
- **React Query** for data fetching
- **Zustand** for state management
- **Framer Motion** for animations

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Layout/          # App layout and navigation
│   │   ├── WorkflowPipeline/ # Main workflow visualization
│   │   └── stages/          # Stage-specific components
│   │       ├── Stage1Upload/
│   │       ├── Stage2Cleansing/
│   │       ├── Stage3Analysis/
│   │       ├── Stage4Statistics/
│   │       ├── Stage5Reports/
│   │       ├── Stage6Confirmation/
│   │       └── Stage7Generation/
│   ├── pages/               # Route pages
│   ├── services/            # API services
│   ├── store/               # State management
│   ├── hooks/               # Custom hooks
│   ├── utils/               # Utility functions
│   └── types/               # TypeScript types
└── public/                  # Static assets
```

## User Decisions by Stage

### Stage 1: Upload
- **Required**: File selection
- **Optional**: Document name, organization, survey type
- **Defaults**: Auto-detect encoding, format, delimiters

### Stage 2: Cleansing
- **Required**: Approve/modify cleaning strategies
- **Optional**: Custom imputation values, outlier thresholds
- **Defaults**: AI-suggested imputation methods

### Stage 3: Analysis
- **Required**: Select key variables
- **Optional**: Analysis depth, custom requests
- **Defaults**: Auto-identify variable types

### Stage 4: Statistics
- **Required**: Weight variable selection
- **Optional**: Confidence levels, stratification
- **Defaults**: 95% confidence, all numeric variables

### Stage 5: Reports
- **Required**: Template selection
- **Optional**: Section customization, branding
- **Defaults**: Standard survey report template

### Stage 6: Confirmation
- **Required**: Final approval
- **Optional**: Last-minute adjustments
- **Defaults**: All content pre-approved

### Stage 7: Generation
- **Required**: None (automatic)
- **Optional**: Distribution settings
- **Defaults**: Generate immediately

## Key Components

### WorkflowPipeline
Visual representation of the 7-stage workflow with:
- Progress tracking
- Stage navigation
- Real-time status updates
- Performance metrics

### DataGrid Integration
- AG-Grid for large datasets
- Virtual scrolling
- Column filtering and sorting
- Export capabilities

### Visualization Suite
- Chart.js for standard charts
- D3.js for custom visualizations
- Recharts for responsive charts
- Real-time data updates

## Development Guidelines

### Code Style
- TypeScript strict mode
- Functional components with hooks
- Atomic design principles
- CSS-in-JS with Emotion

### Performance
- Lazy loading for routes
- Code splitting
- Memoization for expensive operations
- Virtual scrolling for large datasets

### Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- High contrast mode

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`

### Key Endpoints
- `POST /api/documents/upload` - Upload survey data
- `GET /api/workflows/{id}/status` - Get workflow status
- `POST /api/stages/{stage}/process` - Process stage
- `GET /api/reports/{id}/download` - Download reports

## Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_VERSION=1.0.0
REACT_APP_ENVIRONMENT=development
```

## Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## Deployment

```bash
# Build for production
npm run build

# Serve production build
npx serve -s build
```

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License
MIT

## Support
For issues and questions, contact the AIDEPS team.