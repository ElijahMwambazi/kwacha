# Collection Strategy

Kwacha! uses hybrid data collection.

## Collection Methods

1. Manual price entry
2. CSV imports
3. Public economic indicator imports
4. Public catalogue/specials scraping
5. Receipt or flyer OCR later
6. Crowdsourced submissions later

## Recommended Source Priority

| Source | Reliability | Difficulty |
|---|---:|---:|
| Manual entry | High | Low |
| Official public data | High | Medium |
| CSV imports | High | Low |
| Catalogue scraping | Medium | Medium |
| Receipt OCR | Medium | High |
| Social media screenshots | Low/Medium | High |

## Rule

Scraped or OCR data should not go directly into final price observations. It should enter a pending review queue first.
