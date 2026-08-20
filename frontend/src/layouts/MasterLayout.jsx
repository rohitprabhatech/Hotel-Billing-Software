import BusinessOutlinedIcon from '@mui/icons-material/BusinessOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import HowToRegOutlinedIcon from '@mui/icons-material/HowToRegOutlined';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import MenuIcon from '@mui/icons-material/Menu';
import PaymentsOutlinedIcon from '@mui/icons-material/PaymentsOutlined';
import PersonOutlinedIcon from '@mui/icons-material/PersonOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import TimelapseOutlinedIcon from '@mui/icons-material/TimelapseOutlined';
import {
  AppBar,
  Box,
  Chip,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Menu,
  MenuItem,
  Toolbar,
  Tooltip,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { useState } from 'react';
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import MainContent from '../components/MainContent';
import MasterNotificationBell from '../components/MasterNotificationBell';
import PageHeader from '../components/PageHeader';
import RouteErrorBoundary from '../components/RouteErrorBoundary';
import ThemeModeToggle from '../components/ThemeModeToggle';
import { COMPANY } from '../constants/company';
import { useAuth } from '../context/AuthContext';
import { PageActionsProvider, PageActionsSlot } from '../context/PageActionsContext';
import { logoutRequest } from '../services/authService';
import { PATHS } from '../routes/paths';
import { DRAWER_WIDTH } from './shell';

const drawerWidth = DRAWER_WIDTH;

const navItems = [
  { to: PATHS.masterDashboard, label: 'Dashboard', icon: <DashboardOutlinedIcon />, end: true },
  {
    to: PATHS.masterRegistrationRequests,
    label: 'Registration requests',
    icon: <HowToRegOutlinedIcon />,
  },
  { to: PATHS.masterTrials, label: 'Trials', icon: <TimelapseOutlinedIcon /> },
  { to: PATHS.masterPlans, label: 'Plans', icon: <PaymentsOutlinedIcon /> },
  { to: PATHS.masterBusinesses, label: 'Businesses', icon: <BusinessOutlinedIcon /> },
  { to: PATHS.masterAudit, label: 'Audit log', icon: <HistoryOutlinedIcon /> },
  { to: PATHS.masterTrialSettings, label: 'Trial settings', icon: <SettingsOutlinedIcon /> },
];

const titles = {
  [PATHS.masterDashboard]: {
    title: 'Master Dashboard',
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
    subtitle: 'Assign plans, extend trials, record a manual renewal, or activate / deactivate / suspend a business. Data is never deleted.',
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

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar sx={{ px: 2 }}>
        <Box sx={{ minWidth: 0, width: '100%' }}>
          <Typography variant="subtitle1" fontWeight={700} noWrap>
            {COMPANY.productName}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Master · {COMPANY.legalName}
          </Typography>
        </Box>
      </Toolbar>
      <Divider />
      <List sx={{ px: 1, pt: 1, flexGrow: 1 }}>
        {navItems.map((item) => (
          <ListItemButton
            key={item.to}
            component={NavLink}
            to={item.to}
            end={item.end}
            onClick={() => setMobileOpen(false)}
            sx={{
              '&.active': {
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
                '& .MuiListItemIcon-root': { color: 'inherit' },
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar sx={{ px: { xs: 1, sm: 2 }, gap: 0.5, minHeight: { xs: 56, sm: 64 } }}>
          {isMobile ? (
            <IconButton edge="start" onClick={() => setMobileOpen(true)} sx={{ mr: 0.5 }} aria-label="Open menu">
              <MenuIcon />
            </IconButton>
          ) : null}
          <Box sx={{ flexGrow: 1, minWidth: 0, mr: 1 }}>
            <Typography variant="subtitle1" fontWeight={700} noWrap>
              {COMPANY.legalName}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              Master Admin · {meta.title}
            </Typography>
          </Box>
          <Chip
            size="small"
            label="MASTER"
            color="primary"
            variant="outlined"
            sx={{ mr: 0.5, display: { xs: 'none', sm: 'inline-flex' } }}
          />
          <MasterNotificationBell />
          <ThemeModeToggle sx={{ mr: 0.25 }} />
          <Tooltip title="Account menu">
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} aria-label="Account menu">
              <PersonOutlinedIcon />
            </IconButton>
          </Tooltip>
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
        </Toolbar>
      </AppBar>

      <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={() => setMobileOpen(false)}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', md: 'none' },
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          open
          sx={{
            display: { xs: 'none', md: 'block' },
            [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
          }}
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
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
