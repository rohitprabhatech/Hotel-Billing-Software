import { Box, Stack, Typography, useTheme } from '@mui/material';
import { DISPLAY_FONT } from './constants';

/** Illustrative billing dashboard in a device frame — not live tenant data. */
export default function BillingDashboardMock() {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';
  const panel = isDark ? '#141C24' : '#FFFFFF';
  const soft = isDark ? 'rgba(255,255,255,0.05)' : '#F4F7F9';
  const ink = isDark ? '#E8EEF2' : '#1A2330';
  const muted = isDark ? '#9AA7B5' : '#5B6775';
  const accent = theme.palette.primary.main;
  const warn = theme.palette.warning.main;
  const bezel = isDark ? '#0A1016' : '#1B2832';

  const kpis = [
    { label: "Today's Sales", value: '₹24,850' },
    { label: 'Bills', value: '128' },
    { label: 'Items Sold', value: '342' },
    { label: 'Low Stock', value: '8', hot: true },
  ];
  const bars = [38, 52, 46, 68, 58, 82, 74];
  const bills = [
    { no: '#1024', amount: '₹1,250', pay: 'Online' },
    { no: '#1023', amount: '₹850', pay: 'Cash' },
    { no: '#1022', amount: '₹2,140', pay: 'Cash' },
  ];
  const tops = ['Rice', 'Chicken Thali', 'Cold Drink', 'Shirt', 'Shoes'];

  return (
    <Box
      aria-hidden
      sx={{
        position: 'relative',
        width: '100%',
        maxWidth: { xs: 420, sm: 480, lg: 520 },
      }}
    >
      {/* Soft glow behind device */}
      <Box
        sx={{
          position: 'absolute',
          inset: { xs: '12% 8% 0', md: '8% 4% -4%' },
          borderRadius: '50%',
          background: isDark
            ? 'radial-gradient(circle, rgba(110,180,200,0.18), transparent 68%)'
            : 'radial-gradient(circle, rgba(31,78,95,0.14), transparent 68%)',
          filter: 'blur(8px)',
          pointerEvents: 'none',
        }}
      />

      {/* Laptop shell */}
      <Box sx={{ position: 'relative', zIndex: 1 }}>
        <Box
          sx={{
            borderRadius: { xs: '12px 12px 0 0', sm: '14px 14px 0 0' },
            bgcolor: bezel,
            p: { xs: '10px 10px 0', sm: '12px 12px 0' },
            boxShadow: isDark
              ? '0 32px 64px rgba(0,0,0,0.55)'
              : '0 28px 56px rgba(15,36,44,0.22)',
          }}
        >
          {/* Camera notch */}
          <Box
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: 'rgba(255,255,255,0.18)',
              mx: 'auto',
              mb: 1,
            }}
          />

          <Box
            sx={{
              borderRadius: '8px 8px 0 0',
              bgcolor: panel,
              overflow: 'hidden',
              border: '1px solid',
              borderColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
            }}
          >
            <Stack
              direction="row"
              alignItems="center"
              justifyContent="space-between"
              sx={{
                px: 1.75,
                py: 1.1,
                borderBottom: '1px solid',
                borderColor: 'divider',
                bgcolor: soft,
              }}
            >
              <Typography
                sx={{
                  fontFamily: DISPLAY_FONT,
                  fontWeight: 700,
                  fontSize: '0.8rem',
                  color: ink,
                }}
              >
                Sales Overview
              </Typography>
              <Typography variant="caption" sx={{ color: muted, fontWeight: 600 }}>
                Sample view
              </Typography>
            </Stack>

            <Box sx={{ p: { xs: 1.5, sm: 1.75 } }}>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 0.9,
                  mb: 1.5,
                }}
              >
                {kpis.map((k) => (
                  <Box
                    key={k.label}
                    sx={{
                      p: 1.15,
                      borderRadius: 1.25,
                      bgcolor: soft,
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Typography
                      variant="caption"
                      sx={{ color: muted, display: 'block', fontSize: '0.68rem' }}
                    >
                      {k.label}
                    </Typography>
                    <Typography
                      sx={{
                        fontFamily: DISPLAY_FONT,
                        fontWeight: 700,
                        fontSize: '1.05rem',
                        color: k.hot ? warn : ink,
                        mt: 0.2,
                        letterSpacing: '-0.02em',
                      }}
                    >
                      {k.value}
                    </Typography>
                  </Box>
                ))}
              </Box>

              <Box
                sx={{
                  mb: 1.5,
                  p: 1.35,
                  borderRadius: 1.25,
                  border: '1px solid',
                  borderColor: 'divider',
                  bgcolor: soft,
                }}
              >
                <Typography variant="caption" sx={{ color: muted, fontWeight: 650 }}>
                  Sales trend
                </Typography>
                <Stack
                  direction="row"
                  alignItems="flex-end"
                  spacing={0.65}
                  sx={{ height: 64, mt: 1 }}
                >
                  {bars.map((h, i) => (
                    <Box
                      key={i}
                      sx={{
                        flex: 1,
                        height: `${h}%`,
                        borderRadius: '3px 3px 0 0',
                        bgcolor: accent,
                        opacity: 0.35 + (i / bars.length) * 0.65,
                        transformOrigin: 'bottom',
                        animation: `barGrow 0.7s ease-out ${0.08 * i}s both`,
                        '@keyframes barGrow': {
                          from: { transform: 'scaleY(0.35)', opacity: 0.2 },
                          to: { transform: 'scaleY(1)' },
                        },
                        '@media (prefers-reduced-motion: reduce)': {
                          animation: 'none',
                        },
                      }}
                    />
                  ))}
                </Stack>
              </Box>

              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr', sm: '1.15fr 0.85fr' },
                  gap: 1,
                }}
              >
                <Box
                  sx={{
                    p: 1.35,
                    borderRadius: 1.25,
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <Typography variant="caption" sx={{ color: muted, fontWeight: 700 }}>
                    Recent Bills
                  </Typography>
                  <Stack spacing={0.85} sx={{ mt: 0.85 }}>
                    {bills.map((b) => (
                      <Stack
                        key={b.no}
                        direction="row"
                        justifyContent="space-between"
                        alignItems="center"
                      >
                        <Box>
                          <Typography
                            variant="body2"
                            fontWeight={650}
                            sx={{ color: ink, fontSize: '0.8rem' }}
                          >
                            Bill {b.no}
                          </Typography>
                          <Typography variant="caption" sx={{ color: muted }}>
                            {b.pay}
                          </Typography>
                        </Box>
                        <Typography
                          variant="body2"
                          fontWeight={700}
                          sx={{ color: ink, fontSize: '0.8rem' }}
                        >
                          {b.amount}
                        </Typography>
                      </Stack>
                    ))}
                  </Stack>
                </Box>
                <Box
                  sx={{
                    p: 1.35,
                    borderRadius: 1.25,
                    border: '1px solid',
                    borderColor: 'divider',
                    display: { xs: 'none', sm: 'block' },
                  }}
                >
                  <Typography variant="caption" sx={{ color: muted, fontWeight: 700 }}>
                    Top Items
                  </Typography>
                  <Stack spacing={0.55} sx={{ mt: 0.85 }}>
                    {tops.map((name, idx) => (
                      <Typography
                        key={name}
                        variant="body2"
                        sx={{ color: ink, fontSize: '0.78rem' }}
                      >
                        {idx + 1}. {name}
                      </Typography>
                    ))}
                  </Stack>
                </Box>
              </Box>
            </Box>
          </Box>
        </Box>

        {/* Laptop base */}
        <Box
          sx={{
            height: { xs: 10, sm: 12 },
            mx: { xs: 1.5, sm: 2.5 },
            borderRadius: '0 0 10px 10px',
            bgcolor: bezel,
            boxShadow: isDark ? '0 8px 20px rgba(0,0,0,0.35)' : '0 8px 18px rgba(15,36,44,0.18)',
          }}
        />
        <Box
          sx={{
            height: 5,
            mx: { xs: 4, sm: 6 },
            borderRadius: '0 0 8px 8px',
            bgcolor: isDark ? '#060A0E' : '#121A20',
            opacity: 0.9,
          }}
        />
      </Box>
    </Box>
  );
}
