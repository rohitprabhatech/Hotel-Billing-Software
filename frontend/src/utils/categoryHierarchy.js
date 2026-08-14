/** Shared category tree helpers for Owner/Billing UI. */

export function buildHierarchyRows(categories) {
  const byParent = new Map();
  (categories || []).forEach((category) => {
    const key = category.parent_id || 'root';
    if (!byParent.has(key)) byParent.set(key, []);
    byParent.get(key).push(category);
  });
  byParent.forEach((list) => list.sort((a, b) => a.name.localeCompare(b.name)));

  const rows = [];
  const walk = (parentKey, depth) => {
    (byParent.get(parentKey) || []).forEach((category) => {
      rows.push({ category, depth });
      walk(category.id, depth + 1);
    });
  };
  walk('root', 0);

  const listed = new Set(rows.map((row) => row.category.id));
  (categories || [])
    .filter((category) => !listed.has(category.id))
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach((category) => rows.push({ category, depth: 0 }));

  return rows;
}

export function formatCategoryPath(pathOrName) {
  if (!pathOrName) return '';
  return String(pathOrName).replace(/\s*[>/]\s*/g, ' → ');
}

export function collectDescendantIds(categories, rootId) {
  const childrenMap = new Map();
  (categories || []).forEach((category) => {
    const parentKey = category.parent_id || '';
    if (!childrenMap.has(parentKey)) childrenMap.set(parentKey, []);
    childrenMap.get(parentKey).push(category.id);
  });

  const descendants = new Set();
  const stack = [...(childrenMap.get(rootId) || [])];
  while (stack.length) {
    const current = stack.pop();
    if (descendants.has(current)) continue;
    descendants.add(current);
    stack.push(...(childrenMap.get(current) || []));
  }
  return descendants;
}
