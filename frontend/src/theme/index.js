import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1F4E5F',
      dark: '#163A47',
      light: '#2F6B80',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#C45C26',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#F3F5F7',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#1A2330',
      secondary: '#5B6775',
    },
    divider: '#D7DEE5',
  },
  typography: {
    fontFamily: '"Source Sans 3", "Segoe UI", sans-serif',
    h4: { fontWeight: 700 },
    h5: { fontWeight: 650 },
    h6: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    MuiButton: {
      defaultProps: { disableElevation: true },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
  },
});

export default theme;