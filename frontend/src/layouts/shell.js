/** Shared app-shell dimensions for Owner + Billing layouts. */
export const DRAWER_WIDTH = 248;
export const MAIN_MAX_WIDTH = 1400;

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
