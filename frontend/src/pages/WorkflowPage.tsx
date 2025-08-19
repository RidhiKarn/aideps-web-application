import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Paper,
  Alert,
  Breadcrumbs,
  Link,
  Chip,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Fab,
  Zoom,
  Backdrop,
} from '@mui/material';
import {
  NavigateNext,
  NavigateBefore,
  Home,
  Save,
  Help,
  Chat,
  Close,
  CheckCircle,
  Warning,
  PlayArrow,
  Pause,
  Stop,
} from '@mui/icons-material';
// import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

// Import stage components
import { Stage1Upload } from '../components/stages/Stage1Upload/Stage1Upload';
import { Stage2Cleansing } from '../components/stages/Stage2Cleansing/Stage2Cleansing';
import { Stage3Analysis } from '../components/stages/Stage3Analysis/Stage3Analysis';
import { Stage4Statistics } from '../components/stages/Stage4Statistics/Stage4Statistics';
import { Stage5Reports } from '../components/stages/Stage5Reports/Stage5Reports';
import { Stage6Confirmation } from '../components/stages/Stage6Confirmation/Stage6Confirmation';
import { Stage7Generation } from '../components/stages/Stage7Generation/Stage7Generation';
import { WorkflowPipeline } from '../components/WorkflowPipeline/WorkflowPipeline';

const stages = [
  { id: 1, name: 'Raw Data Upload', component: Stage1Upload },
  { id: 2, name: 'Data Cleansing', component: Stage2Cleansing },
  { id: 3, name: 'Analysis & Discovery', component: Stage3Analysis },
  { id: 4, name: 'Statistics & Weights', component: Stage4Statistics },
  { id: 5, name: 'Propose Reports', component: Stage5Reports },
  { id: 6, name: 'User Confirmation', component: Stage6Confirmation },
  { id: 7, name: 'Final Report Generation', component: Stage7Generation },
];

