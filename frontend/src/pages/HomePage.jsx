import CloseIcon from '@mui/icons-material/Close';
import MenuIcon from '@mui/icons-material/Menu';
import {
  Alert,
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  Link,
  List,
  ListItemButton,
  ListItemText,
  Stack,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { Link as RouterLink, Navigate } from 'react-router-dom';
import { COMPANY, SUBSCRIPTION_PLAN } from '../constants/company';
import SubscriptionPlanInfo from '../components/SubscriptionPlanInfo';
import ThemeModeToggle from '../components/ThemeModeToggle';
import { useAuth } from '../context/AuthContext';
import { useColorMode } from '../context/ColorModeContext';
import { fetchHealth } from '../services/healthService';
import { PATHS } from '../routes/paths';
import { homePathForRole, isValidRole } from '../utils/authRouting';

const NAV_LINKS = [
  { href: '#features', label: 'Features' },
  { href: '#modules', label: 'Modules' },
  { href: '#ai', label: 'AI Insights' },
  { href: '#pricing', label: 'Pricing' },
  { href: '#about', label: 'About' },
  { href: '#contact', label: 'Contact' },
];

const FEATURES = [
  { title: 'Fast billing', body: 'Search items, build a cart, apply discount, choose Cash or Online, and generate a bill in seconds.' },
  { title: 'Item management', body: 'Catalog with price, GST, optional SKU, cost, and stock — soft-deactivate without losing history.' },
  { title: 'Categories & parents', body: 'Organize as main categories and subcategories so staff find products quickly.' },
  { title: 'GST / tax support', body: 'Line-level GST with server-calculated totals you can trust on every receipt.' },
  { title: 'Cash & online payments', body: 'Record how each bill was paid and filter sales by payment method.' },
  { title: 'Bill printing', body: 'Browser print for counter receipts with business details and line snapshots.' },
  { title: 'Sales reports', body: 'Today, weekly, and monthly views with exports for ownership reporting.' },
  { title: 'Audit & users', body: 'Know who billed, changed passwords, or edited the catalog — scoped to your business.' },
  { title: 'AI business insights', body: 'Recommendations grounded in your finalized sales — never invented numbers.' },
  { title: 'Multi-business security', body: 'Each registered business is an isolated tenant. Dark mode included.' },
];

const MODULES = [
  { name: 'Billing counter', detail: 'New bill, cart, discount, payment, print' },
  { name: 'Items & categories', detail: 'Catalog with parent/child structure' },
  { name: 'Bill history', detail: 'Search, view, cancel, reprint' },
  { name: 'Sales reports', detail: 'Daily / weekly / monthly + export' },
  { name: 'AI assistant', detail: 'Owner insights from real bills' },
  { name: 'Audit & activity', detail: 'Immutable activity trail' },
];

const BUSINESSES = [
  'Restaurant',
  'Clothing store',
  'Footwear store',
  'Kirana store',
  'Grocery store',
  'Electronics store',
  'Retail store',
  'Other businesses',
];

const WHY_US = [
  {
    title: 'Built for real counters',
    body: 'Billing stays fast when the queue is long — search, filter, and finalize without clutter.',
  },
  {
    title: 'Owner visibility',
    body: 'Dashboards, reports, and audit stay with the owner while staff focus on the counter.',
  },
  {
    title: 'Honest AI',
    body: 'Insights only from your sales data. Thin history is labeled clearly — no fake forecasts.',
  },
];

const displayFont = '"Sora", "Source Sans 3", sans-serif';
const contentMax = 1120;

function Section({ id, eyebrow, title, body, children, tone = 'default' }) {
  return (
    <Box
      id={id}
      component="section"
      sx={{
        px: { xs: 2, sm: 3, md: 6 },
        py: { xs: 7, md: 9 },
        bgcolor:
          tone === 'muted'
            ? 'action.hover'
            : tone === 'ink'
              ? 'primary.main'
              : 'transparent',
        color: tone === 'ink' ? 'primary.contrastText' : 'text.primary',
      }}
    >
      <Box sx={{ maxWidth: contentMax, mx: 'auto' }}>
        {eyebrow ? (
          <Typography
            variant="overline"
            sx={{
              letterSpacing: '0.14em',
              fontWeight: 700,
              color: tone === 'ink' ? 'rgba(255,255,255,0.72)' : 'primary.main',
            }}
          >
            {eyebrow}
          </Typography>
        ) : null}
        <Typography
          variant="h3"
          component="h2"
          sx={{
            mt: eyebrow ? 1 : 0,
            mb: body ? 1.5 : 3,
            fontFamily: displayFont,
            fontWeight: 650,
            fontSize: { xs: '1.65rem', md: '2.05rem' },
            letterSpacing: '-0.03em',
            maxWidth: 620,
            lineHeight: 1.2,
          }}
        >
          {title}
        </Typography>
        {body ? (
          <Typography
            sx={{
              mb: 4,
              maxWidth: 540,
              fontSize: '1.02rem',
              lineHeight: 1.55,
              color: tone === 'ink' ? 'rgba(255,255,255,0.82)' : 'text.secondary',
            }}
          >
            {body}
          </Typography>
        ) : null}
        {children}
      </Box>
    </Box>
  );
}

export default function HomePage() {
  const { isAuthenticated, role } = useAuth();
  const { isDark } = useColorMode();
  const [health, setHealth] = useState(null);
  const [error, setError] = useState('');
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [activeHash, setActiveHash] = useState('');

  useEffect(() => {
    let active = true;
    fetchHealth()
      .then((payload) => {
        if (active) setHealth(payload);
      })
      .catch(() => {
        if (active) setError('API offline — start the backend to connect live data.');
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    const ids = NAV_LINKS.map((l) => l.href.slice(1));
    const elements = ids.map((id) => document.getElementById(id)).filter(Boolean);
    if (!elements.length) return undefined;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]?.target?.id) {
          setActiveHash(`#${visible[0].target.id}`);
        }
      },
      { rootMargin: '-20% 0px -55% 0px', threshold: [0.1, 0.35, 0.6] },
    );
    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  if (isAuthenticated && isValidRole(role)) {
    return <Navigate to={homePathForRole(role)} replace />;
  }

  const closeMenu = () => setMenuOpen(false);

  const scrollToHash = (href) => {
    const id = href.replace('#', '');
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setActiveHash(href);
    window.history.replaceState(null, '', href);
  };

  const navLinkSx = (href) => ({
    position: 'relative',
    fontSize: '0.9rem',
    fontWeight: 600,
    letterSpacing: '0.005em',
    whiteSpace: 'nowrap',
    color: activeHash === href ? 'primary.main' : 'text.primary',
    opacity: activeHash === href ? 1 : 0.78,
    px: 0.35,
    py: 0.5,
    lineHeight: 1.2,
    transition: 'color 0.15s ease, opacity 0.15s ease',
    '&::after': {
      content: '""',
      position: 'absolute',
      left: 2,
      right: 2,
      bottom: -2,
      height: 2,
      borderRadius: 1,
      bgcolor: 'primary.main',
      transform: activeHash === href ? 'scaleX(1)' : 'scaleX(0)',
      transformOrigin: 'center',
      transition: 'transform 0.18s ease',
    },
    '&:hover': {
      color: 'primary.main',
      opacity: 1,
      '&::after': { transform: 'scaleX(1)' },
    },
  });

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        color: 'text.primary',
        scrollPaddingTop: '80px',
        '@keyframes landingFadeUp': {
          from: { opacity: 0, transform: 'translateY(14px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        '@media (prefers-reduced-motion: reduce)': {
          '& *': { animation: 'none !important' },
        },
        '& section[id]': {
          scrollMarginTop: '80px',
        },
      }}
    >
      {/* Navbar — brand | centered links | actions */}
      <Box
        component="header"
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 40,
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: isDark ? 'rgba(15, 22, 28, 0.97)' : 'rgba(255, 255, 255, 0.97)',
          backdropFilter: 'blur(14px)',
          boxShadow: scrolled
            ? isDark
              ? '0 10px 28px rgba(0,0,0,0.38)'
              : '0 10px 28px rgba(15, 36, 44, 0.09)'
            : 'none',
          transition: 'box-shadow 0.2s ease',
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: { xs: 1.5, lg: 3 },
            px: { xs: 2, sm: 3, md: 4 },
            height: 68,
            maxWidth: 1280,
            mx: 'auto',
            width: '100%',
          }}
        >
          {/* Brand + section links */}
          <Stack
            direction="row"
            alignItems="center"
            spacing={{ xs: 1.5, lg: 3.5 }}
            sx={{ minWidth: 0, flex: 1 }}
          >
            <Stack
              component={RouterLink}
              to={PATHS.home}
              direction="row"
              alignItems="center"
              spacing={1.25}
              title={`${COMPANY.productName} by Prabha Technology`}
              sx={{
                minWidth: 0,
                textDecoration: 'none',
                color: 'inherit',
                flexShrink: 0,
                height: 40,
              }}
            >
              <Box
                aria-hidden
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 1.25,
                  flexShrink: 0,
                  display: 'grid',
                  placeItems: 'center',
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  fontFamily: displayFont,
                  fontWeight: 700,
                  fontSize: '0.8rem',
                  letterSpacing: '-0.04em',
                }}
              >
                BB
              </Box>
              <Typography
                sx={{
                  fontFamily: displayFont,
                  fontWeight: 700,
                  fontSize: { xs: '1rem', sm: '1.06rem' },
                  letterSpacing: '-0.03em',
                  lineHeight: 1,
                  whiteSpace: 'nowrap',
                }}
              >
                {COMPANY.productName}
              </Typography>
            </Stack>

            <Stack
              direction="row"
              component="nav"
              aria-label="Page sections"
              spacing={{ lg: 2.5, xl: 3 }}
              sx={{
                display: { xs: 'none', lg: 'flex' },
                alignItems: 'center',
                pl: { lg: 2.5, xl: 3 },
                ml: { lg: 0.5 },
                borderLeft: '1px solid',
                borderColor: 'divider',
                height: 32,
              }}
            >
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  underline="none"
                  onClick={(e) => {
                    e.preventDefault();
                    scrollToHash(link.href);
                  }}
                  sx={navLinkSx(link.href)}
                >
                  {link.label}
                </Link>
              ))}
            </Stack>
          </Stack>

          {/* Actions */}
          <Stack
            direction="row"
            spacing={1}
            alignItems="center"
            sx={{ flexShrink: 0, height: 40 }}
          >
            <ThemeModeToggle size="small" />
            <Button
              component={RouterLink}
              to={PATHS.login}
              color="inherit"
              size="small"
              sx={{
                display: { xs: 'none', sm: 'inline-flex' },
                fontWeight: 600,
                px: 1.5,
                height: 36,
                borderRadius: 1.5,
              }}
            >
              Login
            </Button>
            <Button
              component={RouterLink}
              to={PATHS.register}
              variant="contained"
              size="small"
              sx={{
                display: { xs: 'none', sm: 'inline-flex' },
                fontWeight: 700,
                px: { sm: 1.75, md: 2 },
                height: 36,
                borderRadius: 1.5,
                whiteSpace: 'nowrap',
              }}
            >
              <Box component="span" sx={{ display: { xs: 'none', md: 'inline' } }}>
                Register Your Business
              </Box>
              <Box component="span" sx={{ display: { xs: 'inline', md: 'none' } }}>
                Register
              </Box>
            </Button>
            <IconButton
              edge="end"
              aria-label="Open menu"
              onClick={() => setMenuOpen(true)}
              sx={{
                display: { xs: 'inline-flex', lg: 'none' },
                width: 36,
                height: 36,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1.5,
              }}
            >
              <MenuIcon />
            </IconButton>
          </Stack>
        </Box>
      </Box>

      <Drawer
        anchor="right"
        open={menuOpen}
        onClose={closeMenu}
        PaperProps={{
          sx: {
            width: 'min(340px, 94vw)',
            bgcolor: 'background.paper',
          },
        }}
      >
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          sx={{ px: 2, py: 1.75, borderBottom: '1px solid', borderColor: 'divider' }}
        >
          <Stack direction="row" spacing={1.25} alignItems="center">
            <Box
              aria-hidden
              sx={{
                width: 32,
                height: 32,
                borderRadius: 1.25,
                display: 'grid',
                placeItems: 'center',
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                fontFamily: displayFont,
                fontWeight: 700,
                fontSize: '0.75rem',
              }}
            >
              BB
            </Box>
            <Box>
              <Typography fontWeight={700} lineHeight={1.2}>
                {COMPANY.productName}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                by Prabha Technology
              </Typography>
            </Box>
          </Stack>
          <IconButton aria-label="Close menu" onClick={closeMenu}>
            <CloseIcon />
          </IconButton>
        </Stack>
        <List sx={{ px: 1, py: 1.5 }}>
          {NAV_LINKS.map((link) => (
            <ListItemButton
              key={link.href}
              selected={activeHash === link.href}
              onClick={() => {
                closeMenu();
                scrollToHash(link.href);
              }}
              sx={{ borderRadius: 1.5, mb: 0.25 }}
            >
              <ListItemText
                primary={link.label}
                primaryTypographyProps={{ fontWeight: activeHash === link.href ? 700 : 600 }}
              />
            </ListItemButton>
          ))}
        </List>
        <Divider />
        <Stack spacing={1.25} sx={{ p: 2 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 0.5 }}>
            <Typography variant="body2" color="text.secondary" fontWeight={600}>
              Appearance
            </Typography>
            <ThemeModeToggle size="small" />
          </Stack>
          <Button component={RouterLink} to={PATHS.login} variant="outlined" fullWidth onClick={closeMenu}>
            Login
          </Button>
          <Button component={RouterLink} to={PATHS.register} variant="contained" fullWidth onClick={closeMenu}>
            Register Your Business
          </Button>
        </Stack>
      </Drawer>

      {/* Hero — brand-first, full-bleed atmosphere (no stock photo) */}
      <Box
        component="section"
        sx={{
          position: 'relative',
          minHeight: { xs: '78vh', md: '86vh' },
          display: 'flex',
          alignItems: 'flex-end',
          overflow: 'hidden',
          color: '#fff',
          background: isDark
            ? 'linear-gradient(145deg, #0B1218 0%, #143744 48%, #1F4E5F 100%)'
            : 'linear-gradient(145deg, #0F242C 0%, #1F4E5F 52%, #2F6B80 100%)',
        }}
      >
        <Box
          aria-hidden
          sx={{
            position: 'absolute',
            inset: 0,
            backgroundImage:
              'linear-gradient(120deg, transparent 40%, rgba(255,255,255,0.06) 40%, rgba(255,255,255,0.06) 41%, transparent 41%), linear-gradient(0deg, rgba(0,0,0,0.35) 0%, transparent 45%)',
            backgroundSize: '100% 100%',
          }}
        />
        <Box
          sx={{
            position: 'relative',
            zIndex: 1,
            width: '100%',
            maxWidth: contentMax,
            mx: 'auto',
            px: { xs: 2.5, md: 6 },
            pb: { xs: 6, md: 9 },
            pt: { xs: 10, md: 14 },
            animation: 'landingFadeUp 0.85s ease-out both',
          }}
        >
          <Typography
            component="p"
            sx={{
              fontFamily: displayFont,
              fontWeight: 700,
              fontSize: { xs: '2.35rem', sm: '3.25rem', md: '4rem' },
              lineHeight: 0.98,
              letterSpacing: '-0.035em',
              maxWidth: 700,
              mb: 2,
            }}
          >
            {COMPANY.productName}
          </Typography>
          <Typography
            sx={{
              fontSize: { xs: '1.1rem', md: '1.3rem' },
              maxWidth: 480,
              opacity: 0.92,
              mb: 1,
              lineHeight: 1.45,
              fontWeight: 600,
            }}
          >
            Smart billing and business management
          </Typography>
          <Typography
            sx={{
              fontSize: { xs: '0.98rem', md: '1.05rem' },
              maxWidth: 480,
              opacity: 0.82,
              mb: 3.5,
              lineHeight: 1.5,
            }}
          >
            Built for restaurants, retail stores, grocery stores, clothing stores, footwear stores, and other businesses.
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ width: { xs: '100%', sm: 'auto' } }}>
            <Button
              component={RouterLink}
              to={PATHS.register}
              variant="contained"
              size="large"
              fullWidth
              sx={{
                bgcolor: '#fff',
                color: 'primary.dark',
                width: { xs: '100%', sm: 'auto' },
                '&:hover': { bgcolor: 'rgba(255,255,255,0.92)' },
              }}
            >
              Register Your Business
            </Button>
            <Button
              component={RouterLink}
              to={PATHS.login}
              variant="outlined"
              size="large"
              fullWidth
              sx={{
                borderColor: 'rgba(255,255,255,0.65)',
                color: '#fff',
                width: { xs: '100%', sm: 'auto' },
                '&:hover': { borderColor: '#fff', bgcolor: 'rgba(255,255,255,0.08)' },
              }}
            >
              Login
            </Button>
          </Stack>
        </Box>
      </Box>

      {/* Value proposition */}
      <Section
        id="value"
        eyebrow="Why Business Billing"
        title="One workspace for the counter and the owner"
        body="Staff bill quickly. Owners see sales, catalog, users, and audit — all scoped to a single registered business."
      >
        <Box
          sx={{
            display: 'grid',
            gap: { xs: 3.5, md: 5 },
            gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
            borderTop: '1px solid',
            borderColor: 'divider',
            pt: 4,
          }}
        >
          {WHY_US.map((item) => (
            <Box key={item.title}>
              <Typography sx={{ fontFamily: displayFont, fontWeight: 650, mb: 1, fontSize: '1.05rem' }}>
                {item.title}
              </Typography>
              <Typography color="text.secondary" sx={{ lineHeight: 1.55 }}>
                {item.body}
              </Typography>
            </Box>
          ))}
        </Box>
      </Section>

      {/* Features */}
      <Section
        id="features"
        tone="muted"
        eyebrow="Features"
        title="Everything you need to run day-to-day billing"
        body="Concise capabilities — no clutter, no fake add-ons."
      >
        <Box
          sx={{
            display: 'grid',
            gap: { xs: 3, md: 3.5 },
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', lg: '1fr 1fr 1fr' },
          }}
        >
          {FEATURES.map((feature) => (
            <Box
              key={feature.title}
              sx={{
                pr: { md: 2 },
                borderTop: '1px solid',
                borderColor: 'divider',
                pt: 2,
              }}
            >
              <Typography fontWeight={700} sx={{ mb: 0.75 }}>
                {feature.title}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.55 }}>
                {feature.body}
              </Typography>
            </Box>
          ))}
        </Box>
      </Section>

      {/* Modules */}
      <Section
        id="modules"
        eyebrow="Modules"
        title="Clear product areas"
        body="Each module has one job — from catalog setup to AI analysis."
      >
        <Stack spacing={0} divider={<Divider flexItem />}>
          {MODULES.map((mod) => (
            <Stack
              key={mod.name}
              direction={{ xs: 'column', sm: 'row' }}
              justifyContent="space-between"
              spacing={0.5}
              sx={{ py: 2 }}
            >
              <Typography fontWeight={650}>{mod.name}</Typography>
              <Typography color="text.secondary" variant="body2">
                {mod.detail}
              </Typography>
            </Stack>
          ))}
        </Stack>
      </Section>

      {/* Business types */}
      <Section
        id="businesses"
        tone="muted"
        eyebrow="Business types"
        title="Generic by design"
        body="Pick a business type at registration. Billing logic stays the same — only labels and optional fields (like FSSAI) adapt."
      >
        <Box
          component="ul"
          sx={{
            m: 0,
            p: 0,
            listStyle: 'none',
            display: 'grid',
            gap: 1.25,
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' },
          }}
        >
          {BUSINESSES.map((name) => (
            <Typography
              key={name}
              component="li"
              sx={{
                py: 1.25,
                borderBottom: '1px solid',
                borderColor: 'divider',
                fontWeight: 600,
                fontSize: '0.95rem',
              }}
            >
              {name}
            </Typography>
          ))}
        </Box>
      </Section>

      {/* Billing */}
      <Section
        id="billing"
        eyebrow="Billing"
        title="Counter billing without the clutter"
        body="Search by name or SKU, adjust quantity, remove a wrong line from the cart (never from your catalog), apply discount, choose Cash or Online, then generate and print."
      />

      {/* Reports */}
      <Section
        id="reports"
        tone="muted"
        eyebrow="Sales & reports"
        title="Know today’s numbers"
        body="Daily, weekly, and monthly sales with cash/online split, top items, category sales, and exports — owner-only and tenant-scoped."
      />

      {/* AI */}
      <Section
        id="ai"
        eyebrow="AI Insights"
        title="AI-powered business insights based on your sales data"
        body="Analyze today’s sales, weekly and monthly trends, top and low performers, and practical recommendations. Future demand estimates only appear when enough history exists — we never invent metrics."
      />

      {/* Security / Why */}
      <Section
        id="about"
        tone="ink"
        eyebrow="Audit & security"
        title="Tenant walls by design"
        body="JWT sessions, Owner and Billing roles, soft-cancel bills, append-only audit logs, and isolation so one business never sees another’s data. Dark mode is built in."
      >
        <Button
          component={RouterLink}
          to={PATHS.register}
          size="large"
          sx={{
            mt: 1,
            bgcolor: '#fff',
            color: 'primary.dark',
            '&:hover': { bgcolor: 'rgba(255,255,255,0.92)' },
          }}
        >
          Register Your Business
        </Button>
      </Section>

      {/* Pricing */}
      <Section
        id="pricing"
        eyebrow="Pricing"
        title={`${SUBSCRIPTION_PLAN.priceDisplay}`}
        body="One clear monthly plan. No in-app payment gateway — register or contact us to subscribe."
      >
        <SubscriptionPlanInfo variant="public" showPublicCtas />
      </Section>

      {/* Support */}
      <Section
        id="support"
        tone="muted"
        eyebrow="24/7 Support"
        title="Technical support when the counter cannot wait"
        body={COMPANY.supportNote}
      >
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          useFlexGap
          flexWrap="wrap"
          sx={{ width: '100%' }}
        >
          <Button
            component="a"
            href={COMPANY.emailHref}
            variant="contained"
            sx={{ width: { xs: '100%', sm: 'auto' } }}
          >
            Email support
          </Button>
          <Button
            component="a"
            href={COMPANY.phoneHref}
            variant="outlined"
            sx={{ width: { xs: '100%', sm: 'auto' } }}
          >
            Call {COMPANY.phoneDisplay}
          </Button>
        </Stack>
      </Section>

      {/* Contact */}
      <Section
        id="contact"
        eyebrow="Contact"
        title="Talk to Prabha Technology"
        body="Inquiries for onboarding, renewals, and technical help."
      >
        <Box
          sx={{
            display: 'grid',
            gap: 4,
            gridTemplateColumns: { xs: '1fr', md: '1.1fr 1fr' },
          }}
        >
          <Box>
            <Typography sx={{ fontFamily: displayFont, fontWeight: 700, mb: 1.25 }}>
              {COMPANY.legalName}
            </Typography>
            {COMPANY.addressLines.map((line) => (
              <Typography key={line} color="text.secondary" sx={{ lineHeight: 1.6 }}>
                {line}
              </Typography>
            ))}
          </Box>
          <Stack spacing={1.25}>
            <Typography>
              Email:{' '}
              <Link href={COMPANY.emailHref} fontWeight={600}>
                {COMPANY.email}
              </Link>
            </Typography>
            <Typography>
              Phone:{' '}
              <Link href={COMPANY.phoneHref} fontWeight={600}>
                {COMPANY.phoneDisplay}
              </Link>
            </Typography>
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} sx={{ pt: 1.5 }}>
              <Button component={RouterLink} to={PATHS.register} variant="contained">
                Register Your Business
              </Button>
              <Button component={RouterLink} to={PATHS.login} variant="outlined">
                Login
              </Button>
            </Stack>
          </Stack>
        </Box>
      </Section>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          borderTop: '1px solid',
          borderColor: 'divider',
          px: { xs: 2, sm: 3, md: 6 },
          py: { xs: 5, md: 6 },
          bgcolor: isDark ? 'background.paper' : 'action.hover',
        }}
      >
        <Box sx={{ maxWidth: contentMax, mx: 'auto' }}>
          <Box
            sx={{
              display: 'grid',
              gap: 4,
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1.4fr 1fr 1fr 1fr' },
              mb: 4,
            }}
          >
            <Box>
              <Typography fontWeight={700} sx={{ mb: 1 }}>
                {COMPANY.productName}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, maxWidth: 280 }}>
                A product of {COMPANY.legalName}
              </Typography>
              {COMPANY.addressLines.map((line) => (
                <Typography key={line} variant="body2" color="text.secondary" sx={{ lineHeight: 1.55 }}>
                  {line}
                </Typography>
              ))}
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1.25 }}>
                Product
              </Typography>
              <Stack spacing={0.75}>
                <Link href="#features" underline="hover" color="text.secondary" variant="body2">Features</Link>
                <Link href="#modules" underline="hover" color="text.secondary" variant="body2">Modules</Link>
                <Link href="#pricing" underline="hover" color="text.secondary" variant="body2">Pricing</Link>
              </Stack>
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1.25 }}>
                Company
              </Typography>
              <Stack spacing={0.75}>
                <Link href="#about" underline="hover" color="text.secondary" variant="body2">About</Link>
                <Link href="#contact" underline="hover" color="text.secondary" variant="body2">Contact</Link>
              </Stack>
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1.25 }}>
                Support
              </Typography>
              <Stack spacing={0.75}>
                <Link href="#support" underline="hover" color="text.secondary" variant="body2">
                  24/7 Technical Support
                </Link>
                <Link href={COMPANY.emailHref} underline="hover" color="text.secondary" variant="body2">
                  {COMPANY.email}
                </Link>
                <Link href={COMPANY.phoneHref} underline="hover" color="text.secondary" variant="body2">
                  {COMPANY.phoneDisplay}
                </Link>
              </Stack>
            </Box>
          </Box>
          <Divider sx={{ mb: 2.5 }} />
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            justifyContent="space-between"
            spacing={1.5}
          >
            <Typography variant="body2" color="text.secondary">
              © {new Date().getFullYear()} {COMPANY.legalName}
            </Typography>
            {health?.success ? (
              <Typography variant="caption" color="text.secondary">
                API connected · {health.data?.service || 'Business Billing API'}
              </Typography>
            ) : null}
          </Stack>
          {error ? (
            <Alert severity="warning" sx={{ mt: 2 }}>
              {error}
            </Alert>
          ) : null}
        </Box>
      </Box>
    </Box>
  );
}
