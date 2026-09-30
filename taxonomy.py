"""
agent/taxonomy.py — Single Source of Truth for Oppora's Tools and GTM Concepts.

This file provides the semantic criteria and menus that Laya's decision heads
evaluate to classify user intent, target criteria, workflow stages, and tool selection.
"""

from typing import Dict, List

# ─────────────────────────────────────────────────────────────────────────────
# 1. Oppora Tool Catalog
# ─────────────────────────────────────────────────────────────────────────────
# Mapped directly to Oppora's real production feature suite.
OPPORA_TOOLS: Dict[str, str] = {
    "company_finder": (
        "Search for company entities, organizations, and firmographics "
        "matching specific industries, employee sizes, and geographic locations."
    ),
    "contact_hunter": (
        "Discover individual decision-makers, executives, founders, and their "
        "verified names and candidate email addresses inside target companies."
    ),
    "verify_emails": (
        "Verify deliverability, analyze SMTP responses, and filter dead or "
        "bouncing email addresses to protect domain sender reputation."
    ),
    "smart_lead_scoring": (
        "Score, rank, and qualify leads and companies against an Ideal Customer "
        "Profile (ICP) and qualification filters."
    ),
    "campaign_sequencer": (
        "Queue and structure multi-step cold outreach sequences and merge-tag "
        "variables for approved leads."
    ),
    "reply_ora": (
        "Triage, classify intent, and formulate automated responses for incoming "
        "prospect replies."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. GTM Intent Taxonomy
# ─────────────────────────────────────────────────────────────────────────────
# Used by Laya to classify the overarching objective of the user's prompt.
GTM_INTENTS: Dict[str, str] = {
    "account_discovery": (
        "Search, discover, and build lists of target company accounts, organizations, "
        "and firmographics without prospecting individual contacts."
    ),
    "outbound_pipeline": (
        "Build a cold outbound prospecting campaign from scratch to discover, "
        "qualify, and engage new target accounts and decision-makers."
    ),
    "contact_hunting": (
        "Find specific decision-maker emails and contact details for an existing "
        "list of target companies."
    ),
    "enrichment_only": (
        "Enrich raw company or lead records with missing firmographics, size, "
        "and email patterns."
    ),
    "crm_cleanup": (
        "Validate, verify, and purge dead, bouncing, or invalid contacts from "
        "an existing database to maintain hygiene."
    ),
    "inbound_triage": (
        "Classify and process incoming sales replies, bounces, or out-of-office "
        "responses from an active campaign."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 3. Target Seniority & Roles
# ─────────────────────────────────────────────────────────────────────────────
TARGET_ROLES: Dict[str, str] = {
    "none_specified": (
        "No specific job title, person, or individual executive was requested; "
        "the query targets companies, accounts, or organizations in general."
    ),
    "founders_c_level": (
        "Founders, Co-Founders, Chief Executive Officers (CEO), Chief Technology "
        "Officers (CTO), and C-Suite executive leadership."
    ),
    "sales_leaders": (
        "VPs of Sales, Heads of Business Development, Chief Revenue Officers (CRO), "
        "and Sales Directors."
    ),
    "engineering_leaders": (
        "VPs of Engineering, Engineering Directors, Technical Leads, and CTOs."
    ),
    "marketing_leaders": (
        "Chief Marketing Officers (CMO), Heads of Growth, and VPs of Marketing."
    ),
    "general_staff": (
        "Individual contributors, developers, designers, and operational staff."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 4. Target Industries
# ─────────────────────────────────────────────────────────────────────────────
INDUSTRIES: Dict[str, str] = {
    "b2b_saas": (
        "Software-as-a-Service, cloud software platforms, B2B tech products, "
        "and digital software solutions."
    ),
    "healthcare": (
        "Healthcare, medical devices, hospitals, clinics, biotech, and pharmaceutical."
    ),
    "fintech": (
        "Financial technology, banking software, payments, investment, and crypto."
    ),
    "ecommerce_retail": (
        "E-commerce stores, consumer retail brands, direct-to-consumer (DTC), "
        "and marketplace platforms."
    ),
    "general_business": (
        "General cross-industry commercial businesses, services, and consulting."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 5. Target Geographies
# ─────────────────────────────────────────────────────────────────────────────
GEOGRAPHIES: Dict[str, str] = {
    "california_west_us": (
        "California, San Francisco Bay Area, Silicon Valley, Los Angeles, and "
        "West Coast United States."
    ),
    "us_nationwide": (
        "Anywhere across the United States nationwide."
    ),
    "europe": (
        "United Kingdom, Germany, France, Netherlands, and European Union countries."
    ),
    "global": (
        "Worldwide international coverage without regional restrictions."
    ),
}

# ─────────────────────────────────────────────────────────────────────────────
# 6. Workflow Blueprints
# ─────────────────────────────────────────────────────────────────────────────
# Canonical sequences that Laya maps user intents onto.
WORKFLOW_BLUEPRINTS: Dict[str, List[Dict[str, str]]] = {
    "account_discovery": [
        {
            "action": "discover_companies",
            "preferred_tool": "company_finder",
            "reasoning": "Establish target account list matching industry and geographic parameters.",
        },
        {
            "action": "qualify_leads",
            "preferred_tool": "smart_lead_scoring",
            "reasoning": "Score and rank discovered companies against ICP criteria.",
        },
    ],
    "outbound_pipeline": [
        {
            "action": "discover_companies",
            "preferred_tool": "company_finder",
            "reasoning": "Establish target account list matching industry and geographic parameters.",
        },
        {
            "action": "find_decision_makers",
            "preferred_tool": "contact_hunter",
            "reasoning": "Identify relevant founders and leadership roles within discovered accounts.",
        },
        {
            "action": "verify_contact_data",
            "preferred_tool": "verify_emails",
            "reasoning": "Execute deliverability checks to protect domain reputation before sending.",
        },
        {
            "action": "qualify_leads",
            "preferred_tool": "smart_lead_scoring",
            "reasoning": "Score leads against ICP parameters to prioritize highest-fit prospects.",
        },
    ],
    "contact_hunting": [
        {
            "action": "find_decision_makers",
            "preferred_tool": "contact_hunter",
            "reasoning": "Locate specific personas inside existing company records.",
        },
        {
            "action": "verify_contact_data",
            "preferred_tool": "verify_emails",
            "reasoning": "Validate deliverability of discovered emails.",
        },
    ],
    "crm_cleanup": [
        {
            "action": "verify_contact_data",
            "preferred_tool": "verify_emails",
            "reasoning": "Run batch bounce triage and mailbox verification across existing CRM lists.",
        },
    ],
}
