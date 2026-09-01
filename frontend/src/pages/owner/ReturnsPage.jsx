import AssignmentReturnOutlinedIcon from '@mui/icons-material/AssignmentReturnOutlined';
import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Checkbox,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Stack,
  Step,
  StepLabel,
  Stepper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import LoadingBlock from '../../components/LoadingBlock';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import SearchInput from '../../components/ui/SearchInput';
import StatusBadge from '../../components/ui/StatusBadge';
import VariantStockGrid from '../../components/VariantStockGrid';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import { useModuleGate } from '../../context/ModulesContext';
import { fetchClothingPosCatalog } from '../../services/clothingService';
import { fetchGroceryPosCatalog } from '../../services/groceryService';
import { createReturn, listReturns, lookupReturnBill } from '../../services/returnService';
import { listSerialUnits } from '../../services/serialService';

const STEPS = ['Find bill', 'Quantities', 'Confirm'];

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

export default function ReturnsPage() {
  const moduleEnabled = useModuleGate('returns_exchange');
  const { role } = useAuth();
  const canWrite = role === 'OWNER' || role === 'MANAGER';

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [wizardOpen, setWizardOpen] = useState(false);
  const [step, setStep] = useState(0);
  const [billNumber, setBillNumber] = useState('');
  const [lookup, setLookup] = useState(null);
  const [qtyByLine, setQtyByLine] = useState({});
  const [kind, setKind] = useState('RETURN');
  const [reason, setReason] = useState('');
  const [exchangePick, setExchangePick] = useState(null);
  const [exchangeSerialByLine, setExchangeSerialByLine] = useState({});
  const [quarantineByLine, setQuarantineByLine] = useState({});
  const [catalog, setCatalog] = useState([]);
  const [serialStock, setSerialStock] = useState([]);
  const [saving, setSaving] = useState(false);

  const loadList = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await listReturns({ per_page: 50 });
      setRows(res.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to load returns');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!moduleEnabled) return;
    loadList();
  }, [moduleEnabled, loadList]);

  const selectedLines = useMemo(() => {
    if (!lookup) return [];
    return (lookup.items || [])
      .map((line) => ({
        ...line,
        quantity: Number(qtyByLine[line.bill_item_id] || 0),
      }))
      .filter((line) => line.quantity > 0);
  }, [lookup, qtyByLine]);

  const hasSerialLines = useMemo(
    () => selectedLines.some((line) => line.is_serial),
    [selectedLines],
  );
  const hasClothingVariantLines = useMemo(
    () => selectedLines.some((line) => !line.is_serial && line.variant_id),
    [selectedLines],
  );
  const hasPlainItemLines = useMemo(
    () => selectedLines.some((line) => !line.is_serial && !line.variant_id),
    [selectedLines],
  );
  const hasNonSerialExchangeLines = hasClothingVariantLines || hasPlainItemLines;

  const openWizard = () => {
    setWizardOpen(true);
    setStep(0);
    setBillNumber('');
    setLookup(null);
    setQtyByLine({});
    setKind('RETURN');
    setReason('');
    setExchangePick(null);
    setExchangeSerialByLine({});
    setQuarantineByLine({});
    setError('');
  };

  const searchBill = async () => {
    setError('');
    try {
      const res = await lookupReturnBill({ bill_number: billNumber.trim() });
      setLookup(res.data);
      const next = {};
      (res.data?.items || []).forEach((line) => {
        next[line.bill_item_id] = line.quantity_returnable > 0 ? '1' : '0';
      });
      setQtyByLine(next);
      setStep(1);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Bill not found');
    }
  };

  const goConfirm = async () => {
    if (!selectedLines.length) {
      setError('Enter a return quantity for at least one line.');
      return;
    }
    setError('');
    if (kind === 'EXCHANGE') {
      try {
        if (hasClothingVariantLines) {
          const res = await fetchClothingPosCatalog({ limit: 200 });
          setCatalog(res.data?.items || []);
        } else if (hasPlainItemLines) {
          const res = await fetchGroceryPosCatalog({ limit: 200 });
          setCatalog(res.data?.items || []);
        } else {
          setCatalog([]);
        }
        if (hasSerialLines) {
          const itemIds = [...new Set(selectedLines.filter((line) => line.is_serial).map((line) => line.item_id))];
          const batches = await Promise.all(
            itemIds.map((itemId) =>
              listSerialUnits({ item_id: itemId, status: 'IN_STOCK', per_page: 100 }).then((res) => res.data || []),
            ),
          );
          setSerialStock(batches.flat());
        } else {
          setSerialStock([]);
        }
      } catch {
        setCatalog([]);
        setSerialStock([]);
      }
    }
    setStep(2);
  };

  const submit = async () => {
    if (!lookup) return;
    if (!reason.trim()) {
      setError('Reason is required.');
      return;
    }
    if (kind === 'EXCHANGE') {
      const serialLine = selectedLines.find((line) => line.is_serial);
      if (serialLine && !exchangeSerialByLine[serialLine.bill_item_id]) {
        setError('Select the replacement serial / IMEI for exchange.');
        return;
      }
      if (hasNonSerialExchangeLines && !exchangePick) {
        setError(
          hasClothingVariantLines
            ? 'Select the size/color to give in exchange.'
            : 'Select the replacement item to give in exchange.',
        );
        return;
      }
    }
    setSaving(true);
    setError('');
    try {
      const payload = {
        bill_id: lookup.bill_id,
        kind,
        reason: reason.trim(),
        items: selectedLines.map((line) => ({
          bill_item_id: line.bill_item_id,
          quantity: line.quantity,
          ...(kind === 'EXCHANGE' && line.is_serial
            ? { exchange_serial_unit_id: exchangeSerialByLine[line.bill_item_id]?.id }
            : {}),
          ...(kind === 'EXCHANGE' && !line.is_serial
            ? {
                exchange_item_id: exchangePick?.item_id,
                exchange_variant_id: exchangePick?.variant_id,
              }
            : {}),
          ...(kind === 'RETURN' && line.is_serial
            ? { quarantine: Boolean(quarantineByLine[line.bill_item_id]) }
            : {}),
        })),
      };
      const res = await createReturn(payload);
      setSuccess(
        `${res.data?.kind === 'EXCHANGE' ? 'Exchange' : 'Return'} ${res.data?.return_number} saved. Refund ${money(
          res.data?.refund_amount,
        )}${Number(res.data?.extra_payable) > 0 ? ` · Extra payable ${money(res.data.extra_payable)}` : ''}.`,
      );
      setWizardOpen(false);
      await loadList();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Could not save return');
    } finally {
      setSaving(false);
    }
  };

  if (!moduleEnabled) {
    return (
      <PageShell>
        <Alert severity="warning">Returns & Exchange is not enabled for this business type.</Alert>
      </PageShell>
    );
  }

  return (
    <>
      <PageActions>
        {canWrite ? (
          <Button variant="contained" startIcon={<AssignmentReturnOutlinedIcon />} onClick={openWizard}>
            New return / exchange
          </Button>
        ) : null}
      </PageActions>
      <PageShell>
        {error && !wizardOpen ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : null}
        {success ? (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        ) : null}
        {!canWrite ? (
          <Alert severity="info" sx={{ mb: 2 }}>
            Billing users can view returns. Owner or manager processes them.
          </Alert>
        ) : null}
        <TableCard>
          {loading ? (
            <LoadingBlock />
          ) : !rows.length ? (
            <EmptyState
              title="No returns yet"
              description="Look up a finalized bill, restock returned goods, or exchange into another item / size / serial."
              actionLabel={canWrite ? 'New return / exchange' : undefined}
              onAction={canWrite ? openWizard : undefined}
            />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Number</TableCell>
                  <TableCell>Kind</TableCell>
                  <TableCell>Original bill</TableCell>
                  <TableCell>Reason</TableCell>
                  <TableCell align="right">Refund</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>{row.return_number}</TableCell>
                    <TableCell>
                      <StatusBadge
                        label={row.kind === 'EXCHANGE' ? 'Exchange' : 'Return'}
                        variant={row.kind === 'EXCHANGE' ? 'info' : 'pending'}
                      />
                    </TableCell>
                    <TableCell>{row.bill_number}</TableCell>
                    <TableCell>
                      <TruncateText value={row.reason} maxWidth={220} />
                    </TableCell>
                    <TableCell align="right">{money(row.refund_amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </TableCard>
      </PageShell>

      <Dialog open={wizardOpen} onClose={() => !saving && setWizardOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>Return / exchange</DialogTitle>
        <DialogContent>
          <Stepper activeStep={step} sx={{ my: 2 }} alternativeLabel>
            {STEPS.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          {error && wizardOpen ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          ) : null}

          {step === 0 ? (
            <Stack spacing={2}>
              <Typography variant="body2" color="text.secondary">
                Enter the original bill number. Only finalized bills can be returned.
              </Typography>
              <SearchInput
                placeholder="Bill number"
                value={billNumber}
                onChange={(e) => setBillNumber(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') searchBill();
                }}
                autoFocus
              />
            </Stack>
          ) : null}

          {step === 1 && lookup ? (
            <Stack spacing={2}>
              <Typography variant="body2">
                Bill {lookup.bill_number} · {money(lookup.grand_total)}
                {lookup.customer_name ? ` · ${lookup.customer_name}` : ''}
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Item</TableCell>
                    <TableCell align="right">Sold</TableCell>
                    <TableCell align="right">Already returned</TableCell>
                    <TableCell align="right">Return qty</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {lookup.items.map((line) => (
                    <TableRow key={line.bill_item_id}>
                      <TableCell>
                        {line.item_name}
                        {line.serial_number ? (
                          <Typography variant="caption" display="block" color="text.secondary">
                            IMEI: {line.serial_number}
                          </Typography>
                        ) : null}
                      </TableCell>
                      <TableCell align="right">{line.quantity_sold}</TableCell>
                      <TableCell align="right">{line.quantity_returned}</TableCell>
                      <TableCell align="right">
                        <TextField
                          type="number"
                          size="small"
                          value={qtyByLine[line.bill_item_id] ?? ''}
                          disabled={line.quantity_returnable <= 0}
                          onChange={(e) =>
                            setQtyByLine((prev) => ({ ...prev, [line.bill_item_id]: e.target.value }))
                          }
                          inputProps={{ min: 0, max: line.quantity_returnable, step: '1' }}
                          sx={{ width: 88 }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Stack>
          ) : null}

          {step === 2 ? (
            <Stack spacing={2}>
              <FormControl>
                <RadioGroup row value={kind} onChange={(e) => setKind(e.target.value)}>
                  <FormControlLabel value="RETURN" control={<Radio />} label="Return (refund / restock)" />
                  <FormControlLabel
                    value="EXCHANGE"
                    control={<Radio />}
                    label={
                      hasSerialLines
                        ? 'Exchange serial / IMEI'
                        : hasClothingVariantLines
                          ? 'Exchange size/color'
                          : 'Exchange item'
                    }
                  />
                </RadioGroup>
              </FormControl>
              <TextField
                label="Reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                required
                fullWidth
                placeholder="Wrong size, damaged, customer request"
              />
              {kind === 'RETURN' && hasSerialLines ? (
                <Stack spacing={1}>
                  {selectedLines
                    .filter((line) => line.is_serial)
                    .map((line) => (
                      <FormControlLabel
                        key={line.bill_item_id}
                        control={
                          <Checkbox
                            checked={Boolean(quarantineByLine[line.bill_item_id])}
                            onChange={(e) =>
                              setQuarantineByLine((prev) => ({
                                ...prev,
                                [line.bill_item_id]: e.target.checked,
                              }))
                            }
                          />
                        }
                        label={`Quarantine ${line.serial_number || 'serial unit'} (do not resell as new)`}
                      />
                    ))}
                </Stack>
              ) : null}
              {kind === 'EXCHANGE' && hasClothingVariantLines ? (
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Tap the replacement size/color. That variant is deducted; the returned one is restocked.
                  </Typography>
                  {(catalog || []).slice(0, 8).map((item) => (
                    <Box key={item.id} sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">{item.name}</Typography>
                      <VariantStockGrid
                        variants={item.variants || []}
                        onSelect={(variant) =>
                          setExchangePick({
                            item_id: item.id,
                            variant_id: variant.id,
                            label: `${item.name} (${variant.size}/${variant.color})`,
                          })
                        }
                      />
                    </Box>
                  ))}
                  {exchangePick ? (
                    <Alert severity="info">Exchanging into {exchangePick.label}</Alert>
                  ) : null}
                </Box>
              ) : null}
              {kind === 'EXCHANGE' && hasPlainItemLines ? (
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    Tap the replacement title. That item is deducted; the returned one is restocked.
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={1}>
                    {(catalog || []).slice(0, 24).map((item) => (
                      <Button
                        key={item.id}
                        size="small"
                        variant={exchangePick?.item_id === item.id ? 'contained' : 'outlined'}
                        onClick={() =>
                          setExchangePick({
                            item_id: item.id,
                            label: item.name,
                          })
                        }
                      >
                        {item.name}
                        {item.isbn ? ` · ${item.isbn}` : ''}
                      </Button>
                    ))}
                  </Stack>
                  {exchangePick ? (
                    <Alert severity="info" sx={{ mt: 1 }}>
                      Exchanging into {exchangePick.label}
                    </Alert>
                  ) : null}
                </Box>
              ) : null}
              {kind === 'EXCHANGE' && hasSerialLines ? (
                <Stack spacing={2}>
                  {selectedLines
                    .filter((line) => line.is_serial)
                    .map((line) => (
                      <Autocomplete
                        key={line.bill_item_id}
                        options={serialStock.filter(
                          (unit) =>
                            unit.item_id === line.item_id &&
                            unit.id !== line.serial_unit_id &&
                            unit.status === 'IN_STOCK',
                        )}
                        getOptionLabel={(option) => `${option.serial} · ${option.item_name || line.item_name}`}
                        value={exchangeSerialByLine[line.bill_item_id] || null}
                        onChange={(_, value) =>
                          setExchangeSerialByLine((prev) => ({ ...prev, [line.bill_item_id]: value }))
                        }
                        renderInput={(params) => (
                          <TextField
                            {...params}
                            label={`Replacement IMEI for ${line.serial_number || line.item_name}`}
                            required
                          />
                        )}
                      />
                    ))}
                  <Typography variant="body2" color="text.secondary">
                    The returned IMEI is quarantined; the replacement is bound to the original bill line.
                  </Typography>
                </Stack>
              ) : null}
            </Stack>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWizardOpen(false)} disabled={saving}>
            Cancel
          </Button>
          {step === 0 ? (
            <Button variant="contained" onClick={searchBill} disabled={!billNumber.trim()}>
              Find bill
            </Button>
          ) : null}
          {step === 1 ? (
            <>
              <Button onClick={() => setStep(0)}>Back</Button>
              <Button variant="contained" onClick={goConfirm}>
                Next
              </Button>
            </>
          ) : null}
          {step === 2 ? (
            <>
              <Button onClick={() => setStep(1)} disabled={saving}>
                Back
              </Button>
              <Button variant="contained" onClick={submit} disabled={saving}>
                {saving ? 'Saving…' : 'Confirm'}
              </Button>
            </>
          ) : null}
        </DialogActions>
      </Dialog>
    </>
  );
}
