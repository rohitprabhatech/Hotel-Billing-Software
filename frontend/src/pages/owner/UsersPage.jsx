import AddOutlinedIcon from '@mui/icons-material/AddOutlined';
import DeleteOutlineOutlinedIcon from '@mui/icons-material/DeleteOutlineOutlined';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import LockResetOutlinedIcon from '@mui/icons-material/LockResetOutlined';
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
import { useEffect, useMemo, useState } from 'react';
import EmptyState from '../../components/EmptyState';
import PageShell from '../../components/PageShell';
import TableCard from '../../components/TableCard';
import TruncateText from '../../components/TruncateText';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import IconActionButton from '../../components/ui/IconActionButton';
import LoadingSkeleton from '../../components/ui/LoadingSkeleton';
import StatusBadge from '../../components/ui/StatusBadge';
import { PageActions } from '../../context/PageActionsContext';
import { useAuth } from '../../context/AuthContext';
import {
  createTenantUser,
  listUsers,
  resetUserPassword,
  updateUser,
} from '../../services/userService';
import { getApiErrorMessage } from '../../utils/apiError';

const emptyForm = { name: '', email: '', password: '', role: 'BILLING_USER' };

const ASSIGNABLE_ROLES = [
  { value: 'BILLING_USER', label: 'Billing User' },
  { value: 'MANAGER', label: 'Manager' },
];

function roleLabel(role) {
  return ASSIGNABLE_ROLES.find((r) => r.value === role)?.label || role;
}

function isValidCreateForm(form) {
  const name = form.name.trim();
  const email = form.email.trim();
  return (
    name.length > 0 &&
    email.includes('@') &&
    email.includes('.') &&
    form.password.length >= 8
  );
}

