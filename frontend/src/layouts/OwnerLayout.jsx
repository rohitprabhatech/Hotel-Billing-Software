import AssessmentOutlinedIcon from '@mui/icons-material/AssessmentOutlined';
import CategoryOutlinedIcon from '@mui/icons-material/CategoryOutlined';
import DashboardOutlinedIcon from '@mui/icons-material/DashboardOutlined';
import HistoryOutlinedIcon from '@mui/icons-material/HistoryOutlined';
import PeopleOutlinedIcon from '@mui/icons-material/PeopleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import RestaurantMenuOutlinedIcon from '@mui/icons-material/RestaurantMenuOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import {
  AppBar,
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
} from '@mui/material';
import { NavLink, Outlet } from 'react-router-dom';

const drawerWidth = 240;

const navItems = [
  { to: '/owner/dashboard', label: 'Dashboard', icon: <DashboardOutlinedIcon /> },
  { to: '/owner/categories', label: 'Categories', icon: <CategoryOutlinedIcon /> },
  { to: '/owner/items', label: 'Items', icon: <RestaurantMenuOutlinedIcon /> },
  { to: '/owner/bills', label: 'Bills', icon: <ReceiptLongOutlinedIcon /> },
  { to: '/owner/reports', label: 'Reports', icon: <AssessmentOutlinedIcon /> },
  { to: '/owner/audit', label: 'Audit', icon: <HistoryOutlinedIcon /> },
  { to: '/owner/users', label: 'Users', icon: <PeopleOutlinedIcon /> },
  { to: '/owner/settings', label: 'Settings', icon: <SettingsOutlinedIcon /> },
];

export default function OwnerLayout() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            Owner Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: 'border-box',
          },
        }}
      >
        <Toolbar />
        <List sx={{ px: 1, pt: 1 }}>
          {navItems.map((item) => (
            <ListItemButton
              key={item.to}
              component={NavLink}
              to={item.to}
              sx={{
                borderRadius: 2,
                mb: 0.5,
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
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Outlet />
      </Box>
    </Box>
  );
}