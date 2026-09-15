# `d13.nycfirst.org` → Webflow `/d13` Page

## Goal

Serve the existing Webflow D13 page at:

`https://d13.nycfirst.org`

while keeping **`d13.nycfirst.org` visible in the browser address bar**.

The organization's existing `nycfirst.org` DNS, GoDaddy account, email records, and main Webflow site should remain unchanged.

---

## Important finding

Webflow does **not** support publishing one page to one custom domain/subdomain. A custom domain is connected at the **site level**, not the page level.

Therefore:

```text
d13.nycfirst.org → Webflow site
```

is supported, but:

```text
d13.nycfirst.org → only Webflow /d13
```

is not supported natively.

A normal Webflow redirect also does not satisfy the requirement because it changes the browser URL to something like:

```text
nycfirst.org/d13
```

Webflow's documented solution for this type of routing is a **self-managed reverse proxy**.

---

# Cost / DNS constraint

## Requirement

- Additional cost: **$0**
- Keep GoDaddy as the organization's DNS provider
- Do not migrate the organization's entire DNS zone
- Keep `d13.nycfirst.org` in the address bar

### Important caveat

A Cloudflare Worker is a good free reverse-proxy technology, but attaching a custom hostname to a Worker normally requires Cloudflare to control/proxy the DNS zone for that hostname.

Therefore, **do not assume that creating a free Cloudflare account and adding a CNAME at GoDaddy will be enough**.

Cloudflare's current documentation distinguishes between:
- full DNS setup, where Cloudflare becomes authoritative for the domain
- partial/subdomain setups, which have plan/product restrictions

Because this is an organization's domain, do **not** migrate the whole domain to Cloudflare just for D13 without approval.

---

# Recommended next step

Before making any DNS changes, verify which of these two architectures is acceptable.

## Option A — Organization is willing to move DNS to Cloudflare

This can be done at $0 for a small site using the Cloudflare Free plan + Workers, but it means moving the authoritative DNS for `nycfirst.org` from GoDaddy to Cloudflare.

The domain registration can remain at GoDaddy. Moving DNS does **not** mean transferring ownership of the domain.

Architecture:

```text
GoDaddy
  │
  │ domain registration
  ↓
Cloudflare DNS
  │
  ├── existing organization records
  ├── existing email records
  ├── www → existing Webflow setup
  │
  └── d13 → Cloudflare Worker
                    │
                    ↓
               Webflow origin
                    │
                    ↓
                  /d13
```

This is technically viable, but it is an **organization-wide DNS change** and therefore not my preferred option without authorization.

---

# Option B — Keep GoDaddy DNS completely authoritative

This is the preferred organizational architecture:

```text
GoDaddy
  │
  ├── www → unchanged
  ├── email → unchanged
  ├── everything else → unchanged
  │
  └── d13 → reverse-proxy service
                    │
                    ↓
               Webflow /d13
```

The challenge is finding a reverse-proxy provider that supports:

1. a custom hostname (`d13.nycfirst.org`)
2. HTTPS
3. path rewriting to Webflow `/d13`
4. keeping the original hostname in the browser
5. $0 cost
6. without requiring the entire `nycfirst.org` DNS zone to move

**Do not purchase anything or migrate DNS until this specific architecture is confirmed.**

---

# Webflow preparation

The Webflow side should use a dedicated **origin hostname** for the reverse proxy rather than relying on the public `d13.nycfirst.org` hostname.

For example:

```text
wf-origin.nycfirst.org
```

The purpose is:

```text
Public visitor:
d13.nycfirst.org
        ↓
Reverse proxy
        ↓
wf-origin.nycfirst.org/d13
        ↓
Webflow
```

Webflow's current self-managed reverse-proxy documentation recommends using a custom Webflow origin rather than proxying the site's `webflow.io` staging URL.

---

# Do not use this as the final setup

Do **not** make:

```text
d13.nycfirst.org
```

the Webflow site's default domain simply to try to make `/d13` appear.

That would make the domain represent the whole Webflow site rather than specifically the D13 page.

Also do not use:

```text
d13.nycfirst.org → 301/302 → nycfirst.org/d13
```

if keeping the subdomain in the browser is a requirement.

---

# If Cloudflare DNS migration is approved

## 1. Keep the domain registered at GoDaddy

There is no need to transfer the domain registration.

GoDaddy can remain the registrar.

## 2. Add `nycfirst.org` to Cloudflare

Create a Cloudflare account and add the domain.

Cloudflare will import the existing DNS records.

**Do not delete the GoDaddy DNS configuration yet.**

## 3. Carefully compare DNS records

Before changing nameservers, verify that Cloudflare has all important records, especially:

- A records
- CNAME records
- MX records
- TXT records
- SPF
- DKIM
- DMARC
- any verification records
- any records used by the existing website

Email records are particularly important.

## 4. Change nameservers only after verification

At GoDaddy, replace the existing authoritative nameservers with the Cloudflare nameservers Cloudflare provides.

This changes who answers DNS queries; it does not transfer the domain registration.

## 5. Create the Worker

A Worker can inspect the incoming hostname and request the appropriate Webflow page.

Conceptually:

```js
export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.hostname === "d13.nycfirst.org") {
      url.pathname = "/d13";
    }

    return fetch(url);
  }
};
```

**Do not deploy this exact code yet.**

The Worker needs to fetch the Webflow **origin hostname**, not simply fetch `d13.nycfirst.org`, or it can create a loop.

The final Worker should use the dedicated Webflow origin hostname and preserve the correct Host/origin behavior required by Webflow.

## 6. Configure the Worker custom domain

Attach:

```text
d13.nycfirst.org
```

to the Worker.

Cloudflare then handles HTTPS and routes the request to the Worker.

## 7. Test

Test:

```text
https://d13.nycfirst.org
```

Verify:

- D13 page loads
- browser still says `d13.nycfirst.org`
- images load
- CSS loads
- JavaScript loads
- links work
- Webflow forms work, if applicable
- other pages do not accidentally become the D13 page
- `nycfirst.org` remains unaffected

---

# Current status

Already completed:

- [x] Existing Webflow Business-level site
- [x] `d13.nycfirst.org` added to Webflow
- [x] `d13.nycfirst.org` verified
- [ ] Decide routing architecture
- [ ] Create Webflow origin hostname
- [ ] Configure reverse proxy
- [ ] Test D13 page
- [ ] Confirm no impact to main organization site

---

# Recommendation

Because this is an organization's production domain, **do not migrate the entire DNS structure to Cloudflare just to solve this one page unless the organization is comfortable with that change.**

The desired end state is:

```text
                 ┌─────────────────────────────┐
                 │       GoDaddy DNS           │
                 │                             │
                 │ nycfirst.org                │
                 │ www / email / other records │
                 │       unchanged             │
                 └──────────────┬──────────────┘
                                │
                         d13.nycfirst.org
                                │
                                ▼
                    ┌──────────────────────┐
                    │   Reverse Proxy      │
                    │   (HTTPS)            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Webflow        │
                    │   /d13 page          │
                    └──────────────────────┘

Browser remains:
https://d13.nycfirst.org
```

The key unresolved requirement is finding a **$0 reverse-proxy service that accepts only this subdomain while GoDaddy remains authoritative for the parent domain**. That should be verified before any production DNS changes.
