# SWAFY mobile app

The citizen app: take a photo of a problem, send it, and follow what happens to it.
Built with React Native, Expo and TypeScript. Part of the SWAFY monorepo (`apps/mobile`).

## Requirements

- Node.js 20.19 or newer (22 recommended)
- An Android phone (the map needs a development build, see below)
- A free [expo.dev](https://expo.dev) account, member of the `swafy-team` organization

## Setup

1. Install dependencies:

   ```bash
   cd apps/mobile
   npm install
   ```

2. Create your own settings file and set the API address:

   ```bash
   cp .env.example .env.local
   ```

   On a real phone, `localhost` means the phone itself. Use your computer's Wi-Fi IP
   address instead (on Linux: `hostname -I`), for example
   `EXPO_PUBLIC_API_BASE_URL=http://192.168.1.20:8000`.
   `.env.local` is ignored by git.

   `EXPO_PUBLIC_USE_MOCK_API=true` makes the app answer API calls itself with fake data
   (no backend needed). Set it to `false` to use the real API.

## Run the app

The map uses native code, so **Expo Go cannot open this app**. Install the SWAFY
development build once:

1. Open expo.dev, then `swafy-team`, then `swafy`, then **Builds**.
2. Open the latest `development` build on your phone and install the APK.

Then, every time you work:

```bash
npx expo start -c
```

Open the **SWAFY** app on your phone and pick your computer in the server list
(or scan the QR code). The phone and the computer must be on the same Wi-Fi.
If the network blocks the connection, use `npx expo start -c --tunnel`.

Rebuild the development build only when you add a library that contains native code:

```bash
npx eas-cli@latest build --profile development --platform android
```

## Project layout

| Path | What it holds |
|---|---|
| `src/app/` | The screens. One file = one screen (Expo Router). |
| `src/components/` | Reusable pieces (tab bar, themed text, map) |
| `src/config/env.ts` | Reads `EXPO_PUBLIC_API_BASE_URL` and `EXPO_PUBLIC_USE_MOCK_API` |
| `src/api/` | API calls (`auth.ts`), fake answers (`mock.ts`), types from the OpenAPI contract |
| `src/auth/` | Who is logged in (`auth-context.tsx`) and the tokens saved in SecureStore |
| `eas.json` | Build profiles (development, preview, production) |

## Rules

- Only edit `apps/mobile/` for mobile work. Need a change elsewhere? Open an issue labelled
  `type:integration` for the owner.
- Categories and statuses come from the generated api-client, never from a hardcoded list.
  See `docs/contracts/enums.md`.
- Never commit `.env.local` or `node_modules`.
