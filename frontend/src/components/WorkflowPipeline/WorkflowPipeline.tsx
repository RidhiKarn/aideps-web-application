import React from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepConnector,
  stepConnectorClasses,
  StepIconProps,
  Typography,
  Chip,
  Paper,
  LinearProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  CloudUpload,
  CleaningServices,
  Analytics,
  Calculate,
  Description,
  CheckCircle,
  AutoAwesome,
  Check,
  Settings,
  GroupAdd,
} from '@mui/icons-material';
// import { motion } from 'framer-motion';

const QontoConnector = styled(StepConnector)(({ theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 22,
    left: 'calc(-50% + 40px)',
    right: 'calc(50% + 40px)',
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: theme.palette.primary.main,
      borderWidth: 3,
      borderRadius: 1,
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: theme.palette.success.main,
      borderWidth: 3,
      borderRadius: 1,
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    borderColor: theme.palette.mode === 'dark' ? theme.palette.grey[800] : '#eaeaf0',
    borderTopWidth: 3,
    borderRadius: 1,
  },
}));

const QontoStepIconRoot = styled('div')<{ ownerState: { active?: boolean; completed?: boolean } }>(
  ({ theme, ownerState }) => ({
    color: theme.palette.mode === 'dark' ? theme.palette.grey[700] : '#eaeaf0',
    display: 'flex',
    height: 44,
    alignItems: 'center',
    ...(ownerState.active && {
      color: theme.palette.primary.main,
      filter: 'drop-shadow(0 4px 10px rgba(0,0,0,0.25))',
    }),
    ...(ownerState.completed && {
      color: theme.palette.success.main,
    }),
    '& .QontoStepIcon-circle': {
      width: 44,
      height: 44,
      borderRadius: '50%',
      backgroundColor: 'currentColor',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    },
    '& .QontoStepIcon-icon': {
      color: '#fff',
      zIndex: 1,
      fontSize: 24,
    },
  })
);

interface StageInfo {
  id: number;
  name: string;
  icon: React.ReactElement;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'error';
  progress?: number;
  metrics?: {
    label: string;
    value: string | number;
  }[];
}

const stages: StageInfo[] = [
  {
    id: 1,
    name: 'Raw Data Upload',
    icon: <CloudUpload />,
    description: 'Upload survey data files',
    status: 'completed',
    metrics: [
      { label: 'Rows', value: '9,260' },
      { label: 'Columns', value: '164' },
    ],
  },
  {
    id: 2,
    name: 'Data Cleansing',
    icon: <CleaningServices />,
    description: 'Clean and prepare data',
    status: 'completed',
    metrics: [
      { label: 'Missing', value: '2.3%' },
      { label: 'Cleaned', value: '156 cells' },
    ],
  },
  {
    id: 3,
    name: 'Analysis & Discovery',
    icon: <Analytics />,
    description: 'Discover patterns and insights',
    status: 'in_progress',
    progress: 65,
    metrics: [
      { label: 'Patterns', value: '12' },
      { label: 'Time', value: '2m 30s' },
    ],
  },
  {
    id: 4,
    name: 'Statistics & Weights',
    icon: <Calculate />,
    description: 'Calculate weighted statistics',
    status: 'pending',
  },
  {
    id: 5,
    name: 'Propose Reports',
    icon: <Description />,
    description: 'AI suggests report templates',
    status: 'pending',
  },
  {
    id: 6,
    name: 'User Confirmation',
    icon: <CheckCircle />,
    description: 'Review and approve',
    status: 'pending',
  },
  {
    id: 7,
    name: 'Final Report',
    icon: <AutoAwesome />,
    description: 'Generate final reports',
    status: 'pending',
  },
];

function QontoStepIcon(props: StepIconProps & { stage: StageInfo }) {
  const { active, completed, className, stage } = props;

  return (
    <QontoStepIconRoot ownerState={{ active, completed }} className={className}>
      <div
        className="QontoStepIcon-circle"
        style={{ transform: active ? 'scale(1.1)' : 'scale(1)' }}
      >
        {completed ? (
          <Check className="QontoStepIcon-icon" />
        ) : (
          React.cloneElement(stage.icon, { className: 'QontoStepIcon-icon' })
        )}
      </div>
    </QontoStepIconRoot>
  );
}

interface WorkflowPipelineProps {
  currentStage: number;
  onStageClick: (stage: number) => void;
}

export const WorkflowPipeline: React.FC<WorkflowPipelineProps> = ({
  currentStage,
  onStageClick,
}) => {
  return (
    <Paper
      elevation={2}
      sx={{
        p: 4,
        mb: 4,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
      }}
    >
      <Typography variant="h4" gutterBottom sx={{ color: 'white', mb: 3 }}>
        Workflow Pipeline
      </Typography>
      
      <Stepper
        alternativeLabel
        activeStep={currentStage - 1}
        connector={<QontoConnector />}
        sx={{ mb: 3 }}
      >
        {stages.map((stage) => (
          <Step key={stage.id} completed={stage.status === 'completed'}>
            <StepLabel
              StepIconComponent={(props) => <QontoStepIcon {...props} stage={stage} />}
              onClick={() => onStageClick(stage.id)}
              sx={{
                cursor: 'pointer',
                '& .MuiStepLabel-label': {
                  color: 'white !important',
                  fontWeight: 500,
                  mt: 1,
                },
                '&:hover': {
                  '& .MuiStepLabel-label': {
                    textDecoration: 'underline',
                  },
                },
              }}
            >
              <Box>
                <Typography variant="subtitle1" sx={{ color: 'white' }}>
                  {stage.name}
                </Typography>
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                  {stage.description}
                </Typography>
                {stage.progress && stage.status === 'in_progress' && (
                  <LinearProgress
                    variant="determinate"
                    value={stage.progress}
                    sx={{
                      mt: 1,
                      height: 4,
                      borderRadius: 2,
                      backgroundColor: 'rgba(255,255,255,0.2)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: 'white',
                      },
                    }}
                  />
                )}
                {stage.metrics && (
                  <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                    {stage.metrics.map((metric, idx) => (
                      <Chip
                        key={idx}
                        size="small"
                        label={`${metric.label}: ${metric.value}`}
                        sx={{
                          backgroundColor: 'rgba(255,255,255,0.2)',
                          color: 'white',
                          fontSize: '0.7rem',
                        }}
                      />
                    ))}
                  </Box>
                )}
              </Box>
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
          Progress: {Math.round(((currentStage - 1) / stages.length) * 100)}% Complete
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip
            icon={<Settings />}
            label="Advanced Settings"
            variant="outlined"
            sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
          />
          <Chip
            icon={<GroupAdd />}
            label="Collaborate"
            variant="outlined"
            sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
          />
        </Box>
      </Box>
    </Paper>
  );
};