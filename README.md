# Relu Company Research Assistant

A Streamlit-based AI company research assistant that supports:

- Company name or website URL inputs
- Serper.dev search enrichment
- Website crawling across common business pages
- OpenRouter AI structured analysis
- Competitor identification
- Downloadable PDF report generation
- Optional Discord report delivery

## Project structure

- [app.py](app.py) – Streamlit UI and workflow orchestration
- [engine.py](engine.py) – Serper search, domain normalization, and crawler logic
- [ai_pdf.py](ai_pdf.py) – OpenRouter call helper, PDF builder, and Discord notifier

## Environment variables

Create a `.env` file or add the values in the sidebar UI.

Required:

- `OPENROUTER_API_KEY`
- `SERPER_API_KEY`

Optional:

- `DISCORD_BOT_TOKEN`
- `DISCORD_CHANNEL_ID`

## Setup

1. Create a Python virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Open the local URL shown by Streamlit, usually:

   ```text
   http://localhost:8501
   ```

## Notes

- The app supports both company names and website URLs.
- If a company name is entered, Serper is used to resolve the likely official website.
- Crawling focuses on business pages such as the homepage, about, products, services, solutions, contact, and pricing routes.
- The final AI response is converted into a structured research view and downloadable PDF.
