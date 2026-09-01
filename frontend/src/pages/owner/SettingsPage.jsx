import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import FormSection from '../../components/FormSection';
import LoadingSkeleton from '../../components/ui/LoadingSkeleton';
import PageShell from '../../components/PageShell';
import SubscriptionPlanInfo from '../../components/SubscriptionPlanInfo';
import ThemeModeToggle from '../../components/ThemeModeToggle';
import { useAuth } from '../../context/AuthContext';
import { useColorMode } from '../../context/ColorModeContext';
import { PATHS } from '../../routes/paths';
import { SUBSCRIPTION_PLAN } from '../../constants/company';
import {
  fetchProfile,
  requestEmailChange,
  updateProfileRequest,
} from '../../services/authService';
import {
  fetchBusinessTypes,
  fetchBillingSettings,
  fetchMyTenant,
  fetchWhatsappConfig,
  saveWhatsappConfig,
  testWhatsappConfig,
  disconnectWhatsappConfig,
  simulateWhatsappDeliveryStatus,
  updateBillingSettings,
  updateMyTenant,
} from '../../services/tenantService';
import BillPreview from '../../print/BillPreview';
import '../../print/receipt.css';

const emptyBusiness = {
  name: '',
  business_name: '',
  business_type: '',
  address: '',
  city: '',
  state: '',
  pincode: '',
  phone: '',
  email: '',
  gst_number: '',
  fssai_number: '',
  bill_number_prefix: '',
};

