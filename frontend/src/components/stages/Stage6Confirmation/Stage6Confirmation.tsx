import React from 'react';
import { Typography } from '@mui/material';

interface Stage6ConfirmationProps {
  documentId?: string;
  data?: any;
  onChange?: (data: any) => void;
}

export const Stage6Confirmation: React.FC<Stage6ConfirmationProps> = ({ documentId, data, onChange }) => {
  return <Typography variant='h5'>Stage6Confirmation Component</Typography>;
};
