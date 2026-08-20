import {
  Alert,
  Chip,
  CircularProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import PaginationBar from '../../components/PaginationBar';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { listMasterTrials } from '../../services/masterService';

function formatWhen(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export default function MasterTrialsPage() {
  const [rows, setRows] = useState([]);
  const [meta, setMeta] = useState({ page: 1, per_page: 25, total: 0 });
  const [page, setPage] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    listMasterTrials({ page, per_page: 25 })
      .then((payload) => {
        if (active) {
          setRows(payload.data || []);
          setMeta(payload.meta || { page, per_page: 25, total: 0 });
        }
      })
      .catch((err) => {
        if (active) {
          setError(err.response?.data?.error?.message || 'Unable to load trials.');
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [page]);

  return (
    <PageShell>
      {error ? <Alert severity="error">{error}</Alert> : null}

      {loading ? (
        <Stack alignItems="center" py={6}>
          <CircularProgress size={28} />
        </Stack>
      ) : rows.length === 0 ? (
        <EmptyState
          title="No active trials"
          description="Approved businesses appear here while their free trial is still running."
        />
      ) : (
        <TableCard>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Business</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Started</TableCell>
                <TableCell>Ends</TableCell>
                <TableCell>Remaining</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    <TruncateText value={row.business_name || row.tenant_id} />
                  </TableCell>
                  <TableCell>
                    <Chip size="small" color="warning" label={row.status} />
                  </TableCell>
                  <TableCell>{formatWhen(row.trial_starts_at || row.starts_at)}</TableCell>
                  <TableCell>{formatWhen(row.trial_ends_at || row.ends_at)}</TableCell>
                  <TableCell>
                    {row.remaining_days == null ? '—' : `${row.remaining_days} days`}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <PaginationBar
            page={meta.page}
            perPage={meta.per_page}
            total={meta.total}
            onPageChange={(next) => {
              setLoading(true);
              setPage(next);
            }}
          />
        </TableCard>
      )}
    </PageShell>
  );
}
