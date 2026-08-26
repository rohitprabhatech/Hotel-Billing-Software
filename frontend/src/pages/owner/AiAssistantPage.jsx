import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import EmptyState from '../../components/EmptyState';
import FilterBar from '../../components/FilterBar';
import KpiCard from '../../components/KpiCard';
import PageShell from '../../components/PageShell';
import Section from '../../components/Section';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { fetchAiAnalysis } from '../../services/aiService';

function money(v) {
  return `₹${Number(v || 0).toLocaleString('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function AiAssistantPage() {
  const [period, setPeriod] = useState('today');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const runAnalysis = async () => {
    setLoading(true);
    setError('');
    try {
      const params = { period };
      if (period === 'custom') {
        params.from = fromDate;
        params.to = toDate;
      }
      const res = await fetchAiAnalysis(params);
      setAnalysis(res.data || null);
    } catch (err) {
      const status = err.response?.status;
      const apiMessage = err.response?.data?.error?.message;
      if (status === 401) {
        setError('Your session expired. Please sign in again.');
      } else if (status === 403) {
        setError('You do not have permission to view AI insights.');
      } else {
        setError(apiMessage || 'Unable to load AI insights right now.');
      }
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  };

  const metrics = analysis?.metrics || {};
  const mix = analysis?.payment_mix || {};
  const canAnalyze = !(period === 'custom' && (!fromDate || !toDate));

  return (
    <PageShell>
      <FilterBar
        actions={
          <Button
            variant="contained"
            onClick={runAnalysis}
            disabled={loading || !canAnalyze}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </Button>
        }
      >
        <FormControl sx={{ minWidth: { xs: '100%', sm: 180 } }}>
          <InputLabel>Period</InputLabel>
          <Select
            label="Period"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
          >
            <MenuItem value="today">Today</MenuItem>
            <MenuItem value="yesterday">Yesterday</MenuItem>
            <MenuItem value="this_week">This Week</MenuItem>
            <MenuItem value="this_month">This Month</MenuItem>
            <MenuItem value="last_month">Last Month</MenuItem>
            <MenuItem value="custom">Custom Range</MenuItem>
          </Select>
        </FormControl>
        {period === 'custom' ? (
          <>
            <TextField
              label="From"
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: { xs: '100%', sm: 160 } }}
            />
            <TextField
              label="To"
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              sx={{ minWidth: { xs: '100%', sm: 160 } }}
            />
          </>
        ) : null}
      </FilterBar>

      {loading ? (
        <Stack alignItems="center" spacing={1.5} sx={{ py: 6 }}>
          <CircularProgress size={36} />
          <Typography color="text.secondary">Analyzing your business data...</Typography>
        </Stack>
      ) : null}

      {error && !loading ? (
        <Alert
          severity="error"
          action={
            <Button color="inherit" size="small" onClick={runAnalysis} disabled={!canAnalyze}>
              Retry
            </Button>
          }
        >
          {error}
        </Alert>
      ) : null}

      {!analysis && !loading && !error ? (
        <EmptyState
          title="No analysis yet"
          description="Choose today, weekly, monthly, or a custom range, then click Analyze."
          actionLabel="Analyze"
          onAction={runAnalysis}
        />
      ) : null}

      {analysis?.insufficient_data && !loading ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {analysis.message || 'Not enough sales data available for analysis yet.'}
        </Alert>
      ) : null}

      {analysis && (analysis.industry_insights || []).length && !loading ? (
        <Section
          title="Industry Insights"
          description="Optional module analyzers — rule-based, tenant-scoped only (not an LLM)."
        >
          <Stack spacing={2} sx={{ mb: 2 }}>
            {analysis.industry_insights.map((block) => (
              <Card key={`${block.module}-${block.title}`} variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" fontWeight={700}>
                    {block.title}
                  </Typography>
                  {block.insufficient_data ? (
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {block.message || 'Not enough industry data for this module.'}
                    </Typography>
                  ) : (
                    <Stack spacing={1.5} sx={{ mt: 1.5 }}>
                      {(block.insights || []).map((insight) => (
                        <Box key={`${insight.type}-${insight.title}`}>
                          <Typography variant="subtitle2">{insight.title}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {insight.detail}
                          </Typography>
                        </Box>
                      ))}
                    </Stack>
                  )}
                </CardContent>
              </Card>
            ))}
          </Stack>
        </Section>
      ) : null}

      {analysis && !analysis.insufficient_data && !loading ? (
        <>
          <Section
            title={analysis.label}
            description={`Source: live tenant sales · ${analysis.business_name}`}
          >
            <Alert severity="info" sx={{ mb: 2 }}>
              {analysis.summary}
            </Alert>
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
              }}
            >
              <KpiCard title="Total Sales" value={money(metrics.total_sales)} />
              <KpiCard title="Bills" value={metrics.bill_count ?? '—'} />
              <KpiCard title="Average Bill" value={money(metrics.average_bill)} />
              <KpiCard
                title="Cash"
                value={money(mix.cash_sales)}
                hint={mix.cash_share_pct != null ? `${mix.cash_share_pct}% of sales` : undefined}
              />
              <KpiCard
                title="Online"
                value={money(mix.online_sales)}
                hint={mix.online_share_pct != null ? `${mix.online_share_pct}% of sales` : undefined}
              />
              <KpiCard title="Cancelled" value={metrics.cancelled_bills ?? '—'} />
            </Box>
          </Section>

          <Section title="Insights">
            <Stack spacing={1.5}>
              {(analysis.insights || []).map((insight) => (
                <Card key={`${insight.type}-${insight.title}`}>
                  <CardContent sx={{ py: 2, '&:last-child': { pb: 2 } }}>
                    <Typography variant="subtitle2">{insight.title}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {insight.detail}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Stack>
          </Section>

          <Section
            title="Decision Support"
            description="Recommendations cite recorded quantities and totals only — not invented forecasts."
          >
            {analysis.decisions?.outlook?.available ? (
              <Alert severity="info" sx={{ mb: 2 }}>
                {analysis.decisions.outlook.detail}
              </Alert>
            ) : analysis.decisions?.outlook?.detail ? (
              <Alert severity="warning" sx={{ mb: 2 }}>
                {analysis.decisions.outlook.detail}
              </Alert>
            ) : null}

            {analysis.decisions?.demand_insufficient ? (
              <Alert severity="warning" sx={{ mb: 2 }}>
                {analysis.decisions.demand_message || 'Demand comparison needs a prior period with sales.'}
              </Alert>
            ) : null}

            <Stack spacing={1.5} sx={{ mb: 3 }}>
              {(analysis.decisions?.recommendations || []).map((rec) => (
                <Card key={`${rec.type}-${rec.title}`}>
                  <CardContent sx={{ py: 2, '&:last-child': { pb: 2 } }}>
                    <Typography variant="subtitle2">{rec.title}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                      {rec.detail}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
              {!analysis.decisions?.recommendations?.length ? (
                <EmptyState
                  title="No recommendations yet"
                  description="Need more item sales history in this period."
                />
              ) : null}
            </Stack>

            <Box
              sx={{
                display: 'grid',
                gap: 3,
                gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
              }}
            >
              <Section title="Best Movers (qty)">
                <TableCard>
                  <Table size="small" sx={{ minWidth: 420 }}>
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(analysis.decisions?.best_movers || []).map((row) => (
                        <TableRow key={`best-${row.item_name}`} hover>
                          <TableCell>
                            <TruncateText value={row.item_name} maxWidth={200} />
                          </TableCell>
                          <TableCell align="right">{row.quantity}</TableCell>
                          <TableCell align="right">{money(row.revenue)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableCard>
              </Section>
              <Section title="Slow Movers (qty)">
                <TableCard>
                  <Table size="small" sx={{ minWidth: 420 }}>
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell align="right">Revenue</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(analysis.decisions?.slow_movers || []).map((row) => (
                        <TableRow key={`slow-${row.item_name}`} hover>
                          <TableCell>
                            <TruncateText value={row.item_name} maxWidth={200} />
                          </TableCell>
                          <TableCell align="right">{row.quantity}</TableCell>
                          <TableCell align="right">{money(row.revenue)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableCard>
              </Section>
            </Box>

            {!analysis.decisions?.demand_insufficient && analysis.decisions?.demand_hints?.length ? (
              <Section title="Demand Hints vs Prior Period">
                <TableCard>
                  <Table size="small" sx={{ minWidth: 420 }}>
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell align="right">Prev Qty</TableCell>
                        <TableCell align="right">Qty</TableCell>
                        <TableCell align="right">Change</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {analysis.decisions.demand_hints.map((row) => (
                        <TableRow key={`demand-${row.item_name}`} hover>
                          <TableCell>
                            <TruncateText value={row.item_name} maxWidth={200} />
                          </TableCell>
                          <TableCell align="right">{row.previous_quantity}</TableCell>
                          <TableCell align="right">{row.quantity}</TableCell>
                          <TableCell align="right">
                            {row.quantity_change > 0 ? '+' : ''}
                            {row.quantity_change}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableCard>
              </Section>
            ) : null}
          </Section>

          <Box
            sx={{
              display: 'grid',
              gap: 3,
              gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
            }}
          >
            <Section title="Top Items">
              <TableCard>
                <Table size="small" sx={{ minWidth: 420 }}>
                  <TableHead>
                    <TableRow>
                      <TableCell>Item</TableCell>
                      <TableCell align="right">Revenue</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(analysis.top_items || []).map((row) => (
                      <TableRow key={row.item_name} hover>
                        <TableCell>
                          <TruncateText value={row.item_name} maxWidth={220} />
                        </TableCell>
                        <TableCell align="right">{money(row.revenue)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableCard>
            </Section>
            <Section title="Category Sales">
              <TableCard>
                <Table size="small" sx={{ minWidth: 420 }}>
                  <TableHead>
                    <TableRow>
                      <TableCell>Category</TableCell>
                      <TableCell align="right">Revenue</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(analysis.category_sales || []).map((row) => (
                      <TableRow key={row.category_name} hover>
                        <TableCell>
                          <TruncateText value={row.category_name} maxWidth={220} />
                        </TableCell>
                        <TableCell align="right">{money(row.revenue)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableCard>
            </Section>
          </Box>
        </>
      ) : null}
    </PageShell>
  );
}
