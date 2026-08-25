import { Button, Table, TableBody, TableCell, TableHead, TableRow, Typography } from '@mui/material';

/**
 * Size × color stock grid. Selecting a cell sells that variant only (BIZ-26).
 */
export default function VariantStockGrid({ variants = [], onSelect, disabled = false }) {
  const sizes = [...new Set(variants.map((row) => row.size))];
  const colors = [...new Set(variants.map((row) => row.color))];
  const byKey = new Map(variants.map((row) => [`${row.size}|${row.color}`, row]));

  if (!variants.length) {
    return (
      <Typography variant="body2" color="text.secondary">
        No size/color variants on this item.
      </Typography>
    );
  }

  return (
    <Table size="small" sx={{ minWidth: 240 }}>
      <TableHead>
        <TableRow>
          <TableCell>Size</TableCell>
          {colors.map((color) => (
            <TableCell key={color} align="center">
              {color}
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {sizes.map((size) => (
          <TableRow key={size}>
            <TableCell sx={{ fontWeight: 600 }}>{size}</TableCell>
            {colors.map((color) => {
              const variant = byKey.get(`${size}|${color}`);
              const stock = variant ? Number(variant.stock_quantity) : null;
              const out = !variant || stock <= 0;
              return (
                <TableCell key={`${size}|${color}`} align="center">
                  <Button
                    size="small"
                    variant={out ? 'outlined' : 'contained'}
                    color={out ? 'inherit' : 'primary'}
                    disabled={disabled || out}
                    onClick={() => variant && onSelect(variant)}
                    sx={{ minWidth: 72, textTransform: 'none' }}
                  >
                    {variant ? `${stock}` : '—'}
                  </Button>
                </TableCell>
              );
            })}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
