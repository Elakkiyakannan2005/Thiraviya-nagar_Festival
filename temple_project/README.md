# Thiraviya Nagar Temple Festival — Django Edition

Your original static site (`index.html` / `style.css` / `style.js`) converted into a
full Django project, plus scroll/entrance animations layered on top of the same design.

## What changed from the static version

| Static site | Django version |
|---|---|
| Hardcoded festival date / schedule text | `FestivalInfo` + `ScheduleItem` models, editable at `/admin/` |
| Hardcoded 3 gallery items | `GalleryItem` model — add/remove/reorder photos & videos from `/admin/` |
| Donation form just showed a JS alert, saved nothing | `Donation` model — every submission is saved to the database, viewable at `/admin/` |
| No animations beyond a basic fade | Staggered hero entrance, floating petals/diyas, scroll-triggered reveals, animated "raised so far" counters, pulsing CTA button, hover/underline effects |

Your original three visuals (`amman.png`, `sudalai.png`, `amman_kovil.mp4`) are preserved as
seeded gallery items, and `pongal.mp4` (uploaded but unused in the original site) has been
added as a fourth gallery entry — remove or edit it anytime from the admin.

## Project layout

```
temple_project/
├── manage.py
├── requirements.txt
├── temple_project/          # project settings, root urls
└── festival/                 # the app
    ├── models.py             # FestivalInfo, ScheduleItem, GalleryItem, Donation
    ├── forms.py               # DonationForm
    ├── views.py                # index page, /donate/ JSON endpoint, receipt PDF endpoint
    ├── admin.py                # admin registrations + receipts + donors summary
    ├── receipts.py              # generates the donation receipt/bill PDF (reportlab)
    ├── fonts/                    # bundled DejaVu Sans font (so ₹ renders in PDFs)
    ├── migrations/
    │   └── 0002_seed_initial_data.py   # auto-loads your original images/videos into gallery
    ├── templates/
    │   ├── festival/index.html
    │   └── admin/festival/       # admin template overrides (donors summary button/page)
    └── static/festival/
        ├── css/style.css        # your original CSS, untouched
        ├── css/animations.css   # new: all the animation rules
        ├── js/style.js           # updated: talks to the Django backend + animations
        └── media/                 # your original assets (source copies)
```

## Setup

