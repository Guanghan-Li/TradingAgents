#!/usr/bin/env python3
"""
Generate a sector-organized PDF summary of TradingAgents batch outputs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


BASE_DIR = Path(__file__).resolve().parent
PDF_FILENAME = BASE_DIR / "full_summary.pdf"
ANALYSIS_DATE = BASE_DIR.name

SECTOR_GROUPS = [
    (
        "Growth - Mega & Large Cap Tech",
        ["NVDA", "MSFT", "AMZN", "META", "TSLA", "CRWD", "PLTR", "GOOGL"],
    ),
    (
        "Semiconductors & AI Hardware",
        ["TSM", "ASML", "AMD", "AVGO", "ARM", "MU"],
    ),
    (
        "Datacenter & Infrastructure",
        ["DLR", "EQIX", "ANET", "DELL", "SMCI"],
    ),
    (
        "AI Software & Cloud",
        ["NOW", "SNOW", "DDOG", "NET"],
    ),
    (
        "Dividend - Income & Stability",
        ["VICI", "MAIN", "JPM", "JNJ", "NEE", "MO", "O"],
    ),
    (
        "Minerals & Materials",
        ["MP", "ALB", "FCX", "SCCO", "VALE"],
    ),
    (
        "ETF / Macro",
        ["QQQ", "VYM", "GLD", "VWO", "BND", "XLE"],
    ),
]


def load_run_summary(ticker: str) -> dict | None:
    path = BASE_DIR / ticker / "run_summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def load_report_text(ticker: str, report_name: str) -> str:
    path = BASE_DIR / ticker / "reports" / report_name
    return path.read_text() if path.exists() else ""


def clean_text(value: str) -> str:
    text = (value or "").replace("\r", "\n")
    text = text.replace("```json", "").replace("```", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate_text(value: str, max_length: int) -> str:
    text = clean_text(value)
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def extract_current_price(ticker: str, summary: dict) -> str:
    text = load_report_text(ticker, "market_report.md")
    patterns = [
        r"\*\*Current Price\*\*[:\s|]+\$?([\d,.]+)",
        r"\*\*Price\*\*[:\s|]+\$?([\d,.]+)",
        r"Current Price[:\s|]+\$?([\d,.]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"${match.group(1)}"
    return "$N/A"


def extract_level(text: str, labels: list[str]) -> str | None:
    for label in labels:
        pattern = rf"{label}[:\s|]+([$\d.,\-\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip().replace("  ", " ")
    return None


def extract_support_resistance(ticker: str) -> tuple[str, str]:
    text = load_report_text(ticker, "market_report.md")
    support = extract_level(text, [r"\*\*Support Levels\*\*", r"\*\*Support\*\*", "Support Levels", "Support"])
    resistance = extract_level(
        text,
        [r"\*\*Resistance Levels\*\*", r"\*\*Resistance\*\*", "Resistance Levels", "Resistance"],
    )
    return support or "N/A", resistance or "N/A"


def extract_key_catalysts(summary: dict) -> list[dict]:
    catalysts = summary.get("catalysts") or []
    return catalysts[:3]


def clean_risk_summary(summary: dict) -> str:
    risk = clean_text(summary.get("risk_summary", ""))
    if not risk:
        return "N/A"

    if risk.startswith("{"):
        try:
            payload = json.loads(risk)
            if isinstance(payload, dict):
                if payload.get("executive_summary"):
                    return clean_text(payload["executive_summary"])
                if payload.get("rating") and payload.get("investment_thesis"):
                    return clean_text(payload["investment_thesis"])
        except json.JSONDecodeError:
            pass

    if "What I can help with instead" in risk:
        risk = risk.split("What I can help with instead", 1)[0].strip()
    return risk


def extract_what_it_said(summary: dict, ticker: str) -> str:
    parts = []
    if summary.get("chief_summary"):
        parts.append(summary["chief_summary"])
    if summary.get("chief_thesis"):
        parts.append(summary["chief_thesis"])

    chief_report = load_report_text(ticker, "chief_analyst_report.md")
    verdict_match = re.search(
        r"### Verdict\s*-\s*Rating:\s*(.*?)\s*-\s*Summary:\s*(.*?)\s*-\s*Thesis:\s*(.*?)(?:###|$)",
        chief_report,
        re.S,
    )
    if verdict_match:
        for group in verdict_match.groups():
            cleaned = clean_text(group)
            if cleaned:
                parts.append(cleaned)

    execution_match = re.search(r"- Trader plan:\s*(.*?)(?:- Portfolio manager guidance:|### Tail Risk|$)", chief_report, re.S)
    if execution_match:
        parts.append(clean_text(execution_match.group(1)))

    if not parts:
        parts.append(summary.get("decision", "No summary available."))
    return truncate_text(" ".join(parts), 450)


def build_sector_entries() -> list[tuple[str, list[dict]]]:
    sector_entries: list[tuple[str, list[dict]]] = []
    for sector_name, tickers in SECTOR_GROUPS:
        entries = []
        for ticker in tickers:
            summary = load_run_summary(ticker)
            if not summary:
                continue
            support, resistance = extract_support_resistance(ticker)
            entries.append(
                {
                    "ticker": ticker,
                    "decision": summary.get("decision", "N/A"),
                    "analysis_date": summary.get("analysis_date", ANALYSIS_DATE),
                    "started_at": (summary.get("started_at") or "N/A")[:19],
                    "ended_at": (summary.get("ended_at") or "N/A")[:19],
                    "current_price": extract_current_price(ticker, summary),
                    "support": support,
                    "resistance": resistance,
                    "catalysts": extract_key_catalysts(summary),
                    "risk_summary": truncate_text(clean_risk_summary(summary), 420),
                    "what_it_said": extract_what_it_said(summary, ticker),
                }
            )
        if entries:
            sector_entries.append((sector_name, entries))
    return sector_entries


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="PageTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#102A43"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#486581"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectorHeader",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.white,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TickerTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#102A43"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="DecisionText",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=14,
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="MetaInfo",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#52606D"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10,
            textColor=colors.HexColor("#1D4E89"),
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.5,
            textColor=colors.HexColor("#1F2933"),
        )
    )
    return styles


def decision_color(decision: str):
    normalized = (decision or "").upper()
    if normalized in {"BUY", "OVERWEIGHT"}:
        return colors.HexColor("#0B6E4F")
    if normalized in {"SELL", "UNDERWEIGHT"}:
        return colors.HexColor("#B42318")
    return colors.HexColor("#B26B00")


def create_stock_box(entry: dict, styles) -> Table:
    header = Table(
        [
            [
                Paragraph(f"<b>{entry['ticker']}</b>", styles["TickerTitle"]),
                Paragraph(
                    f"<b>{entry['decision']}</b>",
                    ParagraphStyle(
                        "DecisionInline",
                        parent=styles["DecisionText"],
                        textColor=decision_color(entry["decision"]),
                    ),
                ),
            ]
        ],
        colWidths=[3.6 * inch, 2.6 * inch],
    )
    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F6FA")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    body = [
        header,
        Spacer(1, 0.08 * inch),
        Paragraph(
            f"<b>Analysis Date:</b> {entry['analysis_date']}<br/>"
            f"<b>Started:</b> {entry['started_at']}<br/>"
            f"<b>Ended:</b> {entry['ended_at']}",
            styles["MetaInfo"],
        ),
        Spacer(1, 0.06 * inch),
        Paragraph(
            f"<b>Current Price:</b> {entry['current_price']}<br/>"
            f"<b>Support:</b> {entry['support']}<br/>"
            f"<b>Resistance:</b> {entry['resistance']}",
            styles["MetaInfo"],
        ),
        Spacer(1, 0.08 * inch),
        Paragraph("Top 3 Key Catalysts", styles["SectionLabel"]),
    ]

    catalysts = entry["catalysts"] or [{"catalyst": "N/A", "date_or_window": "N/A", "expected_impact": "N/A"}]
    for idx, catalyst in enumerate(catalysts[:3], start=1):
        cat_name = clean_text(catalyst.get("catalyst", "N/A"))
        cat_date = clean_text(catalyst.get("date_or_window", "N/A"))
        cat_impact = truncate_text(catalyst.get("expected_impact", "N/A"), 150)
        body.append(
            Paragraph(
                f"<b>{idx}. {cat_name}</b><br/>"
                f"<font color='#52606D'>{cat_date}</font><br/>"
                f"{cat_impact}",
                styles["BodySmall"],
            )
        )
        body.append(Spacer(1, 0.04 * inch))

    body.extend(
        [
            Paragraph("What It Said", styles["SectionLabel"]),
            Paragraph(entry["what_it_said"], styles["BodySmall"]),
            Spacer(1, 0.06 * inch),
            Paragraph("Risk Summary", styles["SectionLabel"]),
            Paragraph(entry["risk_summary"], styles["BodySmall"]),
        ]
    )

    table = Table([[body]], colWidths=[6.7 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1.1, colors.HexColor("#BCCCDC")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def create_sector_banner(name: str, styles) -> Table:
    banner = Table([[Paragraph(name, styles["SectorHeader"])]], colWidths=[6.9 * inch])
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1D4E89")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return banner


def build_story():
    styles = build_styles()
    sector_entries = build_sector_entries()
    total_stocks = sum(len(entries) for _, entries in sector_entries)

    story = [
        Spacer(1, 1.1 * inch),
        Paragraph("Trading Agents Analysis Summary", styles["PageTitle"]),
        Paragraph(f"Analysis Date: {ANALYSIS_DATE}", styles["SubTitle"]),
        Paragraph(f"Total Stocks Analyzed: {total_stocks}", styles["SubTitle"]),
        Spacer(1, 0.5 * inch),
        Paragraph(
            "Sector-organized summary with decision, timestamps, price levels, catalysts, and condensed risk guidance.",
            styles["SubTitle"],
        ),
        PageBreak(),
    ]

    first_sector = True
    for sector_name, entries in sector_entries:
        if not first_sector:
            story.append(PageBreak())
        first_sector = False
        story.append(create_sector_banner(sector_name, styles))
        story.append(Spacer(1, 0.15 * inch))
        for idx, entry in enumerate(entries):
            story.append(create_stock_box(entry, styles))
            if idx != len(entries) - 1:
                story.append(Spacer(1, 0.18 * inch))
    return story


def main():
    story = build_story()
    doc = SimpleDocTemplate(
        str(PDF_FILENAME),
        pagesize=letter,
        rightMargin=0.45 * inch,
        leftMargin=0.45 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.45 * inch,
    )
    doc.build(story)
    print(f"Generated: {PDF_FILENAME}")


if __name__ == "__main__":
    main()
