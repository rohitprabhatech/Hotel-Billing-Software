import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  spacing: 8,
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
    success: {
      main: '#2E7D4F',
    },
    error: {
      main: '#B42318',
    },
    warning: {
      main: '#B54708',
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
    h4: { fontWeight: 700, letterSpacing: '-0.02em', fontSize: '1.75rem' },
    h5: { fontWeight: 650, letterSpacing: '-0.015em', fontSize: '1.5rem' },
    h6: { fontWeight: 600, fontSize: '1.125rem', lineHeight: 1.35 },
    subtitle1: { fontWeight: 600, fontSize: '1rem' },
    subtitle2: { fontWeight: 600, fontSize: '0.875rem' },
    button: { textTransform: 'none', fontWeight: 600, fontSize: '0.875rem' },
    body1: { fontSize: '0.9375rem', lineHeight: 1.55 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
    caption: { fontSize: '0.75rem', lineHeight: 1.4 },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          WebkitFontSmoothing: 'antialiased',
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
        size: 'medium',
      },
      styleOverrides: {
        root: {
          minHeight: 38,
          borderRadius: 8,
          paddingInline: 16,
          gap: 8,
        },
        sizeSmall: {
          minHeight: 32,
          paddingInline: 12,
          fontSize: '0.8125rem',
        },
        sizeLarge: {
          minHeight: 40,
          paddingInline: 18,
        },
        startIcon: {
          marginRight: 0,
        },
        endIcon: {
          marginLeft: 0,
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
        sizeSmall: {
          padding: 8,
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        size: 'small',
        variant: 'outlined',
      },
    },
    MuiOutlinedInput: {
      defaultProps: {
        size: 'small',
      },
      styleOverrides: {
        root: {
          borderRadius: 8,
          backgroundColor: '#FFFFFF',
        },
        input: {
          paddingTop: 10,
          paddingBottom: 10,
        },
        inputSizeSmall: {
          paddingTop: 10,
          paddingBottom: 10,
        },
      },
    },
    MuiFormControl: {
      defaultProps: {
        size: 'small',
      },
    },
    MuiInputLabel: {
      defaultProps: {
        size: 'small',
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          border: '1px solid #D7DEE5',
          borderRadius: 12,
          boxShadow: '0 1px 2px rgba(26, 35, 48, 0.04)',
        },
      },
    },
    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 24,
          '&:last-child': {
            paddingBottom: 24,
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiAppBar: {
      defaultProps: {
        color: 'inherit',
        elevation: 0,
      },
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderBottom: '1px solid #D7DEE5',
          backgroundColor: '#FFFFFF',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid #D7DEE5',
          backgroundColor: '#FFFFFF',
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-head': {
            fontWeight: 650,
            fontSize: '0.8125rem',
            backgroundColor: '#F7F9FB',
            color: '#1A2330',
            borderBottom: '1px solid #D7DEE5',
          },
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: 'rgba(31, 78, 95, 0.04)',
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottomColor: '#E8EEF2',
          fontSize: '0.875rem',
          paddingTop: 14,
          paddingBottom: 14,
          paddingLeft: 16,
          paddingRight: 16,
        },
        sizeSmall: {
          paddingTop: 14,
          paddingBottom: 14,
          paddingLeft: 16,
          paddingRight: 16,
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 12,
          margin: 16,
        },
      },
    },
    MuiDialogTitle: {
      styleOverrides: {
        root: {
          padding: '20px 24px 12px',
          fontSize: '1.125rem',
          fontWeight: 650,
        },
      },
    },
    MuiDialogContent: {
      styleOverrides: {
        root: {
          padding: '8px 24px 8px',
        },
      },
    },
    MuiDialogActions: {
      styleOverrides: {
        root: {
          padding: '16px 24px 20px',
          gap: 8,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiTooltip: {
      defaultProps: {
        arrow: true,
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          marginBottom: 4,
          minHeight: 44,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 600,
        },
        sizeSmall: {
          height: 24,
        },
      },
    },
  },
});

export default theme;
