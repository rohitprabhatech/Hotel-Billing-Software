import { Box, Button, Stack, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useState } from 'react';
import PrintableReceipt from './PrintableReceipt';

export default function BillPreview({ bill, onPrint, printing = false }) {
  const [width, setWidth] = useState('80');

  if (!bill) return null;

  return (
    <Stack spacing={2} alignItems="center">
      <ToggleButtonGroup
        className="no-print"
        exclusive
        size="small"
        value={width}
        onChange={(_, value) => {
          if (value) setWidth(value);
        }}
      >
        <ToggleButton value="58">58mm</ToggleButton>
        <ToggleButton value="80">80mm</ToggleButton>
      </ToggleButtonGroup>

      <Box
        sx={{
          border: '1px solid',
          borderColor: 'divider',
          bgcolor: '#fff',
          p: 1,
          maxWidth: '100%',
          overflowX: 'auto',
        }}
      >
        <PrintableReceipt bill={bill} width={width} />
      </Box>

      <Button
        className="no-print"
        variant="contained"
        onClick={() => onPrint?.(width)}
        disabled={printing}
      >
        Print Receipt
      </Button>
    </Stack>
  );
}