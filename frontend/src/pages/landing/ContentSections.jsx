import {
  Alert,
  Box,
  Button,
  Chip,
  Stack,
  Typography,
  useTheme,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { PATHS } from '../../routes/paths';
import {
  BILLING_CAPABILITIES,
  BUSINESSES,
  DISPLAY_FONT,
  FEATURES,
  OWNER_CAPABILITIES,
  SECURITY_POINTS,
  WORKFLOW_STEPS,
} from './constants';
import { LandingSection } from './LandingSection';

export function FeaturesSection() {
  return (
    <LandingSection
      id="features"
      eyebrow="Features"
      title="Everything the counter and the owner need"
      body="From fast GST bills to stock control, WhatsApp delivery, reports, and audit — without bolting on five other tools."
    >
      <Box
        sx={{
          display: 'grid',
          gap: { xs: 0, md: 0 },
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: 'repeat(4, 1fr)' },
          borderTop: '1px solid',
          borderColor: 'divider',
        }}
      >
        {FEATURES.map((f, idx) => (
          <Box
            key={f.n}
            sx={{
              py: { xs: 2.75, md: 3.25 },
              px: { xs: 0, sm: 2.25, lg: 2.5 },
              pr: { lg: 3 },
              borderBottom: '1px solid',
              borderRight: {
                xs: 'none',
                sm: idx % 2 === 0 ? '1px solid' : 'none',
                lg: (idx + 1) % 4 === 0 ? 'none' : '1px solid',
              },
              borderColor: 'divider',
              transition: 'background-color 0.2s ease',
              '&:hover': {
                bgcolor: (t) =>
                  t.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : 'rgba(31,78,95,0.028)',
              },
            }}
          >
            <Typography
              sx={{
                fontFamily: DISPLAY_FONT,
                fontWeight: 700,
                color: 'secondary.main',
                mb: 1.25,
                fontSize: '0.75rem',
                letterSpacing: '0.08em',
              }}
            >
              {f.n}
            </Typography>
            <Typography
              fontWeight={700}
              sx={{
                mb: 0.9,
                fontFamily: DISPLAY_FONT,
                fontSize: '1.05rem',
                letterSpacing: '-0.025em',
              }}
            >
              {f.title}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
              {f.body}
            </Typography>
          </Box>
        ))}
      </Box>
    </LandingSection>
  );
}

export function WorkflowSection() {
  return (
    <LandingSection
      id="how-it-works"
      tone="muted"
      eyebrow="How it works"
      title="From cart to professional bill — in seconds"
      body="A clear counter path: build the cart, apply tax and payment, then print or send."
    >
      <Box
        sx={{
          display: 'grid',
          gap: 0,
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(3, 1fr)' },
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 2,
          overflow: 'hidden',
          bgcolor: 'background.paper',
        }}
      >
        {WORKFLOW_STEPS.map((step, idx) => (
          <Box
            key={step}
            sx={{
              p: 2.5,
              borderRight: {
                xs: 'none',
                sm: idx % 2 === 0 ? '1px solid' : 'none',
                md: (idx + 1) % 3 === 0 ? 'none' : '1px solid',
              },
              borderBottom: {
                xs: idx < WORKFLOW_STEPS.length - 1 ? '1px solid' : 'none',
                sm: idx < WORKFLOW_STEPS.length - 2 ? '1px solid' : 'none',
                md: idx < 3 ? '1px solid' : 'none',
              },
              borderColor: 'divider',
            }}
          >
            <Typography
              variant="caption"
              color="secondary.main"
              fontWeight={700}
              sx={{ letterSpacing: '0.08em' }}
            >
              STEP {idx + 1}
            </Typography>
            <Typography
              fontWeight={650}
              sx={{ mt: 0.75, fontFamily: DISPLAY_FONT, letterSpacing: '-0.02em' }}
            >
              {step}
            </Typography>
          </Box>
        ))}
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2.5 }}>
        Every finalized bill records cash or online payment for cleaner reports.
      </Typography>
    </LandingSection>
  );
}

