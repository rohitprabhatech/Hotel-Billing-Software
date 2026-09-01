import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import HowToRegOutlinedIcon from '@mui/icons-material/HowToRegOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import TimelapseOutlinedIcon from '@mui/icons-material/TimelapseOutlined';
import { Box, Divider, ListItemIcon, Menu, MenuItem, Toolbar, Typography, useMediaQuery } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import MainContent from '../components/MainContent';
import BrandLogo from '../components/BrandLogo';
import MasterNotificationBell from '../components/MasterNotificationBell';
import PageHeader from '../components/PageHeader';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import AppNavDrawer from '../components/shell/AppNavDrawer';
import AppShellDrawers from '../components/shell/AppShellDrawers';
import AppTopBar from '../components/shell/AppTopBar';
import { sidebarTokens } from '../components/shell/navStyles';
import { COMPANY } from '../constants/company';
import { useAuth } from '../context/AuthContext';
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';
import { layout } from '../theme/tokens';

const masterNav = [
  { type: 'section', label: 'Platform' },
  { to: PATHS.masterDashboard, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  {
    to: PATHS.masterRegistrationRequests,
    label: 'Registration requests',
    icon: <HowToRegOutlinedIcon />,
  },
  { to: PATHS.masterTrials, label: 'Trials', icon: <TimelapseOutlinedIcon /> },
  { to: PATHS.masterPlans, label: 'Plans', icon: <PaymentsOutlinedIcon /> },
  { to: PATHS.masterBusinesses, label: 'Businesses', icon: <BusinessOutlinedIcon /> },
  { type: 'section', label: 'Administration' },
  { to: PATHS.masterAudit, label: 'Audit log', icon: <HistoryOutlinedIcon /> },
  { to: PATHS.masterTrialSettings, label: 'Trial settings', icon: <SettingsOutlinedIcon /> },
];

const titles = {
  [PATHS.masterDashboard]: {
    title: 'Platform Dashboard',
    hidePageHeader: true,
  },
  [PATHS.masterRegistrationRequests]: {
    title: 'Registration requests',
    subtitle: 'Review public signups. Approve creates the business and owner login.',
  },
  [PATHS.masterTrials]: {
    title: 'Active trials',
    subtitle: 'Businesses currently on a free trial. Changing global settings does not alter these dates.',
  },
  [PATHS.masterPlans]: {
    title: 'Plans',
    subtitle: 'Create and edit subscription plans. Changing a price does not alter existing billed amounts.',
  },
  [PATHS.masterBusinesses]: {
    title: 'Businesses',
    subtitle:
      'Assign plans, extend trials, record a manual renewal, or activate / deactivate / suspend a business. Data is never deleted.',
  },
  [PATHS.masterAudit]: {
    title: 'Platform audit',
    subtitle: 'Master Admin actions only. Passwords and tokens are never stored.',
  },
  [PATHS.masterTrialSettings]: {
    title: 'Trial settings',
    subtitle: 'Applies to newly approved businesses only — existing trials stay as they are.',
  },
  [PATHS.masterChangePassword]: {
    title: 'Change Password',
    subtitle: 'Update the Master Admin password. Other sessions will be signed out.',
  },
};

export default function MasterLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);

  const meta = titles[location.pathname] || {
    title: 'Master Console',
    subtitle: '',
  };

  const onLogout = async () => {
    try {
      await logoutRequest();
    } catch {
      // Client logout proceeds even if API logout fails
    }
    logout();
    navigate(PATHS.masterLogin, { replace: true });
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppTopBar
        isMobile={isMobile}
        onMenuOpen={() => setMobileOpen(true)}
        title={COMPANY.shortName}
        subtitle={`Master Admin · ${meta.title}`}
        badge="MASTER"
        brandLogo={<BrandLogo size={32} showText={false} href={null} />}
        notificationSlot={<MasterNotificationBell />}
        accountMenu={{
          onOpen: (e) => setAnchorEl(e.currentTarget),
          menu: (
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
              <MenuItem disabled>
                <Box>
                  <Typography variant="body2" fontWeight={600}>
                    {user?.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {user?.email}
                  </Typography>
                </Box>
              </MenuItem>
              <Divider />
              <MenuItem
                onClick={() => {
                  setAnchorEl(null);
                  navigate(PATHS.masterChangePassword);
                }}
              >
                <ListItemIcon>
                  <LockOutlinedIcon fontSize="small" />
                </ListItemIcon>
                Change Password
              </MenuItem>
              <MenuItem
                onClick={() => {
                  setAnchorEl(null);
                  onLogout();
                }}
              >
                <ListItemIcon>
                  <LogoutOutlinedIcon fontSize="small" />
                </ListItemIcon>
                Logout
              </MenuItem>
            </Menu>
          ),
        }}
      />

      <AppShellDrawers mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)}>
        <AppNavDrawer
          brandLogo={
            <BrandLogo
              size={36}
              title={COMPANY.shortName}
              subtitle={`Master · ${COMPANY.productName}`}
              textColor={sidebarTokens(theme.palette.mode).text}
              mutedColor={sidebarTokens(theme.palette.mode).textMuted}
              href={null}
            />
          }
          navItems={masterNav}
          onNavigate={() => setMobileOpen(false)}
        />
      </AppShellDrawers>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${layout.drawerWidth}px)` },
          minWidth: 0,
          bgcolor: 'background.default',
        }}
      >
        <Toolbar />
        <PageActionsProvider>
          <MasterMain meta={meta} />
        </PageActionsProvider>
      </Box>
    </Box>
  );
}

function MasterMain({ meta }) {
  const location = useLocation();
  return (
    <MainContent>
      {!meta.hidePageHeader ? (
        <PageHeader title={meta.title} subtitle={meta.subtitle} actions={<PageActionsSlot />} />
      ) : null}
      <RouteErrorBoundary key={location.pathname}>
        <Outlet />
      </RouteErrorBoundary>
    </MainContent>
  );
}
