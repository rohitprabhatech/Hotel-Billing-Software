import { Alert, Box, Grid, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import { COMPANY } from '../../constants/company';
import { PATHS, masterBusinessesPath } from '../../routes/paths';
import { fetchMasterDashboardSummary } from '../../services/masterService';

export default function MasterDashboardPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    fetchMasterDashboardSummary()
      .then((payload) => {
        if (active) setSummary(payload.data || null);
      })
      .catch((err) => {
        if (active) {
          setError(err.response?.data?.error?.message || 'Unable to load dashboard');
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <PageShell>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ mb: 0.75 }}>
          Master Dashboard
        </Typography>
        <Typography color="text.secondary">
          {COMPANY.legalName} · platform operations. Counts below are live tenant rows — not sample
          data.
        </Typography>
      </Box>

      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : null}

      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Box
            component={RouterLink}
            to={PATHS.masterBusinesses}
            sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
          >
            <KpiCard title="Total businesses" value={summary?.total_businesses ?? '—'} hint="All approved businesses" />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Box
            component={RouterLink}
            to={masterBusinessesPath({ tenant_status: 'ACTIVE' })}
            sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
          >
            <KpiCard
              title="Active businesses"
              value={summary?.active_businesses ?? '—'}
              hint="Account active — login allowed"
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Box
            component={RouterLink}
            to={masterBusinessesPath({ tenant_status: 'SUSPENDED' })}
            sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
          >
            <KpiCard
              title="Suspended businesses"
              value={summary?.suspended_businesses ?? '—'}
              hint="Deactivated accounts — login blocked"
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Box
            component={RouterLink}
            to={PATHS.masterRegistrationRequests}
            sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
          >
            <KpiCard
              title="Pending requests"
              value={summary?.pending_requests ?? '—'}
              hint="Open the registration queue"
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Box
            component={RouterLink}
            to={PATHS.masterTrials}
            sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
          >
            <KpiCard
              title="Trial businesses"
              value={summary?.trial_businesses ?? '—'}
              hint="Active free trials"
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Box
            component={RouterLink}
            to={masterBusinessesPath({ status: 'EXPIRING' })}
            sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
          >
            <KpiCard
              title="Expiring soon"
              value={summary?.expiring_soon ?? '—'}
              hint="Within the warning window"
            />
          </Box>
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <Box
            component={RouterLink}
            to={masterBusinessesPath({ status: 'EXPIRED' })}
            sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
          >
            <KpiCard
              title="Expired subscriptions"
              value={summary?.expired_subscriptions ?? '—'}
              hint="Need a manual renewal"
            />
          </Box>
        </Grid>
      </Grid>
    </PageShell>
  );
}