export function BillPreviewSection() {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const lines = [
    { name: 'Chicken Thali', qty: 2, rate: '180.00', amt: '360.00' },
    { name: 'Cold Drink 750ml', qty: 1, rate: '40.00', amt: '40.00' },
    { name: 'Rice 5kg', qty: 1, rate: '320.00', amt: '320.00' },
  ];

  return (
    <LandingSection
      id="resources"
      eyebrow="Resources"
      title="Professional bills your customers can trust"
      body="Preview shows the receipt structure used in the product — business details, lines, GST, and payment method. Policy pages are linked below."
    >
      <Box
        sx={{
          maxWidth: 360,
          mx: { xs: 0, sm: 'auto' },
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 2,
          bgcolor: isDark ? '#1a222b' : '#fff',
          p: 2.5,
          fontFamily: '"Source Sans 3", monospace',
          boxShadow: isDark ? 'none' : '0 12px 40px rgba(15,36,44,0.08)',
        }}
      >
        <Typography align="center" fontWeight={700} sx={{ fontFamily: DISPLAY_FONT }}>
          Shree Retail Store
        </Typography>
        <Typography align="center" variant="caption" color="text.secondary" display="block">
          Sample address · GSTIN example
        </Typography>
        <Typography align="center" variant="caption" color="text.secondary" display="block" sx={{ mb: 1.5 }}>
          Bill #1024 · 16 Aug 2026
        </Typography>
        <Box sx={{ borderTop: '1px dashed', borderColor: 'divider', pt: 1, mb: 1 }}>
          <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
            <Typography variant="caption" fontWeight={700}>
              Item
            </Typography>
            <Typography variant="caption" fontWeight={700}>
              Amt
            </Typography>
          </Stack>
          {lines.map((l) => (
            <Stack key={l.name} direction="row" justifyContent="space-between" sx={{ mb: 0.75 }}>
              <Box>
                <Typography variant="body2">{l.name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {l.qty} × ₹{l.rate}
                </Typography>
              </Box>
              <Typography variant="body2">₹{l.amt}</Typography>
            </Stack>
          ))}
        </Box>
        <Box sx={{ borderTop: '1px dashed', borderColor: 'divider', pt: 1 }}>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2">Subtotal</Typography>
            <Typography variant="body2">₹720.00</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between">
            <Typography variant="body2">GST</Typography>
            <Typography variant="body2">₹36.00</Typography>
          </Stack>
          <Stack direction="row" justifyContent="space-between" sx={{ mt: 0.75 }}>
            <Typography fontWeight={700}>Total</Typography>
            <Typography fontWeight={700}>₹756.00</Typography>
          </Stack>
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
            Payment: Cash
          </Typography>
        </Box>
      </Box>
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={1.5}
        sx={{ mt: 3, justifyContent: { sm: 'center' } }}
      >
        <Button component={RouterLink} to={PATHS.privacy} variant="outlined" size="small">
          Privacy Policy
        </Button>
        <Button component={RouterLink} to={PATHS.terms} variant="outlined" size="small">
          Terms of Service
        </Button>
        <Button href="#contact" variant="text" size="small">
          Contact support
        </Button>
      </Stack>
    </LandingSection>
  );
}

export function StockSection() {
  const rows = [
    { name: 'Rice 5 kg', stock: '4', status: 'Low Stock', color: 'warning' },
    { name: 'Cold Drink 750 ml', stock: '0', status: 'Out of Stock', color: 'error' },
    { name: 'Cotton Shirt M', stock: '42', status: 'In Stock', color: 'success' },
  ];

  return (
    <LandingSection
      id="solutions"
      tone="muted"
      eyebrow="Stock management"
      title="Stay ahead of low stock before the counter does"
      body="Prevent billing beyond available inventory and get notified when stock falls below your configured threshold."
    >
      <Box
        sx={{
          display: 'grid',
          gap: 3,
          gridTemplateColumns: { xs: '1fr', md: '1.1fr 0.9fr' },
          alignItems: 'start',
        }}
      >
        <Stack spacing={1.25}>
          {rows.map((r) => (
            <Stack
              key={r.name}
              direction="row"
              justifyContent="space-between"
              alignItems="center"
              sx={{
                p: 2,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper',
              }}
            >
              <Box>
                <Typography fontWeight={650}>{r.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Available stock: {r.stock}
                </Typography>
              </Box>
              <Chip size="small" label={r.status} color={r.color} />
            </Stack>
          ))}
        </Stack>
        <Stack spacing={1.5}>
          <Alert severity="warning">Rice 5kg has only 4 units remaining.</Alert>
          <Alert severity="error">Cold Drink 750ml is out of stock.</Alert>
          <Typography variant="body2" color="text.secondary">
            Owners and authorized Billing Users can receive operational stock notifications in the
            app.
          </Typography>
        </Stack>
      </Box>
    </LandingSection>
  );
}

export function AnalyticsSection() {
  const theme = useTheme();
  const accent = theme.palette.primary.main;
  const bars = [35, 48, 42, 60, 55, 78, 70];

  return (
    <LandingSection
      eyebrow="Sales analytics"
      title="See today’s, weekly, and monthly performance"
      body="Reports and dashboards help owners review sales trends and top-selling items — using your business’s own bill data."
    >
      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', md: '1.2fr 0.8fr' },
        }}
      >
        <Box
          sx={{
            p: 2.5,
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
            {[
              { l: "Today's Sales", v: '₹24,850' },
              { l: 'This Week', v: '₹1,42,300' },
              { l: 'This Month', v: '₹5,18,900' },
            ].map((k) => (
              <Box key={k.l} sx={{ minWidth: 120 }}>
                <Typography variant="caption" color="text.secondary">
                  {k.l}
                </Typography>
                <Typography fontWeight={700} sx={{ fontFamily: DISPLAY_FONT }}>
                  {k.v}
                </Typography>
              </Box>
            ))}
          </Stack>
          <Typography variant="caption" color="text.secondary" fontWeight={650}>
            Sales trend (example UI)
          </Typography>
          <Stack direction="row" alignItems="flex-end" spacing={1} sx={{ height: 100, mt: 1.5 }}>
            {bars.map((h, i) => (
              <Box
                key={i}
                sx={{
                  flex: 1,
                  height: `${h}%`,
                  borderRadius: '4px 4px 0 0',
                  bgcolor: accent,
                  opacity: 0.45 + i * 0.07,
                }}
              />
            ))}
          </Stack>
        </Box>
        <Box
          sx={{
            p: 2.5,
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider',
            bgcolor: 'background.paper',
          }}
        >
          <Typography fontWeight={700} sx={{ mb: 1.5, fontFamily: DISPLAY_FONT }}>
            Top selling items
          </Typography>
          {['Chicken Thali', 'Rice', 'Cold Drink', 'Shirt', 'Shoes'].map((n, i) => (
            <Typography key={n} variant="body2" sx={{ mb: 1 }}>
              {i + 1}. {n}
            </Typography>
          ))}
        </Box>
      </Box>
    </LandingSection>
  );
}

export function AiSection() {
  const insights = [
    'Chicken Thali is one of the highest-selling items this week.',
    'Cold drink sales increased compared with the previous period.',
    'Rice inventory is approaching the configured low-stock level.',
    'Consider reviewing stock levels for your top-selling products.',
  ];

  return (
    <LandingSection
      id="ai"
      tone="muted"
      eyebrow="AI business insights"
      title="Turn your sales data into better business decisions"
      body="AI-powered insights help you understand sales trends and product performance using your own finalized bills — never invented numbers."
    >
      <Box
        sx={{
          display: 'grid',
          gap: 1.5,
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
        }}
      >
        {insights.map((text) => (
          <Box
            key={text}
            sx={{
              p: 2.25,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
            }}
          >
            <Typography variant="body2" sx={{ lineHeight: 1.55 }}>
              {text}
            </Typography>
          </Box>
        ))}
      </Box>
    </LandingSection>
  );
}

export function WhatsAppSection() {
  const steps = ['Bill Generated', 'Send on WhatsApp', 'Customer Receives Bill'];

  return (
    <LandingSection
      eyebrow="WhatsApp billing"
      title="Can't print the bill? Send it on WhatsApp."
      body="Generate the bill once and send the same bill to the customer's WhatsApp when a printer is unavailable. Uses WhatsApp Business Cloud API when configured for your business."
    >
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        spacing={1.5}
        alignItems={{ xs: 'stretch', sm: 'center' }}
      >
        {steps.map((s, i) => (
          <Stack
            key={s}
            direction={{ xs: 'column', sm: 'row' }}
            alignItems="center"
            spacing={1.5}
            sx={{ flex: 1 }}
          >
            <Box
              sx={{
                width: '100%',
                p: 2,
                borderRadius: 2,
                border: '1px solid',
                borderColor: 'divider',
                bgcolor: 'background.paper',
                textAlign: 'center',
                fontWeight: 650,
              }}
            >
              {s}
            </Box>
            {i < steps.length - 1 ? (
              <Typography color="text.secondary" sx={{ display: { xs: 'none', sm: 'block' } }}>
                →
              </Typography>
            ) : null}
          </Stack>
        ))}
      </Stack>
    </LandingSection>
  );
}

export function MultiBusinessSection() {
  return (
    <LandingSection
      tone="ink"
      eyebrow="Multi-business SaaS"
      title="One platform. Every kind of shop."
      body="Secure tenant isolation so each business keeps its own products, bills, reports, users, and settings."
    >
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: { xs: 1.25, md: 1.75 },
          maxWidth: 820,
        }}
      >
        {BUSINESSES.map((b) => (
          <Typography
            key={b}
            component="span"
            sx={{
              fontFamily: DISPLAY_FONT,
              fontWeight: 600,
              fontSize: { xs: '0.95rem', md: '1.05rem' },
              letterSpacing: '-0.02em',
              color: 'rgba(255,255,255,0.92)',
              borderBottom: '1px solid rgba(255,255,255,0.28)',
              pb: 0.15,
            }}
          >
            {b}
          </Typography>
        ))}
      </Box>
    </LandingSection>
  );
}

