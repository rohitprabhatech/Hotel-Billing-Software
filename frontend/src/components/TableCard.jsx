import { Box, Card, CardContent } from '@mui/material';

/** Card wrapper that scrolls wide tables without scrolling the whole page. */
export default function TableCard({ children, sx = {}, contentSx = {} }) {
  return (
    <Card sx={sx}>
      <CardContent sx={{ p: 0, '&:last-child': { pb: 0 }, ...contentSx }}>
        <Box
          sx={{
            width: '100%',
            overflowX: 'auto',
            '& .MuiTableCell-root': {
              px: { xs: 1.25, sm: 2 },
              py: 1.75,
            },
            '& .MuiTableCell-head': {
              py: 1.75,
            },
          }}
        >
          {children}
        </Box>
      </CardContent>
    </Card>
  );
}
