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
import { NavLink, Outlet } from 'react-router-dom';

export default function BillingLayout() {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar position="sticky">
        <Toolbar sx={{ gap: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Billing Counter
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