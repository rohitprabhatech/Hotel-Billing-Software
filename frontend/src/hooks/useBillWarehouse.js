import { useEffect, useMemo, useState } from 'react';
import { listWarehouses } from '../services/warehouseService';

/** Pick a valid warehouse id for bill checkout, or undefined to let the server default. */
export function resolveBillWarehouseId(warehouseEnabled, warehouseId, warehouses) {
  if (!warehouseEnabled) return undefined;
  const rows = (warehouses || []).filter((w) => w.is_active !== false);
  if (!rows.length) return undefined;
  if (warehouseId && rows.some((w) => w.id === warehouseId)) return warehouseId;
  const def = rows.find((w) => w.is_default) || rows[0];
  return def?.id;
}

export function useBillWarehouse(warehouseEnabled) {
  const [warehouses, setWarehouses] = useState([]);
  const [warehouseId, setWarehouseId] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    if (!warehouseEnabled) {
      setWarehouses([]);
      setWarehouseId('');
      setLoadError('');
      return undefined;
    }

    let active = true;
    setLoading(true);
    setLoadError('');

    listWarehouses()
      .then((res) => {
        if (!active) return;
        const rows = (res.data || []).filter((w) => w.is_active !== false);
        setWarehouses(rows);
        setWarehouseId((prev) => {
          if (prev && rows.some((w) => w.id === prev)) return prev;
          const def = rows.find((w) => w.is_default) || rows[0];
          return def?.id || '';
        });
      })
      .catch((err) => {
        if (!active) return;
        setWarehouses([]);
        setWarehouseId('');
        setLoadError(
          err.response?.data?.error?.message || 'Could not load warehouses. Bills will use the main store.',
        );
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [warehouseEnabled]);

  const resolvedWarehouseId = useMemo(
    () => resolveBillWarehouseId(warehouseEnabled, warehouseId, warehouses),
    [warehouseEnabled, warehouseId, warehouses],
  );

  return {
    warehouses,
    warehouseId,
    setWarehouseId,
    resolvedWarehouseId,
    loading,
    loadError,
  };
}
