import ArrowBackOutlinedIcon from '@mui/icons-material/ArrowBackOutlined';
import { Box, Button, Container, Stack, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import ThemeModeToggle from '../../components/ThemeModeToggle';
import { COMPANY } from '../../constants/company';
import { PATHS } from '../../routes/paths';

const displayFont = '"Sora", "Source Sans 3", sans-serif';

export default function LegalPageShell({ title, updated, children }) {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', color: 'text.primary' }}>
      <Box
        component="header"
        sx={{
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: 'background.paper',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <Container maxWidth="md" sx={{ py: 1.5 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2}>
            <Button
              component={RouterLink}
              to={PATHS.home}
              startIcon={<ArrowBackOutlinedIcon />}
              sx={{ fontWeight: 650 }}
            >
              {COMPANY.productName}
            </Button>
            <ThemeModeToggle size="small" />
          </Stack>
        </Container>
      </Box>

      <Container maxWidth="md" sx={{ py: { xs: 4, md: 6 } }}>
        <Typography
          component="h1"
          sx={{
            fontFamily: displayFont,
            fontWeight: 700,
            fontSize: { xs: '1.75rem', md: '2.15rem' },
            letterSpacing: '-0.03em',
            mb: 1,
          }}
        >
          {title}
        </Typography>
        {updated ? (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3.5 }}>
            Last updated: {updated}
          </Typography>
        ) : null}
        <Stack spacing={2.5}>{children}</Stack>
        <Box sx={{ mt: 5, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="body2" color="text.secondary">
            {COMPANY.legalName}
          </Typography>
          {COMPANY.addressLines.map((line) => (
            <Typography key={line} variant="body2" color="text.secondary">
              {line}
            </Typography>
          ))}
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {COMPANY.email} · {COMPANY.phoneDisplay}
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export function LegalParagraph({ children }) {
  return (
    <Typography color="text.secondary" sx={{ lineHeight: 1.65 }}>
      {children}
    </Typography>
  );
}

export function LegalHeading({ children }) {
  return (
    <Typography
      component="h2"
      sx={{ fontFamily: displayFont, fontWeight: 700, fontSize: '1.15rem', mt: 1 }}
    >
      {children}
    </Typography>
  );
}
