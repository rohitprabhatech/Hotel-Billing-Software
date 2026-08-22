import RefreshOutlinedIcon from '@mui/icons-material/RefreshOutlined';
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { usePermissions } from '../../hooks/usePermissions';
import { getKitchenQueue, updateKotStatus } from '../../services/kotService';

const CHANNEL_LABELS = {
  dine_in: 'Dine-in',
  takeaway: 'Takeaway',
  delivery: 'Delivery',
};

const COLUMNS = [
  { key: 'queued', label: 'Queued', color: '#ffb74d' },
  { key: 'preparing', label: 'Preparing', color: '#64b5f6' },
  { key: 'ready', label: 'Ready', color: '#81c784' },
];

const NEXT_ACTIONS = {
  queued: [{ status: 'preparing', label: 'Start preparing' }],
  preparing: [{ status: 'ready', label: 'Mark ready' }],
  ready: [],
};

function KotCard({ kot, onStatusChange, updating, canUpdateStatus }) {
  const actions = NEXT_ACTIONS[kot.status] || [];

  return (
    <Card
      sx={{
        bgcolor: '#1e1e1e',
        color: '#f5f5f5',
        border: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <CardContent sx={{ pb: 1 }}>
        <Stack spacing={1}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              {kot.kot_number}
            </Typography>
            <Chip size="small" label={kot.status} sx={{ textTransform: 'capitalize' }} />
          </Stack>
          <Typography variant="body2" color="rgba(255,255,255,0.72)">
            {kot.order_number} · {CHANNEL_LABELS[kot.channel] || kot.channel}
            {kot.dining_table_code ? ` · Table ${kot.dining_table_code}` : ''}
          </Typography>
          <Stack spacing={0.5} sx={{ mt: 1 }}>
            {(kot.items || []).map((line) => (
              <Stack key={line.id} direction="row" justifyContent="space-between">
                <Typography variant="body1">{line.item_name}</Typography>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  × {line.quantity}
                </Typography>
              </Stack>
            ))}
          </Stack>
          {kot.notes ? (
            <Typography variant="body2" color="warning.light">
              Note: {kot.notes}
            </Typography>
          ) : null}
        </Stack>
      </CardContent>
      {canUpdateStatus && actions.length ? (
        <CardActions sx={{ px: 2, pb: 2, flexDirection: 'column', gap: 1 }}>
          {actions.map((action) => (
            <Button
              key={action.status}
              fullWidth
              variant="contained"
              size="large"
              disabled={updating === kot.id}
              onClick={() => onStatusChange(kot.id, action.status)}
              sx={{ minHeight: 48, fontSize: '1rem' }}
            >
              {action.label}
            </Button>
          ))}
        </CardActions>
      ) : null}
    </Card>
  );
}

export default function KitchenPage() {
  const moduleEnabled = useModuleGate('kitchen');
  const { canUpdateKotStatus } = usePermissions();
  const [kots, setKots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState('');

  const load = useCallback(async () => {
    if (!moduleEnabled) return;
    setError('');
    try {
      const response = await getKitchenQueue();
      setKots(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load kitchen queue.');
    } finally {
      setLoading(false);
    }
  }, [moduleEnabled]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!moduleEnabled) return undefined;
    const timer = window.setInterval(load, 20000);
    return () => window.clearInterval(timer);
  }, [load, moduleEnabled]);

  const grouped = useMemo(() => {
    const map = { queued: [], preparing: [], ready: [] };
    kots.forEach((kot) => {
      if (map[kot.status]) map[kot.status].push(kot);
    });
    return map;
  }, [kots]);

  const onStatusChange = async (kotId, status) => {
    setUpdating(kotId);
    setError('');
    try {
      await updateKotStatus(kotId, status);
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update KOT status.');
    } finally {
      setUpdating('');
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Kitchen dashboard is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      <PageActions>
        <Button variant="outlined" startIcon={<RefreshOutlinedIcon />} onClick={load}>
          Refresh
        </Button>
      </PageActions>

      <PageShell>
        <Box
          sx={{
            bgcolor: '#121212',
            color: '#f5f5f5',
            borderRadius: 2,
            p: { xs: 2, md: 3 },
            minHeight: '60vh',
          }}
        >
          <Stack spacing={2}>
            <Typography variant="h5" sx={{ fontWeight: 700 }}>
              Kitchen board
            </Typography>
            {error ? <Alert severity="error">{error}</Alert> : null}
            {loading ? (
              <LoadingBlock />
            ) : kots.length === 0 ? (
              <EmptyState
                title="Kitchen queue is empty"
                description="Fire a KOT from an open order to send items to the kitchen."
              />
            ) : (
              <Grid container spacing={2}>
                {COLUMNS.map((column) => (
                  <Grid item xs={12} md={4} key={column.key}>
                    <Stack spacing={1.5}>
                      <Typography
                        variant="subtitle1"
                        sx={{ fontWeight: 700, color: column.color, textTransform: 'uppercase' }}
                      >
                        {column.label} ({grouped[column.key].length})
                      </Typography>
                      <Stack spacing={1.5}>
                        {grouped[column.key].map((kot) => (
                          <KotCard
                            key={kot.id}
                            kot={kot}
                            updating={updating}
                            canUpdateStatus={canUpdateKotStatus}
                            onStatusChange={onStatusChange}
                          />
                        ))}
                        {grouped[column.key].length === 0 ? (
                          <Typography variant="body2" color="rgba(255,255,255,0.5)">
                            No tickets
                          </Typography>
                        ) : null}
                      </Stack>
                    </Stack>
                  </Grid>
                ))}
              </Grid>
            )}
          </Stack>
        </Box>
      </PageShell>
    </>
  );
}
