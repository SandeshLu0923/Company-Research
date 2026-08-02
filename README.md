# Relu Company Research Assistant

A Streamlit-based AI company research assistant that provides comprehensive company intelligence through automated web crawling, AI analysis, and professional report generation.

## Project Structure

- [app.py](app.py) – Streamlit UI and workflow orchestration
- [engine.py](engine.py) – Serper search, domain normalization, and crawler logic
- [ai_pdf.py](ai_pdf.py) – OpenRouter call helper, PDF builder, and Discord notifier

## Setup Instructions

1. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the project root or configure via the sidebar UI:
   ```env
   OPENROUTER_API_KEY=your_openrouter_key
   SERPER_API_KEY=your_serper_key
   DISCORD_BOT_TOKEN=your_discord_bot_token  # Optional
   DISCORD_CHANNEL_ID=your_channel_id       # Optional
   ```

4. **Start the application:**
   ```bash
   streamlit run app.py
   ```

5. **Access the application:**
   Open the local URL shown by Streamlit, usually:
   ```
   http://localhost:8501
   ```

## Environment Variable Documentation

### Required Variables

- **`OPENROUTER_API_KEY`**: API key for OpenRouter to access AI models (GPT-4, Claude, etc.)
  - Get your key at: https://openrouter.ai/keys
  - Required for AI-powered company analysis and competitor identification

- **`SERPER_API_KEY`**: API key for Serper.dev search API
  - Get your key at: https://serper.dev/api-key
  - Required for website resolution and search context enrichment

### Optional Variables

- **`DISCORD_BOT_TOKEN`**: Discord bot token for report delivery
  - Create a bot at: https://discord.com/developers/applications
  - Enable bot privileges and message content intent
  - Required for Discord integration feature

- **`DISCORD_CHANNEL_ID`**: Target Discord channel ID for report delivery
  - Enable developer mode in Discord to copy channel ID
  - Bot must have permissions to send messages in this channel

## Website Crawling Implementation

The crawling system (`engine.py`) automatically discovers and extracts content from key business pages:

**Target Pages:**
- Homepage (`/`)
- About pages (`/about`, `/about-us`, `/company`)
- Product/Service pages (`/products`, `/services`, `/solutions`)
- Pricing pages (`/pricing`, `/plans`)
- Contact pages (`/contact`, `/contact-us`)

**Crawler Features:**
- Autonomous page discovery using BeautifulSoup
- Content extraction from semantic HTML elements
- Text cleaning and normalization
- Timeout handling for slow-loading pages
- Error recovery for failed requests

**Implementation Details:**
```python
# The crawler uses asyncio for concurrent page fetching
web_text = asyncio.run(engine.execute_autonomous_crawler(url))
# Returns aggregated text content from all discovered pages
```

## AI Company Research

The AI research component leverages OpenRouter to analyze crawled content and generate structured intelligence:

**AI Models Supported:**
- `openai/gpt-4o-mini` (default)
- `google/gemini-1.5-pro`
- `anthropic/claude-3.5-sonnet`

**Research Output Structure:**
```json
{
  "company_name": "Company Name",
  "website": "https://example.com",
  "phone_number": "Contact number",
  "address": "Company address",
  "products_services": "Detailed description",
  "summary": "Executive summary",
  "pain_points": "Identified challenges",
  "competitors": [
    {"name": "Competitor 1", "website": "https://competitor1.com"}
  ]
}
```

**Analysis Process:**
1. Combines crawled website content with search context
2. Sends structured prompt to AI model
3. Parses JSON response with error handling
4. Validates and normalizes extracted data

## Competitor Analysis

The system automatically identifies and analyzes competitors through AI-powered analysis:

**Competitor Identification:**
- AI analyzes company positioning and market segment
- Identifies direct and indirect competitors
- Extracts competitor names and websites
- Validates competitor information through search

**Output Format:**
- List of competitor objects with name and website
- Integrated into PDF report with dedicated section
- Used for comparative analysis in research

**Example Output:**
```
• Adobe XD - https://www.adobe.com/products/xd.html
• Sketch - https://www.sketch.com
• Canva - https://www.canva.com
• Framer - https://www.framer.com
```

## PDF Generation

Professional PDF reports are generated using FPDF with a standardized corporate design:

**Report Sections:**
1. **Header**: Company name and branding
2. **Company Information**: Website, phone, address
3. **Products & Services**: Detailed offerings
4. **AI-Generated Pain Points**: Identified challenges
5. **Competitors**: Competitor analysis with URLs

**Design Features:**
- Professional dark theme header
- Purple accent color scheme (#667eea)
- Clean typography with Helvetica font
- Structured section dividers
- Responsive layout for A4 format

**Generation Process:**
```python
pdf_data = ai_pdf.build_pdf_binary(report_pkg)
# Returns binary PDF data for download or Discord delivery
```

**Customization:**
- Margins: 15mm on all sides
- Auto page breaks with 15mm margin
- Section headers in bold with accent color
- Content in readable dark gray text

## Discord Integration (Bonus)

Optional Discord integration enables automated report delivery to specified channels:

**Setup Requirements:**
1. Create Discord bot application
2. Enable bot privileges:
   - Send Messages
   - Attach Files
   - Message Content Intent
3. Invite bot to target server
4. Configure bot token and channel ID

**Delivery Format:**
```
🧬 Relu Hackathon Sync Complete
👤 Candidate: Name (email)
🏢 Company: Company Name
🌐 URL: https://company.com
[PDF attachment]
```

**Error Handling:**
- Detailed error logging for debugging
- HTTP status code reporting
- Graceful failure with user feedback
- Validation of required credentials

**Troubleshooting Common Issues:**
- **403 Forbidden**: Check bot permissions and token validity
- **404 Not Found**: Verify channel ID is correct
- **413 Payload Too Large**: PDF may exceed Discord's 25MB limit
- **Network Errors**: Check internet connectivity and API status

**Implementation:**
```python
sent = ai_pdf.post_to_discord_channel(
    bot_token, channel_id, applicant_name, 
    applicant_email, report_data, pdf_bytes
)
```
