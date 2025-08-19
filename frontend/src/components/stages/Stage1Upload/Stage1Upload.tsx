import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Collapse,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  CloudUpload,
  InsertDriveFile,
  CheckCircle,
  Error,
  Info,
  ExpandMore,
  ExpandLess,
  Storage,
  TableChart,
  Assessment,
  Warning,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { API_ENDPOINTS } from '../../../config/api';

interface FileInfo {
  name: string;
  size: number;
  type: string;
  lastModified: number;
}

interface UploadResponse {
  document_id: string;
  workflow_id: string;
  file_info: {
    filename: string;
    size: number;
    rows: number;
    columns: number;
    columns_list: string[];
  };
  message: string;
}

interface Stage1UploadProps {
  documentId?: string;
  data?: any;
  onChange?: (data: any) => void;
}

export const Stage1Upload: React.FC<Stage1UploadProps> = ({ documentId, data, onChange }) => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [columns, setColumns] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Form fields
  const [documentName, setDocumentName] = useState('');
  const [organization, setOrganization] = useState('');
  const [surveyType, setSurveyType] = useState('auto-detect');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setFile(file);
      setDocumentName(file.name.replace(/\.[^/.]+$/, ''));
      
      // Simulate reading first few rows for preview
      const reader = new FileReader();
      reader.onload = (e) => {
        // Parse CSV preview (simplified)
        const text = e.target?.result as string;
        const lines = text.split('\n').slice(0, 101); // First 100 rows + header
        const headers = lines[0].split(',').map(h => h.trim());
        
        const cols = headers.map((header, idx) => ({
          field: `col${idx}`,
          headerName: header,
          width: 150,
          editable: false,
        }));
        setColumns(cols);
        
        const rows = lines.slice(1, 11).map((line, idx) => {
          const values = line.split(',');
          const row: any = { id: idx };
          values.forEach((val, colIdx) => {
            row[`col${colIdx}`] = val.trim();
          });
          return row;
        });
        setPreviewData(rows);
      };
      reader.readAsText(file.slice(0, 100000)); // Read first 100KB for preview
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setUploadProgress(0);
    
    // Simulate upload progress
    const progressInterval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 200);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_name', documentName);
      formData.append('organization', organization);
      formData.append('survey_type', surveyType);
      
      const response = await fetch(API_ENDPOINTS.uploadDocument, {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setUploadResponse(data);
        setUploadProgress(100);
        toast.success('File uploaded successfully!');
        
        // Notify parent component about the upload
        if (onChange) {
          onChange(data);
        }
      } else {
        throw new window.Error('Upload failed');
      }
    } catch (error) {
      toast.error('Upload failed. Please try again.');
      console.error('Upload error:', error);
    } finally {
      clearInterval(progressInterval);
      setUploading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Stage 1: Raw Data Upload
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload your survey data file to begin the automated preparation process.
      </Typography>

      <Grid container spacing={3}>
        {/* Upload Section */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3 }}>
            {!file ? (
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  backgroundColor: isDragActive ? 'action.hover' : 'background.default',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <input {...getInputProps()} />
                <CloudUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop the file here' : 'Drag & drop your data file here'}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  or click to browse files
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Supported formats: CSV, XLS, XLSX (Max size: 100MB)
                </Typography>
              </Box>
            ) : (
              <Box>
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <InsertDriveFile sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6">{file.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                      </Box>
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        onClick={() => {
                          setFile(null);
                          setPreviewData([]);
                          setColumns([]);
                        }}
                      >
                        Remove
                      </Button>
                    </Box>
                    
                    {uploading && (
                      <Box sx={{ mt: 2 }}>
                        <LinearProgress variant="determinate" value={uploadProgress} />
                        <Typography variant="caption" sx={{ mt: 1 }}>
                          Uploading... {uploadProgress}%
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                </Card>

                {/* Metadata Form */}
                <Grid container spacing={2} sx={{ mb: 3 }}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Document Name"
                      value={documentName}
                      onChange={(e) => setDocumentName(e.target.value)}
                      helperText="Give your dataset a meaningful name"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Organization"
                      value={organization}
                      onChange={(e) => setOrganization(e.target.value)}
                      helperText="Optional: Your organization name"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Survey Type</InputLabel>
                      <Select
                        value={surveyType}
                        onChange={(e) => setSurveyType(e.target.value)}
                        label="Survey Type"
                      >
                        <MenuItem value="auto-detect">Auto Detect</MenuItem>
                        <MenuItem value="health">Health Survey</MenuItem>
                        <MenuItem value="demographic">Demographic Survey</MenuItem>
                        <MenuItem value="economic">Economic Survey</MenuItem>
                        <MenuItem value="education">Education Survey</MenuItem>
                        <MenuItem value="custom">Custom</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                {/* Advanced Options */}
                <Box>
                  <Button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    endIcon={showAdvanced ? <ExpandLess /> : <ExpandMore />}
                  >
                    Advanced Options
                  </Button>
                  <Collapse in={showAdvanced}>
                    <Alert severity="info" sx={{ mt: 2 }}>
                      Advanced options like encoding, delimiter, and column mapping will be
                      auto-detected but can be customized after upload.
                    </Alert>
                  </Collapse>
                </Box>

                {/* Data Preview */}
                {previewData.length > 0 && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      Data Preview (First 10 rows)
                    </Typography>
                    <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                      <Table stickyHeader size="small">
                        <TableHead>
                          <TableRow>
                            {columns.map((col: any) => (
                              <TableCell key={col.field}>{col.headerName}</TableCell>
                            ))}
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {previewData.map((row: any) => (
                            <TableRow key={row.id}>
                              {columns.map((col: any) => (
                                <TableCell key={col.field}>{row[col.field]}</TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </Box>
                )}

                {/* Upload Button */}
                <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => {
                      setFile(null);
                      setPreviewData([]);
                      setColumns([]);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleUpload}
                    disabled={uploading || !file}
                    startIcon={<CloudUpload />}
                  >
                    {uploading ? 'Uploading...' : 'Upload & Start Processing'}
                  </Button>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Info Panel */}
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              <Info sx={{ verticalAlign: 'middle', mr: 1 }} />
              Quick Guide
            </Typography>
            <List dense>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Automatic Detection"
                  secondary="File encoding and format are detected automatically"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Smart Defaults"
                  secondary="AI suggests optimal settings based on your data"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <CheckCircle color="success" fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary="Data Validation"
                  secondary="Automatic validation and quality checks"
                />
              </ListItem>
            </List>
          </Paper>

          {uploadResponse && uploadResponse.document_id && (
            <Paper elevation={2} sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom color="success.main">
                <CheckCircle sx={{ verticalAlign: 'middle', mr: 1 }} />
                Upload Successful
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <Storage fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Document ID"
                    secondary={uploadResponse.document_id}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <TableChart fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Data Size"
                    secondary={
                      uploadResponse.file_info
                        ? `${uploadResponse.file_info.rows?.toLocaleString() || '0'} rows × ${uploadResponse.file_info.columns || '0'} columns`
                        : 'Processing...'
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <Assessment fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Data Quality"
                    secondary="Initial assessment complete"
                  />
                </ListItem>
              </List>
              <Button
                variant="contained"
                fullWidth
                sx={{ mt: 2 }}
                onClick={() => {
                  // Navigate to next stage
                  navigate(`/workflow/${uploadResponse.document_id}/2`);
                }}
              >
                Proceed to Data Cleansing
              </Button>
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};