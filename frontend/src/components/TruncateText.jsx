import { Tooltip, Typography } from '@mui/material';

/** Single-line ellipsis with full value in tooltip. */
export default function TruncateText({
  value,
  maxWidth = 220,
  variant = 'body2',
  ...props
}) {
  const text = value == null || value === '' ? '—' : String(value);
  return (
    <Tooltip title={text === '—' ? '' : text} disableHoverListener={text === '—' || text.length < 24}>
      <Typography
        variant={variant}
        noWrap
        sx={{
          maxWidth,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          display: 'block',
        }}
        {...props}
      >
        {text}
      </Typography>
    </Tooltip>
  );
}