export default function UsersPage() {
  const { user: authUser } = useAuth();
  const isHotel = authUser?.tenant?.business_type === 'hotel_restaurant';
  const [users, setUsers] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [resetUser, setResetUser] = useState(null);
  const [resetPassword, setResetPassword] = useState('');
  const [editUser, setEditUser] = useState(null);
  const [editForm, setEditForm] = useState({ name: '', email: '', is_active: true });
  const [deleteUser, setDeleteUser] = useState(null);

  const visibleUsers = useMemo(() => {
    if (!isHotel) return users;
    return users.filter((u) => u.role === 'BILLING_USER' || u.role === 'MANAGER');
  }, [users, isHotel]);

  const load = async () => {
    setError('');
    try {
      const response = await listUsers();
      setUsers(response.data || []);
    } catch (err) {
      setError(getApiErrorMessage(err, 'Unable to load users. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onCreate = async () => {
    if (!isValidCreateForm(form)) {
      setError('Enter name, a valid email, and a password with at least 8 characters.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await createTenantUser({
        name: form.name.trim(),
        email: form.email.trim(),
        password: form.password,
        role: isHotel ? 'BILLING_USER' : form.role,
      });
      setOpen(false);
      setForm(emptyForm);
      setSuccess('User created successfully.');
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to create user'));
    } finally {
      setSaving(false);
    }
  };

  const openEditDialog = (user) => {
    setEditUser(user);
    setEditForm({
      name: user.name || '',
      email: user.email || '',
      is_active: user.is_active,
    });
  };

  const onSaveEdit = async () => {
    if (!editUser) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateUser(editUser.id, {
        name: editForm.name.trim(),
        email: editForm.email.trim(),
        is_active: editForm.is_active,
      });
      setSuccess('User updated successfully.');
      setEditUser(null);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to update user'));
    } finally {
      setSaving(false);
    }
  };

  const onDeactivateUser = async () => {
    if (!deleteUser) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await updateUser(deleteUser.id, { is_active: false });
      setSuccess(`${deleteUser.name} has been deactivated.`);
      setDeleteUser(null);
      await load();
    } catch (err) {
      setError(getApiErrorMessage(err, 'Failed to deactivate user'));
    } finally {
      setSaving(false);
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
      setError(getApiErrorMessage(err, 'Failed to reset password'));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageActions>
        <Button variant="contained" startIcon={<AddOutlinedIcon />} onClick={() => setOpen(true)}>
          {isHotel ? 'Add Billing User' : 'Add User'}
        </Button>
      </PageActions>

      <PageShell>
        {isHotel ? (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Manage billing counter users. Deactivated users remain on historical bills and audit records.
          </Typography>
        ) : null}
        {error ? <Alert severity="error">{error}</Alert> : null}
        {success ? <Alert severity="success">{success}</Alert> : null}

        <TableCard>
          {loading ? (
            <Box sx={{ p: 2 }}>
              <LoadingSkeleton rows={5} height={56} />
            </Box>
          ) : (
            <Table size="small" sx={{ minWidth: 780 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  {!isHotel ? <TableCell>Role</TableCell> : null}
                  <TableCell>Status</TableCell>
                  <TableCell>Last Login</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {visibleUsers.map((user) => (
                  <TableRow key={user.id} hover>
                    <TableCell>
                      <TruncateText value={user.name} maxWidth={160} />
                    </TableCell>
                    <TableCell>
                      <TruncateText value={user.email} maxWidth={220} />
                    </TableCell>
                    {!isHotel ? (
                      <TableCell>
                        <StatusBadge label={roleLabel(user.role)} variant="info" />
                      </TableCell>
                    ) : null}
                    <TableCell>
                      <StatusBadge label={user.is_active ? 'Active' : 'Unavailable'} />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'nowrap' }}>
                        {user.last_login_at ? new Date(user.last_login_at).toLocaleString() : '—'}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      {user.role !== 'OWNER' ? (
                        <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                          <IconActionButton title="Edit Billing User" onClick={() => openEditDialog(user)}>
                            <EditOutlinedIcon fontSize="small" />
                          </IconActionButton>
                          {user.is_active ? (
                            <IconActionButton
                              title="Delete Billing User"
                              color="error"
                              onClick={() => setDeleteUser(user)}
                            >
                              <DeleteOutlineOutlinedIcon fontSize="small" />
                            </IconActionButton>
                          ) : null}
                          <IconActionButton title="Reset password" onClick={() => setResetUser(user)}>
                            <LockResetOutlinedIcon fontSize="small" />
                          </IconActionButton>
                        </Stack>
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
          {!loading && !visibleUsers.length ? (
            <EmptyState
              title={isHotel ? 'No billing users found' : 'No users found'}
              description={
                isHotel
                  ? 'Create a billing user to start counter operations.'
                  : 'Create a billing user to start counter operations.'
              }
              actionLabel={isHotel ? 'Add Billing User' : 'Add User'}
              onAction={() => setOpen(true)}
            />
          ) : null}
        </TableCard>
      </PageShell>

      <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm">
        <DialogTitle>{isHotel ? 'Add Billing User' : 'Add User'}</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            {!isHotel ? (
              <FormControl fullWidth required>
                <InputLabel id="user-role-label">Role</InputLabel>
                <Select
                  labelId="user-role-label"
                  label="Role"
                  value={form.role}
                  onChange={(e) => setForm((f) => ({ ...f, role: e.target.value }))}
                >
                  {ASSIGNABLE_ROLES.map((option) => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : null}
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
          <Button
            variant="contained"
            onClick={onCreate}
            disabled={saving || !isValidCreateForm(form)}
          >
            {saving ? 'Saving...' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={Boolean(editUser)} onClose={() => setEditUser(null)} fullWidth maxWidth="sm">
        <DialogTitle>Edit Billing User</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ mt: 1 }}>
            <TextField
              label="Name"
              value={editForm.name}
              onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))}
              fullWidth
              required
            />
            <TextField
              label="Email"
              type="email"
              value={editForm.email}
              onChange={(e) => setEditForm((f) => ({ ...f, email: e.target.value }))}
              fullWidth
              required
            />
            <FormControl fullWidth>
              <InputLabel id="edit-user-status-label">Status</InputLabel>
              <Select
                labelId="edit-user-status-label"
                label="Status"
                value={editForm.is_active ? 'active' : 'inactive'}
                onChange={(e) =>
                  setEditForm((f) => ({ ...f, is_active: e.target.value === 'active' }))
                }
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditUser(null)}>Cancel</Button>
          <Button variant="contained" onClick={onSaveEdit} disabled={saving}>
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={Boolean(deleteUser)}
        title="Delete Billing User?"
        description={`Deactivate ${deleteUser?.name || 'this user'}? Historical bills and audit records will still show their name.`}
        confirmLabel="Delete"
        loading={saving}
        onClose={() => setDeleteUser(null)}
        onConfirm={onDeactivateUser}
      />

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
