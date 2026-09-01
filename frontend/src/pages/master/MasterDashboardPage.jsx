import BlockOutlinedIcon from '@mui/icons-material/BlockOutlined';
import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined';
import CheckCircleOutlineOutlinedIcon from '@mui/icons-material/CheckCircleOutlineOutlined';
import EventBusyOutlinedIcon from '@mui/icons-material/EventBusyOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import HowToRegOutlinedIcon from '@mui/icons-material/HowToRegOutlined';
import LaunchOutlinedIcon from '@mui/icons-material/LaunchOutlined';
import OpenInNewOutlinedIcon from '@mui/icons-material/OpenInNewOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import TimelapseOutlinedIcon from '@mui/icons-material/TimelapseOutlined';
import WarningAmberOutlinedIcon from '@mui/icons-material/WarningAmberOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useEffect, useMemo, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import LoadingSkeleton from '../../components/ui/LoadingSkeleton';
import { COMPANY } from '../../constants/company';
import { useAuth } from '../../context/AuthContext';
import { PATHS, masterBusinessesPath } from '../../routes/paths';
import { fetchMasterDashboardSummary } from '../../services/masterService';

const QUICK_ACTIONS = [
  {
    to: PATHS.masterRegistrationRequests,
    title: 'Registration queue',
    description: 'Review and approve new business sign-ups.',
    icon: <HowToRegOutlinedIcon />,
  },
  {
    to: PATHS.masterBusinesses,
    title: 'All businesses',
    description: 'Plans, renewals, activate or suspend accounts.',
    icon: <BusinessOutlinedIcon />,
  },
  {
    to: PATHS.masterPlans,
    title: 'Subscription plans',
    description: 'Create and edit pricing for tenants.',
    icon: <PaymentsOutlinedIcon />,
  },
  {
    to: PATHS.masterAudit,
    title: 'Platform audit',
    description: 'Review master admin activity history.',
    icon: <HistoryOutlinedIcon />,
  },
];

