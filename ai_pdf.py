import json
import httpx
from fpdf import FPDF


def verify_serper_authentication(api_key: str) -> bool:
    """Executes a minimalist ping test to confirm the Serper key is active."""
    if not api_key:
        return False
    try:
        response = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json={"q": "ping", "num": 1},
            timeout=8,
        )
        return response.status_code == 200
    except Exception:
        return False


def verify_openrouter_authentication(api_key: str) -> bool:
    """Queries the OpenRouter auth endpoint to verify token legitimacy."""
    if not api_key:
        return False
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = httpx.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=8)
        return response.status_code == 200
    except Exception:
        return False


def execute_openrouter_call(prompt: str, api_key: str, model: str) -> str:
    """Interfaces cleanly with OpenRouter universal endpoint layer."""
    if not api_key:
        return "Error: Missing AI validation token."
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a professional corporate intelligence extraction agent. Return only valid raw JSON matching the schema exactly and do not wrap the output in markdown code fences.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    try:
        response = httpx.post(url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        content = response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        return content
    except Exception as exc:
        return f"AI Error: {str(exc)}"


def build_pdf_binary(report: dict) -> bytes:
    """Compiles unified research profiles cleanly into a standardized corporate PDF."""
    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.set_margins(12, 12)
    pdf.set_auto_page_break(auto=True, margin=10)

    safe_width = 186
    safe_text = lambda value: str(value or "N/A")

    pdf.set_fill_color(12, 12, 12)
    pdf.rect(0, 0, 210, 36, "F")
    pdf.set_text_color(246, 176, 67)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 10, "RELU CONSULTANCY · COMPANY RESEARCH REPORT", 0, 1, "C")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, safe_text(report.get("name", "Unknown Company")), 0, 1, "C")
    pdf.ln(4)

    pdf.set_draw_color(246, 176, 67)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(246, 176, 67)
    pdf.cell(0, 6, "COMPANY INFORMATION", 0, 1, "L")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 6, f"Website: {safe_text(report.get('url', 'N/A'))}", 0, 1, "L")
    pdf.cell(0, 6, f"Phone: {safe_text(report.get('phone', 'N/A'))}", 0, 1, "L")
    pdf.cell(0, 6, f"Address: {safe_text(report.get('address', 'N/A'))}", 0, 1, "L")
    pdf.ln(4)

    sections = [
        ("PRODUCTS & SERVICES", report.get("products_services", "N/A")),
        ("AI-GENERATED PAIN POINTS", report.get("pain_points", "N/A")),
    ]

    for title, content in sections:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(246, 176, 67)
        pdf.cell(0, 6, title, 0, 1, "L")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(20, 20, 20)
        pdf.multi_cell(safe_width, 5, safe_text(content))
        pdf.ln(4)

    competitors = report.get("competitors", [])
    if competitors:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(246, 176, 67)
        pdf.cell(0, 6, "COMPETITORS", 0, 1, "L")
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(20, 20, 20)
        for competitor in competitors:
            if isinstance(competitor, dict):
                name = safe_text(competitor.get("name", "Unknown"))
                website = safe_text(competitor.get("website", "N/A"))
            else:
                name = safe_text(competitor)
                website = "N/A"
            pdf.multi_cell(safe_width, 5, f"- {name}: {website}")
        pdf.ln(3)

    return bytes(pdf.output(dest="S"))


def post_to_discord_channel(token: str, ch_id: str, app_name: str, app_email: str, r_data: dict, pdf_bytes: bytes) -> bool:
    """Dispatches report binaries and research data arrays straight to Discord via API."""
    if not token or not ch_id:
        return False

    url = f"https://discord.com/api/v10/channels/{ch_id}/messages"
    message = (
        f"🧬 **Relu Hackathon Sync Complete**\n"
        f"👤 **Candidate:** {app_name} ({app_email})\n"
        f"🏢 **Company:** {r_data.get('name', 'Unknown')}\n"
        f"🌐 **URL:** {r_data.get('url', 'N/A')}"
    )

    try:
        files = [("file", ("Intelligence_Report.pdf", pdf_bytes, "application/pdf"))]
        data = {"payload_json": json.dumps({"content": message})}
        response = httpx.post(
            url,
            headers={"Authorization": f"Bot {token}"},
            data=data,
            files=files,
            timeout=20,
        )
        response.raise_for_status()
        return True
    except Exception:
        return False
