import React from 'react';
import { Typography } from '@mui/material';

interface Stage5ReportsProps {
  documentId?: string;
  data?: any;
  onChange?: (data: any) => void;
}

export const Stage5Reports: React.FC<Stage5ReportsProps> = ({ documentId, data, onChange }) => {
  return <Typography variant='h5'>Stage5Reports Component</Typography>;
};
