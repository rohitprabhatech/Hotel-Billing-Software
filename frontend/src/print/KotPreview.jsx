export default function KotPreview({ kot, tenantName = 'Kitchen' }) {
  if (!kot) return null;

  const channelLabel =
    kot.channel === 'dine_in'
      ? 'Dine-in'
      : kot.channel === 'takeaway'
        ? 'Takeaway'
        : kot.channel === 'delivery'
          ? 'Delivery'
          : kot.channel;

  return (
    <div className="receipt">
      <div className="receipt-header">
        <h1>{tenantName}</h1>
        <p className="receipt-meta">Kitchen Order Ticket</p>
      </div>
      <div className="receipt-section">
        <p>
          <strong>{kot.kot_number}</strong>
        </p>
        <p>Order: {kot.order_number}</p>
        <p>Channel: {channelLabel}</p>
        {kot.dining_table_code ? <p>Table: {kot.dining_table_code}</p> : null}
        <p>Status: {kot.status}</p>
        {kot.notes ? <p>Notes: {kot.notes}</p> : null}
      </div>
      <table className="receipt-lines">
        <thead>
          <tr>
            <th align="left">Item</th>
            <th align="right">Qty</th>
          </tr>
        </thead>
        <tbody>
          {(kot.items || []).map((line) => (
            <tr key={line.id}>
              <td>{line.item_name}</td>
              <td align="right">{line.quantity}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="receipt-footer">
        <p>Print #{kot.print_count || 1}</p>
        <p>{new Date(kot.printed_at || kot.created_at).toLocaleString()}</p>
      </div>
    </div>
  );
}
