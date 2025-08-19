import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Badge,
} from '@mui/material';
import {
  Analytics,
  TrendingUp,
  Insights,
  Category,
  Numbers,
  TextFields,
  CalendarMonth,
  LocationOn,
  ExpandMore,
  CheckCircle,
  Warning,
  Info,
  AutoAwesome,
  Timeline,
  BubbleChart,
  ScatterPlot,
  ShowChart,
  PieChart as PieChartIcon,
  BarChart as BarChartIcon,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import toast from 'react-hot-toast';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

interface VariableAnalysis {
  name: string;
  type: 'numeric' | 'categorical' | 'datetime' | 'text';
  uniqueValues: number;
  distribution: string;
  importance: number;
  correlations: { variable: string; value: number }[];
  statistics?: {
    mean?: number;
    median?: number;
    std?: number;
    min?: number;
    max?: number;
  };
}

interface Stage3AnalysisProps {
  documentId?: string;
  data?: any;
  onChange?: (data: any) => void;
}

export const Stage3Analysis: React.FC<Stage3AnalysisProps> = ({ documentId, data, onChange }) => {
  const [tabValue, setTabValue] = useState(0);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [selectedVariable, setSelectedVariable] = useState('');
  const [variables, setVariables] = useState<VariableAnalysis[]>([]);
  const [correlationMatrix, setCorrelationMatrix] = useState<any[]>([]);
  const [patterns, setPatterns] = useState<any[]>([]);

  useEffect(() => {
    loadInitialAnalysis();
  }, []);

  const loadInitialAnalysis = async () => {
    // Simulate loading analysis
    setVariables([
      {
        name: 'TOTINCM',
        type: 'numeric',
        uniqueValues: 1523,
        distribution: 'right-skewed',
        importance: 0.92,
        correlations: [
          { variable: 'POPU_LSA', value: 0.78 },
          { variable: 'CENTLIB', value: 0.65 },
        ],
        statistics: {
          mean: 45678,
          median: 42000,
          std: 12345,
          min: 10000,
          max: 150000,
        },
      },
      {
        name: 'POPU_LSA',
        type: 'numeric',
        uniqueValues: 892,
        distribution: 'normal',
        importance: 0.86,
        correlations: [
          { variable: 'TOTINCM', value: 0.78 },
          { variable: 'STATNAME', value: 0.52 },
        ],
        statistics: {
          mean: 25000,
          median: 24500,
          std: 8900,
          min: 1000,
          max: 100000,
        },
      },
      {
        name: 'STATNAME',
        type: 'categorical',
        uniqueValues: 28,
        distribution: 'uniform',
        importance: 0.73,
        correlations: [],
      },
    ]);

    setPatterns([
      {
        type: 'Seasonal Pattern',
        description: 'Income shows quarterly variations with peaks in Q4',
        confidence: 0.89,
        affected: ['TOTINCM', 'EXPENDITURE'],
      },
      {
        type: 'Geographic Clustering',
        description: 'Rural areas show similar income distribution patterns',
        confidence: 0.92,
        affected: ['STATNAME', 'DISTRICT', 'TOTINCM'],
      },
      {
        type: 'Outlier Group',
        description: 'High-income outliers concentrated in urban centers',
        confidence: 0.85,
        affected: ['TOTINCM', 'URBAN_RURAL'],
      },
    ]);
  };

  const handleRunAnalysis = async () => {
    setProcessing(true);
    
    // Simulate analysis
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setAnalysisComplete(true);
    setProcessing(false);
    toast.success('Deep analysis completed successfully!');
  };

  const distributionData = [
    { range: '0-20k', count: 1234 },
    { range: '20-40k', count: 2456 },
    { range: '40-60k', count: 3234 },
    { range: '60-80k', count: 1678 },
    { range: '80-100k', count: 892 },
    { range: '100k+', count: 456 },
  ];

  const typeDistribution = [
    { name: 'Numeric', value: 45, fill: COLORS[0] },
    { name: 'Categorical', value: 30, fill: COLORS[1] },
    { name: 'DateTime', value: 15, fill: COLORS[2] },
    { name: 'Text', value: 10, fill: COLORS[3] },
  ];

  const correlationData = [
    { x: 10, y: 20, z: 40 },
    { x: 20, y: 35, z: 60 },
    { x: 30, y: 45, z: 80 },
    { x: 40, y: 58, z: 100 },
    { x: 50, y: 65, z: 120 },
    { x: 60, y: 72, z: 140 },
  ];

  const radarData = [
    { subject: 'Completeness', A: 95, B: 90, fullMark: 100 },
    { subject: 'Validity', A: 92, B: 85, fullMark: 100 },
    { subject: 'Consistency', A: 88, B: 82, fullMark: 100 },
    { subject: 'Uniqueness', A: 85, B: 80, fullMark: 100 },
    { subject: 'Timeliness', A: 90, B: 88, fullMark: 100 },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Stage 3: Deep Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Comprehensive data analysis with AI-powered insights
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<AutoAwesome />}
            onClick={handleRunAnalysis}
            disabled={processing}
          >
            {processing ? 'Analyzing...' : 'Run Deep Analysis'}
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Analytics sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Variables Analyzed
                </Typography>
              </Box>
              <Typography variant="h3">164</Typography>
              <Typography variant="caption" color="success.main">
                All variables processed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Insights sx={{ color: 'warning.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Patterns Found
                </Typography>
              </Box>
              <Typography variant="h3">12</Typography>
              <Typography variant="caption">
                3 high confidence
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Key Correlations
                </Typography>
              </Box>
              <Typography variant="h3">28</Typography>
              <Typography variant="caption">
                Above 0.7 threshold
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <BubbleChart sx={{ color: 'info.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Data Quality
                </Typography>
              </Box>
              <Typography variant="h3">94%</Typography>
              <LinearProgress
                variant="determinate"
                value={94}
                sx={{ mt: 1, height: 6, borderRadius: 3 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
              <Tab label="Variable Analysis" />
              <Tab label="Correlations" />
              <Tab label="Patterns" />
              <Tab label="Distributions" />
            </Tabs>

            {tabValue === 0 && (
              <Box>
                <Alert severity="info" sx={{ mb: 3 }}>
                  AI has automatically categorized and analyzed all 164 variables
                </Alert>
                
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Variable</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Distribution</TableCell>
                        <TableCell>Importance</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {variables.map((variable) => (
                        <TableRow key={variable.name}>
                          <TableCell>
                            <Typography variant="subtitle2">{variable.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {variable.uniqueValues} unique values
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              size="small"
                              icon={
                                variable.type === 'numeric' ? <Numbers /> :
                                variable.type === 'categorical' ? <Category /> :
                                variable.type === 'datetime' ? <CalendarMonth /> :
                                <TextFields />
                              }
                              label={variable.type}
                              color={variable.type === 'numeric' ? 'primary' : 'default'}
                            />
                          </TableCell>
                          <TableCell>{variable.distribution}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <LinearProgress
                                variant="determinate"
                                value={variable.importance * 100}
                                sx={{ width: 60, mr: 1 }}
                              />
                              <Typography variant="caption">
                                {(variable.importance * 100).toFixed(0)}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Button size="small">Details</Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}

            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Discovered Patterns
                </Typography>
                {patterns.map((pattern, idx) => (
                  <Accordion key={idx}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle1">{pattern.type}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {pattern.description}
                          </Typography>
                        </Box>
                        <Chip
                          label={`${(pattern.confidence * 100).toFixed(0)}% confidence`}
                          color={pattern.confidence > 0.9 ? 'success' : 'warning'}
                          size="small"
                        />
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box>
                        <Typography variant="subtitle2" gutterBottom>
                          Affected Variables:
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                          {pattern.affected.map((var_name: string) => (
                            <Chip key={var_name} label={var_name} size="small" />
                          ))}
                        </Box>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            )}

            {tabValue === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Income Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={distributionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="range" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Side Visualizations */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Variable Types
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={typeDistribution}
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  dataKey="value"
                >
                  {typeDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>

          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Data Quality Radar
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar
                  name="Current"
                  dataKey="A"
                  stroke="#8884d8"
                  fill="#8884d8"
                  fillOpacity={0.6}
                />
                <Radar
                  name="Baseline"
                  dataKey="B"
                  stroke="#82ca9d"
                  fill="#82ca9d"
                  fillOpacity={0.6}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Button variant="outlined" size="large">
          Back to Cleansing
        </Button>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" size="large">
            Export Analysis
          </Button>
          <Button
            variant="contained"
            size="large"
            disabled={!analysisComplete}
          >
            Proceed to Statistics
          </Button>
        </Box>
      </Box>
    </Box>
  );
};