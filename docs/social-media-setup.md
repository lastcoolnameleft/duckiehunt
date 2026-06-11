# Social Media Posting Setup

This guide explains how to configure Duckiehunt to automatically post duck sightings to Facebook, Instagram, and LinkedIn.

## Facebook Page Setup

### Prerequisites
- A Facebook Page for Duckiehunt (or your project)
- A personal Facebook account that is an admin of that Page

### Step 1: Create a Meta App

1. Go to [developers.facebook.com/apps/create](https://developers.facebook.com/apps/create)
2. Enter an **App name** (e.g., `Duckiehunt`)
3. On "Use cases" select **"Authenticate and request data from users with Facebook Login"**
4. Skip the business portfolio ("I don't want to connect a business portfolio yet")
5. Click through Requirements and Overview, then **Create App**

### Step 2: Add Page Permissions to Your App

1. Go to your app's **Use cases** page (left sidebar)
2. Click **Customize** on the Facebook Login use case
3. Click **"Add more to this use case"** in the left panel
4. Find and add **`pages_manage_posts`** and **`pages_read_engagement`**

### Step 3: Get a Page Access Token

1. Go to **Tools → Graph API Explorer** ([developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer))
2. Select your app in the **Meta App** dropdown
3. Set **User or Page** to "Get User Access Token"
4. Add `pages_manage_posts` and `pages_read_engagement` to Permissions
5. Click **Generate Access Token** and authorize
6. Change the query to: `/me/accounts?fields=id,name,access_token`
7. Click **Submit**
8. Your Page's `access_token` is in the response JSON

If "Get Page Access Token" works in the dropdown, use that instead — it's more direct.

### Step 4: Find Your Page ID

Your Page ID is in the URL when you visit your Page:
```
https://www.facebook.com/profile.php?id=61590411966962
                                        ^^^^^^^^^^^^^^
                                        This is your Page ID
```

You can also find it in the `/me/accounts` response from Step 3.

### Step 5: Test It

```bash
# Post a text message to your Page
curl -X POST "https://graph.facebook.com/v25.0/YOUR_PAGE_ID/feed" \
  -d "message=Test post from Duckiehunt! 🦆" \
  -d "access_token=YOUR_PAGE_ACCESS_TOKEN"

# Post a photo to your Page
curl -X POST "https://graph.facebook.com/v25.0/YOUR_PAGE_ID/photos" \
  -d "url=https://your-domain.com/path/to/photo.jpg" \
  -d "caption=Duck #42 spotted at the park!" \
  -d "access_token=YOUR_PAGE_ACCESS_TOKEN"
```

A successful response looks like:
```json
{"id": "61590411966962_123456789"}
```

### Step 6: Configure Environment Variables

Add to your `.env` file (or server environment):

```bash
FB_PAGE_ID=61590411966962
FB_PAGE_ACCESS_TOKEN=EAAOAuj...your_token_here
```

### Token Expiration

Page Access Tokens obtained from a long-lived User Token typically **never expire** as long as:
- The user remains an admin of the Page
- The app isn't removed from the Page

To extend a short-lived token:
1. Go to [developers.facebook.com/tools/debug/accesstoken](https://developers.facebook.com/tools/debug/accesstoken)
2. Paste your token and click **Debug**
3. Click **Extend Access Token**

---

## Instagram Setup (Optional)

### Prerequisites
- An Instagram **Professional account** (Business or Creator — free to convert)
- The Instagram account linked to your Facebook Page

### Step 1: Convert to Professional Account

Instagram → Settings → Account → Switch to Professional Account → choose Creator or Business.

### Step 2: Get Instagram User ID and Token

1. In Graph API Explorer, query: `/me/accounts?fields=id,instagram_business_account`
2. The `instagram_business_account.id` is your **IG User ID**
3. Your Page Access Token works for Instagram too (same Meta ecosystem)

### Step 3: Configure Environment Variables

```bash
IG_USER_ID=your_instagram_user_id
IG_ACCESS_TOKEN=your_page_access_token
```

### Limitations
- Photos must be **JPEG** format
- Photos must be on a **publicly accessible URL** (Instagram's servers fetch from your URL)
- Rate limit: 100 posts per 24-hour window

---

## LinkedIn Setup (Optional)

### Prerequisites
- A LinkedIn account (for personal posting) or admin access to a LinkedIn Company Page
- A LinkedIn Developer app

### Step 1: Create a LinkedIn app

1. Go to [LinkedIn Developer Apps](https://www.linkedin.com/developers/apps)
2. Click **Create app**
3. Fill out app name, company page, and app logo
4. Create the app

### Step 2: Add products / scopes

In your app:
1. Open **Products**
2. Request/enable:
   - **Share on LinkedIn** (personal feed posting; scope `w_member_social`)
   - If posting to company page, also enable organization posting (`w_organization_social`)

### Step 3: Configure OAuth redirect URL

1. Open **Auth**
2. Under **OAuth 2.0 settings**, add the Duckiehunt admin callback URL:
   - `http://localhost:8042/admin/linkedin-token/callback`
   - If you already use `LI_REDIRECT_URI=http://localhost:8042/auth/linkedin/callback`, keep that URI registered too.
3. Save

### Step 4: Generate an access token (manual flow)

You can use OAuth 2.0 Authorization Code flow in your browser:

1. Build auth URL (replace placeholders):
   - `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http%3A%2F%2Flocalhost%3A8042%2Fauth%2Flinkedin%2Fcallback&scope=w_member_social%20openid%20profile%20email`
2. Open URL, approve permissions
3. Copy `code` from callback URL
4. Exchange code for token:

```bash
curl -X POST "https://www.linkedin.com/oauth/v2/accessToken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "redirect_uri=http://localhost:8042/auth/linkedin/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

LinkedIn access tokens typically expire in ~60 days.

### Step 4b: One-click refresh from Duckiehunt admin

After initial setup, use the built-in admin page:

1. Log in as a staff/admin user
2. Open `/admin/linkedin-token`
3. Click **Refresh LinkedIn Token**

Duckiehunt will update runtime env vars and write new values into the active env file (`ENV_FILE` when set, otherwise `.env`).
By default, the admin flow requests `w_member_social openid profile`.  
If your LinkedIn app is approved for refresh tokens, set `LI_SCOPES=w_member_social openid profile offline_access`.

### Optional: Use the automation script

If you already set `LI_CLIENT_ID`, `LI_CLIENT_SECRET`, and `LI_REDIRECT_URI` in your env file,
you can automate auth URL generation + token exchange:

```bash
./scripts/linkedin_oauth_setup.py --env-file .env --write-env
```

The script opens LinkedIn auth, exchanges the code, fetches userinfo (when permitted), and can write
`LI_ACCESS_TOKEN` / `LI_PERSON_URN` back into your env file.

To only run a LinkedIn posting smoke test using existing env vars:

```bash
./scripts/linkedin_oauth_setup.py --smoke-test-only
```

### Step 5: Get your posting URN

#### Personal feed (recommended)

```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  "https://api.linkedin.com/v2/userinfo"
```

Use `sub` from response to build:
- `LI_PERSON_URN=urn:li:person:SUB_VALUE`

#### Company page feed

Use your organization URN:
- `LI_ORGANIZATION_URN=urn:li:organization:123456`

You can also set:
- `LI_AUTHOR_URN=urn:li:person:...` or `urn:li:organization:...`

### Step 6: Configure environment variables

```bash
LI_ACCESS_TOKEN=your_linkedin_access_token
LI_REFRESH_TOKEN=your_linkedin_refresh_token
LI_PERSON_URN=urn:li:person:your_person_id
# Used by admin refresh callback:
LI_REDIRECT_URI=http://localhost:8042/admin/linkedin-token/callback
# Optional override:
# LI_AUTHOR_URN=urn:li:person:your_person_id
# LI_ORGANIZATION_URN=urn:li:organization:your_org_id
LI_API_VERSION=202504
```

### Step 7: Token renewal

Set a reminder every 45 days to refresh token before expiration.

---

## How It Works in Duckiehunt

The social sharing code lives in `django/duck/social.py`. It uses an extensible provider pattern:

- **`FacebookProvider`** — posts photos/text to your Facebook Page
- **`InstagramProvider`** — posts photos to your Instagram Professional account
- **`LinkedInProvider`** — posts text and image sightings via LinkedIn REST APIs
- Future: TikTok (#117)

### Auto-posting
When configured, approved sightings are shared automatically via Django-Q background tasks after a new location is submitted.

### Without credentials
If no `FB_PAGE_ID` or `FB_PAGE_ACCESS_TOKEN` is set, the social module simply does nothing. The app runs fine without social media configured.
