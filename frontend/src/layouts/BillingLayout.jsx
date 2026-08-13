import LogoutOutlinedIcon from '@mui/icons-material/LogoutOutlined';
import PointOfSaleOutlinedIcon from '@mui/icons-material/PointOfSaleOutlined';
import ReceiptLongOutlinedIcon from '@mui/icons-material/ReceiptLongOutlined';
import {
  AppBar,
  Box,
  Button,
  Container,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { logoutRequest } from '../services/authService';

export default function BillingLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = async () => {
    try {
      await logoutRequest();
    } catch {
      // continue local logout
    }
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="sticky">
        <Toolbar sx={{ gap: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {user?.tenant?.business_name || 'Billing Counter'}
          </Typography>
          <Button
            color="inherit"
            component={NavLink}
            to="/billing"
            startIcon={<PointOfSaleOutlinedIcon />}
          >
            Home
          </Button>
          <Button
            color="inherit"
            component={NavLink}
            to="/billing/new"
            startIcon={<ReceiptLongOutlinedIcon />}
          >
            New Bill
          </Button>
          <Button color="inherit" component={NavLink} to="/billing/bills">
            Today&apos;s Bills
          </Button>
          <Button color="inherit" startIcon={<LogoutOutlinedIcon />} onClick={onLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Stack spacing={2}>
          <Outlet />
        </Stack>
      </Container>
    </Box>
  );
}