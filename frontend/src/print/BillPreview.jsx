import { Box, Button, Stack } from '@mui/material';
import { useMemo } from 'react';
import PrintableReceipt from './PrintableReceipt';
import TravelAgencyReceipt from './TravelAgencyReceipt';
import { receiptClassFromSettings } from '../utils/auditLabels';
import { BILL_FORMAT_TRAVEL, resolveBillFormat } from '../utils/billFormat';

function previewWidth(settings = {}, billFormat) {
  const paper = settings.paper_size || (billFormat === BILL_FORMAT_TRAVEL ? 'A5' : '80mm');
  if (paper === 'A4') return 860;
  if (paper === 'A5') return 620;
  if (paper === 'custom' && settings.width_mm) return Math.min(settings.width_mm * 3.2, 900);
  return 420;
}

export default function BillPreview({
  bill,
  onPrint,
  printing = false,
  billingSettings = null,
  showSizeControls = false,
}) {
  const settings = billingSettings || bill?.tenant?.billing_settings || {};
  const widthClass = useMemo(() => receiptClassFromSettings(settings), [settings]);
  const billFormat = useMemo(
    () => resolveBillFormat(settings, bill?.tenant || {}),
    [settings, bill?.tenant],
  );
  const ReceiptComponent = billFormat === BILL_FORMAT_TRAVEL ? TravelAgencyReceipt : PrintableReceipt;
  const previewMaxWidth = previewWidth(settings, billFormat);

  if (!bill) return null;

  return (
    <Stack spacing={2} alignItems="center" sx={{ width: '100%' }}>
      <Box
        sx={{
          border: '1px solid',
          borderColor: 'divider',
          bgcolor: '#fff',
          p: billFormat === BILL_FORMAT_TRAVEL ? 2 : 1,
          width: '100%',
          maxWidth: previewMaxWidth,
          overflowX: 'auto',
        }}
      >
        <ReceiptComponent bill={bill} width={widthClass} billingSettings={settings} />
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
