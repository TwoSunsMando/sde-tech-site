#!/usr/bin/env python3
"""SDE Tech static site generator.

Emits pure static HTML into public/ with a shared header/footer copied into
every file (no build step at deploy time — nginx just serves public/).

Run: `python3 build.py`. Re-run after editing this file. The generator is a
developer convenience; the site itself has no build dependencies.
"""
from __future__ import annotations

import os
import re
import textwrap
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")

LAST_UPDATED = "May 6, 2026"
COPYRIGHT_YEAR = 2026

NAV_ITEMS = [
    ("IT Services", "it-services.html", "it-services"),
    ("VoIP Phones", "voip-phones.html", "voip-phones"),
    ("Website Services", "website-services.html", "website-services"),
    ("Software Development", "software-development.html", "software-development"),
    ("AI & Automation", "ai-automation.html", "ai-automation"),
    ("About", "about-us.html", "about"),
    ("Contact", "contact-us.html", "contact"),
]

# Pages that map to the "About" nav slot.
ABOUT_KEYS = {"about-us", "team-leaders"}


def head(title: str, description: str, slug: str) -> str:
    canonical = f"https://sde-tech.com/{slug}.html" if slug != "index" else "https://sde-tech.com/"
    og_title = title if "sde tech" in title.lower() else f"{title} | SDE Tech"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{og_title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="SDE Tech">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap">
<link rel="stylesheet" href="css/style.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>"""


def header(active_key: str) -> str:
    items = []
    for label, href, key in NAV_ITEMS:
        is_active = (key == active_key) or (key == "about" and active_key in ABOUT_KEYS)
        cls = ' class="active"' if is_active else ""
        items.append(f'      <li><a href="{href}"{cls}>{label}</a></li>')
    nav_html = "\n".join(items)
    return f"""
<header class="site-header">
  <div class="container">
    <a class="brand" href="index.html" aria-label="SDE Tech home">
      <img src="images/sde_tech_logo_web.png" alt="SDE Tech">
    </a>
    <input type="checkbox" id="nav-toggle" class="nav-toggle" aria-label="Toggle navigation">
    <label for="nav-toggle" class="nav-toggle-label" aria-hidden="true">
      <span></span><span></span><span></span>
    </label>
    <nav class="primary-nav" aria-label="Primary">
      <ul>
{nav_html}
      </ul>
    </nav>
  </div>
</header>"""


def page_title(title: str, breadcrumb: str | None = None) -> str:
    crumb = ""
    if breadcrumb:
        crumb = f'<div class="breadcrumbs"><a href="index.html">Home</a> &rsaquo; {breadcrumb}</div>'
    return f"""
<section class="page-title">
  <div class="container">
    <h1>{title}</h1>
    {crumb}
  </div>
</section>"""


FOOTER = f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4>SDE Tech</h4>
        <p>2912 Bee Ridge Road<br>Sarasota, FL 34239</p>
        <p>P: <a href="tel:+18663712265">866-371-2265</a></p>
        <p><a href="mailto:info@sde-tech.com">info@sde-tech.com</a></p>
      </div>
      <div>
        <h4>Partners</h4>
        <div class="partner-badges">
          <a href="https://www.3cx.com/" target="_blank" rel="noopener" aria-label="3CX Certified Partner">
            <img src="images/3CX_Certified_Partner-150x150.png" alt="3CX Certified Partner" width="80" height="80">
          </a>
          <a href="https://www.manateechamber.com/" target="_blank" rel="noopener" aria-label="Manatee Chamber of Commerce member">
            <img src="images/MCC-150x150.png" alt="Manatee Chamber of Commerce member" width="80" height="80">
          </a>
        </div>
      </div>
      <div>
        <h4>Compliance</h4>
        <ul>
          <li><a href="privacy-policy.html">Privacy Policy</a></li>
          <li><a href="terms-of-service.html">Terms of Service</a></li>
          <li><a href="sms-messaging-policy.html">SMS Messaging Policy</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      &copy; {COPYRIGHT_YEAR} SDE Tech LLC. All rights reserved.
    </div>
  </div>
</footer>
</body>
</html>
"""


def render(slug: str, title: str, description: str, body: str,
           active_key: str | None = None,
           hero: bool = False, breadcrumb: str | None = None,
           page_h1: str | None = None) -> str:
    if active_key is None:
        active_key = slug
    parts = [head(title, description, slug), header(active_key)]
    if not hero:
        parts.append(page_title(page_h1 or title, breadcrumb=breadcrumb))
    parts.append('<main id="main">')
    parts.append(body)
    parts.append("</main>")
    parts.append(FOOTER)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Page bodies
# ---------------------------------------------------------------------------

HOME_HERO = """
<section class="hero">
  <div class="container">
    <h1>One Sarasota team for IT, phones, websites, and software.</h1>
    <p class="lead">SDE Tech is the long-running local partner small and mid-size businesses
    turn to when they want their technology handled by people they can actually reach. No
    outsourced help desks. No vendor sprawl. Just the four things that keep your business
    running, all under one roof.</p>
    <a class="btn" href="contact-us.html">Talk to our team</a>
    <a class="btn btn-outline" href="about-us.html" style="margin-left:12px;">About SDE Tech</a>
  </div>
</section>
"""

# Inline SVG icons (24x24, currentColor) for the four service tiles.
ICON_IT = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="1.5"/><path d="M8 20h8M12 16v4"/></svg>"""
ICON_PHONE = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A15 15 0 0 1 3 6a2 2 0 0 1 2-2z"/></svg>"""
ICON_WEB = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>"""
ICON_CODE = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/></svg>"""
ICON_AI = """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l1.7 4.8L18.5 9.5l-4.8 1.7L12 16l-1.7-4.8L5.5 9.5l4.8-1.7L12 3z"/><path d="M18.5 16l.9 2.6L22 19.5l-2.6.9L18.5 23l-.9-2.6L15 19.5l2.6-.9L18.5 16z"/></svg>"""

HOME_TILES = f"""
<section class="section">
  <div class="container">
    <h2 style="text-align:center;">What we do</h2>
    <p class="muted" style="text-align:center;max-width:640px;margin:0 auto;">Five practice areas, one local team. Pick what you need today, expand as your business grows.</p>
    <div class="tile-grid">
      <a class="tile" href="it-services.html">
        <div class="icon">{ICON_IT}</div>
        <h3>IT Services</h3>
        <p>Networks, hardware, backups, and day-to-day support &mdash; handled, so your team can get on with their work.</p>
      </a>
      <a class="tile" href="voip-phones.html">
        <div class="icon">{ICON_PHONE}</div>
        <h3>VoIP Phones</h3>
        <p>Modern 3CX phone systems with the features you need at a fraction of the cost of legacy lines.</p>
      </a>
      <a class="tile" href="website-services.html">
        <div class="icon">{ICON_WEB}</div>
        <h3>Website Services</h3>
        <p>Clean, fast, mobile-ready sites your customers can find on Google and read on any device.</p>
      </a>
      <a class="tile" href="software-development.html">
        <div class="icon">{ICON_CODE}</div>
        <h3>Software Development</h3>
        <p>Custom software built around how your business actually runs &mdash; not the other way around.</p>
      </a>
      <a class="tile" href="ai-automation.html">
        <div class="icon">{ICON_AI}</div>
        <h3>AI &amp; Automation</h3>
        <p>Practical AI agents and workflow automation that take repetitive work off your team&rsquo;s plate &mdash; built around your business, not bolted on.</p>
      </a>
    </div>
  </div>
</section>
"""

HOME_ABOUT_TEASER = """
<section class="section alt">
  <div class="container">
    <div class="about-teaser">
      <div>
        <h2>Local, hands-on, and easy to reach.</h2>
        <p>SDE Tech is owned and run by Dan Steiner and Steve Johnson, with combined experience that spans the full range of business technology &mdash; from medical offices to manufacturing to retail. We pick up the phone, we show up on site when it matters, and we don&rsquo;t pad invoices.</p>
        <p><a href="about-us.html">Read more about SDE Tech &rsaquo;</a></p>
      </div>
      <div class="teaser-card">
        <p style="font-size:18px;font-weight:600;margin-bottom:8px;">Why local matters.</p>
        <p>When something breaks, you&rsquo;re not opening a ticket with someone three time zones away. You&rsquo;re calling a Sarasota number and getting a Sarasota answer.</p>
      </div>
    </div>
  </div>
</section>
"""

HOME_CTA = """
<section class="cta-band">
  <div class="container">
    <h2>Ready to talk?</h2>
    <p>Tell us what your business runs on today. We&rsquo;ll tell you what we&rsquo;d change, what we&rsquo;d leave alone, and what it would cost.</p>
    <p style="margin-top:24px;"><a class="btn" href="contact-us.html">Contact us today</a></p>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

ABOUT_BODY = """
<section class="section">
  <div class="container">
    <article class="prose">
      <p>The owners of SDE Tech have over 20 years of experience working in the Information
      Technology arena. They have worked with large companies of more than 1,000 employees and
      with small offices of two to five people, and just about every size in between. There is
      rarely a situation they have not seen or a problem they have not solved.</p>

      <p>Experience counts when the clock is ticking and it&rsquo;s on your dime. While most
      shops stretch out solutions, we pride ourselves on getting in and out quickly &mdash;
      without cutting corners &mdash; so you can focus on your bottom line. Our rates are
      straightforward, easy to calculate, and below market most of the time. We have built a
      following of clients on quality, reputation, and honest pricing.</p>

      <p>SDE Tech got its start maintaining a large number of medical offices, environments
      that demand the latest in technology when it comes to computers, internet connectivity,
      phone systems, and specialized business applications. Our team has since worked across
      manufacturing, retail, wholesale, shipping and packaging, web-based companies, healthcare,
      financial services, and more.</p>

      <h2>Meet the team</h2>
      <p>SDE Tech is owned by Dan Steiner and Steve Johnson. <a href="team-leaders.html">Read more about our team leaders &rsaquo;</a></p>
    </article>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

TEAM_BODY = """
<!--
  Team leader content needs to come from Dan.
  Each card below is a placeholder. Fill in:
    - <h3> with the leader's full name
    - .role with their title
    - .photo-placeholder div: replace with an <img> tag once a headshot is available
    - .bio paragraph with 2-4 sentences of background
  When ready, remove this comment block.
-->
<section class="section">
  <div class="container">
    <article class="prose" style="max-width:880px;">
      <p>SDE Tech is owned and operated by two long-tenured technology professionals with
      complementary backgrounds across IT operations, networking, telephony, and business
      software. Below is a quick introduction to the people you&rsquo;ll be working with.</p>

      <div class="team-grid">
        <div class="team-card">
          <div class="photo-placeholder" aria-hidden="true">Photo</div>
          <h3>Dan Steiner</h3>
          <p class="role">Co-Owner</p>
          <p class="bio">Bio placeholder &mdash; Dan, please add 2&ndash;4 sentences covering
          background, areas of focus, and what you typically handle for clients.</p>
        </div>

        <div class="team-card">
          <div class="photo-placeholder" aria-hidden="true">Photo</div>
          <h3>Steve Johnson</h3>
          <p class="role">Co-Owner</p>
          <p class="bio">Bio placeholder &mdash; Steve, please add 2&ndash;4 sentences covering
          background, areas of focus, and what you typically handle for clients.</p>
        </div>
      </div>

      <p style="margin-top:32px;">Want to know more about how we work? <a href="about-us.html">Read about SDE Tech &rsaquo;</a></p>
    </article>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

CONTACT_BODY = """
<section class="section">
  <div class="container">
    <div class="contact-grid">
      <div>
        <h2 style="margin-top:0;">Get in touch</h2>
        <p>Tell us what your business is dealing with and what you&rsquo;d like to change. We
        respond to inquiries within one business day.</p>

        <form class="contact-form" action="mailto:info@sde-tech.com" method="post" enctype="text/plain">
          <div class="field">
            <label for="cf-name">Your name</label>
            <input type="text" id="cf-name" name="name" required>
          </div>
          <div class="field">
            <label for="cf-company">Company</label>
            <input type="text" id="cf-company" name="company">
          </div>
          <div class="field">
            <label for="cf-email">Email</label>
            <input type="email" id="cf-email" name="email" required>
          </div>
          <div class="field">
            <label for="cf-phone">Phone (optional)</label>
            <input type="tel" id="cf-phone" name="phone">
            <p class="help">By providing your phone number, you consent to receive SMS messages
            from SDE Tech regarding your inquiry. See our <a href="sms-messaging-policy.html">SMS Messaging Policy</a>.</p>
          </div>
          <div class="field">
            <label for="cf-topic">What can we help with?</label>
            <select id="cf-topic" name="topic">
              <option>IT Services</option>
              <option>VoIP Phones</option>
              <option>Website Services</option>
              <option>Software Development</option>
              <option>Something else</option>
            </select>
          </div>
          <div class="field">
            <label for="cf-message">Message</label>
            <textarea id="cf-message" name="message" required></textarea>
          </div>
          <button type="submit" class="btn btn-primary">Send message</button>
          <p class="help" style="margin-top:12px;">This form opens your email client. Prefer to write us directly? Email <a href="mailto:info@sde-tech.com">info@sde-tech.com</a>.</p>
        </form>
      </div>

      <div>
        <div class="info-card">
          <h3>SDE Tech</h3>
          <p class="label">Office</p>
          <p class="value">2912 Bee Ridge Road<br>Sarasota, FL 34239</p>
          <p class="label">Phone</p>
          <p class="value"><a href="tel:+18663712265">866-371-2265</a></p>
          <p class="label">Email</p>
          <p class="value"><a href="mailto:info@sde-tech.com">info@sde-tech.com</a></p>
          <p class="label">Hours</p>
          <p class="value">Monday &ndash; Friday, 8:00 AM &ndash; 5:00 PM ET<br>
          <span class="muted">After-hours support available for managed-service clients.</span></p>
        </div>

        <iframe class="map"
          title="Map showing 2912 Bee Ridge Road, Sarasota, FL 34239"
          src="https://www.google.com/maps?q=2912+Bee+Ridge+Road,+Sarasota,+FL+34239&output=embed"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </div>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

IT_BODY = """
<section class="section">
  <div class="container">
    <article class="prose">
      <p>SDE Tech offers IT consulting services that include managed network services, on-site
      premise services, and business application selection. We have over 20 years of experience
      implementing every facet of local and wide area networks. There&rsquo;s no job too big or
      too small.</p>
      <p>Let us help you streamline your business processes while reducing your total cost of
      ownership &mdash; and finally let you realize your return on investment.</p>
    </article>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <div class="col-grid">
      <div class="col">
        <h3>Managed Network Services</h3>
        <ul>
          <li>Proactive monitoring and management of your computer system and network</li>
          <li>On-site and off-site backups</li>
          <li>Business continuity, disaster recovery, and co-location services</li>
          <li>Hosting solutions for all business applications</li>
          <li>Hosted or on-site email solutions</li>
          <li>Remote connectivity for home or satellite offices</li>
          <li>Spam and content filtering</li>
          <li>Remote troubleshooting and support</li>
        </ul>
      </div>
      <div class="col">
        <h3>On-site Premise Services</h3>
        <ul>
          <li>Virus and malware removal and updates</li>
          <li>Computer troubleshooting, repair, and new setups</li>
          <li>Network cabling &mdash; voice and data</li>
          <li>Internet connectivity: broadband, T1, FIOS, cable, DSL</li>
          <li>Wireless systems</li>
          <li>VoIP telephone systems, toll-free, and e-faxing</li>
          <li>Server setup, maintenance, and troubleshooting</li>
          <li>Firewall installation and administration</li>
          <li>Employee adds, moves, and changes</li>
        </ul>
      </div>
      <div class="col">
        <h3>Business Application Selection</h3>
        <ul>
          <li>iPhone, iPad, and Android applications</li>
          <li>Microsoft Office applications</li>
          <li>Medical billing (practice management) and electronic health records (EHR)</li>
          <li>HIPAA, Meaningful Use, and ePrescribing</li>
          <li>Medical transcription</li>
          <li>Messaging, email, and contacts</li>
          <li>Customer relationship management (CRM)</li>
          <li>Enterprise warehousing &mdash; ERP (pick, pack, and ship)</li>
          <li>Image acquisition and storage solutions</li>
          <li>Inbound and outbound electronic faxing</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <article class="prose">
      <h2>On-site IT person</h2>
      <p>Whether you need a specialized IT person in your building for a large project or a set
      number of hours per week, we&rsquo;ve got you covered. Our knowledgeable staff is
      available for on-site IT services that fit your schedule and your budget.</p>
      <p><em>An affordable way to have an &ldquo;IT person&rdquo; on staff.</em></p>
    </article>
  </div>
</section>

<section class="cta-band">
  <div class="container">
    <h2>Want a second opinion on your IT setup?</h2>
    <p>We&rsquo;ll walk through what you have, where it&rsquo;s costing you, and what we&rsquo;d do differently. No pressure, no commitment.</p>
    <p style="margin-top:24px;"><a class="btn" href="contact-us.html">Schedule a consultation</a></p>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

VOIP_BODY = """
<section class="section">
  <div class="container">
    <article class="prose">
      <p>SDE Tech is a provider of VoIP systems for businesses both large and small. Using the
      latest in Internet Protocol phone systems and top-of-the-line phones, we deliver the
      features below &mdash; and many more &mdash; for less than your traditional phone system,
      with better call quality and clarity.</p>
      <p>VoIP telephone systems give you the flexibility to use different types of phones from
      practically anywhere, including home and remote offices. You can cancel your expensive
      legacy lines and use a simple, pay-as-you-go SIP trunk that runs over your existing
      high-speed internet, often saving hundreds of dollars per month.</p>
    </article>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <h2 style="text-align:center;">Connect.</h2>
    <p class="muted" style="text-align:center;max-width:640px;margin:0 auto 16px;">Reach the right people, the first time.</p>
    <ul style="max-width:640px;margin:0 auto;">
      <li>Queues for sales and customer service</li>
      <li>Intercom and paging options</li>
      <li>Custom ring groups and timing</li>
      <li>Auto attendant / digital receptionist</li>
    </ul>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 style="text-align:center;">Communicate.</h2>
    <p class="muted" style="text-align:center;max-width:640px;margin:0 auto 16px;">See what&rsquo;s happening across your team at a glance.</p>
    <ul style="max-width:640px;margin:0 auto;">
      <li>Co-worker availability at a glance</li>
      <li>Instant messaging via dashboard</li>
      <li>Screen pops with caller information</li>
      <li>Digital voicemail integrated with email</li>
    </ul>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <h2 style="text-align:center;">Collaborate.</h2>
    <p class="muted" style="text-align:center;max-width:640px;margin:0 auto 16px;">Connect branch offices and remote staff like one team.</p>
    <ul style="max-width:640px;margin:0 auto;">
      <li>Seamless remote capabilities</li>
      <li>Connecting branch locations as one</li>
      <li>Video conferencing options</li>
      <li>Web-based user portal for easy access</li>
    </ul>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 style="text-align:center;">Cultivate.</h2>
    <p class="muted" style="text-align:center;max-width:640px;margin:0 auto 16px;">Coach your team using the calls they&rsquo;re actually making.</p>
    <ul style="max-width:640px;margin:0 auto;">
      <li>Variety of training tools</li>
      <li>Call recording for training access</li>
      <li>Whisper, listen, and barge options</li>
      <li>Management call monitoring access</li>
    </ul>
  </div>
</section>

<section class="cta-band">
  <div class="container">
    <h2>Ready to retire your old phone bill?</h2>
    <p>We&rsquo;ll quote a 3CX phone system sized for your team and walk you through what it would replace.</p>
    <p style="margin-top:24px;"><a class="btn" href="contact-us.html">Get a VoIP quote</a></p>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

WEB_BODY = """
<section class="section">
  <div class="container">
    <article class="prose">
      <p><strong>Websites have become the new first impression.</strong></p>
      <p>When you hear about &mdash; or look for &mdash; a product or service, where does your
      research start? <strong>The internet.</strong></p>
      <p>At SDE Tech we understand the need for a cohesive digital footprint: a clean, clear,
      and concise website paired with social media and print design that helps your potential
      customer spot your brand. We&rsquo;ll work with you side by side to achieve your vision
      and grow your internet presence.</p>
    </article>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <h2 style="text-align:center;margin-bottom:8px;">Aspects of our website design and development</h2>
    <div class="col-grid" style="grid-template-columns:repeat(2,1fr);max-width:880px;margin:32px auto 0;">
      <div class="col">
        <h3>Domain / Host</h3>
        <p>You own your domains &mdash; we&rsquo;ll help configure them. We can also host your
        website at a low monthly cost, ensuring your site is up, running, and available to
        your clients at all times.</p>
      </div>
      <div class="col">
        <h3>Develop</h3>
        <p>Once the design is complete we develop the site from header to footer. We can
        integrate with your current applications and build interactive forms.</p>
      </div>
      <div class="col">
        <h3>Design</h3>
        <p>We design clean, easy-to-read sites that reflect your brand image, using high-quality
        photos and video to catch your readers&rsquo; eye.</p>
      </div>
      <div class="col">
        <h3>SEO / SMO</h3>
        <p>On-page SEO basics are included in our website packages. We can also implement a
        full Search Engine Optimization plan that leverages every channel leading back to
        your site.</p>
      </div>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="container">
    <h2>Need a website you&rsquo;re not embarrassed to share?</h2>
    <p>Send us your current site (or what you have so far). We&rsquo;ll tell you what&rsquo;s working, what&rsquo;s costing you customers, and what we&rsquo;d build instead.</p>
    <p style="margin-top:24px;"><a class="btn" href="contact-us.html">Start a website project</a></p>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

SOFTWARE_BODY = """
<section class="section">
  <div class="container">
    <article class="prose">
      <h2 style="margin-top:0;">Custom software</h2>
      <p>Looking for an edge over your competition or a more efficient way to run your
      business? The answer is custom software. Why use something that was produced for the
      masses when you can have something that is tailored specifically to your company and
      the way you run it? With custom software development you stay in control, and the
      system is built around what you have in place as a successful business owner. From
      medical offices to flower shops, we have worked with all types of companies to put them
      in the driver&rsquo;s seat.</p>
    </article>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <h2 style="text-align:center;margin-top:0;">How it works</h2>
    <div class="steps">
      <div class="step">
        <span class="step-num">Step 1</span>
        <h3>Brainstorm</h3>
        <p>We&rsquo;ll sit down with you and go through your day-to-day pain points, procedures,
        and ideas. Tell us what you need and we&rsquo;ll figure out how to make it happen. Don&rsquo;t
        hesitate to describe your dream system &mdash; chances are we can build it.</p>
      </div>
      <div class="step">
        <span class="step-num">Step 2</span>
        <h3>Research</h3>
        <p>We research what you&rsquo;re looking for and the best way to deliver it. Coming
        into your office and watching your team&rsquo;s daily procedures hands-on helps us
        understand your workflow and often surfaces features you hadn&rsquo;t considered.</p>
      </div>
      <div class="step">
        <span class="step-num">Step 3</span>
        <h3>Create</h3>
        <p>Once we have a comprehensive view of your ideas and business procedures we get to
        work building your custom system, keeping you involved and informed at every step.
        By the end you&rsquo;ll have a system built for your company and your company alone.</p>
      </div>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="container">
    <h2>Got a process that no off-the-shelf tool quite fits?</h2>
    <p>That&rsquo;s the conversation we want to have. Tell us how your business actually runs and we&rsquo;ll sketch what a custom system would look like.</p>
    <p style="margin-top:24px;"><a class="btn" href="contact-us.html">Discuss a software project</a></p>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

AI_AUTOMATION_BODY = """
<section class="section">
  <div class="container">
    <article class="prose">
      <p>Everyone&rsquo;s talking about AI. We&rsquo;re busy building it. SDE Tech designs
      and ships practical AI tools that handle real work for real businesses &mdash; the
      same way we&rsquo;ve built production software for two decades. No hype, no science
      projects. Just automation that earns its keep.</p>
    </article>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <h2 style="text-align:center;margin-top:0;">What we build</h2>
    <div class="col-grid" style="grid-template-columns:repeat(2,1fr);max-width:880px;margin:32px auto 0;">
      <div class="col">
        <h3>Customer messaging assistants</h3>
        <p>AI that answers, qualifies, and books over text and web chat, so leads don&rsquo;t slip through the cracks.</p>
      </div>
      <div class="col">
        <h3>Workflow automation</h3>
        <p>Take the repetitive steps out of your day &mdash; data entry, scheduling, follow-ups, reporting &mdash; and let software handle them.</p>
      </div>
      <div class="col">
        <h3>Document &amp; data processing</h3>
        <p>Pull structure out of invoices, forms, records, and email so your team stops copying and pasting.</p>
      </div>
      <div class="col">
        <h3>Custom AI agents</h3>
        <p>Purpose-built assistants trained on how your business actually works, connected to the tools you already use.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <article class="prose">
      <h2>How we work</h2>
      <p>We start by understanding what actually slows your business down &mdash; then we
      tell you where AI helps and, just as honestly, where it doesn&rsquo;t. We build it,
      put it in production, and maintain it. One local team owns the whole thing, start to
      finish.</p>

      <h2>Why SDE Tech</h2>
      <p>We&rsquo;ve been shipping production software since before &ldquo;AI&rdquo; was a
      marketing word. We know the difference between a flashy demo and a system you can
      actually run your business on. And when you need us, you&rsquo;re calling a Sarasota
      number and getting a straight answer.</p>
    </article>
  </div>
</section>

<section class="cta-band">
  <div class="container">
    <h2>Curious where AI could help?</h2>
    <p>Tell us what your business runs on today. We&rsquo;ll tell you where AI would make a real difference &mdash; and where it wouldn&rsquo;t.</p>
    <p style="margin-top:24px;"><a class="btn" href="contact-us.html">Contact us today</a></p>
  </div>
</section>
"""

# ---------------------------------------------------------------------------
# Compliance pages
# ---------------------------------------------------------------------------

PRIVACY_BODY = f"""
<section class="legal">
  <div class="container">
    <article>
      <p class="updated">Last updated: {LAST_UPDATED}</p>

      <p>This Privacy Policy describes how SDE Tech LLC (&ldquo;SDE Tech,&rdquo;
      &ldquo;we,&rdquo; or &ldquo;us&rdquo;) collects, uses, and protects information you
      provide when you visit <a href="https://sde-tech.com">sde-tech.com</a> or otherwise
      interact with our business.</p>

      <h2>1. Information we collect</h2>
      <p>We collect only the information you choose to provide, including:</p>
      <ul>
        <li><strong>Contact information</strong> &mdash; name, company, email address, phone
        number, and mailing address that you submit through our contact form, by email, or
        by phone.</li>
        <li><strong>Inquiry details</strong> &mdash; the contents of your message and the
        service area you&rsquo;re asking about.</li>
        <li><strong>Basic web logs</strong> &mdash; standard server logs (IP address,
        browser type, pages visited, timestamp) used for site reliability and security.</li>
      </ul>
      <p>We do not use third-party advertising trackers or behavioral retargeting cookies on
      this website.</p>

      <h2>2. How we use your information</h2>
      <p>We use the information you provide solely to:</p>
      <ul>
        <li>Respond to your inquiry and provide the services you have requested.</li>
        <li>Schedule appointments, send support ticket updates, and send service-related
        announcements.</li>
        <li>Maintain records required to operate our business, comply with applicable law,
        and resolve disputes.</li>
      </ul>

      <h2>3. SMS / text messaging data</h2>
      <p>If you provide a mobile phone number, you may receive text messages from SDE Tech
      relating to your service inquiry, appointment scheduling, support ticket updates, or
      service announcements. <strong>Phone numbers and SMS opt-in data are never shared with
      third parties for marketing purposes.</strong> See our
      <a href="sms-messaging-policy.html">SMS Messaging Policy</a> for opt-in, opt-out, and
      message-frequency details.</p>

      <h2>4. How we share your information</h2>
      <p>We do not sell, rent, or trade your personal information. We share information only
      as needed with:</p>
      <ul>
        <li>Service providers we use to operate our business (for example, email and
        hosting providers), under contractual confidentiality obligations.</li>
        <li>Law enforcement or other parties when required by a valid legal process.</li>
      </ul>

      <h2>5. Data retention</h2>
      <p>We keep your information only as long as needed to fulfill the purposes described
      in this policy or as required by law. You may ask us to delete your information at
      any time by emailing <a href="mailto:info@sde-tech.com">info@sde-tech.com</a>.</p>

      <h2>6. Security</h2>
      <p>We use reasonable administrative, technical, and physical safeguards to protect the
      information you provide. No method of transmission over the internet is 100&#37;
      secure, but we work to follow current best practices.</p>

      <h2>7. Children&rsquo;s privacy</h2>
      <p>Our services are intended for businesses and adult professionals. We do not
      knowingly collect personal information from anyone under 18.</p>

      <h2>8. Your choices</h2>
      <p>You may opt out of SMS messages at any time by replying <strong>STOP</strong> to
      any text message we send. You may opt out of email contact by replying to any email
      from us or by emailing <a href="mailto:info@sde-tech.com">info@sde-tech.com</a>.</p>

      <h2>9. Changes to this policy</h2>
      <p>We may update this policy from time to time. The &ldquo;Last updated&rdquo; date
      above will reflect the most recent revision.</p>

      <h2>10. Contact us</h2>
      <p>Questions about this Privacy Policy or about your data:<br>
      SDE Tech LLC<br>
      2912 Bee Ridge Road, Sarasota, FL 34239<br>
      <a href="mailto:info@sde-tech.com">info@sde-tech.com</a><br>
      866-371-2265</p>
    </article>
  </div>
</section>
"""

TOS_BODY = f"""
<section class="legal">
  <div class="container">
    <article>
      <p class="updated">Last updated: {LAST_UPDATED}</p>

      <p>These Terms of Service (&ldquo;Terms&rdquo;) govern your access to the website at
      <a href="https://sde-tech.com">sde-tech.com</a> (the &ldquo;Site&rdquo;) and any
      services provided by SDE Tech LLC (&ldquo;SDE Tech,&rdquo; &ldquo;we,&rdquo; or
      &ldquo;us&rdquo;). By using the Site or engaging our services, you agree to these
      Terms.</p>

      <h2>1. About SDE Tech</h2>
      <p>SDE Tech LLC is a Florida limited liability company providing IT consulting,
      managed network services, VoIP phone systems, website services, and custom software
      development to business clients.</p>

      <h2>2. Use of the Site</h2>
      <p>You may use the Site for lawful, informational purposes. You agree not to:</p>
      <ul>
        <li>Use the Site in a way that could damage, disable, or impair its operation.</li>
        <li>Attempt to gain unauthorized access to any portion of the Site or its
        underlying systems.</li>
        <li>Use automated tools to scrape, index, or harvest content beyond standard,
        well-behaved search engine indexing.</li>
      </ul>

      <h2>3. Services and engagements</h2>
      <p>Specific terms for engagements (project scope, fees, deliverables, payment terms,
      and confidentiality) are set out in the proposal or service agreement signed by you
      and SDE Tech. Where those documents conflict with these Terms, the signed agreement
      controls for that engagement.</p>

      <h2>4. Service availability</h2>
      <p>We strive to keep the Site available at all times but do not guarantee uninterrupted
      access. The Site may be temporarily unavailable for maintenance, upgrades, or factors
      outside our reasonable control. Service-level commitments for managed-service
      engagements, where applicable, are defined in the relevant service agreement.</p>

      <h2>5. Third-party links</h2>
      <p>The Site may link to third-party websites for convenience. We do not control and
      are not responsible for the content, policies, or practices of those sites.</p>

      <h2>6. Intellectual property</h2>
      <p>All content on the Site &mdash; including text, graphics, logos, and the SDE Tech
      name &mdash; is owned by SDE Tech or its licensors and is protected by U.S.
      intellectual property law. You may not reproduce, distribute, or create derivative
      works without our prior written permission, except as expressly permitted under these
      Terms or applicable law.</p>

      <h2>7. Disclaimer of warranties</h2>
      <p>The Site is provided on an &ldquo;as is&rdquo; and &ldquo;as available&rdquo; basis.
      To the fullest extent permitted by law, SDE Tech disclaims all warranties, whether
      express or implied, including warranties of merchantability, fitness for a particular
      purpose, and non-infringement, with respect to information published on the Site.</p>

      <h2>8. Limitation of liability</h2>
      <p>To the fullest extent permitted by law, SDE Tech and its owners, employees, and
      contractors shall not be liable for any indirect, incidental, special, consequential,
      or punitive damages, or for any loss of profits, revenues, data, or goodwill arising
      out of or in connection with your use of the Site. Liability for any direct damages
      arising from a paid engagement shall not exceed the fees paid to SDE Tech for the
      services that gave rise to the claim during the three (3) months preceding the
      claim.</p>

      <h2>9. Indemnification</h2>
      <p>You agree to indemnify and hold SDE Tech harmless from any claim arising out of
      your breach of these Terms or your misuse of the Site.</p>

      <h2>10. Governing law and venue</h2>
      <p>These Terms are governed by the laws of the State of Florida, without regard to
      its conflict-of-laws principles. Any dispute arising under these Terms shall be
      brought exclusively in the state or federal courts located in Sarasota County,
      Florida, and you consent to the personal jurisdiction of those courts.</p>

      <h2>11. Changes to these Terms</h2>
      <p>We may update these Terms from time to time. The &ldquo;Last updated&rdquo; date
      above will reflect the most recent revision. Continued use of the Site after a
      revision constitutes acceptance of the updated Terms.</p>

      <h2>12. Contact</h2>
      <p>SDE Tech LLC<br>
      2912 Bee Ridge Road, Sarasota, FL 34239<br>
      <a href="mailto:info@sde-tech.com">info@sde-tech.com</a><br>
      866-371-2265</p>
    </article>
  </div>
</section>
"""

SMS_BODY = f"""
<section class="legal">
  <div class="container">
    <article>
      <p class="updated">Last updated: {LAST_UPDATED}</p>

      <h2 style="margin-top:0;">About SDE Tech</h2>
      <p>SDE Tech LLC is an IT consulting and services company based in Sarasota, Florida.
      We provide managed IT services, VoIP phone systems, website services, and custom
      software development to business clients.</p>

      <h2>What messages you can expect</h2>
      <p>If you provide your mobile phone number to SDE Tech &mdash; through our website
      contact form, by email, or by phone &mdash; you may receive SMS (text) messages from
      us related to your interaction with our business. Examples include:</p>
      <ul>
        <li>Responses to a service inquiry you submitted.</li>
        <li>Appointment scheduling, confirmations, and reminders.</li>
        <li>Support ticket updates and resolution notices.</li>
        <li>Service announcements relevant to your account (for example, scheduled
        maintenance windows for managed-service clients).</li>
      </ul>

      <h2>Consent (opt-in)</h2>
      <p><strong>By providing your phone number, you consent to receive SMS messages from
      SDE Tech regarding your service inquiry, appointment scheduling, support ticket
      updates, or service announcements.</strong> Consent is not required as a condition of
      purchasing any goods or services.</p>

      <h2>Opt-out</h2>
      <p><strong>Reply STOP at any time to unsubscribe.</strong> Once you reply STOP, we
      will send a single confirmation message and you will not receive further SMS messages
      from SDE Tech unless you opt back in. Reply <strong>HELP</strong> for help, or contact
      us at <a href="mailto:info@sde-tech.com">info@sde-tech.com</a> or 866-371-2265.</p>

      <h2>Message frequency</h2>
      <p>Message frequency varies based on your inquiry. Typical interactions involve a
      handful of messages over the course of a single conversation; managed-service clients
      may receive occasional service announcements.</p>

      <h2>Cost</h2>
      <p>Message and data rates may apply. Check with your mobile carrier for details on
      your plan.</p>

      <h2>Privacy</h2>
      <p>We do not share your phone number with third parties for marketing or any other
      purpose unrelated to delivering the service you requested. SMS opt-in data, including
      phone numbers and consent records, is not shared with third parties. See our
      <a href="privacy-policy.html">Privacy Policy</a> for full details on how we handle
      your information.</p>

      <h2>Supported carriers</h2>
      <p>SDE Tech&rsquo;s SMS messaging supports the major U.S. mobile carriers, including
      AT&amp;T, Verizon Wireless, T-Mobile, Sprint, U.S. Cellular, Boost Mobile, Cricket
      Wireless, MetroPCS, Virgin Mobile, and most regional carriers operating on those
      networks. Carriers are not liable for delayed or undelivered messages.</p>

      <h2>Eligibility</h2>
      <p>You must be at least 18 years old, or have authority to act on behalf of a
      business, to consent to receive SMS messages from SDE Tech.</p>

      <h2>Changes to this policy</h2>
      <p>We may update this SMS Messaging Policy from time to time. The &ldquo;Last
      updated&rdquo; date above will reflect the most recent revision. Material changes
      affecting your prior consent will be communicated before they take effect.</p>

      <h2>Questions</h2>
      <p>For questions about SDE Tech&rsquo;s SMS messaging program, contact:<br>
      SDE Tech LLC<br>
      <a href="mailto:info@sde-tech.com">info@sde-tech.com</a><br>
      866-371-2265<br>
      2912 Bee Ridge Road, Sarasota, FL 34239</p>
    </article>
  </div>
</section>
"""

# ---------------------------------------------------------------------------

PAGES = [
    {
        "slug": "index",
        "title": "SDE Tech &mdash; IT, Phones, Websites &amp; Software in Sarasota, FL",
        "description": "SDE Tech is a Sarasota, Florida IT services company providing managed IT, 3CX VoIP phone systems, website services, and custom software development to small and mid-size businesses.",
        "active_key": "home",
        "hero": True,
        "body": HOME_HERO + HOME_TILES + HOME_ABOUT_TEASER + HOME_CTA,
    },
    {
        "slug": "about-us",
        "title": "About SDE Tech",
        "description": "SDE Tech is owned by Dan Steiner and Steve Johnson and brings over 20 years of IT experience to small and mid-size businesses across Sarasota and the Gulf Coast.",
        "breadcrumb": "About",
        "body": ABOUT_BODY,
    },
    {
        "slug": "team-leaders",
        "title": "Our Team Leaders",
        "description": "Meet the team leaders behind SDE Tech &mdash; the people running your IT, phone, website, and software projects in Sarasota.",
        "active_key": "about",
        "breadcrumb": '<a href="about-us.html">About</a> &rsaquo; Team Leaders',
        "body": TEAM_BODY,
    },
    {
        "slug": "contact-us",
        "title": "Contact SDE Tech",
        "description": "Reach SDE Tech in Sarasota, Florida. Phone 866-371-2265, email info@sde-tech.com, or send a message through our contact form.",
        "active_key": "contact",
        "breadcrumb": "Contact",
        "body": CONTACT_BODY,
    },
    {
        "slug": "it-services",
        "title": "IT Services",
        "description": "Managed network services, on-site IT support, and business application selection for Sarasota-area small and mid-size businesses.",
        "breadcrumb": "IT Services",
        "body": IT_BODY,
    },
    {
        "slug": "voip-phones",
        "title": "VoIP Phones",
        "description": "3CX-certified VoIP phone systems for businesses &mdash; better call quality, more features, and lower monthly cost than traditional phone lines.",
        "breadcrumb": "VoIP Phones",
        "body": VOIP_BODY,
    },
    {
        "slug": "website-services",
        "title": "Website Services",
        "description": "Website design, development, hosting, and SEO for Sarasota-area businesses. Clean, fast, mobile-ready sites that customers can find and read on any device.",
        "breadcrumb": "Website Services",
        "body": WEB_BODY,
    },
    {
        "slug": "software-development",
        "title": "Software Development",
        "description": "Custom software development for businesses that have outgrown off-the-shelf tools. Built around how your company actually runs.",
        "breadcrumb": "Software Development",
        "body": SOFTWARE_BODY,
    },
    {
        "slug": "ai-automation",
        "title": "AI &amp; Automation | SDE Tech | Sarasota, FL",
        "page_h1": "AI &amp; Automation",
        "description": "SDE Tech builds practical AI agents and workflow automation for small and mid-size businesses &mdash; customer messaging, document processing, and custom AI tools, built and maintained by a local Sarasota team.",
        "breadcrumb": "AI &amp; Automation",
        "body": AI_AUTOMATION_BODY,
    },
    {
        "slug": "privacy-policy",
        "title": "Privacy Policy",
        "description": "How SDE Tech LLC collects, uses, and protects the information you provide. Includes our data-handling practices for SMS messaging.",
        "active_key": "",
        "breadcrumb": "Privacy Policy",
        "body": PRIVACY_BODY,
    },
    {
        "slug": "terms-of-service",
        "title": "Terms of Service",
        "description": "Terms of Service for SDE Tech LLC and the sde-tech.com website. Governed by the laws of the State of Florida.",
        "active_key": "",
        "breadcrumb": "Terms of Service",
        "body": TOS_BODY,
    },
    {
        "slug": "sms-messaging-policy",
        "title": "SMS Messaging Policy",
        "description": "How SDE Tech&rsquo;s SMS messaging works: opt-in, opt-out, message frequency, cost, supported carriers, and privacy.",
        "active_key": "",
        "breadcrumb": "SMS Messaging Policy",
        "body": SMS_BODY,
    },
]


def write_sitemap():
    from datetime import date as _date
    today = _date.today().isoformat()
    urls = []
    for p in PAGES:
        loc = "https://sde-tech.com/" if p["slug"] == "index" else f"https://sde-tech.com/{p['slug']}.html"
        priority = "1.0" if p["slug"] == "index" else "0.8"
        urls.append(
            f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{priority}</priority>\n  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n"
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def build():
    os.makedirs(OUT, exist_ok=True)
    written = []
    for p in PAGES:
        html = render(
            slug=p["slug"],
            title=p["title"],
            description=p["description"],
            body=p["body"],
            active_key=p.get("active_key", p["slug"]),
            hero=p.get("hero", False),
            breadcrumb=p.get("breadcrumb"),
            page_h1=p.get("page_h1"),
        )
        path = os.path.join(OUT, f"{p['slug']}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        written.append((p["slug"], len(html)))

    write_sitemap()

    # Word-count summary (visible text only).
    print(f"{'page':<26}{'bytes':>8}  words")
    for slug, size in written:
        with open(os.path.join(OUT, f"{slug}.html"), "r", encoding="utf-8") as f:
            html = f.read()
        text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&[a-zA-Z]+;", " ", text)
        words = len(text.split())
        print(f"{slug:<26}{size:>8}  {words}")
    print(f"\nWrote {len(written)} pages + sitemap.xml")


if __name__ == "__main__":
    build()
