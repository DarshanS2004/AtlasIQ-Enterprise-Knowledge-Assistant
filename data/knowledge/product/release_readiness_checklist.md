# Release Readiness Checklist

An enterprise release may move to production only when all release gates pass.

Release gates:
- Product manager signs off on scope freeze.
- Engineering confirms rollback steps are tested.
- Quality engineering validates critical path regression results.
- Security reviews high-risk changes and confirms threat-model updates.
- Customer success receives release notes and support guidance before launch.

For enterprise-tier customers, launch windows must avoid regional blackout periods and require an on-call owner for the first two hours after deployment.

