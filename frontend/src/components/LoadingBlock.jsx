import { Box, CircularProgress } from '@mui/material';

/** Standard centered loading block for table/page shells. */
export default function LoadingBlock({ size = 28, py = 8 }) {
  return (
    <Box sx={{ py, display: 'grid', placeItems: 'center' }}>
      <CircularProgress size={size} />
    </Box>
  );
}
