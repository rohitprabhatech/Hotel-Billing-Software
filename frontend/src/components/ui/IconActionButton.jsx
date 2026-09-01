import { IconButton, Tooltip } from '@mui/material';

export default function IconActionButton({
  title,
  onClick,
  children,
  color = 'default',
  disabled = false,
  size = 'small',
  ...rest
}) {
  return (
    <Tooltip title={title}>
      <span>
        <IconButton
          size={size}
          color={color}
          onClick={onClick}
          disabled={disabled}
          aria-label={title}
          {...rest}
        >
          {children}
        </IconButton>
      </span>
    </Tooltip>
  );
}