export default function SettingsPage() {
  const { user, login } = useAuth();
  const { mode } = useColorMode();
  const [business, setBusiness] = useState(emptyBusiness);
  const [businessTypes, setBusinessTypes] = useState([]);
  const [profileName, setProfileName] = useState('');
  const [profilePhone, setProfilePhone] = useState('');
  const [profileEmail, setProfileEmail] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [savingBusiness, setSavingBusiness] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [waStatus, setWaStatus] = useState(null);
  const [waForm, setWaForm] = useState({
    phone_number_id: '',
    waba_id: '',
    access_token: '',
    display_phone: '',
    template_name: '',
    template_language: 'en',
  });
  const [waSaving, setWaSaving] = useState(false);
  const [waTesting, setWaTesting] = useState(false);
  const [waSimForm, setWaSimForm] = useState({
    provider_message_id: '',
    status: 'delivered',
    error_message: '',
  });
  const [waSimulating, setWaSimulating] = useState(false);
  const [billingForm, setBillingForm] = useState({
    paper_size: '80mm',
    width_mm: 80,
    height_mm: '',
  });
  const [savingBilling, setSavingBilling] = useState(false);
  const [showBillPreview, setShowBillPreview] = useState(false);

  const isHotel = user?.tenant?.business_type === 'hotel_restaurant';

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchMyTenant(), fetchProfile(), fetchBusinessTypes(), fetchWhatsappConfig(), fetchBillingSettings()])
      .then(([tenantRes, profileRes, typesRes, waRes, billingRes]) => {
        const t = tenantRes.data || {};
        setBusiness({
          name: t.name || '',
          business_name: t.business_name || '',
          business_type: t.business_type || 'other',
          address: t.address || '',
          city: t.city || '',
          state: t.state || '',
          pincode: t.pincode || '',
          phone: t.phone || '',
          email: t.email || '',
          gst_number: t.gst_number || '',
          fssai_number: t.fssai_number || '',
          bill_number_prefix: t.bill_number_prefix || '',
        });
        setBusinessTypes(typesRes.data?.business_types || []);
        const profile = profileRes.data || {};
        setProfileName(profile.name || '');
        setProfilePhone(profile.phone || '');
        setProfileEmail(profile.email || '');
        const wa = waRes.data || {};
        setWaStatus(wa);
        setWaForm((prev) => ({
          ...prev,
          display_phone: wa.display_phone_e164 || '',
          template_name: wa.template_name || '',
          template_language: wa.template_language || 'en',
          phone_number_id: '',
          waba_id: '',
          access_token: '',
        }));
        const bs = billingRes.data || {};
        setBillingForm({
          paper_size: bs.paper_size || '80mm',
          width_mm: bs.width_mm || 80,
          height_mm: bs.height_mm ?? '',
        });
      })
      .catch((err) => {
        setError(err.response?.data?.error?.message || 'Unable to load settings.');
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (loading) return undefined;
    if (window.location.hash !== '#subscription') return undefined;
    const timer = window.setTimeout(() => {
      document.getElementById('subscription')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
    return () => window.clearTimeout(timer);
  }, [loading]);

  const onBusinessChange = (field) => (event) => {
    setBusiness((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const selectedType = businessTypes.find((row) => row.code === business.business_type);
  const showFssaiHint = selectedType?.fssai_relevant ?? false;

  const onSaveBusiness = async (event) => {
    event.preventDefault();
    setSavingBusiness(true);
    setError('');
    setSuccess('');
    try {
      const response = await updateMyTenant(business);
      if (response.data) {
        setBusiness((prev) => ({
          ...prev,
          ...response.data,
          business_type: response.data.business_type || prev.business_type,
        }));
      }
      setSuccess('Business information updated successfully.');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save business settings');
    } finally {
      setSavingBusiness(false);
    }
  };

  const onSaveBilling = async (event) => {
    event.preventDefault();
    setSavingBilling(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        paper_size: billingForm.paper_size,
        width_mm: billingForm.paper_size === 'custom' ? Number(billingForm.width_mm) : undefined,
        height_mm:
          billingForm.paper_size === 'custom' && billingForm.height_mm !== ''
            ? Number(billingForm.height_mm)
            : null,
      };
      const response = await updateBillingSettings(payload);
      setBillingForm({
        paper_size: response.data?.paper_size || billingForm.paper_size,
        width_mm: response.data?.width_mm || billingForm.width_mm,
        height_mm: response.data?.height_mm ?? '',
      });
      setSuccess('Billing / invoice settings saved.');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save billing settings');
    } finally {
      setSavingBilling(false);
    }
  };

  const previewBill = {
    bill_number: 'PREVIEW-001',
    created_at: new Date().toISOString(),
    table_number: 'T-01',
    created_by_name: user?.name || 'Staff',
    payment_method: 'cash',
    subtotal: 450,
    discount: 0,
    taxable_amount: 450,
    cgst_amount: 11.25,
    sgst_amount: 11.25,
    round_off: 0,
    grand_total: 472.5,
    status: 'FINALIZED',
    items: [
      {
        id: '1',
        item_name: 'Sample Dish',
        quantity: 2,
        unit_price: 150,
        gst_percentage: 5,
      },
      {
        id: '2',
        item_name: 'Sample Beverage',
        quantity: 1,
        unit_price: 150,
        gst_percentage: 5,
      },
    ],
    tenant: {
      business_name: business.business_name || 'Your Business',
      business_type: business.business_type,
      address: business.address,
      city: business.city,
      pincode: business.pincode,
      phone: business.phone,
      gst_number: business.gst_number,
      fssai_number: business.fssai_number,
      billing_settings: {
        paper_size: billingForm.paper_size,
        width_mm: billingForm.paper_size === 'custom' ? Number(billingForm.width_mm) : billingForm.width_mm,
        height_mm:
          billingForm.height_mm === '' || billingForm.height_mm == null
            ? null
            : Number(billingForm.height_mm),
      },
    },
  };

  const onSaveProfile = async (event) => {
    event.preventDefault();
    setSavingProfile(true);
    setError('');
    setSuccess('');
    try {
      const response = await updateProfileRequest({ name: profileName, phone: profilePhone });
      setSuccess('Profile updated successfully.');
      if (user && response.data) {
        const token = localStorage.getItem('access_token');
        login(token, {
          ...user,
          ...response.data,
          tenant: response.data.tenant || user.tenant,
        });
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to save profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const onRequestEmailChange = async (event) => {
    event.preventDefault();
    setEmailLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await requestEmailChange({ new_email: newEmail });
      setSuccess(response.data?.message || 'Verification email sent.');
      setNewEmail('');
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Failed to request email change');
    } finally {
      setEmailLoading(false);
    }
  };

  if (loading) {
    return (
      <PageShell maxWidth={880}>
        <LoadingSkeleton rows={6} height={88} />
      </PageShell>
    );
  }

  return (
    <PageShell maxWidth={880}>
      <Stack spacing={3}>
      {error ? <Alert severity="error">{error}</Alert> : null}
      {success ? <Alert severity="success">{success}</Alert> : null}

      <FormSection
        title="Profile"
        description="Your personal account details for this business."
      >
        <Stack component="form" spacing={2.5} onSubmit={onSaveProfile}>
          <Box
            sx={{
              display: 'grid',
              gap: 2.5,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            }}
          >
            <TextField
              label="Owner Name"
              value={profileName}
              onChange={(e) => setProfileName(e.target.value)}
              required
              fullWidth
            />
            <TextField
              label="Mobile"
              value={profilePhone}
              onChange={(e) => setProfilePhone(e.target.value)}
              fullWidth
            />
            <TextField
              label="Email"
              value={profileEmail}
              fullWidth
              disabled
              helperText="Use Email / Account below to change email"
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
          </Box>
          <Button
            type="submit"
            variant="contained"
            disabled={savingProfile}
            sx={{ alignSelf: 'flex-start' }}
          >
            {savingProfile ? 'Saving...' : 'Save Changes'}
          </Button>
        </Stack>
      </FormSection>

      <FormSection
        title="Business Information"
        description="Details shown on receipts and used across billing."
      >
        <Stack component="form" spacing={2.5} onSubmit={onSaveBusiness}>
          <Box
            sx={{
              display: 'grid',
              gap: 2.5,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            }}
          >
            <TextField
              label="Display Name"
              value={business.name}
              onChange={onBusinessChange('name')}
              required
              fullWidth
            />
            <TextField
              label="Business Name"
              value={business.business_name}
              onChange={onBusinessChange('business_name')}
              required
              fullWidth
            />
            <FormControl fullWidth required>
              <InputLabel id="settings-business-type-label">Business Type</InputLabel>
              <Select
                labelId="settings-business-type-label"
                label="Business Type"
                value={business.business_type || ''}
                onChange={onBusinessChange('business_type')}
              >
                {businessTypes.map((row) => (
                  <MenuItem key={row.code} value={row.code}>
                    {row.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Address"
              value={business.address}
              onChange={onBusinessChange('address')}
              fullWidth
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
            <TextField label="City" value={business.city} onChange={onBusinessChange('city')} fullWidth />
            <TextField label="State" value={business.state} onChange={onBusinessChange('state')} fullWidth />
            <TextField
              label="Pincode"
              value={business.pincode}
              onChange={onBusinessChange('pincode')}
              fullWidth
            />
            <TextField
              label="Phone"
              value={business.phone}
              onChange={onBusinessChange('phone')}
              fullWidth
            />
            <TextField
              label="Business Email"
              value={business.email}
              onChange={onBusinessChange('email')}
              fullWidth
            />
            <TextField
              label="GSTIN"
              value={business.gst_number}
              onChange={onBusinessChange('gst_number')}
              fullWidth
            />
            <TextField
              label="FSSAI (optional)"
              value={business.fssai_number}
              onChange={onBusinessChange('fssai_number')}
              fullWidth
              helperText={
                showFssaiHint
                  ? 'Relevant for restaurants and hotels'
                  : 'Optional — usually not required for this business type'
              }
            />
            <TextField
              label="Bill Number Prefix"
              value={business.bill_number_prefix}
              onChange={onBusinessChange('bill_number_prefix')}
              helperText="Example: INV-A-"
              fullWidth
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
          </Box>
          <Button
            type="submit"
            variant="contained"
            disabled={savingBusiness}
            sx={{ alignSelf: 'flex-start' }}
          >
            {savingBusiness ? 'Saving...' : 'Save Changes'}
          </Button>
        </Stack>
      </FormSection>

      {isHotel ? (
        <FormSection
          title="Billing / Invoice Settings"
          description="Configure the printed bill format for all billing users. Counter staff only see Print — not these controls."
        >
          <Stack component="form" spacing={2.5} onSubmit={onSaveBilling} maxWidth={640}>
            <FormControl fullWidth>
              <InputLabel id="paper-size-label">Paper / Bill Size</InputLabel>
              <Select
                labelId="paper-size-label"
                label="Paper / Bill Size"
                value={billingForm.paper_size}
                onChange={(e) => {
                  const paper = e.target.value;
                  const presets = {
                    '58mm': 58,
                    '80mm': 80,
                    A4: 210,
                    A5: 148,
                  };
                  setBillingForm((prev) => ({
                    ...prev,
                    paper_size: paper,
                    width_mm: presets[paper] || prev.width_mm,
                    height_mm: paper === 'A4' ? 297 : paper === 'A5' ? 210 : '',
                  }));
                }}
              >
                <MenuItem value="58mm">58mm Thermal</MenuItem>
                <MenuItem value="80mm">80mm Thermal</MenuItem>
                <MenuItem value="A4">A4</MenuItem>
                <MenuItem value="A5">A5</MenuItem>
                <MenuItem value="custom">Custom</MenuItem>
              </Select>
            </FormControl>
            <Box
              sx={{
                display: 'grid',
                gap: 2,
                gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
              }}
            >
              <TextField
                label="Width (mm)"
                type="number"
                value={billingForm.width_mm}
                onChange={(e) => setBillingForm((p) => ({ ...p, width_mm: e.target.value }))}
                disabled={billingForm.paper_size !== 'custom'}
                inputProps={{ min: 40, max: 300 }}
                fullWidth
              />
              <TextField
                label="Height (mm)"
                type="number"
                value={billingForm.height_mm}
                onChange={(e) => setBillingForm((p) => ({ ...p, height_mm: e.target.value }))}
                disabled={billingForm.paper_size !== 'custom'}
                placeholder="Auto"
                inputProps={{ min: 50, max: 500 }}
                fullWidth
                helperText="Leave blank for auto height on thermal rolls"
              />
            </Box>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
              <Button type="submit" variant="contained" disabled={savingBilling}>
                {savingBilling ? 'Saving…' : 'Save Settings'}
              </Button>
              <Button type="button" variant="outlined" onClick={() => setShowBillPreview((v) => !v)}>
                {showBillPreview ? 'Hide Preview' : 'Preview Bill'}
              </Button>
            </Stack>
            {showBillPreview ? (
              <Box sx={{ pt: 1 }}>
                <BillPreview bill={previewBill} billingSettings={previewBill.tenant.billing_settings} />
              </Box>
            ) : null}
          </Stack>
        </FormSection>
      ) : null}

      <FormSection
        title="WhatsApp Business Integration"
        description="Configure official WhatsApp Cloud API credentials for this business only. Access tokens are stored securely on the server and never shown again."
      >
        <Stack spacing={2.5} maxWidth={640}>
          <Typography variant="body2">
            Status:{' '}
            <strong>
              {waStatus?.status === 'connected' ? 'Connected' : 'Not Connected'}
            </strong>
            {waStatus?.has_token ? ' · Token on file' : ''}
          </Typography>
          {waStatus?.phone_number_id_masked ? (
            <Typography variant="body2" color="text.secondary">
              Phone Number ID: {waStatus.phone_number_id_masked}
            </Typography>
          ) : null}
          {waStatus?.waba_id_masked ? (
            <Typography variant="body2" color="text.secondary">
              WhatsApp Business Account: {waStatus.waba_id_masked}
            </Typography>
          ) : null}
          {waStatus?.display_phone_e164 ? (
            <Typography variant="body2" color="text.secondary">
              Business phone: {waStatus.display_phone_e164}
            </Typography>
          ) : null}
          <Box
            sx={{
              display: 'grid',
              gap: 2,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
            }}
          >
            <TextField
              label="Phone Number ID"
              value={waForm.phone_number_id}
              onChange={(e) => setWaForm((p) => ({ ...p, phone_number_id: e.target.value }))}
              fullWidth
              placeholder={waStatus?.has_token ? 'Leave blank to keep current' : ''}
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
            <TextField
              label="WhatsApp Business Account ID"
              value={waForm.waba_id}
              onChange={(e) => setWaForm((p) => ({ ...p, waba_id: e.target.value }))}
              fullWidth
              placeholder={waStatus?.has_token ? 'Leave blank to keep current' : ''}
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
            <TextField
              label="Access Token"
              type="password"
              value={waForm.access_token}
              onChange={(e) => setWaForm((p) => ({ ...p, access_token: e.target.value }))}
              fullWidth
              autoComplete="new-password"
              helperText="Write-only — never displayed after save"
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
            <TextField
              label="Display phone (optional)"
              value={waForm.display_phone}
              onChange={(e) => setWaForm((p) => ({ ...p, display_phone: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Template language"
              value={waForm.template_language}
              onChange={(e) => setWaForm((p) => ({ ...p, template_language: e.target.value }))}
              fullWidth
            />
            <TextField
              label="Approved template name"
              value={waForm.template_name}
              onChange={(e) => setWaForm((p) => ({ ...p, template_name: e.target.value }))}
              fullWidth
              helperText="Must match a Meta-approved WhatsApp template"
              sx={{ gridColumn: { sm: '1 / -1' } }}
            />
          </Box>
          <Stack direction="row" spacing={1.5} useFlexGap flexWrap="wrap">
            <Button
              variant="contained"
              disabled={waSaving}
              onClick={async () => {
                setWaSaving(true);
                setError('');
                setSuccess('');
                try {
                  const payload = {
                    template_name: waForm.template_name,
                    template_language: waForm.template_language,
                    display_phone: waForm.display_phone || null,
                  };
                  if (waForm.phone_number_id.trim()) {
                    payload.phone_number_id = waForm.phone_number_id.trim();
                  }
                  if (waForm.waba_id.trim()) payload.waba_id = waForm.waba_id.trim();
                  if (waForm.access_token.trim()) {
                    payload.access_token = waForm.access_token.trim();
                  }
                  const res = await saveWhatsappConfig(payload);
                  setWaStatus(res.data);
                  setWaForm((p) => ({ ...p, access_token: '', phone_number_id: '', waba_id: '' }));
                  setSuccess('WhatsApp configuration saved.');
                } catch (err) {
                  setError(err.response?.data?.error?.message || 'Failed to save WhatsApp settings.');
                } finally {
                  setWaSaving(false);
                }
              }}
            >
              {waSaving ? 'Saving...' : 'Save Configuration'}
            </Button>
            <Button
              variant="outlined"
              disabled={waTesting || waStatus?.status !== 'connected'}
              onClick={async () => {
                setWaTesting(true);
                setError('');
                setSuccess('');
                try {
                  const res = await testWhatsappConfig();
                  setSuccess(res.data?.message || 'WhatsApp connection successful.');
                  if (res.data?.display_phone) {
                    setWaStatus((s) => ({
                      ...(s || {}),
                      display_phone_e164: res.data.display_phone,
                    }));
                  }
                } catch (err) {
                  setError(err.response?.data?.error?.message || 'WhatsApp test failed.');
                } finally {
                  setWaTesting(false);
                }
              }}
            >
              {waTesting ? 'Testing...' : 'Test Connection'}
            </Button>
            <Button
              color="warning"
              variant="outlined"
              disabled={waStatus?.status !== 'connected'}
              onClick={async () => {
                setError('');
                setSuccess('');
                try {
                  const res = await disconnectWhatsappConfig();
                  setWaStatus(res.data);
                  setSuccess('WhatsApp disconnected for this business.');
                } catch (err) {
                  setError(err.response?.data?.error?.message || 'Failed to disconnect WhatsApp.');
                }
              }}
            >
              Disconnect
            </Button>
          </Stack>
          {waStatus?.provider === 'mock' ? (
            <Box
              sx={{
                mt: 1,
                p: 2,
                borderRadius: 1,
                border: '1px dashed',
                borderColor: 'divider',
              }}
            >
              <Typography variant="subtitle2" gutterBottom>
                Mock delivery webhook simulator
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
                Paste a provider message id from a sent bill (visible in bill delivery history) to
                advance status without Meta. Only available when WHATSAPP_PROVIDER=mock.
              </Typography>
              <Box
                sx={{
                  display: 'grid',
                  gap: 1.5,
                  gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
                  mb: 1.5,
                }}
              >
                <TextField
                  label="Provider message id"
                  value={waSimForm.provider_message_id}
                  onChange={(e) =>
                    setWaSimForm((p) => ({ ...p, provider_message_id: e.target.value }))
                  }
                  fullWidth
                  sx={{ gridColumn: { sm: '1 / -1' } }}
                />
                <FormControl fullWidth>
                  <InputLabel>Simulated status</InputLabel>
                  <Select
                    label="Simulated status"
                    value={waSimForm.status}
                    onChange={(e) => setWaSimForm((p) => ({ ...p, status: e.target.value }))}
                  >
                    <MenuItem value="sent">sent</MenuItem>
                    <MenuItem value="delivered">delivered</MenuItem>
                    <MenuItem value="read">read</MenuItem>
                    <MenuItem value="failed">failed</MenuItem>
                  </Select>
                </FormControl>
                {waSimForm.status === 'failed' ? (
                  <TextField
                    label="Error message"
                    value={waSimForm.error_message}
                    onChange={(e) =>
                      setWaSimForm((p) => ({ ...p, error_message: e.target.value }))
                    }
                    fullWidth
                  />
                ) : null}
              </Box>
              <Button
                variant="outlined"
                disabled={waSimulating || !waSimForm.provider_message_id.trim()}
                onClick={async () => {
                  setWaSimulating(true);
                  setError('');
                  setSuccess('');
                  try {
                    const payload = {
                      provider_message_id: waSimForm.provider_message_id.trim(),
                      status: waSimForm.status,
                    };
                    if (waSimForm.status === 'failed' && waSimForm.error_message.trim()) {
                      payload.error_message = waSimForm.error_message.trim();
                    }
                    const res = await simulateWhatsappDeliveryStatus(payload);
                    setSuccess(
                      `Simulated WhatsApp status → ${res.data?.status || waSimForm.status.toUpperCase()}.`,
                    );
                  } catch (err) {
                    setError(
                      err.response?.data?.error?.message || 'Failed to simulate delivery status.',
                    );
                  } finally {
                    setWaSimulating(false);
                  }
                }}
              >
                {waSimulating ? 'Simulating...' : 'Simulate webhook status'}
              </Button>
            </Box>
          ) : null}
        </Stack>
      </FormSection>

      <Box id="subscription">
        <FormSection
          title="Subscription"
          description={`${SUBSCRIPTION_PLAN.priceDisplay} · informational plan details (no in-app payment).`}
        >
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            Current status:{' '}
            <strong>{user?.tenant?.subscription?.status || 'None'}</strong>
            {user?.tenant?.subscription?.remaining_days != null
              ? ` · ${user.tenant.subscription.remaining_days} days remaining`
              : user?.tenant?.subscription?.is_complimentary
                ? ' · complimentary (no expiry)'
                : ''}
          </Typography>
          <SubscriptionPlanInfo variant="owner" dense />
        </FormSection>
      </Box>

      <FormSection
        title="Appearance"
        description="Choose light or dark mode. Your preference is saved on this device."
        actions={<ThemeModeToggle />}
      >
        <Typography variant="body2" color="text.secondary">
          Current theme: <strong>{mode === 'dark' ? 'Dark' : 'Light'}</strong>
        </Typography>
      </FormSection>

      <FormSection
        title="Security"
        description="Keep your account secure with a strong password."
        actions={
          <Button
            component={RouterLink}
            to={PATHS.ownerChangePassword}
            variant="outlined"
            startIcon={<LockOutlinedIcon />}
          >
            Change Password
          </Button>
        }
      >
        <Typography variant="body2" color="text.secondary">
          You will be signed out after a successful password update.
        </Typography>
      </FormSection>

      <FormSection
        title="Email / Account"
        description="Request a change to your login email address."
      >
        <Stack component="form" spacing={2.5} onSubmit={onRequestEmailChange} maxWidth={480}>
          <TextField label="Current Email" value={profileEmail} fullWidth disabled />
          <TextField
            label="New Email"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            required
            fullWidth
          />
          <Button
            type="submit"
            variant="contained"
            disabled={emailLoading}
            sx={{ alignSelf: 'flex-start' }}
          >
            {emailLoading ? 'Sending...' : 'Request Email Change'}
          </Button>
        </Stack>
      </FormSection>
      </Stack>
    </PageShell>
  );
}
