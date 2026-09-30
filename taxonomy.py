"""Supported demo decisions and their planning-only tool mappings.

These are a small demo catalog, not Oppora's complete production tool registry.
"""

OPPORA_TOOLS = {
    "company_finder": "Discover companies matching the requested industry and location.",
    "contact_hunter": "Find people matching requested roles and company constraints.",
    "verify_emails": "Check existing or discovered email addresses for deliverability.",
    "smart_lead_scoring": "Assess lead fit against an explicitly provided customer profile.",
    "company_enrichment": "Fill missing firmographics on existing company or lead records.",
    "reply_ora": "Classify incoming replies, bounces and out-of-office messages. No reply writing in this demo.",
    "campaign_sequencer": "Plan an approved outreach sequence. No email writing or sending in this demo.",
}

GTM_INTENTS = {
    "account_discovery": "Find NEW COMPANIES or organizations. No individual people or outreach requested.",
    "contact_hunting": "Find PEOPLE, job titles or contact details. Companies may be constraints; a company list is not required.",
    "outbound_pipeline": "Explicitly build an OUTBOUND or OUTREACH workflow/campaign, including discovery and qualification.",
    "enrichment_only": "Fill MISSING FIELDS on EXISTING company or lead records. Do not discover new accounts.",
    "crm_cleanup": "VERIFY or CLEAN existing contact/email records, such as invalid addresses or duplicate records.",
    "inbound_triage": "CLASSIFY INCOMING replies, bounces or out-of-office messages. Do not start a new outbound workflow.",
}

TARGET_ROLES = {
    "none_specified": "No target job title or role is requested, including company-only and record-maintenance requests.",
    "founders_c_level": "Founders, co-founders, CEOs, CTOs and other chief executives.",
    "engineering_leaders": "VPs of Engineering, Engineering Directors, Heads of Engineering and Technical Leads.",
    "sales_leaders": "VPs of Sales, Sales Directors, Heads of Business Development and Chief Revenue Officers.",
    "marketing_leaders": "VPs of Marketing, Marketing Directors, Heads of Growth and Chief Marketing Officers.",
    "general_staff": "Individual contributors, developers, designers, managers or staff without a more specific supported leadership category.",
}

INDUSTRIES = {
    "none_specified": "No target industry is stated. A job title or location is not an industry.",
    "it_services": "IT services, IT consulting, managed IT, software development agencies and technology outsourcing.",
    "b2b_saas": "SaaS, cloud software and subscription software products.",
    "healthcare": "Healthcare, hospitals, clinics, medical devices, biotech and pharmaceuticals.",
    "fintech": "Fintech, financial technology, banking, payments, investment and crypto.",
    "ecommerce_retail": "E-commerce, retail, DTC and marketplaces.",
    "general_business": "Explicit cross-industry business services or general consulting.",
    "other": "An explicitly requested industry outside this demo's supported industry catalog.",
}

GEOGRAPHIES = {
    "none_specified": "No location is stated. Do not assume the US or worldwide coverage.",
    "india": "India or Indian locations.",
    "california_west_us": "California, San Francisco, Silicon Valley, Los Angeles or the US West Coast.",
    "us_nationwide": "USA, US, United States, America or nationwide US coverage.",
    "europe": "Europe, European Union, UK, Germany, France or Netherlands.",
    "global": "Explicit worldwide, global, international or any-location coverage.",
    "other": "An explicitly requested location outside this demo's supported location catalog.",
}

