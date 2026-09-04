# Telegram Bot — Current State Analysis

**Date:** 2026-09-05  
**Repository:** `levrangit/Family_beacon`  
**Branch:** `develop`  
**Scope:** `telegram_bot/`, related backend Telegram tests/services, and Telegram-related Supabase migrations/state.  
**Changes during analysis:** none before this document was created.

## 1. Executive summary

The Telegram bot is an existing implementation, not a placeholder. The parent-facing flow is substantially implemented: `/start`, Telegram-ID lookup, parent registration, parent profile/family/children views, family invites, and account deletion UI/backend wiring are present.

The main current gaps and inconsistencies are:

1. Child registration through Telegram is only a stub in the current bot UI.
2. GitHub contains migration `024_parent_account_deletion.sql`, but the inspected Supabase migration state stops at `023`; the `delete_parent_account` RPC is not present in the current database function list.
3. The parent-registration backend tests call `/auth/register-parent` without `X-Telegram-Bot-Key`, while the current endpoint requires that header. This explains the previously observed `401 Telegram bot authentication required` when the header is omitted.
4. The backend Telegram tests mock the account-deletion RPC, so they do not prove that the RPC exists in the live Supabase database.

No project code, migrations, database schema, or configuration were modified as part of the analysis. The only repository change authorized after the analysis is this documentation file.

## 2. `telegram_bot/` structure

```text
telegram_bot/
├── backend_client.py
├── bot.py
├── config.py
├── handlers/
│   ├── __init__.py
│   └── start.py
├── registration.py
├── requirements.txt
└── tests/
    ├── test_backend_client.py
    ├── test_parent_menu.py
    └── test_registration.py
```

## 3. Telegram bot layer

### `bot.py`

The bot uses Telethon. It creates a `TelegramClient`, creates a `BackendClient`, registers handlers for `/start`, registration messages, role callbacks, and `parent:*` callbacks, then starts with the configured bot token and runs until disconnected.

### `config.py`

Required environment variables:

- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_SHARED_SECRET`

Optional configuration includes `FAMILY_BEACON_BACKEND_URL` (default `http://127.0.0.1:8000`) and `TELEGRAM_SESSION_PATH`.

### `backend_client.py`

The client communicates with FastAPI over HTTP and sends `X-Telegram-Bot-Key` on requests. Implemented operations cover Telegram-ID lookup, parent registration, profile, family, children, invites, invite creation, and parent account deletion.

### `registration.py`

Registration uses an in-memory `RegistrationSession` state machine. Parent registration progresses through login and password states and returns the Telegram ID, login, and password to the handler for backend registration. Registration state is not persisted.

### `handlers/start.py`

The `/start` flow first looks up the sender's Telegram ID. Existing parents receive the parent menu; admin/child roles receive role-specific messages; unknown Telegram IDs receive role selection.

The parent menu contains:

- My family
- My profile
- Children
- My invitations
- Issue an invitation to a child
- Forget me

Parent registration is implemented as a two-step login/password conversation.

The child role handler currently only reports that the next step is registration; there is no complete child registration flow in the inspected Telegram handler.

## 4. Backend Telegram layer

The FastAPI application contains Telegram-specific endpoints for lookup and parent operations, plus `/auth/register-parent`.

The Telegram endpoints are protected by the shared secret header `X-Telegram-Bot-Key`. Parent operations additionally verify that the Telegram ID belongs to an active parent.

`TelegramParentService` handles:

- parent profile retrieval;
- family retrieval;
- child listing;
- invite listing;
- invite creation;
- parent account deletion.

The Telegram layer therefore follows this architecture:

```text
Telegram / Telethon
        |
        | HTTP + X-Telegram-Bot-Key
        v
FastAPI Telegram endpoints
        |
        v
TelegramParentService
        |
        v
Supabase
```

## 5. Parent registration

Current flow:

```text
/start
  -> Parent
  -> enter e-mail/login
  -> enter password
  -> POST /auth/register-parent
  -> Supabase Auth sign_up
```

The registration request includes `telegram_id`, login/e-mail, and password. The backend passes `telegram_id` into Supabase Auth user metadata.

