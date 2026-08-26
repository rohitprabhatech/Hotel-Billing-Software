import PrintOutlinedIcon from '@mui/icons-material/PrintOutlined';
import {
  Alert,
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import KpiCard from '../../components/KpiCard';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import { useModuleGate } from '../../context/ModulesContext';
import { fetchOutstandingReport } from '../../services/reportService';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

const BUCKET_COLS = [
  { key: '0_30', label: '0–30' },
  { key: '31_60', label: '31–60' },
  { key: '61_90', label: '61–90' },
  { key: '90_plus', label: '90+' },
];

export default function OutstandingReportPage() {
  const creditEnabled = useModuleGate('customer_credit');
  const [partyTab, setPartyTab] = useState('customers');
  const [partyType, setPartyType] = useState('all');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetchOutstandingReport({
        party_type: partyType === 'all' ? undefined : partyType,
      });
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load outstanding report.');
      setReport(null);
    } finally {
      setLoading(false);
    }
  }, [partyType]);

  useEffect(() => {
    if (creditEnabled) load();
  }, [creditEnabled, load]);

  if (!creditEnabled) {
    return (
      <PageShell>
        <EmptyState
          title="Outstanding report not available"
          description="Enable customer credit for this business to see aged dues."
        />
      </PageShell>
    );
  }

  const section = partyTab === 'customers' ? report?.customers : report?.suppliers;
  const parties = section?.parties || [];
  const summary = section?.summary || {};

  return (
    <PageShell>
      <PageActions>
        <Stack direction="row" spacing={1} alignItems="center">
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel id="party-filter">Party</InputLabel>
            <Select
              labelId="party-filter"
              label="Party"
              value={partyType}
              onChange={(e) => setPartyType(e.target.value)}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="customer">Customers</MenuItem>
              <MenuItem value="supplier">Suppliers</MenuItem>
            </Select>
          </FormControl>
          <Button variant="outlined" onClick={load} disabled={loading}>
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PrintOutlinedIcon />}
            onClick={() => window.print()}
            disabled={!report}
          >
            Print
          </Button>
        </Stack>
      </PageActions>

      {error ? <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert> : null}

      {loading ? (
        <LoadingBlock />
      ) : (
        <Box className="outstanding-print-root">
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            As of {report?.as_of || '—'} · FIFO aging of open credit charges
          </Typography>

          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={2}
            sx={{ mb: 2 }}
            useFlexGap
            flexWrap="wrap"
          >
            <KpiCard title="Total outstanding" value={money(summary.total)} />
            <KpiCard title="Parties" value={String(summary.party_count || 0)} />
            <KpiCard title="0–30 days" value={money(summary['0_30'])} />
            <KpiCard title="90+ days" value={money(summary['90_plus'])} />
          </Stack>

          <Tabs
            value={partyTab}
            onChange={(_, v) => setPartyTab(v)}
            sx={{ mb: 2 }}
          >
            <Tab value="customers" label="Customers" />
            <Tab value="suppliers" label="Suppliers" />
          </Tabs>

          {parties.length === 0 ? (
            <EmptyState
              title="No outstanding balances"
              description="Credit sales and purchases with open dues appear here."
            />
          ) : (
            <TableCard>
              <Table size="small" sx={{ minWidth: 720 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Party</TableCell>
                    <TableCell align="right">Balance</TableCell>
                    {BUCKET_COLS.map((col) => (
                      <TableCell key={col.key} align="right">
                        {col.label}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {parties.map((row) => (
                    <TableRow key={row.id} hover>
                      <TableCell>
                        <TruncateText value={row.name} maxWidth={220} />
                      </TableCell>
                      <TableCell align="right">{money(row.balance)}</TableCell>
                      {BUCKET_COLS.map((col) => (
                        <TableCell key={col.key} align="right">
                          {money(row.aging?.[col.key])}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableCard>
          )}
        </Box>
      )}

      <style>{`
        @media print {
          body * { visibility: hidden; }
          .outstanding-print-root, .outstanding-print-root * { visibility: visible; }
          .outstanding-print-root { position: absolute; left: 0; top: 0; width: 100%; }
        }
      `}</style>
    </PageShell>
  );
}
