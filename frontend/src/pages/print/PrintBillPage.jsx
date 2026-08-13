import { Alert, Box, Button, CircularProgress, Stack, Typography } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import BillPreview from '../../print/BillPreview';
import '../../print/receipt.css';
import { getBill, recordBillPrint } from '../../services/billService';

export default function PrintBillPage() {
  const { billId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [bill, setBill] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [printing, setPrinting] = useState(false);
  const auto = searchParams.get('auto') === '1';
  const autoPrinted = useRef(false);

  useEffect(() => {
    let active = true;
    getBill(billId)
      .then((res) => {
        if (active) setBill(res.data);
      })
      .catch((err) => {
        if (active) {
          setError(err.response?.data?.error?.message || 'Failed to load bill');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [billId]);

  const handlePrint = async () => {
    setPrinting(true);
    setError('');
    try {
      await recordBillPrint(billId);
      window.print();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to record print');
    } finally {
      setPrinting(false);
    }
  };

  useEffect(() => {
    if (auto && bill && !autoPrinted.current) {
      autoPrinted.current = true;
      handlePrint();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auto, bill]);

  if (loading) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="print-root" sx={{ minHeight: '100vh', bgcolor: '#f5f5f5', py: 3 }}>
      <Stack className="no-print" spacing={1} alignItems="center" mb={2}>
        <Typography variant="h6">Print Bill #{bill?.bill_number}</Typography>
        {error ? <Alert severity="error">{error}</Alert> : null}
        <Button onClick={() => navigate(-1)}>Back</Button>
      </Stack>
      <BillPreview bill={bill} onPrint={handlePrint} printing={printing} />
    </Box>
  );
}