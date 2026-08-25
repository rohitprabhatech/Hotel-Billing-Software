import './receipt.css';
import { paymentMethodLabel } from '../utils/paymentMethod';

/** Food-service types where FSSAI is typically relevant (mirrors backend). */
const FSSAI_RELEVANT_TYPES = new Set([
  'hotel_restaurant',
  'cafe_tea',
  'bakery_sweet',
  // legacy codes (pre–BIZ-01) — safe if old payloads remain
  'restaurant',
  'hotel',
]);

function formatMoney(value) {
  return Number(value || 0).toFixed(2);
}

function formatDate(value) {
  if (!value) return '';
  const d = new Date(value);
  return d.toLocaleString('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function commonGstRate(items = []) {
  const rates = [...new Set(items.map((i) => Number(i.gst_percentage)))];
  if (rates.length === 1) return rates[0];
  return null;
}

function showFssai(tenant = {}) {
  if (!tenant.fssai_number) return false;
  const type = String(tenant.business_type || '').toLowerCase();
  if (!type) return true; // legacy tenants without type still print if number set
  return FSSAI_RELEVANT_TYPES.has(type);
}

export default function PrintableReceipt({ bill, width = '80' }) {
  if (!bill) return null;

  const tenant = bill.tenant || {};
  const items = bill.items || [];
  const gstRate = commonGstRate(items);
  const halfRate = gstRate != null ? (gstRate / 2).toFixed(2) : null;
  const cityLine = [tenant.city, tenant.pincode].filter(Boolean).join(' / ');
  const businessName = tenant.business_name || 'BUSINESS';

  return (
    <div className={`receipt receipt--${width}`}>
      <div className="receipt__center receipt__business">{businessName}</div>
      {tenant.address ? <div className="receipt__center">{tenant.address}</div> : null}
      {cityLine ? <div className="receipt__center">{cityLine}</div> : null}
      {tenant.phone ? <div className="receipt__center">Mobile: {tenant.phone}</div> : null}

      <div className="receipt__divider" />
      <div className="receipt__center receipt__title">Cash Memo</div>
      {bill.status === 'CANCELLED' ? (
        <div className="receipt__center receipt__cancelled">*** CANCELLED ***</div>
      ) : null}
      <div className="receipt__divider" />

      <div className="receipt__row">
        <span>Date : {formatDate(bill.created_at)}</span>
        <span>Bill No. : {bill.bill_number}</span>
      </div>
      <div className="receipt__row">
        <span>Ref.: {bill.reference || bill.table_number || '-'}</span>
        <span>Emp. : {bill.created_by_name || '-'}</span>
      </div>

      <div className="receipt__divider" />
      <div className="receipt__cols receipt__cols--head">
        <span className="c-name">Particulars</span>
        <span className="c-qty">Qty</span>
        <span className="c-rate">Rate</span>
        <span className="c-amt">Amount</span>
      </div>
      <div className="receipt__divider" />

      {items.map((line) => (
        <div key={line.id}>
          <div className="receipt__cols">
            <span className="c-name">{line.item_name}</span>
            <span className="c-qty">{Number(line.quantity)}</span>
            <span className="c-rate">{formatMoney(line.unit_price)}</span>
            <span className="c-amt">
              {formatMoney(Number(line.unit_price) * Number(line.quantity))}
            </span>
          </div>
          {line.warranty_until ? (
            <div className="receipt__center" style={{ fontSize: '0.85em', marginBottom: 4 }}>
              Warranty until {line.warranty_until}
            </div>
          ) : null}
        </div>
      ))}

      <div className="receipt__divider" />
      <div className="receipt__row">
        <span>Sub Total :</span>
        <span>{formatMoney(bill.subtotal)}</span>
      </div>
      {Number(bill.discount) > 0 ? (
        <div className="receipt__row">
          <span>Discount :</span>
          <span>{formatMoney(bill.discount)}</span>
        </div>
      ) : null}
      <div className="receipt__row">
        <span>
          CGST{halfRate ? ` @ ${halfRate}%` : ''} On {formatMoney(bill.taxable_amount)} :
        </span>
        <span>{formatMoney(bill.cgst_amount)}</span>
      </div>
      <div className="receipt__row">
        <span>
          SGST{halfRate ? ` @ ${halfRate}%` : ''} On {formatMoney(bill.taxable_amount)} :
        </span>
        <span>{formatMoney(bill.sgst_amount)}</span>
      </div>
      {Number(bill.round_off) !== 0 ? (
        <div className="receipt__row">
          <span>Round Off :</span>
          <span>{formatMoney(bill.round_off)}</span>
        </div>
      ) : null}
      <div className="receipt__divider" />
      <div className="receipt__row receipt__total">
        <span>Total :</span>
        <span>{formatMoney(bill.grand_total)}</span>
      </div>
      <div className="receipt__row">
        <span>Payment Method :</span>
        <span>{paymentMethodLabel(bill.payment_method)}</span>
      </div>
      <div className="receipt__divider" />

      {tenant.gst_number ? <div>GSTIN: {tenant.gst_number}</div> : null}
      {showFssai(tenant) ? <div>FSSAI NO: {tenant.fssai_number}</div> : null}

      <div className="receipt__center receipt__thanks">Thank You</div>
      <div className="receipt__center">Visit Again</div>
    </div>
  );
}
