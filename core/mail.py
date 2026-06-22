import requests
from config import config


def send_email(to, subject, html_body):
    api_key = config.MAILGUN_API_KEY
    domain = config.MAILGUN_DOMAIN
    mail_from = config.MAIL_FROM

    if not api_key or not domain:
        return False

    try:
        resp = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": mail_from,
                "to": to,
                "subject": subject,
                "html": html_body,
            },
            timeout=30,
        )
        return resp.ok
    except Exception:
        return False


def send_newsletter(to, items):
    html_items = "".join(
        f'<li><a href="{config.SITE_URL}/haber/{item["id"]}" style="color:#c0392b;text-decoration:none;">'
        f'<strong>{item["title"]}</strong></a><br><small style="color:#888;">{item.get("summary", "")[:100]}...</small></li>'
        for item in items
    )
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;background:#f8f7f4;padding:20px;">
<div style="max-width:600px;margin:auto;background:white;padding:24px;border-top:3px solid #c0392b;">
<h1 style="color:#1a1a2e;font-size:24px;">{config.SITE_NAME} Günlük Bülten</h1>
<p style="color:#666;">Günün önemli haberleri</p>
<ul style="padding-left:0;list-style:none;">{html_items}</ul>
<hr style="border:1px solid #eee;">
<p style="color:#999;font-size:12px;">
Bu e-postayı {config.SITE_NAME} bültenine abone olduğunuz için alıyorsunuz.<br>
<a href="{config.SITE_URL}/abonelik-iptal" style="color:#c0392b;">Abonelikten çık</a>
</p></div></body></html>"""
    return send_email(to, f"{config.SITE_NAME} - Günlük Haber Bülteni", html)
