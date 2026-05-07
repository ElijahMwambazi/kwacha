# Scraping and Import Policy

Kwacha! should collect data respectfully and transparently.

## Rules

- Prefer official public sources.
- Store source URLs.
- Do not scrape private groups or accounts.
- Do not bypass login, paywalls, or anti-bot systems.
- Do not overload websites.
- Respect robots.txt where applicable.
- Treat scraped data as uncertain until reviewed.
- Keep raw imported data for auditing.
- Use confidence scores for imported observations.

## Review Flow

Imported data
→ pending_price_observations
→ user reviews
→ approve/edit/reject
→ approved data becomes price_observation
