import NotificationsNoneOutlinedIcon from '@mui/icons-material/NotificationsNoneOutlined';
import {
  Badge,
  Box,
  Button,
  Divider,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Popover,
  Stack,
  Typography,
} from '@mui/material';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PATHS } from '../routes/paths';
import {
  fetchMasterUnreadNotificationCount,
  listMasterNotifications,
  markAllMasterNotificationsRead,
  markMasterNotificationRead,
} from '../services/masterService';

function formatWhen(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function MasterNotificationBell() {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState(null);
  const [rows, setRows] = useState([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);

  const refreshCount = useCallback(async () => {
    try {
      const res = await fetchMasterUnreadNotificationCount();
      setUnread(res.data?.unread_count || 0);
    } catch {
      // ignore transient errors in chrome
    }
  }, []);

  const loadList = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listMasterNotifications({ per_page: 20 });
      setRows(res.data || []);
      setUnread(res.meta?.unread_count ?? unread);
    } catch {
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [unread]);

  useEffect(() => {
    refreshCount();
    const timer = setInterval(refreshCount, 60000);
    return () => clearInterval(timer);
  }, [refreshCount]);

  const open = Boolean(anchorEl);

  const handleOpen = async (event) => {
    setAnchorEl(event.currentTarget);
    await loadList();
  };

  const handleClose = () => setAnchorEl(null);

  const handleRead = async (id) => {
    try {
      await markMasterNotificationRead(id);
      setRows((prev) => prev.map((row) => (row.id === id ? { ...row, is_read: true } : row)));
      setUnread((n) => Math.max(0, n - 1));
    } catch {
      // keep list as-is
    }
  };

  const handleReadAll = async () => {
    try {
      await markAllMasterNotificationsRead();
      setRows((prev) => prev.map((row) => ({ ...row, is_read: true })));
      setUnread(0);
    } catch {
      // keep list as-is
    }
  };

  const handleRowClick = async (row) => {
    if (!row.is_read) await handleRead(row.id);
    handleClose();
    navigate(PATHS.masterBusinesses);
  };

  return (
    <>
      <IconButton color="inherit" aria-label="Master notifications" onClick={handleOpen}>
        <Badge badgeContent={unread} color="error" max={99}>
          <NotificationsNoneOutlinedIcon />
        </Badge>
      </IconButton>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        slotProps={{ paper: { sx: { width: 360, maxWidth: '92vw' } } }}
      >
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ px: 2, py: 1.25 }}>
          <Typography fontWeight={700}>Notifications</Typography>
          <Button size="small" onClick={handleReadAll} disabled={!unread}>
            Mark all read
          </Button>
        </Stack>
        <Divider />
        {loading ? (
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Loading…
            </Typography>
          </Box>
        ) : null}
        {!loading && !rows.length ? (
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              No notifications yet.
            </Typography>
          </Box>
        ) : null}
        {!loading && rows.length ? (
          <List dense sx={{ maxHeight: 360, overflow: 'auto', py: 0 }}>
            {rows.map((row) => (
              <ListItem
                key={row.id}
                alignItems="flex-start"
                sx={{
                  bgcolor: row.is_read ? 'transparent' : 'action.hover',
                  cursor: 'pointer',
                }}
                onClick={() => handleRowClick(row)}
              >
                <ListItemText
                  primary={
                    <Typography variant="subtitle2" fontWeight={row.is_read ? 500 : 700}>
                      {row.title}
                    </Typography>
                  }
                  secondary={
                    <>
                      <Typography variant="body2" color="text.secondary" component="span">
                        {row.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                        {formatWhen(row.created_at)}
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        ) : null}
      </Popover>
    </>
  );
}