export const WorkflowPage: React.FC = () => {
  const { documentId, stage } = useParams();
  const navigate = useNavigate();
  
  const [currentStage, setCurrentStage] = useState(parseInt(stage || '1'));
  const [completedStages, setCompletedStages] = useState<number[]>([]);
  const [stageData, setStageData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [confirmDialog, setConfirmDialog] = useState(false);

  useEffect(() => {
    // Load workflow data
    if (documentId) {
      loadWorkflowData();
    }
  }, [documentId]);

  useEffect(() => {
    // Update URL when stage changes
    if (documentId && documentId !== 'new') {
      navigate(`/workflow/${documentId}/${currentStage}`, { replace: true });
    }
  }, [currentStage]);

  const loadWorkflowData = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock completed stages
      if (documentId === 'demo') {
        setCompletedStages([1, 2]);
        setCurrentStage(3);
      }
    } catch (error) {
      toast.error('Failed to load workflow data');
    } finally {
      setLoading(false);
    }
  };

  const validateStage = (): boolean => {
    const errors: string[] = [];
    
    // Stage-specific validation
    switch (currentStage) {
      case 1:
        if (!stageData.fileUploaded) {
          errors.push('Please upload a file before proceeding');
        }
        break;
      case 2:
        if (!stageData.cleaningComplete) {
          errors.push('Please complete data cleaning before proceeding');
        }
        break;
      case 6:
        if (!stageData.userConfirmed) {
          errors.push('Please confirm your selections before proceeding');
        }
        break;
    }
    
    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleNext = async () => {
    // Skip validation for now to allow testing
    // if (!validateStage()) {
    //   toast.error('Please complete all required fields');
    //   return;
    // }
    
    setIsProcessing(true);
    try {
      // Save current stage data
      await saveStageData();
      
      // Mark current stage as completed
      setCompletedStages([...completedStages, currentStage]);
      
      // Move to next stage
      if (currentStage < stages.length) {
        setCurrentStage(currentStage + 1);
        toast.success(`Stage ${currentStage} completed!`);
      }
    } catch (error) {
      toast.error('Failed to save progress');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleBack = () => {
    if (currentStage > 1) {
      setCurrentStage(currentStage - 1);
    }
  };

  const handleStageClick = (stageNumber: number) => {
    // Can only navigate to completed stages or the next stage
    if (completedStages.includes(stageNumber) || stageNumber === completedStages.length + 1) {
      setCurrentStage(stageNumber);
    } else {
      toast.error('Complete previous stages first');
    }
  };

  const saveStageData = async () => {
    // Simulate API call to save stage data
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Saving stage data:', stageData);
  };

  const handleStageDataChange = (data: any) => {
    setStageData({ ...stageData, [currentStage]: data });
    
    // If we get a document_id from Stage 1, update the URL
    if (currentStage === 1 && data?.document_id) {
      navigate(`/workflow/${data.document_id}/2`, { replace: true });
    }
  };

  const CurrentStageComponent = stages[currentStage - 1]?.component;

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Header */}
      <Paper elevation={0} sx={{ borderRadius: 0, borderBottom: 1, borderColor: 'divider' }}>
        <Container maxWidth="xl" sx={{ py: 2 }}>
          <Breadcrumbs separator={<NavigateNext fontSize="small" />}>
            <Link
              component="button"
              variant="body1"
              onClick={() => navigate('/')}
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              <Home sx={{ mr: 0.5, fontSize: 20 }} />
              Dashboard
            </Link>
            <Link
              component="button"
              variant="body1"
              onClick={() => navigate('/workflows')}
            >
              Workflows
            </Link>
            <Typography color="text.primary">
              {documentId || 'New Workflow'}
            </Typography>
            <Typography color="text.primary">
              Stage {currentStage}: {stages[currentStage - 1]?.name}
            </Typography>
          </Breadcrumbs>
        </Container>
      </Paper>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Workflow Pipeline Visualization */}
        <WorkflowPipeline
          currentStage={currentStage}
          onStageClick={handleStageClick}
        />

        {/* Validation Errors */}
        {validationErrors.length > 0 && (
          <div>
            <Alert
                severity="error"
                sx={{ mb: 3 }}
                action={
                  <IconButton
                    size="small"
                    onClick={() => setValidationErrors([])}
                  >
                    <Close fontSize="small" />
                  </IconButton>
                }
              >
                <Typography variant="subtitle2" gutterBottom>
                  Please fix the following issues:
                </Typography>
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                  {validationErrors.map((error, idx) => (
                    <li key={idx}>{error}</li>
                  ))}
                </ul>
              </Alert>
          </div>
        )}

        {/* Stage Content */}
        <Paper elevation={2} sx={{ p: 4, mb: 4 }}>
          {CurrentStageComponent && (
            <CurrentStageComponent
              documentId={documentId}
              data={stageData[currentStage]}
              onChange={handleStageDataChange}
            />
          )}
        </Paper>

        {/* Navigation Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button
            variant="outlined"
            size="large"
            onClick={handleBack}
            disabled={currentStage === 1 || isProcessing}
            startIcon={<NavigateBefore />}
          >
            Previous
          </Button>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              size="large"
              onClick={() => saveStageData()}
              disabled={isProcessing}
              startIcon={<Save />}
            >
              Save Progress
            </Button>
            
            {currentStage < stages.length ? (
              <Button
                variant="contained"
                size="large"
                onClick={handleNext}
                disabled={isProcessing}
                endIcon={<NavigateNext />}
              >
                {isProcessing ? 'Processing...' : 'Next Stage'}
              </Button>
            ) : (
              <Button
                variant="contained"
                color="success"
                size="large"
                onClick={() => setConfirmDialog(true)}
                disabled={isProcessing}
                startIcon={<CheckCircle />}
              >
                Complete Workflow
              </Button>
            )}
          </Box>
        </Box>
      </Container>

      {/* Floating Action Buttons */}
      <Box sx={{ position: 'fixed', bottom: 24, right: 24, display: 'flex', flexDirection: 'column', gap: 2 }}>
        <Zoom in={true} timeout={300}>
          <Fab
            color="primary"
            size="medium"
            onClick={() => setShowChat(true)}
          >
            <Chat />
          </Fab>
        </Zoom>
        <Zoom in={true} timeout={400}>
          <Fab
            color="secondary"
            size="medium"
            onClick={() => setShowHelp(true)}
          >
            <Help />
          </Fab>
        </Zoom>
      </Box>

      {/* Help Dialog */}
      <Dialog
        open={showHelp}
        onClose={() => setShowHelp(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Help - Stage {currentStage}: {stages[currentStage - 1]?.name}
        </DialogTitle>
        <DialogContent>
          <Typography paragraph>
            This stage helps you {stages[currentStage - 1]?.name.toLowerCase()}.
          </Typography>
          <Typography variant="subtitle2" gutterBottom>
            Key Actions:
          </Typography>
          <ul>
            <li>Review all options carefully</li>
            <li>Use AI suggestions as a starting point</li>
            <li>Customize based on your specific needs</li>
            <li>Save your progress regularly</li>
          </ul>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHelp(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Completion Dialog */}
      <Dialog
        open={confirmDialog}
        onClose={() => setConfirmDialog(false)}
      >
        <DialogTitle>Complete Workflow?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to complete this workflow? Make sure all stages are properly reviewed.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="success"
            onClick={() => {
              toast.success('Workflow completed successfully!');
              navigate('/');
            }}
          >
            Complete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Processing Backdrop */}
      <Backdrop
        sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
        open={isProcessing}
      >
        <CircularProgress color="inherit" />
      </Backdrop>
    </Box>
  );
};