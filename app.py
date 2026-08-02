import os
import json
import asyncio
import streamlit as st
import engine
import ai_pdf

st.set_page_config(page_title="Relu Research Systems", page_icon="🧬", layout="wide")

st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .hero-title { font-size: 3.5rem; font-weight: 700; line-height: 1.1; text-align: center; margin-top: 2rem; color: #ffffff; }
        .hero-subtitle { text-align: center; color: #9ca3af; margin: 1rem auto 2rem; max-width: 600px; font-size: 1rem; line-height: 1.5; }
        .hero-chip { background: linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%); color: #e0e7ff; border: 1px solid #4f46e5; border-radius: 12px; padding: 0.5rem 1rem; font-size: 0.9rem; font-weight: 500; transition: all 0.3s ease; }
        .hero-chip:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); }
        .report-card { background: linear-gradient(145deg, #1a1f35 0%, #0f1220 100%); border: 1px solid #3b4261; border-radius: 20px; padding: 1.5rem; margin-top: 1rem; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
        .reference-panel { background: linear-gradient(145deg, #1a1f35 0%, #0f1220 100%); border: 1px solid #3b4261; border-radius: 16px; padding: 1.5rem; margin: 1.5rem auto 2rem; max-width: 900px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
        .reference-badge { background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: #ecfdf5; border-radius: 20px; font-size: 0.75rem; font-weight: 600; padding: 0.3rem 0.8rem; display: inline-block; margin-left: 0.5rem; box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3); }
        [data-testid="stDataFrame"] { background: #0f1220; border-radius: 12px; }
        .stButton > button { border-radius: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 600; padding: 0.6rem 1.5rem; transition: all 0.3s ease; border: none; }
        .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
        .stDownloadButton > button { border-radius: 12px; background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; font-weight: 600; padding: 0.6rem 1.5rem; transition: all 0.3s ease; border: none; }
        .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4); }
        .stAlert { border-radius: 16px; border: none; }
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] { background: #1a1f35; border-radius: 12px; color: #9ca3af; font-weight: 500; }
        .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1220 0%, #0a0c12 100%); border-right: 1px solid #3b4261; }
        [data-testid="stSidebar"] > div { padding-top: 0rem; }
        [data-testid="stSidebarContent"] { position: relative; overflow-y: auto; }
        .sidebar-brand {
            display: flex;
            align-items: center;
            gap: 1rem;
            background: linear-gradient(135deg, #1a1f35 0%, #0f1220 100%);
            padding: 1.2rem 0.5rem 1.5rem;
            margin: -0.5rem -0.5rem 1.5rem;
            border-bottom: 1px solid #3b4261;
            border-radius: 0 0 16px 16px;
        }
        .sidebar-brand-icon { width: 48px; height: 48px; flex: 0 0 48px; border-radius: 14px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 1.2rem; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
        .sidebar-brand-title { margin: 0; font-size: 1.25rem; font-weight: 700; line-height: 1.2; color: #e0e7ff; }
        .sidebar-brand-subtitle { margin: 0.25rem 0 0; font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: #9ca3af; font-weight: 600; }
        button[aria-label="Collapse sidebar"], [data-testid="collapsedControl"] { display: none !important; }
        div[data-testid="stSidebarNav"] { display: none; }
        .stTextInput > div > div > input {
            background: #1a1f35;
            border: 1px solid #3b4261;
            border-radius: 12px;
            color: #e0e7ff;
            font-size: 1rem;
        }
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        }
        .stStatus { border-radius: 16px; background: #1a1f35; border: 1px solid #3b4261; }
        .stStatus > div { padding: 1rem; }
        [data-testid="stChatMessage"] { background: #1a1f35; border-radius: 16px; border: 1px solid #3b4261; padding: 1.2rem; margin: 0.5rem 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "openrouter_api_key" not in st.session_state:
    st.session_state.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
if "serper_api_key" not in st.session_state:
    st.session_state.serper_api_key = os.getenv("SERPER_API_KEY", "")
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "openai/gpt-4o-mini"
if "discord_bot_token" not in st.session_state:
    st.session_state.discord_bot_token = ""
if "discord_channel_id" not in st.session_state:
    st.session_state.discord_channel_id = ""
if "applicant_name" not in st.session_state:
    st.session_state.applicant_name = ""
if "applicant_email" not in st.session_state:
    st.session_state.applicant_email = ""

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">⌁</div>
            <div>
                <div class="sidebar-brand-title">Relu Consultancy</div>
                <div class="sidebar-brand-subtitle">Company Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div>', unsafe_allow_html=True)
    if st.button("+ New Research", use_container_width=True):
        st.session_state.history = [{"role": "assistant", "content": "Welcome candidate. Submit a company name or website URL below to construct active intelligence."}]
        st.session_state.last_report = None
        st.session_state.research_input = ""
        st.session_state.submitted = False
    st.markdown('</div>', unsafe_allow_html=True)

    tab_a, tab_b = st.tabs(["API", "DISCORD"])
    with tab_a:
        with st.form("api_config_form", clear_on_submit=False):
            or_key = st.text_input("OpenRouter API Key", type="password", key="openrouter_api_key")
            sp_key = st.text_input("Serper.dev API Key", type="password", key="serper_api_key")
            model = st.selectbox("AI Model", ["openai/gpt-4o-mini", "google/gemini-1.5-pro", "anthropic/claude-3.5-sonnet"], key="selected_model")
            st.form_submit_button("Save Configuration", use_container_width=True)
    with tab_b:
        with st.form("discord_config_form", clear_on_submit=False):
            st.info("Discord bot integration is enabled once both fields are configured.")
            d_token = st.text_input("Bot Token", type="password", key="discord_bot_token")
            ch_id = st.text_input("Channel ID", key="discord_channel_id")
            st.subheader("Applicant Details")
            app_name = st.text_input("Full Name", key="applicant_name")
            app_email = st.text_input("Email Address", key="applicant_email")
            st.form_submit_button("Save Discord Config", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption("How it works")
    st.markdown("1. Enter a company name or website URL\n2. Resolve the official site using Serper\n3. Crawl the domain and enrich with live search context\n4. Generate a polished PDF report")

if "history" not in st.session_state:
    st.session_state.history = [{"role": "assistant", "content": "Welcome candidate. Submit a company name or website URL below to construct active intelligence."}]

if "last_report" not in st.session_state:
    st.session_state.last_report = None

st.markdown('<div class="hero-title">Know any company<br/>in minutes.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Enter a company name or website URL to get AI-powered insights, competitor analysis, and a professional PDF report.</div>',
    unsafe_allow_html=True,
)

# Example company chips
example_companies = ["notion.so", "Figma", "Linear", "Vercel"]
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("notion.so", key="chip_notion", use_container_width=True):
        st.session_state.research_input = "notion.so"
        st.rerun()
with col2:
    if st.button("Figma", key="chip_figma", use_container_width=True):
        st.session_state.research_input = "Figma"
        st.rerun()
with col3:
    if st.button("Linear", key="chip_linear", use_container_width=True):
        st.session_state.research_input = "Linear"
        st.rerun()
with col4:
    if st.button("Vercel", key="chip_vercel", use_container_width=True):
        st.session_state.research_input = "Vercel"
        st.rerun()

with st.form("research_form", clear_on_submit=False):
    c1, c2 = st.columns([6, 1])
    with c1:
        user_input = st.text_input(
            "Research input",
            placeholder="Enter a company name (e.g. Stripe) or website URL (e.g. https://stripe.com)...",
            label_visibility="collapsed",
            key="research_input",
        )
    with c2:
        submitted = st.form_submit_button("Research →", use_container_width=True)

if submitted and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    with st.spinner("Validating API access..."):
        is_sp_ok = ai_pdf.verify_serper_authentication(sp_key)
        is_or_ok = ai_pdf.verify_openrouter_authentication(or_key)

    if not is_sp_ok or not is_or_ok:
        st.error("Please provide valid Serper.dev and OpenRouter API keys in the sidebar before running the research workflow.")
    else:
        with st.status("🔍 Resolving official domain and search context...", expanded=True):
            url, company_name = engine.extract_company_website(user_input, sp_key)
            if not url:
                url = engine.ensure_http_url(user_input)
                company_name = user_input

        with st.status("🌐 Crawling the target company site...", expanded=True):
            web_text = asyncio.run(engine.execute_autonomous_crawler(url))

        with st.status("📊 Enriching the brief with public search context...", expanded=True):
            search_context = engine.summarize_search_results(company_name, url, sp_key)
            search_blob = json.dumps(search_context, ensure_ascii=False)

        with st.status("🧠 Generating the AI-powered research summary...", expanded=True):
            prompt = (
                "You are a company intelligence agent. Return strict JSON only. "
                "Do not include markdown fences. The schema must include fields: company_name, website, phone_number, address, "
                "products_services, summary, pain_points, competitors. Use the sources to create a concise but useful brief. "
                f"\nCompany Input: {company_name}\nWebsite: {url}\nScraped Content:\n{web_text}\nSearch Context:\n{search_blob}\n"
                "Return valid JSON with competitor objects shaped as [{\"name\": ..., \"website\": ...}]"
            )
            ai_response = ai_pdf.execute_openrouter_call(prompt, or_key, model)
            try:
                parsed = json.loads(ai_response.strip().lstrip("```json").rstrip("```").strip())
            except Exception:
                parsed = {
                    "company_name": company_name,
                    "website": url,
                    "phone_number": "Not Listed",
                    "address": "Not Listed",
                    "products_services": "Unable to extract from the model response.",
                    "summary": ai_response,
                    "pain_points": "Unable to extract from the model response.",
                    "competitors": [],
                }

        competitors = parsed.get("competitors", []) or []
        final_pkg = {
            "name": parsed.get("company_name") or company_name,
            "url": parsed.get("website") or url,
            "phone": parsed.get("phone_number") or "Not Listed",
            "address": parsed.get("address") or "Not Listed",
            "products_services": parsed.get("products_services") or "Not Listed",
            "summary": parsed.get("summary") or "Not Listed",
            "pain_points": parsed.get("pain_points") or "Not Listed",
            "competitors": competitors,
        }
        final_pkg["_pdf_data"] = ai_pdf.build_pdf_binary(final_pkg)
        st.session_state.last_report = final_pkg
        st.session_state.history.append({"role": "assistant", "content": f"Research completed for {company_name}. Download the PDF or share the result to Discord."})

for chat in st.session_state.history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

if st.session_state.last_report:
    report_pkg = st.session_state.last_report
    pdf_data = report_pkg.get("_pdf_data") or ai_pdf.build_pdf_binary(report_pkg)
    with st.container(border=True):
        st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:center;'><h2 style='margin:0;'>{report_pkg['name']}</h2><span style='padding:0.2rem 0.55rem; background:#0d3b2a; color:#6ce39b; border-radius:999px; font-size:0.72rem;'>RESEARCH COMPLETE</span></div>", unsafe_allow_html=True)
        st.caption(f"Website: {report_pkg['url']}")
        c_phone, c_addr = st.columns([1, 1])
        with c_phone:
            st.caption(f"Phone: {report_pkg['phone']}")
        with c_addr:
            st.caption(f"Address: {report_pkg['address']}")

        st.markdown("### Products / Services")
        st.write(report_pkg["products_services"])

        st.markdown("### AI-generated Pain Points")
        st.write(report_pkg["pain_points"])

        st.markdown("### Competitor Analysis")
        competitor_html = ""
        for item in report_pkg["competitors"][:5]:
            competitor_html += f"<div style='display:inline-block; margin:0.2rem 0.35rem 0.2rem 0; padding:0.36rem 0.6rem; border:1px solid #303544; border-radius:8px; background:#0f1420;'>{item.get('name', 'Unknown')} - {item.get('website', 'N/A')}</div>"
        st.markdown(competitor_html, unsafe_allow_html=True)

        col_dl, col_discord = st.columns([1, 1])
        with col_dl:
            st.download_button("📥 Download PDF Report", data=pdf_data, file_name=f"{report_pkg['name']}_report.pdf", mime="application/pdf")
        if d_token and ch_id and app_name and app_email:
            with col_discord:
                if st.button("Send to Discord"):
                    sent = ai_pdf.post_to_discord_channel(d_token, ch_id, app_name, app_email, report_pkg, pdf_data)
                    if sent:
                        st.success("Discord report delivered successfully.")
                    else:
                        st.warning("Discord delivery failed. Please verify the bot token, channel ID, and Discord permissions.")
        else:
            with col_discord:
                st.info("Enter a Discord bot token, channel ID, and applicant details to enable Discord delivery.")

    st.caption(f"Last generated report: {report_pkg['name']}")
