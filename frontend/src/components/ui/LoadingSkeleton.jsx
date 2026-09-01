import { Box, Skeleton } from '@mui/material';

export default function LoadingSkeleton({ rows = 4, height = 72 }) {
  return (
    <Box sx={{ display: 'grid', gap: 2 }}>
      {Array.from({ length: rows }).map((_, index) => (
        <Skeleton key={index} variant="rounded" height={height} sx={{ borderRadius: 2 }} />
      ))}
    </Box>
  );
}
