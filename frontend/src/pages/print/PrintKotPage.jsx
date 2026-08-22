import { Alert, Box, Button, CircularProgress, Stack, Typography } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import KotPreview from '../../print/KotPreview';
import '../../print/receipt.css';
import { getKot } from '../../services/kotService';
import { useAuth } from '../../context/AuthContext';

export default function PrintKotPage() {
  const { kotId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [kot, setKot] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const auto = searchParams.get('auto') === '1';
  const autoPrinted = useRef(false);

  useEffect(() => {
    let active = true;
    getKot(kotId)
      .then((res) => {
        if (active) setKot(res.data);
      })
      .catch((err) => {
        if (active) {
          setError(err.response?.data?.error?.message || 'Failed to load KOT');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [kotId]);

  const handlePrint = () => {
    window.print();
  };

  useEffect(() => {
    if (auto && kot && !autoPrinted.current) {
      autoPrinted.current = true;
      window.setTimeout(() => window.print(), 300);
    }
  }, [auto, kot]);

  if (loading) {
    return (
      <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3, maxWidth: 480, mx: 'auto' }}>
        <Alert severity="error">{error}</Alert>
        <Button sx={{ mt: 2 }} onClick={() => navigate(-1)}>
          Go back
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Stack direction="row" spacing={1} sx={{ mb: 2, '@media print': { display: 'none' } }}>
        <Button variant="contained" onClick={handlePrint}>
          Print KOT
        </Button>
        <Button variant="outlined" onClick={() => navigate(-1)}>
          Back
        </Button>
      </Stack>
      <KotPreview kot={kot} tenantName={user?.tenant_name || 'Kitchen'} />
    </Box>
  );
}
