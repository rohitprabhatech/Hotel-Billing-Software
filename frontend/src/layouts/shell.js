import { layout } from '../theme/tokens';

/** Shared app-shell dimensions for Owner + Billing layouts. */
export const DRAWER_WIDTH = layout.drawerWidth;
export const MAIN_MAX_WIDTH = layout.mainMaxWidth;

export const mainContentSx = {
  px: { xs: 2, sm: 3, lg: 4 },
  py: { xs: 2.5, md: 3 },
  width: '100%',
  maxWidth: MAIN_MAX_WIDTH,
  mx: 'auto',
  boxSizing: 'border-box',
  minWidth: 0,
};

export const filterControlSx = {
  minWidth: { xs: '100%', sm: 160 },
};

/** Slightly wider filter control (category / search-adjacent selects). */
export const filterControlWideSx = {
  minWidth: { xs: '100%', sm: 200 },
};
