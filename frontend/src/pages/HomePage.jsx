import { Alert, Box } from '@mui/material';
import { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useColorMode } from '../context/ColorModeContext';
import { fetchHealth } from '../services/healthService';
import { homePathForRole, isValidRole } from '../utils/authRouting';
import CapabilityStrip from './landing/CapabilityStrip';
import {
  AiSection,
  AnalyticsSection,
  BillPreviewSection,
  FeaturesSection,
  MultiBusinessSection,
  RolesSection,
  SecuritySection,
  StockSection,
  WhatsAppSection,
  WorkflowSection,
} from './landing/ContentSections';
import { NAV_LINKS } from './landing/constants';
import HeroSection from './landing/HeroSection';
import LandingNav from './landing/LandingNav';
import ProductPreviewSection from './landing/ProductPreviewSection';
import {
  ContactSection,
  FinalCtaSection,
  LandingFooter,
  PricingSection,
} from './landing/PricingFooter';
import { listPublicPlans } from '../services/publicService';

export default function HomePage() {
  const { isAuthenticated, role } = useAuth();
  const { isDark } = useColorMode();
  const [health, setHealth] = useState(null);
  const [publicPlans, setPublicPlans] = useState([]);
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
    let active = true;
    listPublicPlans()
      .then((payload) => {
        if (active) setPublicPlans(payload.data || []);
      })
      .catch(() => {
        if (active) setPublicPlans([]);
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

  const scrollToHash = (href) => {
    const id = href.replace('#', '');
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setActiveHash(href);
    window.history.replaceState(null, '', href);
  };

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
        '& section[id]': { scrollMarginTop: '80px' },
        backgroundImage: (t) =>
          t.palette.mode === 'dark'
            ? 'none'
            : 'linear-gradient(180deg, #F7FAFB 0%, #F3F5F7 28%, #F3F5F7 100%)',
      }}
    >
      <LandingNav
        isDark={isDark}
        scrolled={scrolled}
        menuOpen={menuOpen}
        setMenuOpen={setMenuOpen}
        activeHash={activeHash}
        scrollToHash={scrollToHash}
      />

      {error ? (
        <Alert severity="warning" sx={{ borderRadius: 0 }}>
          {error}
        </Alert>
      ) : null}

      <HeroSection isDark={isDark} scrollToHash={scrollToHash} plans={publicPlans} />
      <ProductPreviewSection />
      <CapabilityStrip />
      <FeaturesSection />
      <WorkflowSection />
      <BillPreviewSection />
      <StockSection />
      <AnalyticsSection />
      <AiSection />
      <WhatsAppSection />
      <MultiBusinessSection />
      <SecuritySection />
      <RolesSection />
      <PricingSection plans={publicPlans} />
      <FinalCtaSection />
      <ContactSection />
      <LandingFooter health={health} error={error} />
    </Box>
  );
}
