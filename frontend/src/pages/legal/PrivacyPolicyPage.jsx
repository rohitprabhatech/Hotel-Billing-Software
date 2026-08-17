import { Link } from '@mui/material';
import { COMPANY } from '../../constants/company';
import LegalPageShell, { LegalHeading, LegalParagraph } from './LegalPageShell';

export default function PrivacyPolicyPage() {
  return (
    <LegalPageShell title="Privacy Policy" updated="16 August 2026">
      <LegalParagraph>
        This Privacy Policy explains how {COMPANY.legalName} (“we”, “us”) handles information when
        you use {COMPANY.productName} (the “Service”), a multi-business billing and sales management
        application.
      </LegalParagraph>

      <LegalHeading>1. Who this applies to</LegalHeading>
      <LegalParagraph>
        This policy applies to business owners and users who register for or use the Service, and to
        visitors of our public website. It is written in plain language for operational clarity and
        is not a substitute for independent legal advice.
      </LegalParagraph>

      <LegalHeading>2. Information we process</LegalHeading>
      <LegalParagraph>
        Depending on how you use the Service, we may process account details (such as name, email,
        and phone), business profile information, catalog and billing records you enter, delivery
        configuration (for example WhatsApp or email settings you provide), audit and activity logs,
        and technical logs needed to operate and secure the Service.
      </LegalParagraph>

      <LegalHeading>3. Tenant isolation</LegalHeading>
      <LegalParagraph>
        The Service is multi-tenant. Business data is scoped by tenant so that one registered
        business’s catalog, bills, reports, users, and settings are not shared with another business
        through normal application access controls.
      </LegalParagraph>

      <LegalHeading>4. How we use information</LegalHeading>
      <LegalParagraph>
        We use information to provide billing, inventory, reporting, notifications, and related
        features; to authenticate users; to support your business when you contact us; to maintain
        security and reliability; and to meet applicable legal obligations.
      </LegalParagraph>

      <LegalHeading>5. Sharing</LegalHeading>
      <LegalParagraph>
        We do not sell your business billing data. We may use infrastructure and messaging providers
        (for example email or WhatsApp Business Cloud API) only as needed to deliver features you
        enable. Those providers process data under their own terms when you configure integrations.
      </LegalParagraph>

      <LegalHeading>6. Retention & security</LegalHeading>
      <LegalParagraph>
        We retain account and operational data while your business uses the Service and as needed
        for backups, audits, dispute resolution, and legal requirements. We apply access controls,
        authentication, and role-based permissions. No method of transmission or storage is
        completely secure.
      </LegalParagraph>

      <LegalHeading>7. Your choices</LegalHeading>
      <LegalParagraph>
        Account holders can update profile and business settings in the application. For access,
        correction, or deletion requests related to your tenant, contact us using the details below.
        Some records (such as finalized bills and audit history) may be retained for business and
        compliance integrity.
      </LegalParagraph>

      <LegalHeading>8. Contact</LegalHeading>
      <LegalParagraph>
        {COMPANY.legalName}
        <br />
        {COMPANY.addressLines.join(', ')}
        <br />
        Email:{' '}
        <Link href={COMPANY.emailHref} fontWeight={650}>
          {COMPANY.email}
        </Link>
        <br />
        Phone:{' '}
        <Link href={COMPANY.phoneHref} fontWeight={650}>
          {COMPANY.phoneDisplay}
        </Link>
      </LegalParagraph>
    </LegalPageShell>
  );
}
