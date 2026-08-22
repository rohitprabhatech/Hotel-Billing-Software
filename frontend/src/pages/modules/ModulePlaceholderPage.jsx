import { Alert, Stack, Typography } from '@mui/material';
import { useModules } from '../../context/ModulesContext';

/**
 * Lightweight industry-module placeholder until feature sprints ship CRUD.
 * Nav is filtered by module flags; this page is a safe landing target.
 */
export default function ModulePlaceholderPage({ moduleCode, title, description }) {
  const { isModuleEnabled, loading } = useModules();
  const enabled = isModuleEnabled(moduleCode);

  if (loading) {
    return <Typography color="text.secondary">Loading modules…</Typography>;
  }

  if (!enabled) {
    return (
      <Alert severity="warning">
        The <strong>{title}</strong> module is not enabled for this business type.
      </Alert>
    );
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h5" component="h1">
        {title}
      </Typography>
      <Typography color="text.secondary">{description}</Typography>
      <Alert severity="info">
        Module <code>{moduleCode}</code> is enabled. Full screens and workflows will arrive in a
        later approved sprint.
      </Alert>
    </Stack>
  );
}
