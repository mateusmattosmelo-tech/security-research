# Mobile App Recon (APK / IPA)

A mobile app is a signed copy of how the backend expects to be called — endpoints, auth flows,
feature flags, and sometimes secrets, all shipped to the device. Decompiling it is account-free
recon that often reveals API surface the web client never touches.

## Get the artifact and unpack it

- **Android (APK/AAB):** pull from the device or a store mirror. Unzip, then decompile:
  `apktool` for resources/smali, `jadx` for readable Java/Kotlin. Merge split APKs first.
- **iOS (IPA):** unzip to the `.app`; decrypt if needed (a jailbroken device or a decryptor), then
  read with a class-dump / disassembler. Strings and the `Info.plist` are quick wins.

## What to pull out

- **Endpoints & hosts:** base URLs, `/api` paths, staging/internal hostnames, websocket URLs.
  Grep strings and the network layer (Retrofit/OkHttp interfaces, Alamofire routers).
- **Secrets in the bundle:** API keys, tokens, signing keys, cloud creds. Distinguish
  client-side-by-design keys (many are meant to ship) from ones that grant server-side power —
  the program policy often says which client config it considers non-sensitive.
- **Auth flow:** how tokens are obtained, stored (Keystore/Keychain vs. SharedPrefs/plist), and
  refreshed. Weak storage of long-lived tokens is a finding.
- **Feature flags & debug:** hidden/unreleased features, debug endpoints, test menus.

## Platform-specific bug classes

- **Deeplinks / URL schemes & App Links / Universal Links:** exported intent filters and custom
  schemes that take parameters — deeplink to a WebView, an auth callback, or an action. Test
  whether an external app/site can invoke sensitive actions or hijack the OAuth redirect.
- **Exported components (Android):** activities, services, broadcast receivers, and content
  providers marked `exported=true` — other apps can call them. Content providers are a common
  path-traversal / data-leak sink.
- **WebView bridges:** `addJavascriptInterface` / `WKScriptMessageHandler` exposing native
  methods to loaded web content — if the WebView loads attacker-influenced content, that bridge
  is RCE-adjacent. Check what the bridge exposes and what the WebView can load.
- **TLS:** certificate pinning presence (and whether it's bypassable for your own testing),
  cleartext traffic flags, custom trust managers that accept all certs.
- **Backup / cache:** sensitive data in app backups or WebView cache (some programs declare cache
  a known issue — check).

## From bundle to backend

Endpoints found in the app go on the same attack-surface map as everything else, then get tested
against the in-scope, authorized backend with an account you own. The app is the map; the bug is
proved against the server.

## Reporting

Cite the exact class/method or smali location and the manifest entry (`file:line`), show the
exported component or bridge, and demonstrate the impact against the running app/backend — a
malicious app or web page invoking the sensitive path, not just its presence in the manifest.
