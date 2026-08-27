import { Box, Button, Stack } from '@mui/material';
import { useMemo } from 'react';
import PrintableReceipt from './PrintableReceipt';
import { receiptClassFromSettings } from '../utils/auditLabels';

export default function BillPreview({
  bill,
  onPrint,
  printing = false,
  billingSettings = null,
  showSizeControls = false,
}) {
  const settings = billingSettings || bill?.tenant?.billing_settings || {};
  const widthClass = useMemo(() => receiptClassFromSettings(settings), [settings]);

  if (!bill) return null;

  return (
    <Stack spacing={2} alignItems="center">
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
        <PrintableReceipt bill={bill} width={widthClass} billingSettings={settings} />
      </Box>

      {!showSizeControls ? (
        <Button
          className="no-print"
          variant="contained"
          onClick={() => onPrint?.(widthClass)}
          disabled={printing}
        >
          Print Receipt
        </Button>
      ) : null}
    </Stack>
  );
}
