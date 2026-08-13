import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import LockResetOutlinedIcon from '@mui/icons-material/LockResetOutlined';
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  IconButton,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import { PageActions } from '../../context/PageActionsContext';
import {
  createBillingUser,
  listUsers,
  resetUserPassword,
  updateUser,
} from '../../services/userService';

const emptyForm = { name: '', email: '', password: '' };

export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [resetUser, setResetUser] = useState(null);
  const [resetPassword, setResetPassword] = useState('');

  const load = async () => {
    setError('');
    try {
      const response = await listUsers();
      setUsers(response.data || []);
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Unable to load users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onCreate = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await createBillingUser(form);
      setOpen(false);
      setForm(emptyForm);
      setSuccess('Billing user created successfully.');
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to create user');
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (user) => {
    setError('');
    try {
      await updateUser(user.id, { is_active: !user.is_active });
      await load();
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to update user');
    }
  };

  const onResetPassword = async () => {
    if (!resetUser) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await resetUserPassword(resetUser.id, resetPassword);
      setSuccess('Password updated successfully.');
      setResetUser(null);
      setResetPassword('');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to reset password');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageActions>
        <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={() => setOpen(true)}>
          Add Billing User
        </Button>
      </PageActions>

      <PageShell>
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <TableCard>
          {loading ? (
            <Box sx={{ py: 8, display: 'grid', placeItems: 'center' }}>
              <CircularProgress size={28} />
            </Box>
          ) : (
            <Table size="small" sx={{ minWidth: 780 }}>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: '16%' }}>Name</TableCell>
                  <TableCell sx={{ width: '22%' }}>Email</TableCell>
                  <TableCell sx={{ width: '12%' }}>Role</TableCell>
                  <TableCell sx={{ width: '14%' }}>Status</TableCell>
                  <TableCell sx={{ width: '16%' }}>Last Login</TableCell>
                  <TableCell sx={{ width: '12%' }}>Created At</TableCell>
                  <TableCell align="right" sx={{ width: '8%' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <TruncateText value={user.name} maxWidth={160} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={user.email} maxWidth={220} />
                    </TableCell>
                    <TableCell>
                      <Chip size="small" label={user.role} variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={1}>
                        <Switch
                          size="small"
                          checked={user.is_active}
                          onChange={() => toggleActive(user)}
                          disabled={user.role === 'OWNER'}
                          inputProps={{ 'aria-label': `Toggle ${user.name} active` }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {user.is_active ? 'Active' : 'Inactive'}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                        {user.last_login_at
                          ? new Date(user.last_login_at).toLocaleString()
                          : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {user.created_at ? new Date(user.created_at).toLocaleDateString() : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {user.role === 'BILLING_USER' ? (
                        <Tooltip title="Reset password">
                          <IconButton
                            size="small"
                            aria-label={`Reset password for ${user.name}`}
                            onClick={() => setResetUser(user)}
                          >
                            <LockResetOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      ) : (
                        <Typography variant="caption" color="text.secondary">
                          —
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          {!loading && !users.length ? (
            <EmptyState
              title="No users found"
              description="Create a billing user to start counter operations."
              actionLabel="Add Billing User"
              onAction={() => setOpen(true)}
            />
          ) : null}
        </TableCard>
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>Add Billing User</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              fullWidth
              required
            />
            <TextField
              label="Email"
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              fullWidth
              required
            />
            <TextField
              label="Password"
              type="password"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              fullWidth
              required
              helperText="Minimum 8 characters"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={onCreate} disabled={saving}>
            {saving ? 'Saving...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(resetUser)} onClose={() => setResetUser(null)} fullWidth maxWidth="xs">
        <DialogTitle>Reset Password</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Set a new password for {resetUser?.email}
            </Typography>
            <TextField
              label="New Password"
              type="password"
              value={resetPassword}
              onChange={(e) => setResetPassword(e.target.value)}
              fullWidth
              required
              helperText="Minimum 8 characters"
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetUser(null)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={onResetPassword}
            disabled={saving || resetPassword.length < 8}
          >
            {saving ? 'Updating...' : 'Update'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
