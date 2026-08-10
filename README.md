# 🏡 Realestate.com.au Property API: sold property prices, rentals, and for-sale listings by suburb

> Give it an Australian suburb. Get back structured JSON: sold property prices with confirmed sale dates, rental listings with advertised rent, and for-sale stock, all from one API with no listing URL to find first.

**Actor page:** [apify.com/johnvc/realestate-au-property-api](https://apify.com/johnvc/realestate-au-property-api?fpr=9n7kx3)
**Input schema:** [apify.com/johnvc/realestate-au-property-api/input-schema](https://apify.com/johnvc/realestate-au-property-api/input-schema?fpr=9n7kx3)

This repo is a working Python client for the Realestate.com.au Property API on Apify. The API turns Australian property listings into clean rows: street address, suburb, state, postcode, property type, beds, baths, parking, land size, floor area, agent details, photo URLs, and latitude and longitude. Ask it for `sold` and you get sold property prices with a confirmed `soldDate` and the selling agency. Ask it for `rent` and you get the advertised rent, which is how you track the australia rental market suburb by suburb. Ask it for `buy` and you get current australian property listings.

## Video Walkthrough

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

The fastest way to pull sold property prices for an Australian suburb is to leave `mode` on `search`, set `listingType` to `sold`, and put one location in `locations`, written as `"Coomera, QLD, 4209"`. You never supply a listing URL: the API builds the search from the suburb, state, and postcode you give it. Each row that comes back carries `streetAddress`, `suburb`, `state`, `postcode`, `bedrooms`, `bathrooms`, `parking`, `landSize`, `soldDate`, `lastSoldAgency`, `estimatedPrice`, `agents`, `latitude`, and `longitude`. The sale date is confirmed; the price is the source's estimate, because Australian sale prices are often never publicly disclosed. Flip `listingType` to `rent` and the same suburb returns current rentals with `rentPrice` and `rentCurrency`, which is what a rental yield calculation needs. Flip it to `buy` and you get what is on the market right now. One concrete use: run `sold` across the suburbs you cover, group by `lastSoldAgency`, and you have a monthly picture of which agency is winning listings in your patch.

A suburb must be paired with its state, because several Australian suburbs share a name. `"Coomera, QLD"` works, `"Coomera"` on its own is rejected with a clear message rather than a silent guess.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- An Apify account and API key ([get a free key here](https://apify.com?fpr=9n7kx3))

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnisanerd/Apify-Realestate-AU-Property-API.git
   cd Apify-Realestate-AU-Property-API
   ```

2. **Install dependencies with uv**
   ```bash
   # Install uv if you do not have it:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies:
   uv sync
   ```

3. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Apify API key
   # Get your free API key at: https://apify.com?fpr=9n7kx3
   ```

4. **Run the example**
   ```bash
   uv run python realestate-au-property-api-example.py
   ```

The default run asks for sold property prices in Coomera, QLD and caps itself at 3 listings, so your first run costs almost nothing.

### Alternative: set the API key directly
```bash
export APIFY_API_TOKEN="your_api_key_here"
uv run python realestate-au-property-api-example.py
```

## Why Use This Realestate.com.au Property API?

**Sold, rent, and for sale from one call.** Most tooling covers one of the three. Here `listingType` is a single field: `sold` for sold property prices, `rent` for the australia rental market, `buy` for current listings. The output shape stays the same across all three, so one parser handles everything.

**Search by suburb, not by URL.** You do not have to find and maintain a list of listing pages. `locations` takes plain Australian strings such as `"Coomera, QLD, 4209"`, up to 20 per run, and the search is built for you. URL mode is still there for pages you already hold.

**realestate.com.au has no public API.** That is the whole point of this Actor. It gives you programmatic access to the same listing data, returned as JSON you can call from Python, from an MCP client, or from a scheduled run.

**Honest about price.** `soldDate` is a confirmed date. `estimatedPrice` is the source's estimate, and it is labelled that way in the schema, in the output, and in this README, so nothing downstream mistakes an estimate for a settled figure. For-sale rows frequently carry no number at all, because Australian agents advertise "Contact Agent" or "AUCTION" instead of a price. Sold and rent rows almost always carry a figure.

**Cost is a dial you control.** You are charged per listing returned, and `maxResultsPerSearch` caps how many that is. Every example in this repo sets it to 3.

**Ready for agents.** Every listing row carries a one-line plain-language `summary`, so an assistant can read a record without post-processing. The five install sections below add the API as an MCP tool.

## Features

### Core capabilities
- Search by suburb, state, and postcode with no listing URL required
- Three listing types from one Actor: `buy`, `rent`, `sold`
- Up to 20 locations per run, up to 2000 listings per search
- URL mode for collecting specific listing pages you already have
- `splitByPropertyType` and `splitByPriceRange` to reach deeper into a large suburb than a single result list allows
- `limitPages` to cap how many result pages get walked

### Data quality
- Confirmed `soldDate` and `lastSoldAgency` on sold listings, plus a link to the fuller property history
- Numeric companions for sorting and filtering: `estimatedPriceValue`, `landSizeValue`, `floorAreaValue`
- `latitude` and `longitude` on listings, so comparables and mapping work out of the box
- Agent entries keep whatever the source published: agency and phone survive even when the individual agent name does not
- Failed searches come back as rows with `result_type: "error"` and a plain-language `error_message`, so an empty result explains itself

## Example runs

The script ships four runs. Each caps `maxResultsPerSearch` at 3 to keep costs down.

### Sold property prices for a suburb (default)

```bash
uv run python realestate-au-property-api-example.py --example sold
```

Searches `sold` in Coomera, QLD 4209 and prints address, beds, baths, parking, land size, the sold date, the selling agency, and the price estimate.

### Rental listings for a suburb

```bash
uv run python realestate-au-property-api-example.py --example rent
```

Searches `rent` in the same suburb and prints the advertised rent from `rentPrice` and `rentCurrency` alongside the property detail.

### Properties for sale across two suburbs

```bash
uv run python realestate-au-property-api-example.py --example buy
```

Passes two locations in one run and shows how for-sale rows behave when the agent published text such as "Contact Agent" instead of a figure.

### Collect specific listing URLs

```bash
uv run python realestate-au-property-api-example.py --example url
```

Switches `mode` to `url` and collects listing pages you already hold. Swap in your own URLs.

**Schedule tip:** save any of these inputs as a Task in the Apify Console and [schedule it](https://apify.com/johnvc/realestate-au-property-api?fpr=9n7kx3) to run daily or weekly. Diff each run against the last and you have new-stock alerts, price-change tracking, or a rolling sold-price history for your suburbs, without touching it by hand.

## Usage Examples

### Basic example

```json
{
  "mode": "search",
  "listingType": "sold",
  "locations": ["Coomera, QLD, 4209"],
  "maxResultsPerSearch": 3
}
```

### Advanced example

```json
{
  "mode": "search",
  "listingType": "buy",
  "locations": ["Coomera, QLD, 4209", "Pimpama, QLD, 4209", "Ormeau, QLD, 4208"],
  "maxResultsPerSearch": 200,
  "limitPages": 5,
  "splitByPropertyType": true,
  "splitByPriceRange": false
}
```

### URL mode

```json
{
  "mode": "url",
  "listingUrls": [
    "https://www.realestate.com.au/property-house-qld-coomera-136778134"
  ]
}
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `mode` | `str` | YES | `search` | `search` builds the search from suburb, state, and postcode and needs no URL. `url` collects specific listing pages you already hold. |
| `listingType` | `str` | no | `buy` | `buy`, `rent`, or `sold`. `sold` is what powers sold-price research. |
| `locations` | `list[str]` | no | `["Coomera, QLD, 4209"]` | Australian locations as `"Suburb, STATE"` or `"Suburb, STATE, POSTCODE"`. A suburb must be paired with its state. Empty searches the whole country. Up to 20 per run. |
| `maxResultsPerSearch` | `int` | no | `50` | Listings returned per search, 1 to 2000. You are charged per listing, so this is your cost control. |
| `daysBack` | `int` | no | none | Only return listings from the last N days, 1 to 365. This needs a date-sorted search; if the source rejects the combination you get an error row explaining it rather than a silent empty result. |
| `limitPages` | `int` | no | none | Cap how many pages of search results to walk, 1 to 50. Useful on large suburbs. |
| `splitByPropertyType` | `bool` | no | `false` | Walk each property type separately. Slower, but reaches deeper into a large suburb. |
| `splitByPriceRange` | `bool` | no | `false` | Walk each price band separately. Same trade-off. |
| `listingUrls` | `list[str]` | Required in `url` mode | none | Specific listing URLs to collect. Up to 500. |

## Output Format

One row per listing. Every row carries `result_type`, which is `"listing"` or `"error"`. Below is a real row from a `sold` search in Coomera, QLD, trimmed for length.

```json
{
  "result_type": "listing",
  "searchLabel": "https://www.realestate.com.au/sold/in-coomera,+qld+4209/list-1",
  "propertyId": "property-house-qld-coomera-140441963",
  "listingUrl": "https://www.realestate.com.au/sold/property-house-qld-coomera-140441963",
  "listingType": "Sold",
  "propertyType": "House",
  "streetAddress": "24 Madison Road",
  "suburb": "Coomera",
  "fullSuburb": "24 Madison Road, Coomera, Qld 4209",
  "state": "QLD",
  "postcode": "4209",
  "bedrooms": 4,
  "bathrooms": 2,
  "parking": 2,
  "landSize": "466m²",
  "landSizeValue": 466,
  "landSizeUnit": "m²",
  "floorArea": "214.44",
  "floorAreaValue": 214.44,
  "estimatedPrice": "$735,000",
  "estimatedPriceValue": 735000,
  "soldDate": "2022-11-24T00:00:00.000Z",
  "lastSoldAgency": "Vibe Realty",
  "propertyHistoryLink": "https://www.realestate.com.au/property/24-madison-rd-coomera-qld-4209/",
  "photoCount": 31,
  "images": ["https://i2.au.reastatic.net/.../image.jpg"],
  "latitude": -27.84333987,
  "longitude": 153.33616143,
  "agents": [
    {
      "name": "Michele Linington",
      "agency": "Vibe Realty",
      "phone": "0438849376",
      "rating": 5,
      "reviewCount": 27
    }
  ],
  "offMarket": true,
  "listedAt": "2026-08-09T01:06:20.924Z",
  "countryCode": "AU",
  "summary": "4-bed house at 24 Madison Road, Coomera, QLD. Sold 2022-11-24. Price estimate $735,000.",
  "fetched_at": "2026-08-09T01:06:48.511409+00:00"
}
```

Rental rows swap in `rentPrice` and `rentCurrency`. A search that returns nothing produces a row like this instead:

```json
{
  "result_type": "error",
  "sourceUrl": "https://www.realestate.com.au/sold/in-coomera,+qld+4209/list-1",
  "error_message": "The recency filter needs a date-sorted search.",
  "error_type": "CollectionError",
  "fetched_at": "2026-08-09T01:06:48.511409+00:00"
}
```

### Fields that are not here

The source publishes an automated valuation on some pages, but in live testing those fields were overwhelmingly empty, so they are left out rather than shipped permanently null. Use `estimatedPrice` and `estimatedPriceValue`, and read them as an estimate.

## People also search for

### Does realestate.com.au have an API?

Not a public one. That is why this Actor exists. It gives you the same listing data as structured JSON, callable from Python, from MCP, or on a schedule, with no listing URLs to manage. The searched phrase "realestate.com.au api" almost always means "I want programmatic access", and this is that access.

### Does realestate com au have a public API?

No. There is no open developer API you can sign up for. Use this Actor on Apify instead: [apify.com/johnvc/realestate-au-property-api](https://apify.com/johnvc/realestate-au-property-api?fpr=9n7kx3).

### How do I check what a property sold for?

Set `listingType` to `sold` and search the suburb. Each row carries a confirmed `soldDate`, the selling agency in `lastSoldAgency`, and `estimatedPrice`. The date is confirmed. The price is an estimate, because Australian sale prices are frequently undisclosed, so do not treat it as a settled figure.

### How do I find a property's sold price for a whole suburb?

One run. `mode: "search"`, `listingType: "sold"`, one location, and `maxResultsPerSearch` set to how many sales you want back. That returns the suburb's recent sales with dates and agencies, which is the practical way to get sold property prices in bulk.

### How do I find commercial property sold prices?

Search the suburb with `listingType: "sold"` and filter the returned rows on `propertyType`. The API returns what the source publishes for that suburb, and `propertyType` tells you what each row is.

### Is this a realestate.com.au scraper or an API?

It is an API on Apify. People search for scraping tools when what they want is structured data, and that is what comes back here: JSON rows you can call from code, no HTML parsing on your side.

### How do I get australian house prices from Python?

Clone this repo, set `APIFY_API_TOKEN`, and run `uv run python realestate-au-property-api-example.py`. That default run pulls sold prices for one suburb. See Quick Start above.

### Can I track the australia rental market with this?

Yes. Set `listingType` to `rent`, list the suburbs you care about in `locations`, and schedule the run. Rental rows carry `rentPrice` and `rentCurrency` alongside beds, baths, and parking, which is everything a yield calculation needs.

### Can I use it with MCP or Claude?

Yes. Use the install sections below to add the Actor as an MCP tool in [Claude Code](https://claude.ai/referral/uIlpa7nPLg) (free trial), [Claude Cowork](https://claude.ai/referral/uIlpa7nPLg) (free trial), Claude on the web, Cursor, or ChatGPT.

---

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Realestate.com.au Property API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/realestate-au-property-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Realestate.com.au Property API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/realestate-au-property-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/realestate-au-property-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Realestate.com.au Property API, for example "what sold in Coomera QLD and which agencies handled it".

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/realestate-au-property-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/realestate-au-property-api`, using OAuth when prompted.
5. Ask Claude to run the Realestate.com.au Property API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/realestate-au-property-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/realestate-au-property-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Realestate.com.au Property API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/realestate-au-property-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

## 🌐 About Alpha OSINT

This example repo is part of [Alpha OSINT](https://www.alphaosint.com), toolset of financial and operations data sources and APIs.
For support or requests for this actor, please start a ticket [directly on our support page](https://apify.com/johnvc/realestate-au-property-api/issues/open?fpr=9n7kx3).

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the Realestate.com.au Property API to put sold property prices, rentals, and for-sale listings into your own pipeline.*

Last Updated: 2026.08.10
