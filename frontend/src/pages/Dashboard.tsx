import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  Chip,
  Avatar,
  AvatarGroup,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Menu,
  MenuItem,
  Tooltip,
  Badge,
  Divider,
  TextField,
  InputAdornment,
  Select,
  FormControl,
  InputLabel,
  Tab,
  Tabs,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Assessment,
  CloudUpload,
  CheckCircle,
  Schedule,
  Error,
  MoreVert,
  Search,
  FilterList,
  Download,
  Share,
  PlayArrow,
  Refresh,
  FolderOpen,
  Timeline,
  Speed,
  Storage,
  Group,
  CalendarToday,
  ArrowForward,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
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
// import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

interface WorkflowItem {
  id: string;
  name: string;
  status: 'in_progress' | 'completed' | 'error' | 'pending';
  stage: number;
  progress: number;
  created: Date;
  modified: Date;
  rows: number;
  columns: number;
  owner: string;
  organization: string;
}

interface StatCard {
  title: string;
  value: string | number;
  change: number;
  icon: React.ReactElement;
  color: string;
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  
  // Mock data - in production, this would come from API
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([
    {
      id: '1',
      name: 'NFHS-5 Survey Data',
      status: 'in_progress',
      stage: 3,
      progress: 42,
      created: new Date('2024-01-15'),
      modified: new Date(),
      rows: 587432,
      columns: 234,
      owner: 'Dr. Sharma',
      organization: 'Health Ministry',
    },
    {
      id: '2',
      name: 'Economic Census 2023',
      status: 'completed',
      stage: 7,
      progress: 100,
      created: new Date('2024-01-10'),
      modified: new Date('2024-01-14'),
      rows: 1234567,
      columns: 456,
      owner: 'Mr. Patel',
      organization: 'Statistics Dept',
    },
    {
      id: '3',
      name: 'Agricultural Survey Q4',
      status: 'in_progress',
      stage: 5,
      progress: 71,
      created: new Date('2024-01-12'),
      modified: new Date(),
      rows: 234567,
      columns: 123,
      owner: 'Ms. Singh',
      organization: 'Agriculture Ministry',
    },
    {
      id: '4',
      name: 'Education Statistics 2024',
      status: 'pending',
      stage: 1,
      progress: 0,
      created: new Date('2024-01-16'),
      modified: new Date('2024-01-16'),
      rows: 98765,
      columns: 87,
      owner: 'Dr. Kumar',
      organization: 'Education Ministry',
    },
  ]);

  const statCards: StatCard[] = [
    {
      title: 'Active Workflows',
      value: workflows.filter(w => w.status === 'in_progress').length,
      change: 12.5,
      icon: <Timeline />,
      color: '#1976d2',
    },
    {
      title: 'Completed This Month',
      value: workflows.filter(w => w.status === 'completed').length,
      change: 8.3,
      icon: <CheckCircle />,
      color: '#4caf50',
    },
    {
      title: 'Total Data Processed',
      value: '2.4M',
      change: 23.1,
      icon: <Storage />,
      color: '#9c27b0',
    },
    {
      title: 'Average Processing Time',
      value: '4.2h',
      change: -15.3,
      icon: <Speed />,
      color: '#ff9800',
    },
  ];

  const processingTrend = [
    { month: 'Jan', workflows: 45, dataPoints: 1200000 },
    { month: 'Feb', workflows: 52, dataPoints: 1400000 },
    { month: 'Mar', workflows: 48, dataPoints: 1300000 },
    { month: 'Apr', workflows: 61, dataPoints: 1600000 },
    { month: 'May', workflows: 58, dataPoints: 1550000 },
    { month: 'Jun', workflows: 67, dataPoints: 1800000 },
  ];

  const stageDistribution = [
    { name: 'Upload', value: 15, fill: COLORS[0] },
    { name: 'Cleansing', value: 25, fill: COLORS[1] },
    { name: 'Analysis', value: 20, fill: COLORS[2] },
    { name: 'Statistics', value: 18, fill: COLORS[3] },
    { name: 'Reports', value: 12, fill: COLORS[4] },
    { name: 'Review', value: 10, fill: COLORS[5] },
  ];

