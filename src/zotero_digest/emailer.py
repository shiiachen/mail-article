from __future__ import annotations

from datetime import UTC, datetime
from email.message import EmailMessage
from html import escape
import smtplib

from zotero_digest.models import MatchResult


def build_email(matches: list[MatchResult], fetched_count: int, email_from: str, recipients: list[str]) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = f"Daily paper digest: {len(matches)} matches"
    message["From"] = email_from
    message["To"] = ", ".join(recipients)
    message.set_content(_build_text(matches, fetched_count))
    message.add_alternative(_build_html(matches, fetched_count), subtype="html")
    return message


def send_email(message: EmailMessage, host: str, port: int, username: str, password: str) -> None:
    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


def _build_text(matches: list[MatchResult], fetched_count: int) -> str:
    lines = [
        f"Generated at: {datetime.now(UTC).isoformat()}",
        f"Fetched {fetched_count} new papers, matched {len(matches)}.",
        "",
    ]
    if not matches:
        lines.append("No new papers matched your keywords today.")
        return "\n".join(lines)

    for index, match in enumerate(matches, start=1):
        paper = match.paper
        lines.extend(
            [
                f"{index}. {paper.title}",
                f"   Authors: {', '.join(paper.authors)}",
                f"   Published: {paper.published_at.date().isoformat()}",
                f"   Keywords: {', '.join(match.matched_keywords)}",
                f"   Score: {match.final_score:.3f}",
                f"   URL: {paper.url}",
                f"   PDF: {paper.pdf_url or 'N/A'}",
                f"   Abstract: {paper.abstract}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def _build_html(matches: list[MatchResult], fetched_count: int) -> str:
    rows = [
        "<h2>Daily paper digest</h2>",
        f"<p>Fetched <strong>{fetched_count}</strong> new papers, matched <strong>{len(matches)}</strong>.</p>",
    ]
    if not matches:
        rows.append("<p>No new papers matched your keywords today.</p>")
        return "".join(rows)

    rows.append("<ol>")
    for match in matches:
        paper = match.paper
        rows.append("<li>")
        rows.append(f"<p><a href=\"{escape(paper.url)}\"><strong>{escape(paper.title)}</strong></a><br>")
        rows.append(f"Authors: {escape(', '.join(paper.authors))}<br>")
        rows.append(f"Published: {paper.published_at.date().isoformat()}<br>")
        rows.append(f"Keywords: {escape(', '.join(match.matched_keywords))}<br>")
        rows.append(f"Score: {match.final_score:.3f}<br>")
        if paper.pdf_url:
            rows.append(f"PDF: <a href=\"{escape(paper.pdf_url)}\">link</a></p>")
        else:
            rows.append("PDF: N/A</p>")
        rows.append(f"<p>{escape(paper.abstract)}</p>")
        rows.append("</li>")
    rows.append("</ol>")
    return "".join(rows)
