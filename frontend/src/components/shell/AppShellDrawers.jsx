import { Box, Drawer } from '@mui/material';
import { layout } from '../../theme/tokens';

export default function AppShellDrawers({ mobileOpen, onMobileClose, children }) {
  const drawerWidth = layout.drawerWidth;
  const paperSx = {
    width: drawerWidth,
    boxSizing: 'border-box',
    border: 'none',
  };

  return (
    <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onMobileClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': paperSx,
        }}
      >
        {children}
      </Drawer>
      <Drawer
        variant="permanent"
        open
        sx={{
          display: { xs: 'none', md: 'block' },
          '& .MuiDrawer-paper': paperSx,
        }}
      >
        {children}
      </Drawer>
    </Box>
  );
}
