import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Badge,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import {
  CleaningServices,
  Warning,
  CheckCircle,
  Error,
  Info,
  ExpandMore,
  AutoFixHigh,
  Timeline,
  BubbleChart,
  Speed,
  Undo,
  Redo,
  Save,
  PlayArrow,
  Visibility,
  CompareArrows,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';
import toast from 'react-hot-toast';

interface ColumnIssue {
  column: string;
  type: string;
  missingCount: number;
  missingPercent: number;
  outlierCount: number;
  suggestedAction: string;
  priority: 'high' | 'medium' | 'low';
}

interface CleaningAction {
  column: string;
  action: string;
  timestamp: Date;
  affectedRows: number;
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

interface Stage2CleansingProps {
  documentId?: string;
  data?: any;
  onChange?: (data: any) => void;
}

export const Stage2Cleansing: React.FC<Stage2CleansingProps> = ({ documentId, data, onChange }) => {
  const [tabValue, setTabValue] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [autoMode, setAutoMode] = useState(true);
  const [columnIssues, setColumnIssues] = useState<ColumnIssue[]>([]);
  const [cleaningActions, setCleaningActions] = useState<CleaningAction[]>([]);
  const [selectedColumn, setSelectedColumn] = useState<string>('');
  const [beforeAfterView, setBeforeAfterView] = useState(false);
  
  // Quality metrics
  const [qualityScore, setQualityScore] = useState(72);
  const [completeness, setCompleteness] = useState(95.3);
  const [consistency, setConsistency] = useState(88.5);
  const [validity, setValidity] = useState(92.1);

  useEffect(() => {
    // Load data quality analysis
    loadQualityAnalysis();
  }, []);

  const loadQualityAnalysis = async () => {
    // Simulate loading quality analysis
    setColumnIssues([
      {
        column: 'TOTINCM',
        type: 'numeric',
        missingCount: 156,
        missingPercent: 1.7,
        outlierCount: 23,
        suggestedAction: 'median',
        priority: 'high',
      },
      {
        column: 'POPU_LSA',
        type: 'numeric',
        missingCount: 45,
        missingPercent: 0.5,
        outlierCount: 8,
        suggestedAction: 'mean',
        priority: 'medium',
      },
      {
        column: 'CENTLIB',
        type: 'categorical',
        missingCount: 89,
        missingPercent: 1.0,
        outlierCount: 0,
        suggestedAction: 'mode',
        priority: 'low',
      },
    ]);
  };

  const handleAutoClean = async () => {
    setProcessing(true);
    
    // Simulate auto-cleaning process
    const actions: CleaningAction[] = [];
    
    for (const issue of columnIssues) {
      if (issue.missingCount > 0) {
        actions.push({
          column: issue.column,
          action: `Imputed ${issue.missingCount} missing values using ${issue.suggestedAction}`,
          timestamp: new Date(),
          affectedRows: issue.missingCount,
        });
      }
      
      if (issue.outlierCount > 0) {
        actions.push({
          column: issue.column,
          action: `Capped ${issue.outlierCount} outliers at 95th percentile`,
          timestamp: new Date(),
          affectedRows: issue.outlierCount,
        });
      }
    }
    
    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setCleaningActions([...cleaningActions, ...actions]);
    setQualityScore(95);
    setCompleteness(99.2);
    setConsistency(94.3);
    setValidity(96.8);
    setProcessing(false);
    
    toast.success(`Data cleaned successfully! ${actions.length} actions applied.`);
  };

  const handleColumnAction = (column: string, action: string) => {
    const newAction: CleaningAction = {
      column,
      action: `Applied ${action} to ${column}`,
      timestamp: new Date(),
      affectedRows: Math.floor(Math.random() * 100) + 1,
    };
    
    setCleaningActions([...cleaningActions, newAction]);
    toast.success(`${action} applied to ${column}`);
  };

  const missingDataChart = [
    { name: 'Complete', value: 97.7, fill: COLORS[1] },
    { name: 'Missing', value: 2.3, fill: COLORS[3] },
  ];

  const qualityTrend = [
    { stage: 'Original', quality: 72, completeness: 95.3, consistency: 88.5 },
    { stage: 'After Imputation', quality: 85, completeness: 98.1, consistency: 91.2 },
    { stage: 'After Outliers', quality: 92, completeness: 98.5, consistency: 93.8 },
    { stage: 'Final', quality: 95, completeness: 99.2, consistency: 94.3 },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Stage 2: Data Cleansing
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Clean and prepare your data with AI-powered suggestions
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoMode}
                onChange={(e) => setAutoMode(e.target.checked)}
                color="primary"
              />
            }
            label="Auto Mode"
          />
          <Button
            variant="outlined"
            startIcon={<Undo />}
            disabled={cleaningActions.length === 0}
          >
            Undo
          </Button>
          <Button
            variant="outlined"
            startIcon={<Save />}
          >
            Save Recipe
          </Button>
        </Box>
      </Box>

      {/* Quality Score Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Speed sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Overall Quality
                </Typography>
              </Box>
              <Typography variant="h3" color="primary.main">
                {qualityScore}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={qualityScore}
                sx={{ mt: 1, height: 6, borderRadius: 3 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Completeness
              </Typography>
              <Typography variant="h4">{completeness}%</Typography>
              <Typography variant="caption" color="success.main">
                +3.9% improved
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Consistency
              </Typography>
              <Typography variant="h4">{consistency}%</Typography>
              <Typography variant="caption" color="success.main">
                +5.8% improved
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Validity
              </Typography>
              <Typography variant="h4">{validity}%</Typography>
              <Typography variant="caption" color="success.main">
                +4.7% improved
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 3 }}>
              <Tab label="Issues Overview" />
              <Tab label="Column Details" />
              <Tab label="Before/After" />
              <Tab label="Action Log" />
            </Tabs>

            {tabValue === 0 && (
              <Box>
                {autoMode && (
                  <Alert severity="info" sx={{ mb: 3 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      AI Recommendations Ready
                    </Typography>
                    <Typography variant="body2">
                      We've analyzed your data and prepared optimal cleaning strategies.
                      Review the suggestions below or click "Auto Clean" to apply all.
                    </Typography>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<AutoFixHigh />}
                      sx={{ mt: 1 }}
                      onClick={handleAutoClean}
                      disabled={processing}
                    >
                      {processing ? 'Processing...' : 'Auto Clean All'}
                    </Button>
                  </Alert>
                )}

                {columnIssues.map((issue) => (
                  <Accordion key={issue.column}>
                    <AccordionSummary expandIcon={<ExpandMore />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="subtitle1">
                            {issue.column}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                            <Chip
                              size="small"
                              label={`${issue.missingCount} missing`}
                              color={issue.missingPercent > 5 ? 'error' : 'warning'}
                            />
                            {issue.outlierCount > 0 && (
                              <Chip
                                size="small"
                                label={`${issue.outlierCount} outliers`}
                                color="info"
                              />
                            )}
                            <Chip
                              size="small"
                              label={issue.priority}
                              color={
                                issue.priority === 'high'
                                  ? 'error'
                                  : issue.priority === 'medium'
                                  ? 'warning'
                                  : 'default'
                              }
                            />
                          </Box>
                        </Box>
                        <Chip
                          label={`Suggested: ${issue.suggestedAction}`}
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={6}>
                          <FormControl fullWidth size="small">
                            <InputLabel>Missing Value Strategy</InputLabel>
                            <Select
                              value={issue.suggestedAction}
                              label="Missing Value Strategy"
                            >
                              <MenuItem value="mean">Mean</MenuItem>
                              <MenuItem value="median">Median</MenuItem>
                              <MenuItem value="mode">Mode</MenuItem>
                              <MenuItem value="forward_fill">Forward Fill</MenuItem>
                              <MenuItem value="backward_fill">Backward Fill</MenuItem>
                              <MenuItem value="drop">Drop Rows</MenuItem>
                              <MenuItem value="custom">Custom Value</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        <Grid item xs={12} md={6}>
                          <FormControl fullWidth size="small">
                            <InputLabel>Outlier Treatment</InputLabel>
                            <Select value="cap" label="Outlier Treatment">
                              <MenuItem value="keep">Keep As Is</MenuItem>
                              <MenuItem value="cap">Cap at Threshold</MenuItem>
                              <MenuItem value="remove">Remove</MenuItem>
                              <MenuItem value="transform">Transform (Log)</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        <Grid item xs={12}>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Button
                              variant="contained"
                              size="small"
                              onClick={() => handleColumnAction(issue.column, issue.suggestedAction)}
                            >
                              Apply Suggestion
                            </Button>
                            <Button variant="outlined" size="small">
                              Preview
                            </Button>
                            <Button variant="text" size="small">
                              Skip
                            </Button>
                          </Box>
                        </Grid>
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            )}

            {tabValue === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Cleaning Actions Log
                </Typography>
                <List>
                  {cleaningActions.map((action, idx) => (
                    <React.Fragment key={idx}>
                      <ListItem>
                        <ListItemText
                          primary={action.action}
                          secondary={`${action.column} • ${action.affectedRows} rows affected • ${action.timestamp.toLocaleTimeString()}`}
                        />
                        <ListItemSecondaryAction>
                          <IconButton size="small">
                            <Undo />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {idx < cleaningActions.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
                {cleaningActions.length === 0 && (
                  <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                    No actions performed yet
                  </Typography>
                )}
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Visualizations */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Missing Data Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={missingDataChart}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {missingDataChart.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mt: 2 }}>
              {missingDataChart.map((entry) => (
                <Box key={entry.name} sx={{ display: 'flex', alignItems: 'center' }}>
                  <Box
                    sx={{
                      width: 12,
                      height: 12,
                      backgroundColor: entry.fill,
                      borderRadius: '50%',
                      mr: 1,
                    }}
                  />
                  <Typography variant="caption">
                    {entry.name}: {entry.value}%
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>

          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quality Improvement Trend
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={qualityTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="stage" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="quality"
                  stroke="#8884d8"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="completeness"
                  stroke="#82ca9d"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Button variant="outlined" size="large">
          Back to Upload
        </Button>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            size="large"
            startIcon={<Visibility />}
            onClick={() => setBeforeAfterView(!beforeAfterView)}
          >
            Compare Before/After
          </Button>
          <Button
            variant="contained"
            size="large"
            startIcon={<PlayArrow />}
            disabled={processing}
          >
            Proceed to Analysis
          </Button>
        </Box>
      </Box>
    </Box>
  );
};