export default function MasterDashboardPage() {
  const theme = useTheme();
  const { user } = useAuth();
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

  const kpis = useMemo(
    () => [
      {
        title: 'Total businesses',
        value: summary?.total_businesses ?? '—',
        hint: 'All approved tenants on the platform',
        icon: <BusinessOutlinedIcon fontSize="small" />,
        to: PATHS.masterBusinesses,
        tone: 'default',
      },
      {
        title: 'Active businesses',
        value: summary?.active_businesses ?? '—',
        hint: 'Login allowed — account active',
        icon: <CheckCircleOutlineOutlinedIcon fontSize="small" />,
        to: masterBusinessesPath({ tenant_status: 'ACTIVE' }),
        tone: 'success',
      },
      {
        title: 'Suspended',
        value: summary?.suspended_businesses ?? '—',
        hint: 'Deactivated — login blocked',
        icon: <BlockOutlinedIcon fontSize="small" />,
        to: masterBusinessesPath({ tenant_status: 'SUSPENDED' }),
        tone: 'warning',
      },
      {
        title: 'Pending requests',
        value: summary?.pending_requests ?? '—',
        hint: 'Awaiting master admin review',
        icon: <HowToRegOutlinedIcon fontSize="small" />,
        to: PATHS.masterRegistrationRequests,
        tone: summary?.pending_requests > 0 ? 'warning' : 'default',
      },
      {
        title: 'Active trials',
        value: summary?.trial_businesses ?? '—',
        hint: 'Businesses on free trial',
        icon: <TimelapseOutlinedIcon fontSize="small" />,
        to: PATHS.masterTrials,
        tone: 'default',
      },
      {
        title: 'Expiring soon',
        value: summary?.expiring_soon ?? '—',
        hint: 'Within renewal warning window',
        icon: <WarningAmberOutlinedIcon fontSize="small" />,
        to: masterBusinessesPath({ status: 'EXPIRING' }),
        tone: summary?.expiring_soon > 0 ? 'warning' : 'default',
      },
      {
        title: 'Expired subscriptions',
        value: summary?.expired_subscriptions ?? '—',
        hint: 'Need manual renewal',
        icon: <EventBusyOutlinedIcon fontSize="small" />,
        to: masterBusinessesPath({ status: 'EXPIRED' }),
        tone: summary?.expired_subscriptions > 0 ? 'warning' : 'default',
      },
    ],
    [summary],
  );

  const isDark = theme.palette.mode === 'dark';
  const heroGradient = isDark
    ? `linear-gradient(135deg, ${COMPANY.brandColor} 0%, #152A45 55%, ${COMPANY.brandAccent} 100%)`
    : `linear-gradient(135deg, ${COMPANY.brandColor} 0%, #1A3352 50%, ${COMPANY.brandAccent} 100%)`;

  return (
    <PageShell>
      <Card
        elevation={0}
        sx={{
          mb: 2,
          borderRadius: 2,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(12,26,46,0.12)',
          background: heroGradient,
          color: '#fff',
        }}
      >
        <CardContent sx={{ py: { xs: 1.25, md: 1.5 }, px: { xs: 1.5, md: 2 }, '&:last-child': { pb: { xs: 1.25, md: 1.5 } } }}>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={1.25}
            alignItems={{ xs: 'flex-start', sm: 'center' }}
            justifyContent="space-between"
          >
            <Stack direction="row" spacing={1.25} alignItems="center" sx={{ minWidth: 0 }}>
              <Box
                sx={{
                  bgcolor: 'rgba(255,255,255,0.12)',
                  borderRadius: 1.5,
                  p: 0.5,
                  lineHeight: 0,
                  flexShrink: 0,
                }}
              >
                <Box
                  component="img"
                  src={COMPANY.logoPath}
                  alt={COMPANY.legalName}
                  sx={{ width: 36, height: 36, objectFit: 'contain', display: 'block' }}
                />
              </Box>
              <Box sx={{ minWidth: 0 }}>
                <Typography
                  variant="caption"
                  sx={{ color: 'rgba(255,255,255,0.75)', letterSpacing: 0.8, display: 'block', lineHeight: 1.2 }}
                >
                  Master Admin Console
                </Typography>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.25 }}>
                  {COMPANY.legalName}
                </Typography>
                <Typography
                  variant="caption"
                  sx={{ color: 'rgba(255,255,255,0.78)', display: 'block', lineHeight: 1.35, mt: 0.25 }}
                >
                  {COMPANY.masterTagline}
                  {user?.name ? (
                    <>
                      {' · '}
                      Signed in as {user.name}
                      {user.email ? ` (${user.email})` : ''}
                    </>
                  ) : null}
                </Typography>
              </Box>
            </Stack>
            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              useFlexGap
              sx={{
                flexShrink: 0,
                alignSelf: { xs: 'stretch', sm: 'center' },
                width: { xs: '100%', sm: 'auto' },
                '& .MuiButton-root': {
                  flex: { xs: 1, sm: '0 0 auto' },
                  minHeight: 32,
                  whiteSpace: 'nowrap',
                  textTransform: 'none',
                  fontWeight: 600,
                  fontSize: '0.8125rem',
                  lineHeight: 1.2,
                  px: 1.5,
                },
              }}
            >
              <Button
                component="a"
                href={COMPANY.website}
                target="_blank"
                rel="noopener noreferrer"
                variant="outlined"
                size="small"
                startIcon={<OpenInNewOutlinedIcon fontSize="inherit" />}
                sx={{
                  color: '#fff',
                  borderColor: 'rgba(255,255,255,0.5)',
                  '&:hover': { borderColor: '#fff', bgcolor: 'rgba(255,255,255,0.1)' },
                  '& .MuiButton-startIcon': { mr: 0.75, ml: -0.25 },
                }}
              >
                Company website
              </Button>
              <Button
                component={RouterLink}
                to={PATHS.masterRegistrationRequests}
                variant="contained"
                size="small"
                startIcon={<LaunchOutlinedIcon fontSize="inherit" />}
                sx={{
                  bgcolor: '#fff',
                  color: COMPANY.brandColor,
                  boxShadow: 'none',
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.92)', boxShadow: 'none' },
                  '& .MuiButton-startIcon': { mr: 0.75, ml: -0.25 },
                }}
              >
                Review sign-ups
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      {error ? (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : null}

      {!summary && !error ? <LoadingSkeleton rows={3} height={96} /> : null}

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>
        Platform overview
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Live tenant counts from your database — click any card to open the related list.
      </Typography>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        {kpis.map((kpi) => (
          <Grid key={kpi.title} size={{ xs: 12, sm: 6, lg: 4, xl: 3 }}>
            <Box
              component={RouterLink}
              to={kpi.to}
              sx={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
            >
              <KpiCard
                title={kpi.title}
                value={kpi.value}
                hint={kpi.hint}
                icon={kpi.icon}
                tone={kpi.tone}
              />
            </Box>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>
        Quick actions
      </Typography>
      <Grid container spacing={2}>
        {QUICK_ACTIONS.map((action) => (
          <Grid key={action.to} size={{ xs: 12, sm: 6, md: 3 }}>
            <Card
              component={RouterLink}
              to={action.to}
              elevation={0}
              sx={{
                height: '100%',
                textDecoration: 'none',
                color: 'inherit',
                border: '1px solid',
                borderColor: 'divider',
                transition: 'border-color 0.15s ease, box-shadow 0.15s ease, transform 0.15s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  boxShadow: isDark ? '0 8px 24px rgba(0,0,0,0.35)' : '0 8px 24px rgba(26,35,48,0.08)',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              <CardContent sx={{ p: 2.5, '&:last-child': { pb: 2.5 } }}>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    bgcolor: isDark ? 'rgba(110,180,200,0.14)' : 'rgba(31, 78, 95, 0.1)',
                    color: 'primary.main',
                    display: 'grid',
                    placeItems: 'center',
                    mb: 1.5,
                  }}
                >
                  {action.icon}
                </Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5 }}>
                  {action.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {action.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </PageShell>
  );
}
