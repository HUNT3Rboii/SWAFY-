# SWAFY mobile app

The citizen app: take a photo of a problem, send it, and follow what happens to it.
Built with React Native, Expo and TypeScript. Part of the SWAFY monorepo (`apps/mobile`).

## Requirements

- Node.js 20.19 or newer (22 recommended)
- An Android phone (the map needs a development build, see below)
- Docker, to run the mock API (`infra/docker-compose.yml`)
- A free [expo.dev](https://expo.dev) account, member of the `swafy-team` organization

## Setup

1. Install dependencies:

   ```bash
   cd apps/mobile
   npm install
   ```

   This also links `@swafy/api-client` from `packages/api-client`.

2. Start the mock API (needs Docker), from the repository root:

   ```bash
   cd infra
   cp .env.example .env
   docker compose up
   ```

   The mock answers with the examples from `docs/contracts/openapi.yaml` on port 4010.

3. Create your own settings file and set the API address:

   ```bash
   cp .env.example .env.local
   ```

   On a real phone, `localhost` means the phone itself. Use your computer's Wi-Fi IP
   address instead (on Linux: `hostname -I`):

   | | `EXPO_PUBLIC_API_BASE_URL` |
   |---|---|
   | Mock API | `http://192.168.1.20:4010` |
   | Real API | `http://192.168.1.20:8000/api/v1` |

   `.env.local` is ignored by git.

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
| `src/config/env.ts` | Reads `EXPO_PUBLIC_API_BASE_URL` |
| `src/api/client.ts` | The API client from `@swafy/api-client` (generated from the contract) and its types |
| `src/api/auth.ts` | Register, login and logout calls |
| `src/auth/` | Who is logged in (`auth-context.tsx`) and the tokens saved in SecureStore |
| `metro.config.js` | Lets Metro load `packages/api-client`, which is outside `apps/mobile` |
| `eas.json` | Build profiles (development, preview, production) |

## Rules

- Only edit `apps/mobile/` for mobile work. Need a change elsewhere? Open an issue labelled
  `type:integration` for the owner.
- Categories and statuses come from the generated api-client, never from a hardcoded list.
  See `docs/contracts/enums.md`.
- Never commit `.env.local` or `node_modules`.
