import { Link } from '@mui/material';
import { COMPANY, SUBSCRIPTION_PLAN } from '../../constants/company';
import LegalPageShell, { LegalHeading, LegalParagraph } from './LegalPageShell';

export default function TermsOfServicePage() {
  return (
    <LegalPageShell title="Terms of Service" updated="16 August 2026">
      <LegalParagraph>
        These Terms of Service (“Terms”) govern use of {COMPANY.productName} provided by{' '}
        {COMPANY.legalName}. By registering a business or signing in, you agree to these Terms.
      </LegalParagraph>

      <LegalHeading>1. The Service</LegalHeading>
      <LegalParagraph>
        {COMPANY.productName} is software for multi-business billing and sales management, including
        catalog, billing, stock, reports, notifications, and related tools described in the product.
        Features may evolve over time.
      </LegalParagraph>

      <LegalHeading>2. Accounts & responsibilities</LegalHeading>
      <LegalParagraph>
        You must provide accurate registration information and keep credentials secure. The business
        owner is responsible for users invited to their tenant, for data entered into the Service,
        and for complying with tax, invoicing, and industry rules that apply to their business.
      </LegalParagraph>

      <LegalHeading>3. Acceptable use</LegalHeading>
      <LegalParagraph>
        You may not misuse the Service, attempt unauthorized access to other tenants, disrupt
        operations, or use the Service for unlawful activity. We may suspend access for security or
        abuse concerns.
      </LegalParagraph>

      <LegalHeading>4. Subscription & pricing</LegalHeading>
      <LegalParagraph>
        Published pricing (currently {SUBSCRIPTION_PLAN.priceDisplay}) is informational. Online
        checkout may not be enabled in the application. Activation, renewal, and invoicing are
        handled by contacting {COMPANY.legalName}. Fees and commercial terms agreed separately with
        us control if they differ from marketing copy.
      </LegalParagraph>

      <LegalHeading>5. Data & backups</LegalHeading>
      <LegalParagraph>
        You retain ownership of business content you submit. You grant us permission to host and
        process that content solely to operate the Service. You should export or retain critical
        records as needed for your own compliance. We provide operational safeguards but do not
        guarantee uninterrupted availability.
      </LegalParagraph>

      <LegalHeading>6. Third-party integrations</LegalHeading>
      <LegalParagraph>
        Optional integrations (such as WhatsApp Business or email delivery) depend on third-party
        platforms and your configuration. Their availability, policies, and fees are outside our
        control.
      </LegalParagraph>

      <LegalHeading>7. Disclaimer & liability</LegalHeading>
      <LegalParagraph>
        The Service is provided on an “as available” basis. To the maximum extent permitted by law,
        {COMPANY.legalName} is not liable for indirect or consequential losses arising from use of
        the Service. Nothing in these Terms limits liability that cannot be limited under applicable
        law.
      </LegalParagraph>

      <LegalHeading>8. Changes</LegalHeading>
      <LegalParagraph>
        We may update these Terms and will revise the “Last updated” date when we do. Continued use
        after changes constitutes acceptance of the updated Terms where permitted by law.
      </LegalParagraph>

      <LegalHeading>9. Contact</LegalHeading>
      <LegalParagraph>
        Questions about these Terms:{' '}
        <Link href={COMPANY.emailHref} fontWeight={650}>
          {COMPANY.email}
        </Link>{' '}
        or{' '}
        <Link href={COMPANY.phoneHref} fontWeight={650}>
          {COMPANY.phoneDisplay}
        </Link>
        .
      </LegalParagraph>
    </LegalPageShell>
  );
}
