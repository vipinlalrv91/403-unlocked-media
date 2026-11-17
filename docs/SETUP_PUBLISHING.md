# Setup: free Instagram + YouTube publishing for 403 UNLOCKED and The Stoic Bull

Goal: put 8 values into GitHub Actions secrets so `.github/workflows/publish.yml` can post Reels/Shorts.
RULES for any assistant helping: the owner logs in and clicks every "Allow"/permission screen personally.
Never paste a token into a chat. Copy values straight into GitHub Secrets (Step C).

## Step A: Meta (Instagram), one app for both pages
Pages (on the owner's Facebook account): "403 UNLOCKED" ↔ @403_unlocked, "The Stoic Bull" ↔ @thestoicbull_ (both Instagram accounts professional).
1. developers.facebook.com → My Apps → Create App → filter "Content management" → tick "Manage messaging & content on Instagram" → Next → skip business portfolio → Create.
2. App → Use cases → Manage messaging & content on Instagram → Customize → "API setup with Facebook login".
3. developers.facebook.com/tools/explorer → Meta App = this app → "Get User Access Token" with permissions:
   instagram_basic, instagram_content_publish, pages_show_list, pages_read_engagement, business_management
   → Generate → in the popup select BOTH pages.
4. ⓘ next to token → Open in Access Token Tool → "Extend Access Token" → copy the long-lived token.
5. Explorer: paste long-lived token, run GET `me/accounts?fields=name,access_token,instagram_business_account`.
   Two results. For each page note `access_token` (page token, does not expire) and `instagram_business_account.id`.

## Step B: Google (YouTube), one project for both channels
1. console.cloud.google.com → New project "shorts-uploader" → APIs & Services → Library → YouTube Data API v3 → Enable.
2. OAuth consent screen (may open as "Google Auth Platform" → Get started) → app name "Shorts Uploader", External, emails → Create. Then Audience → Publish app → status **In production** (Testing mode expires tokens after 7 days).
3. Credentials → Create credentials → OAuth client ID → Web application → Authorized redirect URI: https://developers.google.com/oauthplayground → copy Client ID + Client secret.
4. developers.google.com/oauthplayground → ⚙ → "Use your own OAuth credentials" → paste ID + secret.
   Scope: https://www.googleapis.com/auth/youtube.upload → Authorize APIs → choose channel **403 UNLOCKED** → Exchange → copy Refresh token.
   Open a NEW Incognito window, repeat → choose **The Stoic Bull** → Exchange → copy second Refresh token.
   Repeat again in a new Incognito window → choose **Kadha Petti Malayalam** → third Refresh token.
   ("Google hasn't verified this app" → Advanced → Continue: it is the owner's own app.)

## Step C: GitHub secrets (11)
https://github.com/vipinlalrv91/403-unlocked-media/settings/secrets/actions → New repository secret, once per row:

| Name | Value |
|---|---|
| IG_USER_ID_403 | instagram_business_account.id of page 403 UNLOCKED |
| IG_TOKEN_403 | access_token of page 403 UNLOCKED |
| IG_USER_ID_STOIC | instagram_business_account.id of page The Stoic Bull |
| IG_TOKEN_STOIC | access_token of page The Stoic Bull |
| YT_CLIENT_ID | Google OAuth Client ID |
| YT_CLIENT_SECRET | Google OAuth Client secret |
| YT_REFRESH_403 | refresh token authorized on 403 UNLOCKED |
| YT_REFRESH_STOIC | refresh token authorized on The Stoic Bull |
| IG_USER_ID_KADHA | instagram_business_account.id of page kadha petti malayalam |
| IG_TOKEN_KADHA | access_token of page kadha petti malayalam |
| YT_REFRESH_KADHA | refresh token authorized on Kadha Petti Malayalam (if it has a YouTube channel) |

## Step D: YouTube API audit (so uploads can be public)
Search "YouTube API Services audit and quota extension form", submit: purpose = uploading the owner's own videos to their own two channels.
Until approved, YouTube forces API uploads to Private.

Done → tell the Claude Code session "secrets added".
