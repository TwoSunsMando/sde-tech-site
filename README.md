# SDE Tech &mdash; static site

Pure static HTML/CSS for [sde-tech.com](https://sde-tech.com). Served by
`nginx:alpine` behind Coolify on the team's DigitalOcean droplet
(`159.203.174.128`).

```
public/                pages, css, images — this is what nginx serves
raw/                   scraped HTML + markdown source-of-truth from the old WordPress site
build.py               optional generator: emits HTML into public/ from shared header/footer
scrape.py              one-time HTML→markdown scraper (kept for reference)
Dockerfile             FROM nginx:alpine, COPY public/, EXPOSE 80
```

## Local development

No build dependencies. To preview locally:

```bash
python3 -m http.server -d public 8000
# open http://localhost:8000/
```

Or with Docker:

```bash
docker build -t sde-tech .
docker run --rm -p 8080:80 sde-tech
# open http://localhost:8080/
```

`build.py` is a developer convenience that regenerates all HTML files from a
shared header/footer template. It's optional &mdash; you can also edit the
HTML files in `public/` directly. To regenerate after editing `build.py`:

```bash
python3 build.py
```

## Deploying to Coolify

1. **Push this repo to GitHub** (placeholder URL: `https://github.com/<org>/sde-tech-site`).
2. **Create a new Coolify resource** of type *Application*, source = this Git repo.
   - Build pack: **Dockerfile**
   - Dockerfile path: `./Dockerfile`
   - Port: `80`
   - Domain field: `https://sde-tech.com,https://www.sde-tech.com` (Coolify will issue Let's Encrypt certs for both).
3. **Update DNS at GoDaddy** &mdash; only touch the A records, leave MX and other records alone:
   - `@` &rarr; `159.203.174.128` (TTL 600)
   - `www` &rarr; `159.203.174.128` (TTL 600)
4. **Deploy** in Coolify. Watch the deploy log; nginx should report it's listening on port 80.
5. **Wait for DNS to propagate** (usually a few minutes; up to an hour worst case).

## Post-deploy verification checklist

- [ ] `https://sde-tech.com/` loads with a valid TLS cert.
- [ ] `https://www.sde-tech.com/` loads with a valid TLS cert and shows the same site.
- [ ] Homepage hero, four service tiles, and footer render correctly on desktop.
- [ ] Mobile menu (hamburger) opens and closes on a phone.
- [ ] All four service pages link from the homepage tiles.
- [ ] Footer links work: Privacy Policy, Terms of Service, SMS Messaging Policy.
- [ ] Contact form opens an email draft to `info@sde-tech.com`.
- [ ] Embedded Google Map on `/contact-us.html` shows the Bee Ridge Road office.
- [ ] Partner badges in the footer link to 3CX and the Manatee Chamber of Commerce.
- [ ] No broken images (especially the logo and partner badges).
- [ ] `mailto:` and `tel:` links work in the footer.

## Rollback

If anything goes wrong, the fastest rollback is to revert the GoDaddy A
records. The previous WordPress hosting IP is the rollback target &mdash;
update the `@` and `www` A records back to that IP and DNS will return to
the old site within minutes (subject to TTL).

You can also redeploy a previous Git commit from the Coolify deployments
panel.

## Site contents

| Page | Purpose |
|------|---------|
| `/` | Homepage &mdash; hero, four service tiles, about teaser, contact CTA |
| `/about-us.html` | About SDE Tech |
| `/contact-us.html` | Contact form, address, hours, embedded map |
| `/it-services.html` | IT services details |
| `/voip-phones.html` | 3CX VoIP phone systems |
| `/website-services.html` | Website design / development / hosting / SEO |
| `/software-development.html` | Custom software development |
| `/privacy-policy.html` | Privacy policy (10DLC compliance) |
| `/terms-of-service.html` | Terms of service |
| `/sms-messaging-policy.html` | **SMS messaging policy &mdash; required for 10DLC SMS approval** |

## What was intentionally dropped from the old site

- The "Add On Marketing &amp; SEO" page is gone &mdash; not built, not linked.
- The Twitter / X handle in the footer is gone (account hadn't been used in years).
- The Google+ link is gone (Google+ was shut down in 2019).
- The 12 stock photos referenced by the old site are not used; the new design
  is type-and-color-led with inline SVG icons.
