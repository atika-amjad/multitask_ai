from __future__ import annotations

import html
import os
import re
import socket
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.policy import SMTP
from email.utils import formataddr

_PLACEHOLDER_HOSTS = {"smtp.example.com", "example.com", "mail.example.com"}
_MAX_BODY_CHARS = 100_000


def _strip_html(text: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.I | re.S)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _sanitize_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) > _MAX_BODY_CHARS:
        text = text[:_MAX_BODY_CHARS] + "\n\n[Content truncated for email size limits.]"
    return text


def _encode_header(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    return str(Header(value, "utf-8"))


def _plain_to_html(plain: str, subject: str = "") -> str:
    plain = _sanitize_text(plain)
    blocks: list[str] = []
    pattern = re.compile(
        r"(\d+)\.\s+(.+?)\n\s+(.+?)\n\s+(.+?)(?=\n\d+\.|\Z)",
        re.S,
    )
    matches = list(pattern.finditer(plain))

    if matches:
        for m in matches:
            title = html.escape(m.group(2).strip())
            url = html.escape(m.group(3).strip())
            snippet = html.escape(m.group(4).strip())
            blocks.append(
                f'<div style="margin:0 0 18px 0;padding:12px 16px;'
                f'border-left:4px solid #1a73e8;background:#f8f9fa;">'
                f'<h3 style="margin:0 0 8px 0;font-size:16px;color:#202124;">{title}</h3>'
                f'<p style="margin:0 0 6px 0;font-size:13px;">'
                f'<a href="{url}" style="color:#1a73e8;">{url}</a></p>'
                f'<p style="margin:0;font-size:14px;color:#3c4043;line-height:1.5;">'
                f"{snippet}</p></div>"
            )
        inner = "\n".join(blocks)
    else:
        paragraphs = [p.strip() for p in plain.split("\n\n") if p.strip()]
        if paragraphs:
            parts = []
            for p in paragraphs:
                line = html.escape(p).replace("\n", "<br>")
                if len(p) < 80 and not p.endswith("."):
                    parts.append(
                        f'<h2 style="font-size:18px;color:#202124;margin:20px 0 8px 0;">{line}</h2>'
                    )
                else:
                    parts.append(
                        f'<p style="margin:0 0 12px 0;font-size:14px;color:#3c4043;line-height:1.6;">{line}</p>'
                    )
            inner = "\n".join(parts)
        else:
            inner = f'<p style="font-size:14px;color:#3c4043;">{html.escape(plain)}</p>'

    heading = html.escape(subject or "Update")
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:24px;background:#ffffff;font-family:Arial,Helvetica,sans-serif;">
  <div style="max-width:640px;margin:0 auto;">
    <h1 style="margin:0 0 20px 0;font-size:22px;color:#202124;">{heading}</h1>
    {inner}
    <p style="margin-top:24px;font-size:12px;color:#80868b;">Sent via Multitask AI Agent</p>
  </div>
</body>
</html>"""


def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: str | None = None,
    sender_name: str | None = None,
    always_html: bool = True,
) -> str:
    host = os.getenv("SMTP_HOST", "").strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "").strip()
    from_addr = os.getenv("SMTP_FROM", user).strip()
    default_sender_name = os.getenv("SMTP_SENDER_NAME", "").strip() or None

    to = to.strip()
    subject = _sanitize_text(subject or "Message from Multitask AI Agent").split("\n")[0]
    if not to or "@" not in to:
        raise ValueError(f"Invalid recipient email: {to!r}")

    if not all([host, user, password, from_addr]):
        raise EnvironmentError(
            "Email requires SMTP_HOST, SMTP_USER, SMTP_PASSWORD, and SMTP_FROM "
            "environment variables."
        )
    if host.lower() in _PLACEHOLDER_HOSTS:
        raise EnvironmentError(
            f"SMTP_HOST is still the placeholder '{host}'. "
            "For Gmail use SMTP_HOST=smtp.gmail.com (with a Google app password)."
        )

    display_name = (sender_name or default_sender_name or "").strip() or None
    plain = _sanitize_text(body)
    html_content = _sanitize_text(html_body) if html_body else ""

    if html_content and not plain:
        plain = _strip_html(html_content)
    if not plain and not html_content:
        raise ValueError("Email body cannot be empty")

    if always_html and not html_content:
        html_content = _plain_to_html(plain, subject)

    msg = MIMEMultipart("alternative")
    if display_name:
        msg["From"] = formataddr((_encode_header(display_name), from_addr))
    else:
        msg["From"] = from_addr
    msg["To"] = to
    msg["Subject"] = _encode_header(subject)

    msg.attach(MIMEText(plain, "plain", "utf-8"))
    if html_content:
        msg.attach(MIMEText(html_content, "html", "utf-8"))

    payload = msg.as_bytes(policy=SMTP)

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(user, password)
            server.sendmail(from_addr, [to], payload)
    except socket.gaierror as exc:
        raise ConnectionError(
            f"Cannot resolve SMTP host '{host}'. Check SMTP_HOST in .env "
            f"(Gmail: smtp.gmail.com, Outlook: smtp-mail.outlook.com)."
        ) from exc
    except smtplib.SMTPException as exc:
        raise RuntimeError(f"SMTP error while sending to {to}: {exc}") from exc

    fmt = "HTML + plain text" if html_content else "plain text"
    return f"Email sent to {to} ({fmt})"
