import os
import json
import datetime
import feedparser
from google import genai
from google.genai import types

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATA_FILE = "data/solutions.json"
HTML_OUTPUT_FILE = "docs/index.html"

# Public RSS Feeds monitoring Romanian civic, administrative, and national news
RSS_FEEDS = [
    "https://www.agerpres.ro/rss/social",
    "https://www.hotnews.ro/rss",
    "https://www.digi24.ro/rss",
    "https://www.g4media.ro/feed"
]

MAX_ARTICLES_TO_SCAN = 15
MAX_NEW_SOLUTIONS_PER_RUN = 3


def initialize_directories():
    os.makedirs("data", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def load_existing_solutions():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_solutions(solutions):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(solutions, f, indent=2, ensure_ascii=False)


def fetch_daily_news(existing_urls):
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                link = entry.get("link", "")
                if link and link not in existing_urls:
                    articles.append({
                        "title": entry.get("title", "No Title"),
                        "summary": entry.get("summary", ""),
                        "link": link,
                        "published": entry.get("published", datetime.date.today().isoformat())
                    })
        except Exception as e:
            print(f"Warning: Could not parse feed {feed_url}: {e}")
    return articles[:MAX_ARTICLES_TO_SCAN]


def analyze_issue_with_gemini(client, article):
    prompt = f"""
    You are an expert Public Administration Consultant and Project Management AI for 'Solutii Romania (.com)'.
    Analyze the following news item regarding Romania:

    Title: {article['title']}
    Summary: {article['summary']}
    Source URL: {article['link']}

    Task:
    1. Determine if this news item reflects a negative event, systemic issue, administrative bottleneck, infrastructure failure, healthcare deficit, environmental hazard, or public service problem involving the Romanian state or public institutions.
    2. If it is NOT a public/administrative problem (e.g., celebrity gossip, sports score, international-only news), return strictly: {{"is_public_issue": false}}
    3. If it IS a public/administrative issue, generate a complete, actionable project management blueprint that a Romanian civil servant (public official) can immediately use to solve the problem legally and administratively.

    Respond ONLY with valid JSON using this exact schema:
    {{
        "is_public_issue": true,
        "sector": "Healthcare | Infrastructure | Environment | Public Administration | Education | Economy",
        "problem_title": "Clear, formal title of the identified systemic problem",
        "stakeholder_analysis": [
            {{"stakeholder": "Name/Group", "role": "Role in issue", "power_interest": "High/Medium/Low", "strategy": "Actionable engagement strategy"}}
        ],
        "problem_tree": {{
            "core_problem": "Central problem statement",
            "causes": ["Root cause 1", "Root cause 2", "Root cause 3"],
            "effects": ["Negative effect 1", "Negative effect 2", "Negative effect 3"]
        }},
        "objective_tree": {{
            "general_objective": "Main measurable goal",
            "specific_objectives": ["Specific objective 1", "Specific objective 2", "Specific objective 3"],
            "expected_impact": "Long-term positive impact on citizens and state"
        }},
        "swot_analysis": {{
            "strengths": ["Internal strength 1", "Internal strength 2"],
            "weaknesses": ["Internal weakness 1", "Internal weakness 2"],
            "opportunities": ["External opportunity 1", "External opportunity 2"],
            "threats": ["External threat 1", "External threat 2"]
        }},
        "ishikawa_fishbone": {{
            "technology": "Technological gap causing the issue",
            "processes": "Bureaucratic or procedural bottleneck",
            "human_resources": "Staffing or training deficit",
            "environment_context": "Legislative or external context factor"
        }},
        "logical_framework": [
            {{"level": "Goal / Impact", "indicators": "Measurable KPI", "verification_sources": "Official document/registry", "assumptions": "Key external condition"}},
            {{"level": "Outcome", "indicators": "Measurable KPI", "verification_sources": "Official report", "assumptions": "Key condition"}},
            {{"level": "Outputs", "indicators": "Deliverable count", "verification_sources": "Audit/Log", "assumptions": "Resource availability"}}
        ],
        "activity_list_and_gantt": [
            {{"phase": "Phase 1 (Week 1-2)", "activity": "Immediate administrative assessment & legal audit", "responsible": "Responsible Department"}},
            {{"phase": "Phase 2 (Week 3-4)", "activity": "Drafting decision/procurement documentation", "responsible": "Legal & Procurement Office"}},
            {{"phase": "Phase 3 (Month 2)", "activity": "Execution and public transparency reporting", "responsible": "Implementation Team"}}
        ],
        "estimated_budget_eur": [
            {{"category": "Administrative & Technical Audit", "cost_eur": 1500, "notes": "Internal reallocation / EU technical assistance"}},
            {{"category": "Direct Operational Intervention", "cost_eur": 10000, "notes": "Estimated intervention cost"}},
            {{"category": "Contingency Reserve (10%)", "cost_eur": 1150, "notes": "Standard risk buffer"}}
        ],
        "civil_servant_action_blueprint": {{
            "legal_basis": "Relevant Romanian administrative framework (e.g., Administrative Code OUG 57/2019, Public Procurement Law 98/2016)",
            "ready_to_use_steps": [
                "Step 1: Register internal memo (Nota de Fundamentare) referencing the public alert.",
                "Step 2: Convene inter-departmental working group within 48 hours.",
                "Step 3: Issue formal administrative decision / corrective action plan."
            ],
            "draft_memo_summary": "A concise, formal executive paragraph ready to be pasted into an official Approval Report (Referat de Aprobare)."
        }}
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        result = json.loads(response.text)
        return result
    except Exception as e:
        print(f"Error calling Gemini API for '{article['title']}': {e}")
        return {"is_public_issue": False}


def render_static_website(solutions):
    last_updated = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards_html = ""

    for idx, item in enumerate(reversed(solutions)):
        data = item["analysis"]
        total_budget = sum(b.get("cost_eur", 0) for b in data.get("estimated_budget_eur", []))

        stakeholders_rows = "".join(
            f"<tr><td>{s['stakeholder']}</td><td>{s['role']}</td><td>{s['power_interest']}</td><td>{s['strategy']}</td></tr>"
            for s in data.get("stakeholder_analysis", [])
        )

        gantt_rows = "".join(
            f"<tr><td><strong>{g['phase']}</strong></td><td>{g['activity']}</td><td>{g['responsible']}</td></tr>"
            for g in data.get("activity_list_and_gantt", [])
        )

        logframe_rows = "".join(
            f"<tr><td><strong>{lf['level']}</strong></td><td>{lf['indicators']}</td><td>{lf['verification_sources']}</td><td>{lf['assumptions']}</td></tr>"
            for lf in data.get("logical_framework", [])
        )

        budget_rows = "".join(
            f"<tr><td>{b['category']}</td><td>{b['cost_eur']:,} EUR</td><td>{b['notes']}</td></tr>"
            for b in data.get("estimated_budget_eur", [])
        )

        causes_li = "".join(f"<li>{c}</li>" for c in data["problem_tree"]["causes"])
        effects_li = "".join(f"<li>{e}</li>" for e in data["problem_tree"]["effects"])
        spec_obj_li = "".join(f"<li>{o}</li>" for o in data["objective_tree"]["specific_objectives"])
        steps_li = "".join(f"<li>{st}</li>" for st in data["civil_servant_action_blueprint"]["ready_to_use_steps"])

        swot = data["swot_analysis"]
        ishikawa = data["ishikawa_fishbone"]
        blueprint = data["civil_servant_action_blueprint"]

        cards_html += f"""
        <article class="case-card">
            <div class="case-header">
                <span class="badge">{data.get('sector', 'Public Policy')}</span>
                <span class="date">Detected: {item['date']}</span>
            </div>
            <h2>{data['problem_title']}</h2>
            <p class="source-link">Source Monitor: <a href="{item['source_url']}" target="_blank" rel="noopener">{item['original_title']}</a></p>

            <div class="blueprint-box">
                <h3>Civil Servant Action Blueprint (Ready for Administrative Execution)</h3>
                <p><strong>Applicable Legal Framework:</strong> {blueprint['legal_basis']}</p>
                <ol>{steps_li}</ol>
                <blockquote><strong>Draft Approval Report (Referat de Aprobare):</strong> {blueprint['draft_memo_summary']}</blockquote>
            </div>

            <details>
                <summary>View Full Project Management Matrix (Stakeholders, Trees, SWOT, Ishikawa, LogFrame, Gantt & Budget)</summary>
                <div class="matrix-content">
                    <h4>1. Stakeholder Analysis</h4>
                    <table>
                        <thead><tr><th>Stakeholder</th><th>Role</th><th>Power/Interest</th><th>Strategy</th></tr></thead>
                        <tbody>{stakeholders_rows}</tbody>
                    </table>

                    <div class="grid-2">
                        <div class="box">
                            <h4>2. Problem Tree</h4>
                            <p><strong>Core Problem:</strong> {data['problem_tree']['core_problem']}</p>
                            <p><strong>Root Causes:</strong></p><ul>{causes_li}</ul>
                            <p><strong>Effects:</strong></p><ul>{effects_li}</ul>
                        </div>
                        <div class="box">
                            <h4>3. Objective Tree</h4>
                            <p><strong>General Objective:</strong> {data['objective_tree']['general_objective']}</p>
                            <p><strong>Specific Objectives:</strong></p><ul>{spec_obj_li}</ul>
                            <p><strong>Expected Impact:</strong> {data['objective_tree']['expected_impact']}</p>
                        </div>
                    </div>

                    <h4>4. SWOT Analysis</h4>
                    <div class="grid-2">
                        <div class="box swot-s"><strong>Strengths:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['strengths'])}</ul></div>
                        <div class="box swot-w"><strong>Weaknesses:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['weaknesses'])}</ul></div>
                        <div class="box swot-o"><strong>Opportunities:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['opportunities'])}</ul></div>
                        <div class="box swot-t"><strong>Threats:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['threats'])}</ul></div>
                    </div>

                    <h4>5. Ishikawa (Fishbone) Root-Cause Analysis</h4>
                    <div class="grid-2">
                        <div class="box"><strong>Technology:</strong> {ishikawa['technology']}</div>
                        <div class="box"><strong>Processes:</strong> {ishikawa['processes']}</div>
                        <div class="box"><strong>Human Resources:</strong> {ishikawa['human_resources']}</div>
                        <div class="box"><strong>Environment / Context:</strong> {ishikawa['environment_context']}</div>
                    </div>

                    <h4>6. Logical Framework Matrix (LogFrame)</h4>
                    <table>
                        <thead><tr><th>Hierarchy</th><th>Objectively Verifiable Indicators</th><th>Verification Sources</th><th>Assumptions</th></tr></thead>
                        <tbody>{logframe_rows}</tbody>
                    </table>

                    <h4>7. Activity Plan & Gantt Schedule</h4>
                    <table>
                        <thead><tr><th>Timeline / Phase</th><th>Activity</th><th>Responsible Unit</th></tr></thead>
                        <tbody>{gantt_rows}</tbody>
                    </table>

                    <h4>8. Estimated Intervention Budget (Total: {total_budget:,} EUR)</h4>
                    <table>
                        <thead><tr><th>Budget Category</th><th>Estimated Cost</th><th>Notes</th></tr></thead>
                        <tbody>{budget_rows}</tbody>
                    </table>
                </div>
            </details>
        </article>
        """

    if not cards_html:
        cards_html = "<p>No public issues processed yet. Run the pipeline to ingest today's news.</p>"

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solutii Romania (.com) — AI Civic & Administrative Solutions Portal</title>
    <style>
        :root {{
            --primary: #002B7F;
            --accent: #FCD116;
            --danger: #CE1126;
            --bg: #f4f6f9;
            --card-bg: #ffffff;
            --text: #1e293b;
            --border: #cbd5e1;
        }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; line-height: 1.6; }}
        header {{ background: var(--primary); color: #fff; padding: 2rem 1rem; text-align: center; border-bottom: 5px solid var(--accent); }}
        header h1 {{ margin: 0; font-size: 2rem; }}
        header p {{ margin: 0.5rem 0 0; opacity: 0.9; }}
        .meta-bar {{ background: #e2e8f0; padding: 0.5rem 1rem; text-align: center; font-size: 0.875rem; }}
        main {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }}
        .case-card {{ background: var(--card-bg); border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border-left: 6px solid var(--primary); }}
        .case-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
        .badge {{ background: var(--primary); color: #fff; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }}
        .date {{ font-size: 0.85rem; color: #64748b; }}
        .source-link {{ font-size: 0.9rem; color: #475569; }}
        .blueprint-box {{ background: #f0fdf4; border: 1px solid #86efac; border-radius: 6px; padding: 1rem 1.25rem; margin: 1rem 0; }}
        .blueprint-box h3 {{ margin-top: 0; color: #166534; }}
        blockquote {{ background: #fff; border-left: 4px solid #166534; margin: 0.75rem 0 0; padding: 0.75rem; font-style: italic; }}
        details {{ margin-top: 1rem; border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem; background: #f8fafc; }}
        summary {{ cursor: pointer; font-weight: 600; color: var(--primary); }}
        .matrix-content {{ margin-top: 1rem; }}
        table {{ width: 100%; border-collapse: collapse; margin: 0.75rem 0 1.5rem; font-size: 0.9rem; background: #fff; }}
        th, td {{ border: 1px solid var(--border); padding: 0.6rem; text-align: left; vertical-align: top; }}
        th {{ background: #e2e8f0; }}
        .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
        .box {{ background: #fff; border: 1px solid var(--border); border-radius: 6px; padding: 1rem; }}
        footer {{ text-align: center; padding: 2rem 1rem; color: #64748b; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <header>
        <h1>Solutii Romania (.com)</h1>
        <p>Open-Source AI Civic Monitor & Administrative Solution Generator for Public Officials</p>
    </header>
    <div class="meta-bar">
        Last Automated AI Scan: <strong>{last_updated}</strong> | Total Indexed Solutions: <strong>{len(solutions)}</strong> | License: MIT (100% Free Public Utility)
    </div>
    <main>
        {cards_html}
    </main>
    <footer>
        Generated automatically via Python & Gemini AI | Open-Source Public Administration Initiative
    </footer>
</body>
</html>
"""
    with open(HTML_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_template)


def main():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    initialize_directories()
    solutions = load_existing_solutions()
    existing_urls = {item["source_url"] for item in solutions}

    print("Fetching daily Romanian public news feeds...")
    candidate_articles = fetch_daily_news(existing_urls)
    print(f"Found {len(candidate_articles)} new articles to evaluate.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    new_count = 0

    for article in candidate_articles:
        if new_count >= MAX_NEW_SOLUTIONS_PER_RUN:
            break

        print(f"Analyzing: {article['title']}")
        analysis = analyze_issue_with_gemini(client, article)

        if analysis.get("is_public_issue"):
            solutions.append({
                "date": datetime.date.today().isoformat(),
                "original_title": article["title"],
                "source_url": article["link"],
                "analysis": analysis
            })
            new_count += 1
            print(f" -> Added administrative solution blueprint ({analysis.get('sector')}).")

    save_solutions(solutions)
    render_static_website(solutions)
    print(f"Pipeline complete. Added {new_count} new solutions and updated {HTML_OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
