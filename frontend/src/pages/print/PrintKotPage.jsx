import ArrowBackOutlinedIcon from '@mui/icons-material/ArrowBackOutlined';
import { Alert, Box, Button, CircularProgress, Stack, Typography } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import KotPreview from '../../print/KotPreview';
import '../../print/receipt.css';
import { useAuth } from '../../context/AuthContext';
import { PATHS } from '../../routes/paths';
import { getKot } from '../../services/kotService';

function defaultKitchenPath(user) {
  if (user?.role === 'OWNER' || user?.role === 'MANAGER') {
    return PATHS.ownerKitchen;
  }
  return PATHS.billingKitchen;
}

export default function PrintKotPage() {
  const { kotId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const [kot, setKot] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const auto = searchParams.get('auto') === '1';
  const autoPrinted = useRef(false);

  useEffect(() => {
    let active = true;
    setLoading(true);
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

  const handleBack = () => {
    const from = location.state?.from;
    if (typeof from === 'string' && from.startsWith('/')) {
      navigate(from, { replace: true });
      return;
    }

    // Print popup opened via window.open — close when possible.
    if (window.opener && !window.opener.closed) {
      window.close();
      return;
    }

    const sameOriginReferrer =
      document.referrer && document.referrer.startsWith(window.location.origin);
    if (sameOriginReferrer && window.history.length > 1) {
      navigate(-1);
      return;
    }

    navigate(defaultKitchenPath(user), { replace: true });
  };

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
        <Button startIcon={<ArrowBackOutlinedIcon />} onClick={handleBack} sx={{ mb: 2 }}>
          Back
        </Button>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2 }}>
      <Stack
        direction="row"
        spacing={1}
        alignItems="center"
        sx={{ mb: 2, '@media print': { display: 'none' } }}
      >
        <Button startIcon={<ArrowBackOutlinedIcon />} variant="outlined" onClick={handleBack}>
          Back
        </Button>
        <Button variant="contained" onClick={handlePrint}>
          Print KOT
        </Button>
        <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
          {kot?.kot_number}
          {kot?.dining_table_code ? ` · ${kot.dining_table_code}` : ''}
        </Typography>
      </Stack>
      <KotPreview kot={kot} tenantName={user?.tenant?.business_name || user?.tenant?.name || 'Kitchen'} />
    </Box>
  );
}
