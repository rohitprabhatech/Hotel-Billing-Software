import { Box, Card, CardActionArea, CardContent, Typography } from '@mui/material';

/** Compact catalog tile used on POS item grids. */
export default function PosCatalogCard({
  title,
  subtitle = null,
  disabled = false,
  onClick,
  selected = false,
}) {
  return (
    <Card
      variant="outlined"
      sx={{
        height: '100%',
        opacity: disabled ? 0.55 : 1,
        borderColor: selected ? 'primary.main' : 'divider',
        transition: 'border-color 0.15s ease, background-color 0.15s ease',
        '&:hover': disabled
          ? undefined
          : {
              borderColor: 'primary.main',
              bgcolor: 'action.hover',
            },
      }}
    >
      <CardActionArea onClick={onClick} disabled={disabled} sx={{ height: '100%' }}>
        <CardContent sx={{ py: 1.5, px: 1.5, '&:last-child': { pb: 1.5 } }}>
          <Typography variant="body2" fontWeight={600} noWrap>
            {title}
          </Typography>
          {subtitle ? (
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.35 }}>
              {subtitle}
            </Typography>
          ) : null}
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
