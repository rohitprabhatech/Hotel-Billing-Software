/** Public-facing company / support contacts for Prabha Technology. */

export const COMPANY = {
  legalName: 'Prabha Technology Pvt. Ltd.',
  productName: 'Business Billing',
  tagline: 'Billing software for every kind of shop.',
  addressLines: [
    'Pune Satara Road, Khed-Shivapur',
    'Pune, Maharashtra 412205',
    'India',
  ],
  email: 'support@prabhatech.in',
  phone: '+91 20 7123 4567',
  phoneHref: 'tel:+912071234567',
  emailHref: 'mailto:support@prabhatech.in',
  supportNote: '24/7 support for registered businesses',
  planPriceLabel: '₹550 / month',
};

/** Informational subscription plan — no online checkout in this product yet. */
export const SUBSCRIPTION_PLAN = {
  name: 'Business Billing Plan',
  priceInr: 550,
  priceLabel: '₹550',
  periodLabel: 'per month',
  priceDisplay: '₹550 / month',
  currencyNote: 'Prices in Indian Rupees (INR).',
  billingNote:
    'Informational pricing only. Online payment is not enabled in the app yet — contact Prabha Technology to activate or renew your plan.',
  includes: [
    'Multi-user billing (Owner + Billing users)',
    'Items, categories, GST billing & receipts',
    'Sales reports and exports',
    'AI business assistant (tenant-scoped)',
    'Audit trail and 24/7 support access',
  ],
  ctaRegister: 'Register Business',
  ctaLogin: 'Login',
  ctaContact: 'Contact to subscribe',
};
