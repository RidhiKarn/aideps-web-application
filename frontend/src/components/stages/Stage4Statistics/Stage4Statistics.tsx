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
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Stack,
} from '@mui/material';
import {
  Functions,
  ShowChart,
  TrendingUp,
  Calculate,
  Speed,
  DataUsage,
  ExpandMore,
  FileDownload,
  Science,
  QueryStats,
  Equalizer,
  AutoGraph,
  CheckCircle,
  Info,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
} from 'recharts';
import toast from 'react-hot-toast';

interface StatisticalTest {
  name: string;
  type: string;
  result: number;
  pValue: number;
  significance: boolean;
  interpretation: string;
}

interface Stage4StatisticsProps {
  documentId?: string;
  data?: any;
  onChange?: (data: any) => void;
}

export const Stage4Statistics: React.FC<Stage4StatisticsProps> = ({ documentId, data, onChange }) => {
  const [tabValue, setTabValue] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [selectedTest, setSelectedTest] = useState('all');
  const [statisticalTests, setStatisticalTests] = useState<StatisticalTest[]>([]);
  const [modelMetrics, setModelMetrics] = useState<any[]>([]);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    // Simulate loading statistics
    setStatisticalTests([
      {
        name: 'Shapiro-Wilk Test',
        type: 'Normality',
        result: 0.982,
        pValue: 0.0234,
        significance: true,
        interpretation: 'Data significantly deviates from normal distribution',
      },
      {
        name: 'Levene\'s Test',
        type: 'Homogeneity',
        result: 2.145,
        pValue: 0.0876,
        significance: false,
        interpretation: 'Variances are homogeneous across groups',
      },
      {
        name: 'Chi-Square Test',
        type: 'Independence',
        result: 45.67,
        pValue: 0.0001,
        significance: true,
        interpretation: 'Variables are significantly dependent',
      },
      {
        name: 'ANOVA',
        type: 'Variance',
        result: 12.34,
        pValue: 0.0023,
        significance: true,
        interpretation: 'Significant differences between group means',
      },
    ]);

    setModelMetrics([
      { model: 'Linear Regression', r2: 0.85, rmse: 1234, mae: 987 },
      { model: 'Random Forest', r2: 0.92, rmse: 892, mae: 678 },
      { model: 'XGBoost', r2: 0.94, rmse: 756, mae: 543 },
    ]);
  };

  const handleRunTests = async () => {
    setProcessing(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setProcessing(false);
    toast.success('Statistical tests completed!');
  };

  const distributionData = [
    { value: 10, frequency: 5 },
    { value: 20, frequency: 12 },
    { value: 30, frequency: 25 },
    { value: 40, frequency: 35 },
    { value: 50, frequency: 28 },
    { value: 60, frequency: 18 },
    { value: 70, frequency: 8 },
  ];

  const regressionData = [
    { x: 1, actual: 10, predicted: 11 },
    { x: 2, actual: 20, predicted: 19 },
    { x: 3, actual: 28, predicted: 30 },
    { x: 4, actual: 42, predicted: 40 },
    { x: 5, actual: 48, predicted: 50 },
    { x: 6, actual: 62, predicted: 60 },
  ];

  const timeSeriesData = [
    { month: 'Jan', value: 4000, trend: 3800 },
    { month: 'Feb', value: 3000, trend: 3900 },
    { month: 'Mar', value: 5000, trend: 4100 },
    { month: 'Apr', value: 4500, trend: 4300 },
    { month: 'May', value: 6000, trend: 4600 },
    { month: 'Jun', value: 5500, trend: 4900 },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Stage 4: Statistical Analysis
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Advanced statistical tests and model validation
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<Science />}
            onClick={handleRunTests}
            disabled={processing}
          >
            {processing ? 'Running Tests...' : 'Run All Tests'}
          </Button>
          <Button variant="outlined" startIcon={<FileDownload />}>
            Export Results
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Functions sx={{ color: 'primary.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Tests Performed
                </Typography>
              </Box>
              <Typography variant="h3">24</Typography>
              <Typography variant="caption" color="success.main">
                All tests completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Speed sx={{ color: 'warning.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Best Model R²
                </Typography>
              </Box>
              <Typography variant="h3">0.94</Typography>
              <Typography variant="caption">XGBoost</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <QueryStats sx={{ color: 'success.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Significant Results
                </Typography>
              </Box>
              <Typography variant="h3">18</Typography>
              <Typography variant="caption">p {'<'} 0.05</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <DataUsage sx={{ color: 'info.main', mr: 1 }} />
                <Typography variant="subtitle2" color="text.secondary">
                  Confidence Level
                </Typography>
              </Box>
              <Typography variant="h3">95%</Typography>
              <LinearProgress
                variant="determinate"
                value={95}
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
              <Tab label="Statistical Tests" />
              <Tab label="Regression Analysis" />
              <Tab label="Time Series" />
              <Tab label="Model Comparison" />
            </Tabs>

            {tabValue === 0 && (
              <Box>
                <FormControl sx={{ mb: 3, minWidth: 200 }}>
                  <InputLabel>Test Category</InputLabel>
                  <Select
                    value={selectedTest}
                    onChange={(e) => setSelectedTest(e.target.value)}
                    label="Test Category"
                  >
                    <MenuItem value="all">All Tests</MenuItem>
                    <MenuItem value="normality">Normality Tests</MenuItem>
                    <MenuItem value="variance">Variance Tests</MenuItem>
                    <MenuItem value="correlation">Correlation Tests</MenuItem>
                  </Select>
                </FormControl>

                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Test Name</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Statistic</TableCell>
                        <TableCell>p-value</TableCell>
                        <TableCell>Result</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {statisticalTests.map((test) => (
                        <TableRow key={test.name}>
                          <TableCell>
                            <Typography variant="subtitle2">{test.name}</Typography>
                          </TableCell>
                          <TableCell>
                            <Chip label={test.type} size="small" />
                          </TableCell>
                          <TableCell>{test.result.toFixed(3)}</TableCell>
                          <TableCell>
                            <Typography
                              variant="body2"
                              color={test.pValue < 0.05 ? 'error.main' : 'text.primary'}
                            >
                              {test.pValue.toFixed(4)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Tooltip title={test.interpretation}>
                              <Chip
                                label={test.significance ? 'Significant' : 'Not Significant'}
                                color={test.significance ? 'success' : 'default'}
                                size="small"
                                icon={test.significance ? <CheckCircle /> : <Info />}
                              />
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}

            {tabValue === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Regression Analysis
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={regressionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="x" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Scatter name="Actual" dataKey="actual" fill="#8884d8" />
                    <Line
                      type="monotone"
                      name="Predicted"
                      dataKey="predicted"
                      stroke="#ff7300"
                      strokeWidth={2}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
                <Alert severity="info" sx={{ mt: 2 }}>
                  R² = 0.94 | RMSE = 756 | MAE = 543
                </Alert>
              </Box>
            )}

            {tabValue === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Time Series Analysis
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={timeSeriesData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.6}
                    />
                    <Line
                      type="monotone"
                      dataKey="trend"
                      stroke="#ff7300"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            )}

            {tabValue === 3 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Model Performance Comparison
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Model</TableCell>
                        <TableCell>R² Score</TableCell>
                        <TableCell>RMSE</TableCell>
                        <TableCell>MAE</TableCell>
                        <TableCell>Performance</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {modelMetrics.map((model) => (
                        <TableRow key={model.model}>
                          <TableCell>
                            <Typography variant="subtitle2">{model.model}</Typography>
                          </TableCell>
                          <TableCell>{model.r2.toFixed(2)}</TableCell>
                          <TableCell>{model.rmse}</TableCell>
                          <TableCell>{model.mae}</TableCell>
                          <TableCell>
                            <LinearProgress
                              variant="determinate"
                              value={model.r2 * 100}
                              sx={{ height: 8, borderRadius: 4 }}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Side Panel */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Distribution Analysis
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={distributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="value" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="frequency" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>

          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Key Insights
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  <TrendingUp color="success" />
                </ListItemIcon>
                <ListItemText
                  primary="Strong positive correlation"
                  secondary="Income and Education Level (r=0.78)"
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemIcon>
                  <AutoGraph color="warning" />
                </ListItemIcon>
                <ListItemText
                  primary="Non-normal distribution"
                  secondary="Income data is right-skewed"
                />
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemIcon>
                  <Equalizer color="info" />
                </ListItemIcon>
                <ListItemText
                  primary="Seasonal pattern detected"
                  secondary="Quarterly variations in spending"
                />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Button variant="outlined" size="large">
          Back to Analysis
        </Button>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="outlined" size="large">
            Save Results
          </Button>
          <Button variant="contained" size="large">
            Generate Reports
          </Button>
        </Box>
      </Box>
    </Box>
  );
};