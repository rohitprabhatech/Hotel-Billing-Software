/** Design tokens for the authenticated application shell (not landing/auth). */

export const layout = {
  drawerWidth: 260,
  mainMaxWidth: 1400,
  headerHeight: 64,
  headerHeightMobile: 56,
};

export const radius = {
  sm: 6,
  md: 8,
  lg: 12,
  xl: 16,
};

export const sidebar = {
  light: {
    background: '#15232C',
    border: 'rgba(255, 255, 255, 0.06)',
    text: '#E8EEF2',
    textMuted: '#9AA7B5',
    section: '#7D8B98',
    hover: 'rgba(255, 255, 255, 0.06)',
    active: '#1F4E5F',
    activeText: '#FFFFFF',
    icon: '#B8C5D0',
  },
  dark: {
    background: '#0C1218',
    border: 'rgba(255, 255, 255, 0.08)',
    text: '#E8EEF2',
    textMuted: '#8B98A6',
    section: '#6E7D8A',
    hover: 'rgba(255, 255, 255, 0.05)',
    active: '#2F6B80',
    activeText: '#FFFFFF',
    icon: '#A8B6C3',
  },
};

export const statusColors = {
  active: { bg: '#E8F5EE', text: '#1B6B42', darkBg: 'rgba(46, 125, 79, 0.18)', darkText: '#7DD4A0' },
  paid: { bg: '#E8F5EE', text: '#1B6B42', darkBg: 'rgba(46, 125, 79, 0.18)', darkText: '#7DD4A0' },
  pending: { bg: '#FFF4E5', text: '#9A4A0A', darkBg: 'rgba(247, 144, 9, 0.16)', darkText: '#FDB022' },
  cancelled: { bg: '#FEF3F2', text: '#912018', darkBg: 'rgba(240, 68, 56, 0.16)', darkText: '#FDA29B' },
  low: { bg: '#FFF4E5', text: '#9A4A0A', darkBg: 'rgba(247, 144, 9, 0.16)', darkText: '#FDB022' },
  info: { bg: '#EFF8FF', text: '#175CD3', darkBg: 'rgba(110, 180, 200, 0.16)', darkText: '#9AD0DE' },
};
