import ArrowBackOutlinedIcon from '@mui/icons-material/ArrowBackOutlined';
import { Alert, Box, Button, CircularProgress, Stack, Typography } from '@mui/material';
import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import BillPreview from '../../print/BillPreview';
import '../../print/receipt.css';
import { PATHS } from '../../routes/paths';
import { getBill, recordBillPrint } from '../../services/billService';

function defaultBillingPath(user) {
  const role = user?.role;
  const isHotel = user?.tenant?.business_type === 'hotel_restaurant';
  if (role === 'OWNER' || role === 'MANAGER') {
    return isHotel ? PATHS.ownerRestaurantBilling : PATHS.ownerDashboard;
  }
  return isHotel ? PATHS.billingNew : PATHS.billingHome;
}

export default function PrintBillPage() {
  const { billId } = useParams();
  const { user } = useAuth();
  const isOwner = user?.role === 'OWNER';
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
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

  const handleBack = () => {
    const from = location.state?.from;
    if (typeof from === 'string' && from.startsWith('/')) {
      navigate(from, { replace: true });
      return;
    }

    // Prefer closing a print popup opened via window.open when possible.
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

    navigate(defaultBillingPath(user), { replace: true });
  };

  if (loading) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="print-root" sx={{ minHeight: '100vh', bgcolor: '#f5f5f5', py: 3 }}>
      <Stack className="no-print" spacing={1} alignItems="stretch" mb={2} sx={{ px: 2, maxWidth: 720, mx: 'auto' }}>
        <Box>
          <Button startIcon={<ArrowBackOutlinedIcon />} onClick={handleBack} sx={{ mb: 1 }}>
            Back
          </Button>
        </Box>
        <Typography variant="h6" textAlign="center">
          Print Bill #{bill?.bill_number}
        </Typography>
        {error ? <Alert severity="error">{error}</Alert> : null}
      </Stack>
      <BillPreview
        bill={bill}
        onPrint={handlePrint}
        printing={printing}
        billingSettings={bill?.tenant?.billing_settings}
        showSizeControls={isOwner && user?.tenant?.business_type !== 'hotel_restaurant'}
      />
    </Box>
  );
}
