import CloseIcon from '@mui/icons-material/Close';
import MenuIcon from '@mui/icons-material/Menu';
import {
  Box,
  Button,
  Divider,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Stack,
  Typography,
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import ThemeModeToggle from '../../components/ThemeModeToggle';
import { COMPANY } from '../../constants/company';
import { PATHS } from '../../routes/paths';
import { CONTENT_MAX, DISPLAY_FONT, NAV_LINKS } from './constants';

export default function LandingNav({
  isDark,
  scrolled,
  menuOpen,
  setMenuOpen,
  activeHash,
  scrollToHash,
}) {
  const closeMenu = () => setMenuOpen(false);

  const navLinkSx = (href) => ({
    position: 'relative',
    fontSize: '0.88rem',
    fontWeight: 600,
    whiteSpace: 'nowrap',
    color: activeHash === href ? 'primary.main' : 'text.primary',
    opacity: activeHash === href ? 1 : 0.78,
    px: 0.4,
    py: 0.5,
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
      transition: 'transform 0.18s ease',
    },
    '&:hover': {
      color: 'primary.main',
      opacity: 1,
      '&::after': { transform: 'scaleX(1)' },
    },
  });

  const BrandMark = ({ size = 36 }) => (
    <Box
      aria-hidden
      sx={{
        width: size,
        height: size,
        borderRadius: 1.1,
        flexShrink: 0,
        display: 'grid',
        placeItems: 'center',
        bgcolor: 'primary.main',
        color: 'primary.contrastText',
        fontFamily: DISPLAY_FONT,
        fontWeight: 700,
        fontSize: size > 32 ? '0.78rem' : '0.7rem',
        letterSpacing: '-0.05em',
        boxShadow: (t) =>
          t.palette.mode === 'dark' ? 'none' : '0 4px 12px rgba(31,78,95,0.22)',
      }}
    >
      BB
    </Box>
  );

  return (
    <>
      <Box
        component="header"
        sx={{
          position: 'sticky',
          top: 0,
          zIndex: 40,
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: isDark ? 'rgba(12, 18, 24, 0.88)' : 'rgba(255, 255, 255, 0.88)',
          backdropFilter: 'blur(16px) saturate(1.2)',
          boxShadow: scrolled
            ? isDark
              ? '0 8px 24px rgba(0,0,0,0.35)'
              : '0 8px 24px rgba(15, 36, 44, 0.07)'
            : 'none',
          transition: 'box-shadow 0.22s ease, background-color 0.22s ease',
        }}
      >
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr auto', lg: 'auto 1fr auto' },
            alignItems: 'center',
            gap: { xs: 1.5, lg: 2 },
            px: { xs: 2, sm: 3, md: 4 },
            height: 64,
            maxWidth: CONTENT_MAX,
            mx: 'auto',
            width: '100%',
          }}
        >
          <Stack
            component={RouterLink}
            to={PATHS.home}
            direction="row"
            alignItems="center"
            spacing={1.25}
            title={`${COMPANY.productName} by Prabha Technology`}
            sx={{ textDecoration: 'none', color: 'inherit', minWidth: 0 }}
          >
            <BrandMark />
            <Box sx={{ minWidth: 0 }}>
              <Typography
                sx={{
                  fontFamily: DISPLAY_FONT,
                  fontWeight: 700,
                  fontSize: { xs: '0.98rem', sm: '1.05rem' },
                  letterSpacing: '-0.03em',
                  lineHeight: 1.1,
                  whiteSpace: 'nowrap',
                }}
              >
                {COMPANY.productName}
              </Typography>
              <Typography
                variant="caption"
                color="text.secondary"
                sx={{ display: { xs: 'none', sm: 'block' }, lineHeight: 1.2 }}
              >
                by Prabha Technology
              </Typography>
            </Box>
          </Stack>

          <Stack
            component="nav"
            direction="row"
            spacing={{ lg: 2, xl: 2.5 }}
            justifyContent="center"
            sx={{ display: { xs: 'none', lg: 'flex' } }}
          >
            {NAV_LINKS.map((link) => (
              <Box
                key={link.href}
                component="button"
                type="button"
                onClick={() => scrollToHash(link.href)}
                sx={{
                  ...navLinkSx(link.href),
                  border: 0,
                  background: 'none',
                  cursor: 'pointer',
                  font: 'inherit',
                }}
              >
                {link.label}
              </Box>
            ))}
          </Stack>

          <Stack direction="row" alignItems="center" spacing={1} justifyContent="flex-end">
            <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
              <ThemeModeToggle size="small" />
            </Box>
            <Button
              component={RouterLink}
              to={PATHS.login}
              variant="text"
              sx={{ display: { xs: 'none', md: 'inline-flex' }, fontWeight: 650 }}
            >
              Login
            </Button>
            <Button
              component={RouterLink}
              to={PATHS.register}
              variant="contained"
              sx={{ display: { xs: 'none', md: 'inline-flex' }, whiteSpace: 'nowrap' }}
            >
              Register Your Business
            </Button>
            <IconButton
              aria-label="Open menu"
              onClick={() => setMenuOpen(true)}
              sx={{ display: { lg: 'none' } }}
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
        PaperProps={{ sx: { width: 'min(340px, 94vw)', bgcolor: 'background.paper' } }}
      >
        <Stack
          direction="row"
          alignItems="center"
          justifyContent="space-between"
          sx={{ px: 2, py: 1.75, borderBottom: '1px solid', borderColor: 'divider' }}
        >
          <Stack direction="row" spacing={1.25} alignItems="center">
            <BrandMark size={32} />
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
          <Stack direction="row" alignItems="center" justifyContent="space-between">
            <Typography variant="body2" color="text.secondary" fontWeight={600}>
              Appearance
            </Typography>
            <ThemeModeToggle size="small" />
          </Stack>
          <Button component={RouterLink} to={PATHS.login} variant="outlined" fullWidth onClick={closeMenu}>
            Login
          </Button>
          <Button
            component={RouterLink}
            to={PATHS.register}
            variant="contained"
            fullWidth
            onClick={closeMenu}
          >
            Register Your Business
          </Button>
        </Stack>
      </Drawer>
    </>
  );
}