# Simple text patterns preserve explicit constraints instead of guessing from a
# weak model score. Keys match the choice menus above.
ROLE_PATTERNS = {
    "engineering_leaders": r"\b(?:vps?|vice[ -]presidents?|heads?|directors?|leads?)\s+(?:of\s+)?engineering\b|\b(?:engineering|technical)\s+(?:vps?|directors?|heads?|leads?|leaders?)\b",
    "sales_leaders": r"\b(?:vps?|vice[ -]presidents?|heads?|directors?)\s+(?:of\s+)?(?:sales|business development)\b|\b(?:sales leaders?|sales directors?|cros?|chief revenue officers?)\b",
    "marketing_leaders": r"\b(?:vps?|vice[ -]presidents?|heads?|directors?)\s+(?:of\s+)?(?:marketing|growth)\b|\b(?:marketing leaders?|marketing directors?|cmos?|chief marketing officers?)\b",
    "founders_c_level": r"\b(?:founders?|co[ -]founders?|ceos?|ctos?|chief executive officers?|chief technology officers?|c[ -]suite|chief officers?)\b",
    "general_staff": r"\b(?:people|contacts?|staff|employees?|executives?|decision[ -]makers?|developers?|designers?|managers?|leaders?|directors?|heads?|vps?|vice[ -]presidents?)\b",
}

INDUSTRY_PATTERNS = {
    "it_services": r"\b(?:it[ -]services?|information technology services?|it consulting|managed it(?: services?)?|technology outsourcing|software development agenc(?:y|ies))\b",
    "b2b_saas": r"\b(?:saas|software[ -]as[ -]a[ -]service|cloud software|software products?)\b",
    "healthcare": r"\b(?:healthcare|medical|hospitals?|clinics?|biotech|pharmaceuticals?)\b",
    "fintech": r"\b(?:fintech|financial technology|banking|payments?|investment|crypto)\b",
    "ecommerce_retail": r"\b(?:e[ -]?commerce|retail|dtc|marketplaces?)\b",
    "general_business": r"\b(?:cross[ -]industry|general business|consulting)\b",
    "other": r"\b(?:manufacturing|education|insurance|construction|automotive|energy|logistics|telecom|hospitality|real estate|agriculture|software)\b",
}

GEOGRAPHY_PATTERNS = {
    "california_west_us": r"\b(?:california|san francisco|silicon valley|los angeles|west coast|bay area)\b",
    "india": r"\b(?:india|indian|bengaluru|bangalore|hyderabad|mumbai|delhi)\b",
    "us_nationwide": r"\b(?:usa|united states|america|american|us)\b|\bu\.s\.(?:a\.?)?",
    "europe": r"\b(?:europe|european|european union|uk|united kingdom|germany|france|netherlands|london|berlin|paris|amsterdam)\b",
    "global": r"\b(?:global|worldwide|international|anywhere|any location)\b",
    "other": r"\b(?:canada|canadian|singapore|australia|australian|japan|china|brazil|uae|dubai|africa|asia|new york|texas|boston|seattle)\b",
}

WORKFLOW_BLUEPRINTS = {
    "account_discovery": [
        {"action": "discover_companies", "preferred_tool": "company_finder", "reasoning": "Discover companies using only the requested target constraints."},
    ],
    "contact_hunting": [
        {"action": "find_decision_makers", "preferred_tool": "contact_hunter", "reasoning": "Find people matching the requested roles and company constraints."},
        {"action": "verify_contact_data", "preferred_tool": "verify_emails", "reasoning": "Verify the requested email/contact data."},
    ],
    "outbound_pipeline": [
        {"action": "discover_companies", "preferred_tool": "company_finder", "reasoning": "Discover target accounts for the requested outbound workflow."},
        {"action": "find_decision_makers", "preferred_tool": "contact_hunter", "reasoning": "Find relevant contacts within the target accounts."},
        {"action": "verify_contact_data", "preferred_tool": "verify_emails", "reasoning": "Check contact deliverability before any future outreach."},
        {"action": "qualify_leads", "preferred_tool": "smart_lead_scoring", "reasoning": "Assess lead fit against the requested customer profile."},
    ],
    "enrichment_only": [
        {"action": "enrich_records", "preferred_tool": "company_enrichment", "reasoning": "Fill missing fields on existing records without discovering new accounts."},
    ],
    "crm_cleanup": [
        {"action": "verify_contact_data", "preferred_tool": "verify_emails", "reasoning": "Identify invalid email/contact records for review. This demo does not delete records."},
    ],
    "inbound_triage": [
        {"action": "classify_incoming_replies", "preferred_tool": "reply_ora", "reasoning": "Classify incoming messages without generating replies or starting outreach."},
    ],
}
