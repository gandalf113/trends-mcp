# Trending Server

MCP server for fetching trending topics from Reddit and Google Trends, and generating PDF reports.

## Features

- Fetch trending topics from Reddit
- Fetch trending topics from Google Trends
- Generate PDF reports from trending news data
- Upload PDFs to Digital Ocean Spaces (or any S3-compatible storage)

## Installation

```bash
poetry install
```

## Environment Variables

### Digital Ocean Spaces Configuration (Recommended)

```bash
# Required
SPACES_BUCKET=your-space-name
SPACES_KEY=your-spaces-access-key
SPACES_SECRET=your-spaces-secret-key
SPACES_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com  # Replace nyc3 with your region

# Optional - for CDN URLs
SPACES_CDN_BASE_URL=https://your-cdn-domain.com
```

### AWS S3 Configuration (Alternative)

If you're using AWS S3 instead of Digital Ocean Spaces:

```bash
# Required
SPACES_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
# No endpoint URL needed for AWS S3

# Optional - for CloudFront CDN URLs
SPACES_CDN_BASE_URL=https://your-cloudfront-domain.cloudfront.net
```

## Usage

### As MCP Server

Run the server:

```bash
poetry run mcp run trending_server.server:app
```

### Available Tools

#### `get_reddit_trending_topics(limit: int = 10)`

Fetches trending topics from Reddit.

#### `get_google_trending_topics(limit: int = 10)`

Fetches trending topics from Google Trends.

#### `create_trending_news_pdf(asOf: str, trending: list[dict], ...)`

Generates a PDF report from trending news data and uploads it to storage.

**Parameters:**
- `asOf` - ISO-8601 timestamp
- `trending` - Array of trending items with:
  - `title` - Story headline
  - `summary` - Story description
  - `category` - One of: ENTERTAINMENT, BUSINESS, POLITICS, SPORTS
  - `audience` - Target audience (e.g., "US", "Virginia")
  - `items` - Array of source URLs
- `bucket_name` - Optional (uses env var if not provided)
- `cdn_base_url` - Optional (uses env var if not provided)
- `endpoint_url` - Optional (uses env var if not provided)
- `filename` - Optional (auto-generated if not provided)

**Returns:** URL to the uploaded PDF (CDN URL if configured, otherwise direct storage URL)

## Digital Ocean Spaces Setup

1. Create a Space in your Digital Ocean account
2. Generate Spaces access keys (Settings → API → Spaces Keys)
3. Note your Space name and region
4. Set the environment variables as shown above
5. (Optional) Enable CDN for your Space and set `SPACES_CDN_BASE_URL`

## License

MIT