> **Already had this project running before?** Just re-run
> `pip install -r requirements.txt` (for the two new PDF libraries) and
> `python manage.py migrate` (for the new receipt fields) — everything else below
> is for a brand-new setup.

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations (this also seeds your festival schedule + gallery
#    from the bundled images/videos automatically)
python manage.py migrate

# 4. Create an admin account
python manage.py createsuperuser

# 5. Run the dev server
python manage.py runserver
```

Then open:
- **http://127.0.0.1:8000/** — the site
- **http://127.0.0.1:8000/admin/** — manage festival date, schedule, gallery, and view donations

## Editing content (no code required)

Log into `/admin/` and you can:
- **Festival Info** — set the real festival date, an announcement line, and the schedule text per time slot.
- **Schedule Items** — add/reorder multiple programs per time slot (morning/afternoon/evening).
- **Gallery Items** — upload new photos/videos, reorder them, unpublish without deleting.
- **Donations** — see every submitted donation (name, mobile, address, amount, timestamp).

## About the donation form

The form now **saves real records to the database** via `POST /donate/` (handled in
`festival/views.py`). It is still a **demo donation** — there is no payment gateway wired
in, so no money actually moves. To take real payments, integrate a gateway such as
Razorpay, Cashfree, or PayU inside `donate()` in `festival/views.py`:

1. On form submit, create a `Donation` row with `is_demo=False` only after the gateway
   confirms payment (use its webhook/callback, not just the client-side response).
2. Add the gateway's checkout JS to `style.js` and swap the "Continue Demo Donation"
   button flow to open its checkout instead of finishing instantly.

## Donation receipts (bills) + Donors admin

Every donation now gets a **PDF receipt/bill**, generated on the fly (nothing stored on disk):

- After a successful donation, the site shows a **"Download Receipt"** button that opens the PDF.
- The receipt includes a receipt number (e.g. `TNF-000007`), date, donor name/mobile/address,
  and the amount — with your temple's name, address, phone, email and PAN (if set) as the
  letterhead. Set these from **Admin → Festival Info → Receipt letterhead**.
- Since no payment gateway is connected yet, every receipt is currently marked as a
  **provisional/demo acknowledgement** (a red notice on the PDF says so) — this stops it from
  being mistaken for a real payment or tax receipt. Once you wire in a real gateway (see the
  section above) and set `is_demo=False` on paid donations, that notice disappears automatically.
- Each receipt's link uses a random ID (not the donation's plain row number), so one donor
  can't guess another donor's receipt URL.

**In `/admin/` → Donations**, you can now:
- See amount, date, and a **View/Download** link for each donation's bill, right in the list.
- **Search** by name, mobile, or address, and filter/drill down by date.
- **Select multiple donations → Actions → "Download bill (PDF) for selected donations"** to get
  one merged PDF with every selected receipt (handy for printing a batch).
- Click **"View Donors Summary"** at the top of the Donations list to see donors grouped
  together — total amount given, number of donations, and their last donation date, sorted by
  top donor first.



- Hero text/buttons fade & rise in on load, staggered.
- Floating petal/diya emoji drifting up behind the hero video.
- Gentle pulse glow on the "Support the Festival" button.
- Scroll-triggered reveal (fade + rise) for festival cards, schedule, gallery items, and
  the donation form, using `IntersectionObserver` — each card/photo staggers slightly
  after the previous one.
- Navbar links get an animated underline on hover.
- Gallery photos lift with a soft shadow on hover; captions slide up.
- "₹ Raised so far" and "Donors" counters animate upward when scrolled into view, and again
  immediately after a successful donation.

All animations respect `prefers-reduced-motion` and are pure CSS/JS — no external libraries
or CDNs required.

## Deploying to Render (free live link)

This project is ready to deploy as-is. Push your latest code to GitHub first (you've
already done this), then:

1. **Create a free PostgreSQL database on Render** (skip this only if you're fine with
   data resetting on every redeploy):
   - Render dashboard → **New +** → **PostgreSQL** → give it a name → **Create Database**
   - Wait for it to finish provisioning, then copy its **Internal Database URL**.

2. **Create the web service:**
   - Render dashboard → **New +** → **Web Service** → connect your GitHub repo
     (`Thiraviya-nagar_Festival`)
   - **Runtime:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn temple_project.wsgi:application`

3. **Add environment variables** (Web Service → **Environment**):

   | Key | Value |
   |---|---|
   | `DJANGO_SECRET_KEY` | any long random string (don't reuse the one in settings.py) |
   | `DJANGO_DEBUG` | `False` |
   | `DATABASE_URL` | paste the Internal Database URL from step 1 (skip if not using Postgres) |

   `DJANGO_ALLOWED_HOSTS` and CSRF don't need manual setup — the app already reads
   Render's own `RENDER_EXTERNAL_HOSTNAME` variable automatically.

4. Click **Create Web Service**. Render will run `build.sh` (installs dependencies,
   collects static files, runs migrations) and then start the app. First deploy takes
   a few minutes — watch the **Logs** tab.

5. Once it's live, open the `.onrender.com` link Render gives you, then visit
   `/admin/` and create a superuser **from the Render Shell tab**:
   ```bash
   python manage.py createsuperuser
   ```
   (Render's free plan puts services to sleep after inactivity — the first request
   after a while takes ~30-60s to wake up, that's normal.)

**About file storage on Render's free tier:** the web service's own disk is *not*
persistent — anything written to it (including a SQLite database, or new gallery
photos/videos uploaded through `/admin/`) is wiped on every redeploy or restart. Using
the Postgres database from step 1 solves this for donations/schedule/festival-info
data. Gallery **media uploads** would still be lost on redeploy under this setup — fine
for the seeded demo gallery (it's re-copied on every `migrate`), but if you plan to
regularly add new photos/videos from the admin, add a Render persistent disk (paid,
cheap) or move media storage to something like Cloudinary/S3 (`django-storages`).

## Notes

- Media files (uploaded gallery photos/videos, including the seeded ones) are served from
  `/media/` in development. For production, configure your web server (Nginx/Apache) or a
  storage backend (e.g. `django-storages` + S3) to serve `MEDIA_ROOT`/`STATIC_ROOT` — Django's
  `runserver` is not meant for production traffic.
- Before deploying: set `DJANGO_DEBUG=False`, set a real `DJANGO_SECRET_KEY` env var, and set
  `DJANGO_ALLOWED_HOSTS` to your domain.
- Run `python manage.py collectstatic` before deploying so `STATIC_ROOT` is populated.
