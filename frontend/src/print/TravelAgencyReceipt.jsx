import './receipt.css';
import { paymentMethodLabel } from '../utils/paymentMethod';
import {
  commonGstRate,
  formatDateLong,
  formatRupee,
  receiptDimensions,
} from './receiptUtils';

export default function TravelAgencyReceipt({ bill, width = 'a5', billingSettings = null }) {
  if (!bill) return null;

  const tenant = bill.tenant || {};
  const items = bill.items || [];
  const gstRate = commonGstRate(items);
  const halfRate = gstRate != null ? (gstRate / 2).toFixed(2) : null;
  const cityLine = [tenant.city, tenant.state, tenant.pincode].filter(Boolean).join(', ');
  const businessName = tenant.business_name || 'TRAVEL AGENCY';
  const settings = billingSettings || tenant.billing_settings || {};
  const customStyle = receiptDimensions(width, settings);
  const contactLine = [tenant.phone, tenant.email].filter(Boolean).join('  |  ');

  return (
    <div className={`receipt receipt--travel receipt--${width}`} style={customStyle}>
      <div className="travel-voucher">
        <header className="travel-voucher__header">
          <div className="travel-voucher__brand">{businessName}</div>
          {tenant.address ? <div className="travel-voucher__sub">{tenant.address}</div> : null}
          {cityLine ? <div className="travel-voucher__sub">{cityLine}</div> : null}
          {contactLine ? <div className="travel-voucher__sub">{contactLine}</div> : null}
        </header>

        <div className="travel-voucher__badge">
          <span>TRAVEL BOOKING VOUCHER</span>
        </div>

        {bill.status === 'CANCELLED' ? (
          <div className="travel-voucher__cancelled">CANCELLED</div>
        ) : null}

        <section className="travel-voucher__details">
          <div className="travel-voucher__detail-block">
            <div className="travel-voucher__detail-title">Guest Details</div>
            <div className="travel-voucher__detail-row">
              <span>Name</span>
              <strong>{bill.customer_name || 'Walk-in'}</strong>
            </div>
            {bill.customer_phone_e164 ? (
              <div className="travel-voucher__detail-row">
                <span>Mobile</span>
                <strong>{bill.customer_phone_e164}</strong>
              </div>
            ) : null}
            <div className="travel-voucher__detail-row">
              <span>Reference</span>
              <strong>{bill.reference || bill.table_number || '-'}</strong>
            </div>
          </div>

          <div className="travel-voucher__detail-block">
            <div className="travel-voucher__detail-title">Booking Info</div>
            <div className="travel-voucher__detail-row">
              <span>Voucher No.</span>
              <strong>{bill.bill_number}</strong>
            </div>
            <div className="travel-voucher__detail-row">
              <span>Date</span>
              <strong>{formatDateLong(bill.created_at)}</strong>
            </div>
            <div className="travel-voucher__detail-row">
              <span>Booked By</span>
              <strong>{bill.created_by_name || '-'}</strong>
            </div>
            <div className="travel-voucher__detail-row">
              <span>Payment</span>
              <strong>{paymentMethodLabel(bill.payment_method)}</strong>
            </div>
          </div>
        </section>

        <table className="travel-voucher__table">
          <thead>
            <tr>
              <th className="col-sno">#</th>
              <th className="col-name">Package / Service</th>
              <th className="col-qty">Pax</th>
              <th className="col-rate">Rate</th>
              <th className="col-amt">Amount</th>
            </tr>
          </thead>
          <tbody>
            {items.map((line, index) => (
              <tr key={line.id}>
                <td className="col-sno">{index + 1}</td>
                <td className="col-name">{line.item_name}</td>
                <td className="col-qty">{Number(line.quantity)}</td>
                <td className="col-rate">{formatRupee(line.unit_price)}</td>
                <td className="col-amt">
                  {formatRupee(Number(line.unit_price) * Number(line.quantity))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <section className="travel-voucher__summary">
          <div className="travel-voucher__summary-lines">
            <div className="travel-voucher__summary-row">
              <span>Sub Total</span>
              <span>{formatRupee(bill.subtotal)}</span>
            </div>
            {Number(bill.discount) > 0 ? (
              <div className="travel-voucher__summary-row">
                <span>Discount</span>
                <span>{formatRupee(bill.discount)}</span>
              </div>
            ) : null}
            <div className="travel-voucher__summary-row">
              <span>CGST{halfRate ? ` @ ${halfRate}%` : ''}</span>
              <span>{formatRupee(bill.cgst_amount)}</span>
            </div>
            <div className="travel-voucher__summary-row">
              <span>SGST{halfRate ? ` @ ${halfRate}%` : ''}</span>
              <span>{formatRupee(bill.sgst_amount)}</span>
            </div>
            {Number(bill.round_off) !== 0 ? (
              <div className="travel-voucher__summary-row">
                <span>Round Off</span>
                <span>{formatRupee(bill.round_off)}</span>
              </div>
            )}
          </div>
          <div className="travel-voucher__total-box">
            <span>Total Payable</span>
            <strong>{formatRupee(bill.grand_total)}</strong>
          </div>
        </section>

        <footer className="travel-voucher__footer">
          {tenant.gst_number ? <div>GSTIN: {tenant.gst_number}</div> : null}
          <div className="travel-voucher__note">
            Please carry this voucher during your journey. Present it at boarding / check-in.
          </div>
          <div className="travel-voucher__signatures">
            <div>
              <div className="travel-voucher__sign-line" />
              <span>Guest Signature</span>
            </div>
            <div>
              <div className="travel-voucher__sign-line" />
              <span>Authorized Signatory</span>
            </div>
          </div>
          <div className="travel-voucher__thanks">Thank you for choosing {businessName}</div>
          <div className="travel-voucher__wish">Safe journey &amp; happy travels!</div>
        </footer>
      </div>
    </div>
  );
}
