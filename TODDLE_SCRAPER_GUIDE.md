# Toddle Scraper Usage Guide

## Quick Start

### 1. Start the Backend Server

```bash
cd backend
python main.py
```

The API will run on `http://localhost:8001`

### 2. Start the Frontend (Optional)

```bash
cd frontend
npm install  # First time only
npm run dev
```

The UI will run on `http://localhost:5173`

## Using the Toddle Scraper

### Method 1: Via Frontend UI

1. Open the frontend at `http://localhost:5173`
2. Navigate to **"Public Docs"** tab
3. Select **"Toddle Docs"** scraper
4. Enter a Toddle collection URL, for example:
   ```
   https://support.toddleapp.com/en/collections/8595214-educators
   ```
5. Click **"Execute Scrape"**
6. The scraped content will appear below in markdown format
7. Click **"Copy Raw Markdown"** to copy the results

### Method 2: Via API (cURL/Postman)

```bash
# Example: Scrape Educators collection
curl -X POST http://localhost:8001/scrape-toddle \
  -H "Content-Type: application/json" \
  -d '{"url": "https://support.toddleapp.com/en/collections/8595214-educators"}'
```

### Method 3: Via Python Test Script

```bash
cd backend
python test_toddle_scraper.py
```

This will:
1. Open a browser for you to manually log in
2. Wait for you to log in to Toddle
3. Scrape the specified collection
4. Save the output to a markdown file

## URL Formats Supported

### Collection URL (Recommended)
Scrapes all topics and articles within a collection:
```
https://support.toddleapp.com/en/collections/COLLECTION_ID-collection-name
```

**Example**:
```
https://support.toddleapp.com/en/collections/8595214-educators
```

### Single Article URL
Scrapes just one article:
```
https://support.toddleapp.com/en/articles/ARTICLE_ID-article-slug
```

**Example**:
```
https://support.toddleapp.com/en/articles/8612033-how-do-i-sign-in-to-my-educator-account-on-web
```

## Output Format

The scraper generates markdown with the following structure:

```markdown
# Toddle Documentation Export

**Total Articles**: 45

---

# Collection: Educators

## Topic: Getting Started

### How do I sign in to my educator account on web?

**Link**: https://support.toddleapp.com/en/articles/8612033-...

[Article content in markdown format...]

---

### Next Article Title

...
```

## Example Collections to Try

- **Educators**: `https://support.toddleapp.com/en/collections/8595214-educators`
- **Families**: `https://support.toddleapp.com/en/collections/8595216-families`
- **Students**: `https://support.toddleapp.com/en/collections/8764636-students`

## Authentication Notes

⚠️ **Important**: Unlike other public scrapers (Odoo, Prompting Guide), Toddle may require authentication to access full documentation content. 

**If content is restricted**:
1. Use the `/launch-login` endpoint to open a browser
2. Manually log in to Toddle support
3. Keep the browser open
4. Run the scraper - it will use the authenticated session

**API Flow**:
```bash
# Step 1: Launch browser
curl -X POST http://localhost:8001/launch-login

# Step 2: Manually log in through the opened browser

# Step 3: Verify authentication
curl http://localhost:8001/check-auth

# Step 4: Scrape (browser session is reused)
curl -X POST http://localhost:8001/scrape-toddle \
  -H "Content-Type: application/json" \
  -d '{"url": "https://support.toddleapp.com/en/collections/8595214-educators"}'
```

## Troubleshooting

### "No articles found"
- The collection page structure might be different than expected
- Try viewing the page source to check the HTML structure
- Check the browser console for JavaScript errors

### "Browser not started"
- Call `/launch-login` first to initialize the browser
- Make sure ChromeDriver is installed

### Scraping is slow
- The scraper waits between requests to be respectful (1 second between articles)
- Large collections with 100+ articles may take several minutes
- Progress is logged to the console

### Content is incomplete
- Some content might be loaded dynamically via JavaScript
- The scraper waits 2-3 seconds for initial page load
- For very slow connections, you may need to increase wait times in `toddle_scraper.py`

## Advanced: Customizing the Scraper

Edit `backend/scrapers/toddle_scraper.py`:

- **Increase wait times**: Adjust `time.sleep()` values
- **Change selectors**: Update CSS selectors if Toddle changes their HTML structure  
- **Add filters**: Filter articles by topic or keywords
- **Custom formatting**: Modify `format_articles_to_markdown()` function
