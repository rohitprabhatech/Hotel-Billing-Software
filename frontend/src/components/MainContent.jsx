import { Box } from '@mui/material';
import { mainContentSx } from '../layouts/shell';

/** Standard padded content column inside Owner / Billing shells. */
export default function MainContent({ children, sx = {} }) {
  return <Box sx={{ ...mainContentSx, ...sx }}>{children}</Box>;
}
