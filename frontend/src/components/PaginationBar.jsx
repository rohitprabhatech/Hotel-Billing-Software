import { Button, Stack, Typography } from '@mui/material';

/**
 * Simple pager for list APIs that return meta.page / meta.per_page / meta.total.
 */
export default function PaginationBar({ page = 1, perPage = 50, total = 0, onPageChange }) {
  const safePage = Math.max(1, Number(page) || 1);
  const safePerPage = Math.max(1, Number(perPage) || 50);
  const safeTotal = Math.max(0, Number(total) || 0);
  const totalPages = Math.max(1, Math.ceil(safeTotal / safePerPage) || 1);
  const from = safeTotal === 0 ? 0 : (safePage - 1) * safePerPage + 1;
  const to = Math.min(safePage * safePerPage, safeTotal);

  if (safeTotal <= safePerPage && safePage === 1) {
    return null;
  }

  return (
    <Stack
      direction={{ xs: 'column', sm: 'row' }}
      spacing={1.5}
      alignItems={{ xs: 'stretch', sm: 'center' }}
      justifyContent="space-between"
      sx={{ px: { xs: 1.5, sm: 2 }, py: 1.5 }}
    >
      <Typography variant="body2" color="text.secondary">
        Showing {from}–{to} of {safeTotal}
      </Typography>
      <Stack direction="row" spacing={1} justifyContent="flex-end">
        <Button
          size="small"
          variant="outlined"
          disabled={safePage <= 1}
          onClick={() => onPageChange?.(safePage - 1)}
        >
          Previous
        </Button>
        <Typography variant="body2" sx={{ alignSelf: 'center', px: 1 }}>
          Page {safePage} / {totalPages}
        </Typography>
        <Button
          size="small"
          variant="outlined"
          disabled={safePage >= totalPages}
          onClick={() => onPageChange?.(safePage + 1)}
        >
          Next
        </Button>
      </Stack>
    </Stack>
  );
}