The database trigger/migration path then supports creation of the corresponding profile and Telegram ID.

Important test mismatch: `backend/tests/test_parent_registration_endpoint.py` invokes `/auth/register-parent` without `X-Telegram-Bot-Key`, although the current endpoint requires that header. Therefore those tests are stale relative to the current endpoint contract unless the authentication dependency is overridden.

## 6. Family invites

Migration `019` creates `family_invites` with hashed invite codes and lifecycle fields including expiration, used, and revoked state.

Migration `020` adds the `create_family_invite` RPC and related family-parent authorization policies.

Migration `021` adds invite redemption logic.

Migration `022` extends redemption so a parent is added to `family_members`.

Migration `023` adds a unique index for non-null child Telegram IDs.

The Telegram parent menu already exposes invite creation and invite listing.

## 7. Child Telegram identity

Migration `017` added `children.telegram_id`.

Migration `023` enforces uniqueness for non-null child Telegram IDs.

The live Supabase schema inspected during the analysis contains `children.telegram_id bigint` and `profiles.telegram_id bigint`.

The database is therefore prepared to associate a child with a Telegram account, but the Telegram bot's child registration flow is not yet implemented.

## 8. Account deletion discrepancy

GitHub contains `024_parent_account_deletion.sql`, defining the `delete_parent_account(p_profile_id uuid)` RPC.

The inspected live Supabase migration state stops at migration `023`. The inspected database function list contains `create_family_invite`, `handle_new_user`, `is_family_parent`, and `redeem_family_invite`, but not `delete_parent_account`.

The current Telegram/backend code calls the deletion RPC. Consequently, the "Forget me" path is wired in the application but is not backed by the corresponding RPC in the inspected live database.

This should be treated as a deployment/schema synchronization issue, not as a reason to create a second deletion implementation.

## 9. Tests

`telegram_bot/tests/test_registration.py` covers the registration state machine.

`telegram_bot/tests/test_backend_client.py` checks HTTP client behavior and the shared-secret header.

`telegram_bot/tests/test_parent_menu.py` covers parent menu behavior and account-deletion confirmation.

`backend/tests/test_telegram_parent.py` covers service behavior for family, invites, and deletion. Deletion tests mock the RPC and therefore do not verify live Supabase availability of `delete_parent_account`.

## 10. Current readiness matrix

| Capability | Telegram | Backend | Supabase | State |
|---|---:|---:|---:|---|
| `/start` | Yes | Yes | Yes | Implemented |
| Telegram-ID lookup | Yes | Yes | Yes | Implemented |
| Parent registration | Yes | Yes | Yes | Mostly implemented |
| Parent profile | Yes | Yes | Yes | Implemented |
| Family view | Yes | Yes | Yes | Implemented |
| Children list | Yes | Yes | Yes | Implemented |
| Create child invite | Yes | Yes | Yes | Implemented |
| List invites | Yes | Yes | Yes | Implemented |
| Invite redemption | Not in current Telegram flow | Present in DB/backend | Yes | Separate flow |
| Child Telegram registration | Stub | Incomplete for Telegram flow | Schema prepared | Not implemented |
| Unique child Telegram ID | N/A | N/A | Yes | Implemented |
| Forget-me/account deletion | Yes | Yes | Missing live RPC | Broken against inspected live DB |
| Admin Telegram UI | Minimal message | N/A | N/A | Not implemented |
| Telegram tests | Yes | Yes | Mocked for some DB operations | Partial coverage |

## 11. Recommended next development sequence

Before adding new Telegram features:

1. Verify and reconcile migration `024` against the live Supabase migration history.
2. Update/align parent-registration tests with the required `X-Telegram-Bot-Key` contract.
3. Define the complete child registration/redeem flow, using the existing invite and `children.telegram_id` database design rather than introducing a parallel mechanism.
4. Add tests for the child Telegram flow and for live-contract boundaries where appropriate.
5. Only then continue expanding Telegram UI/features.

## 12. Important project rule

No implementation or database changes should be made in `Family_beacon` without the user's explicit authorization. This analysis was read-only; the current document is the sole repository write authorized by the user after the analysis.
