# Mobile App Attacks (Android / iOS) — Deep Dive

Beyond pulling endpoints from the bundle, mobile has its own exploitable surface: exported
components, deeplinks, WebView bridges, and insecure storage. This is the mechanic level for each,
for authorized testing of apps in scope.

## Android — exported components

The manifest declares which components other apps can invoke. `exported=true` (explicit, or
implicit when an `intent-filter` is present) means any installed app can call it.

- **Activities:** an exported activity that takes `Intent` extras and acts on them (loads a URL in
  a WebView, performs an action, shows data) → a malicious app launches it with crafted extras.
  Classic: an exported activity that loads `intent.getStringExtra("url")` into a WebView →
  attacker app loads its own page in the victim app's context.
- **Services / BroadcastReceivers:** exported ones accept `Intent`s → trigger privileged actions,
  or receive broadcasts carrying data.
- **Content Providers:** the highest-yield. An exported provider with `grantUriPermissions` or weak
  path checks → other apps read/write its data. Test `content://<authority>/...` for:
  - **SQL injection** in the `selection`/`projection` (providers back onto SQLite).
  - **Path traversal** in `openFile()` → read arbitrary app-private files
    (`content://authority/../../databases/x.db`).

## Deeplinks & App Links / Universal Links

- **Custom scheme** (`myapp://`) and **App Links** (`https://` verified via `assetlinks.json`) route
  external URLs into the app.
- **Attacks:** a deeplink that carries an auth token/OAuth callback → another app registering the
  same scheme (scheme hijacking on Android) intercepts it. A deeplink that drives a sensitive
  action (`myapp://transfer?to=...`) invocable from a web page or another app → CSRF-like abuse.
- **WebView + deeplink:** a deeplink that sets the WebView's URL → load attacker content into the
  app (feeds the bridge attack below).
- Check `assetlinks.json` / `apple-app-site-association` for over-broad path patterns.

## WebView JavaScript bridges

`addJavascriptInterface` (Android) / `WKScriptMessageHandler` + evaluateJavaScript (iOS) expose
native methods to loaded web content. If the WebView can load attacker-influenced content (via a
deeplink, an open redirect, a MITM on cleartext, or a loaded remote page), the bridge is reachable:

- Enumerate the exposed interface methods (from decompiled code) — do any read files, return
  tokens, make authenticated requests, or perform actions?
- On old Android (`< 4.2`) `addJavascriptInterface` exposed reflection → RCE; modern is limited to
  `@JavascriptInterface`-annotated methods, but those methods themselves are the surface.
- **Cleartext/mixed content** or missing cert pinning lets a network attacker inject into the
  WebView and reach the bridge.

## Insecure storage & transport

- **Storage:** tokens/PII in `SharedPreferences`/plist/SQLite/`NSUserDefaults` unencrypted; secrets
  that should be in Keystore/Keychain. WebView cache holding sensitive data.
- **Transport:** cleartext (`usesCleartextTraffic`), a custom `TrustManager`/`ServerTrustEvaluating`
  that accepts all certs, or bypassable pinning (relevant for *your* testing, and a finding if
  absent where it should protect sensitive flows).
- **Backups:** `android:allowBackup=true` → app data extractable via adb backup.

## Method

1. Decompile (jadx/apktool for APK; class-dump/decrypt for IPA) and read the manifest/Info.plist.
2. List exported components, deeplink schemes, WebView usages, and bridge methods.
3. Build a tiny **attacker app** (or an `adb`/web PoC) that invokes the exported component / deeplink
   / loads content into the WebView, and show the effect.
4. For providers, query `content://` with injection/traversal.

## Reporting

Cite the manifest entry / class+method (`file:line` in decompiled source), show the PoC app or
`adb`/web invocation, and demonstrate the concrete impact (file read, token theft, action as the
user) against the running app. Presence in the manifest alone isn't the finding — the invocation
and its effect are.