  const qualityMetrics = [
    { metric: 'Completeness', current: 95, target: 98 },
    { metric: 'Accuracy', current: 92, target: 95 },
    { metric: 'Consistency', current: 88, target: 90 },
    { metric: 'Validity', current: 94, target: 95 },
    { metric: 'Timeliness', current: 85, target: 90 },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'info';
      case 'error': return 'error';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle />;
      case 'in_progress': return <Schedule />;
      case 'error': return <Error />;
      default: return <Schedule />;
    }
  };

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, workflowId: string) => {
    setAnchorEl(event.currentTarget);
    setSelectedWorkflow(workflowId);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedWorkflow(null);
  };

  const filteredWorkflows = workflows.filter(w => {
    const matchesSearch = w.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          w.organization.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || w.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back! Here's an overview of your data preparation workflows.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <div>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar
                      sx={{
                        bgcolor: `${card.color}20`,
                        color: card.color,
                        width: 48,
                        height: 48,
                      }}
                    >
                      {card.icon}
                    </Avatar>
                    <Box sx={{ ml: 'auto' }}>
                      <Chip
                        size="small"
                        label={`${card.change > 0 ? '+' : ''}${card.change}%`}
                        color={card.change > 0 ? 'success' : 'error'}
                        icon={card.change > 0 ? <TrendingUp /> : <TrendingDown />}
                      />
                    </Box>
                  </Box>
                  <Typography variant="h4" gutterBottom>
                    {card.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {card.title}
                  </Typography>
                </CardContent>
              </Card>
            </div>
          </Grid>
        ))}
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Processing Trend
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={processingTrend}>
                <defs>
                  <linearGradient id="colorWorkflows" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorData" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <RechartsTooltip />
                <Legend />
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="workflows"
                  stroke="#8884d8"
                  fillOpacity={1}
                  fill="url(#colorWorkflows)"
                />
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="dataPoints"
                  stroke="#82ca9d"
                  fillOpacity={1}
                  fill="url(#colorData)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Stage Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stageDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {stageDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Quality Metrics */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Data Quality Metrics
        </Typography>
        <Grid container spacing={2}>
          {qualityMetrics.map((metric) => (
            <Grid item xs={12} md={2.4} key={metric.metric}>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{metric.metric}</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {metric.current}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metric.current}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'grey.200',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: metric.current >= metric.target ? 'success.main' : 'warning.main',
                    },
                  }}
                />
                <Typography variant="caption" color="text.secondary">
                  Target: {metric.target}%
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Workflows Table */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Recent Workflows
          </Typography>
          <TextField
            size="small"
            placeholder="Search workflows..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
            sx={{ mr: 2 }}
          />
          <FormControl size="small" sx={{ minWidth: 120, mr: 2 }}>
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="in_progress">In Progress</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="error">Error</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="contained"
            startIcon={<CloudUpload />}
            onClick={() => navigate('/workflow/new')}
          >
            New Upload
          </Button>
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Stage</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Data Size</TableCell>
                <TableCell>Owner</TableCell>
                <TableCell>Modified</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredWorkflows.map((workflow) => (
                <TableRow
                  key={workflow.id}
                  hover
                  sx={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/workflow/${workflow.id}/1`)}
                >
                  <TableCell>
                    <Box>
                      <Typography variant="subtitle2">{workflow.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {workflow.organization}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={workflow.status.replace('_', ' ')}
                      color={getStatusColor(workflow.status) as any}
                      icon={getStatusIcon(workflow.status)}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      Stage {workflow.stage}/7
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={workflow.progress}
                        sx={{ width: 60, height: 6, borderRadius: 3 }}
                      />
                      <Typography variant="caption">{workflow.progress}%</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {workflow.rows.toLocaleString()} × {workflow.columns}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Avatar sx={{ width: 24, height: 24, fontSize: 12 }}>
                        {workflow.owner.charAt(0)}
                      </Avatar>
                      <Typography variant="body2">{workflow.owner}</Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {format(workflow.modified, 'MMM dd, HH:mm')}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMenuClick(e, workflow.id);
                      }}
                    >
                      <MoreVert />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => {
            navigate(`/workflow/${selectedWorkflow}`);
            handleMenuClose();
          }}>
            <FolderOpen sx={{ mr: 1, fontSize: 20 }} /> Open
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <Share sx={{ mr: 1, fontSize: 20 }} /> Share
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>
            <Download sx={{ mr: 1, fontSize: 20 }} /> Download
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleMenuClose} sx={{ color: 'error.main' }}>
            <Error sx={{ mr: 1, fontSize: 20 }} /> Delete
          </MenuItem>
        </Menu>
      </Paper>
    </Box>
  );
};