export function SecuritySection() {
  return (
    <LandingSection
      eyebrow="Security & trust"
      title="Designed for tenant isolation and accountable access"
      body="We describe controls that exist in the product today — without claiming unverified certifications."
    >
      <Box
        sx={{
          display: 'grid',
          gap: 1.5,
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
        }}
      >
        {SECURITY_POINTS.map((p) => (
          <Box
            key={p}
            sx={{
              p: 2,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
              fontWeight: 600,
            }}
          >
            {p}
          </Box>
        ))}
      </Box>
    </LandingSection>
  );
}

export function RolesSection() {
  return (
    <LandingSection
      tone="muted"
      eyebrow="Roles"
      title="Built for owners and counter staff"
      body="Two clear experiences so the counter stays fast while the owner keeps control."
    >
      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
        }}
      >
        {[
          { title: 'Business Owner', items: OWNER_CAPABILITIES },
          { title: 'Billing User', items: BILLING_CAPABILITIES },
        ].map((role) => (
          <Box
            key={role.title}
            sx={{
              p: 3,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
            }}
          >
            <Typography
              sx={{ fontFamily: DISPLAY_FONT, fontWeight: 700, mb: 1.5, fontSize: '1.2rem' }}
            >
              {role.title}
            </Typography>
            <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1}>
              {role.items.map((i) => (
                <Chip key={i} label={i} size="small" variant="outlined" />
              ))}
            </Stack>
          </Box>
        ))}
      </Box>
    </LandingSection>
  );
}
