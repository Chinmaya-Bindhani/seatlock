# Mini Helpdesk — Project Structure and Build Plan

This is a proposed repository layout, not generated application code. Create files when their phase begins instead of building empty abstractions up front.

Related documents: [Architecture](ARCHITECTURE.md) · [System design](SYSTEM_DESIGN.md).

## 1. Target repository layout

```text
mini-helpdesk/
├── README.md
├── pyproject.toml                  # Dependencies, test and lint configuration
├── uv.lock                         # Commit a lockfile if using uv
├── .env.example                    # Names and safe placeholder values
├── .gitignore
├── Dockerfile
├── compose.yaml                    # Web, PostgreSQL, Redis, worker, scheduler
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── test.py
│   ├── urls.py                     # Page routes and /api/v1/ routes
│   ├── asgi.py                     # HTTP + authenticated/origin-checked WebSockets
│   ├── wsgi.py                     # Conventional Django entrypoint; ASGI is used here
│   ├── celery.py                   # Worker app and periodic recovery schedule
│   └── wiring.py                   # Construct TicketService with a publisher
├── apps/
│   ├── __init__.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py               # AbstractUser + role
│   │   ├── admin.py
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py            # Current user and logout
│   │   │   └── urls.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_auth.py
│   ├── tickets/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py               # Ticket, Comment, Tag and DB constraints
│   │   ├── admin.py                # Inspect tickets; manage tags
│   │   ├── services.py             # TicketService: create, claim, comment, resolve
│   │   ├── selectors.py            # Scoped reads, annotations, joins, prefetches
│   │   ├── policies.py             # Shared role/ownership checks
│   │   ├── contracts.py            # EventPublisher Protocol, PublishError
│   │   ├── events.py               # Change-hint payload construction
│   │   ├── exceptions.py           # Domain conflicts and permission errors
│   │   ├── views.py                # Template page views
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py      # Separate read and write shapes
│   │   │   ├── permissions.py      # HTTP permission adapters
│   │   │   ├── views.py            # Thin API endpoints
│   │   │   └── urls.py
│   │   ├── management/
│   │   │   ├── __init__.py
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       └── seed_demo.py    # Demo users and realistic query fixtures
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_services.py
│   │       ├── test_api.py
│   │       ├── test_permissions.py
│   │       ├── test_query_counts.py
│   │       └── test_concurrency.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── models.py               # WebhookEvent, WebhookDelivery
│   │   ├── admin.py                # Read-only event/delivery inspection
│   │   ├── signatures.py           # Sign/verify exact bytes
│   │   ├── http_client.py          # Timeouts, fixed destination, response mapping
│   │   ├── tasks.py                # Thin worker and recovery task entrypoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── incoming.py         # Atomic deduplication; injected TicketService
│   │   │   ├── outgoing.py         # Insert immutable resolution delivery snapshot
│   │   │   └── delivery.py         # Lease, send, result update, retry decisions
│   │   ├── migrations/
│   │   │   └── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── serializers.py      # Incoming event schema
│   │   │   ├── views.py            # Verify signature before applying payload
│   │   │   └── urls.py
│   │   ├── management/
│   │   │   ├── __init__.py
│   │   │   └── commands/
│   │   │       ├── __init__.py
│   │   │       └── retry_delivery.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_signatures.py
│   │       ├── test_incoming.py
│   │       ├── test_outgoing.py
│   │       └── test_delivery_recovery.py
│   └── realtime/
│       ├── __init__.py
│       ├── consumers.py            # Subscribe, authorize, forward change hints
│       ├── routing.py
│       ├── publishers.py           # ChannelsPublisher and initial NoOpPublisher
│       └── tests/
│           ├── __init__.py
│           ├── test_consumers.py
│           └── test_publisher_contract.py
├── common/
│   ├── __init__.py
│   ├── api_errors.py               # Consistent API error envelope
│   └── request_ids.py              # Request correlation middleware
├── templates/
│   ├── base.html
│   ├── registration/
│   │   └── login.html
│   └── tickets/
│       ├── list.html               # Includes a small create-ticket form
│       └── detail.html
├── static/
│   ├── css/app.css
│   └── js/
│       ├── api.js                  # Session/CSRF HTTP calls
│       └── ticket_detail.js        # Connect, buffer hints, refetch, reconnect
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures/factories
│   └── integration/
│       ├── __init__.py
│       └── test_resolution_flow.py # Real worker/broker/receiver scenario
├── tools/
│   ├── send_contact_event.py       # Signed requests and duplicate replay
│   └── webhook_receiver.py         # Local receiver with durable SQLite dedup
└── docs/
    ├── ARCHITECTURE.md
    ├── SYSTEM_DESIGN.md
    └── PROJECT_STRUCTURE.md
```

The delivered Markdown files belong in the proposed repository's `docs/` directory when implementation starts. Their relative links already work together.

## 2. Responsibilities and import direction

Keep these rules explicit in code review:

1. API serializers validate shapes and field limits; they do not implement claim/resolve transactions.
2. `tickets/services.py` owns writes; API views and integration handlers reuse it.
3. `tickets/selectors.py` returns permission-scoped queries; consumers and HTTP reads use the same visibility rules.
4. `tickets/contracts.py` does not import Channels or Celery. `realtime/publishers.py` implements its interface.
5. Ticket resolution imports the narrow database-only function in `integrations/services/outgoing.py`. That module receives primitive IDs/snapshots and does not import `TicketService`.
6. `integrations/services/incoming.py` receives a ticket service instance from the API view. It does not construct the service or import `config/wiring.py` itself.
7. `config/wiring.py` composes the service and adapter; `integrations/tasks.py` calls delivery logic. Avoid implicit business workflows in Django signals.
8. Keep `common/` limited to genuinely shared HTTP infrastructure. Domain rules stay with their owner.

Illustrative service surface:

```python
TicketService.create_ticket(actor, *, title, description)
TicketService.claim_ticket(actor, *, ticket_id)
TicketService.add_comment(actor, *, ticket_id, body)
TicketService.resolve_ticket(actor, *, ticket_id)
```

The actor is a verified user. The signed incoming integration uses its configured customer as actor after signature verification. Services still validate that user's role/activity and applicable ticket access.

## 3. Configuration contract

Document these in `.env.example`; keep actual secrets out of Git.

| Variable | Purpose | Phase |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Session/application signing secret | 1 |
| `DJANGO_SETTINGS_MODULE` | Local or test settings | 1 |
| `DJANGO_DEBUG` | Explicit development setting | 1 |
| `DJANGO_ALLOWED_HOSTS` | Allowed application hosts | 1 |
| `DATABASE_URL` | PostgreSQL connection | 1 |
| `CHANNEL_REDIS_URL` | Channels Redis connection/namespace | 3 |
| `INCOMING_WEBHOOK_SECRET` | Contact-form signature secret | 4 |
| `CONTACT_FORM_CUSTOMER_ID` | Pre-provisioned integration customer | 4 |
| `OUTGOING_WEBHOOK_ENABLED` | Enable future resolution delivery creation | 5 |
| `OUTGOING_WEBHOOK_URL` | Fixed demo receiver URL | 5 |
| `OUTGOING_WEBHOOK_SECRET` | Outgoing signature secret | 5 |
| `CELERY_BROKER_URL` | Broker connection separate from channel-layer configuration | 5 |

Map these into Django settings explicitly; Django does not automatically interpret these environment variable names. No Celery result backend is needed because delivery results live in PostgreSQL. Validate required integration settings when enabling the relevant feature.

For the custom user, set `AUTH_USER_MODEL = "accounts.User"` before the first migration. Use app configurations such as `name = "apps.accounts"`; the app label remains `accounts`. Use string model references in cross-app foreign keys and preserve generated migration dependencies.

## 4. Build sequence and completion gates

### Phase 1 — Working ticket system

Create settings, custom user, ticket/comment/tag models, migrations, seed command, session login, REST endpoints, and the three pages. Use a no-op live publisher and keep outgoing integration disabled.

Implement ticket locking and state rules now: they are harder to retrofit around inconsistent write paths. Keep admin ticket fields read-only except the tag-management surface; do not allow admin edits to bypass ticket workflow rules.

**Done when:** a customer creates a ticket; an agent claims it, comments, and resolves it; the customer can read the result; access-control and state-transition tests pass.

### Phase 2 — Database and concurrency lab

Generate realistic fixtures. Measure a naive serializer, optimize the list selector, and save the comparison in the README. Test competing claims and comment/resolution ordering with separate PostgreSQL connections.

**Done when:** list serialization has bounded query counts, filters produce correct scoped results, and races cannot violate assignment/status rules.

### Phase 3 — WebSocket updates

Add Redis, Channels routing, the publisher adapter, and authenticated ticket subscriptions. Implement snapshot refresh, version handling, reconnect, and visible-tab refresh.

**Done when:** two browser sessions see committed ticket changes, unauthorized subscribers receive no ticket data, and reconnect restores the current state.

### Phase 4 — Incoming webhooks

Add `WebhookEvent`, signature verification, the contact-form endpoint, and the sender utility. Use one configured customer. Exercise duplicates, concurrent duplicates, malformed bodies, stale timestamps, and payload conflicts.

**Done when:** a valid external event creates one ticket, repeated events return that same ticket, and rejected requests create nothing.

### Phase 5 — Outgoing jobs and reliability

Add `WebhookDelivery`, transactional snapshot creation, worker execution, leases, retry policy, periodic recovery, and a local receiver. The receiver stores event IDs and side effects atomically in a small local SQLite database so restarting it does not erase deduplication history. This SQLite utility is separate from the application's PostgreSQL database.

Have the receiver simulate `500`, timeout, and successful acceptance followed by lost acknowledgement. Enable outgoing integration only once durable creation and recovery are both implemented.

**Done when:** pending work survives broker downtime, failed attempts follow the policy, crash recovery can redeliver safely, and the receiver records only one effect for repeated event IDs.

### Phase 6 — SOLID review and cleanup

Inspect whether views, services, selectors, and transport adapters each have clear responsibilities. Run publisher contract tests. Keep explicit dependencies; remove abstractions that have no concrete use. Document startup and the failure demonstrations in the README.

**Done when:** a test publisher can replace Channels without editing ticket workflows, all earlier acceptance gates pass, and another developer can run the demos from the README.

## 5. Suggested test organization

| Test group | Infrastructure | Main focus |
| --- | --- | --- |
| Signature and retry-policy unit tests | Injected clock/HTTP client | Bytes, timestamp boundaries, retry classification |
| Model/service/API tests | PostgreSQL | Permissions, transactions, constraints, payloads |
| Query-count tests | PostgreSQL with populated fixtures | Bounded reads while serializing actual responses |
| Concurrency tests | PostgreSQL, separate connections | Claim and comment/resolve races |
| Consumer tests | Channels test communicator; in-memory layer for isolated tests | Authorization and message schema |
| Integration tests | PostgreSQL + Redis + real worker + receiver | Commit-to-delivery path, broker failure, recovery |

An in-memory channel layer is sufficient only for isolated consumer tests; it cannot demonstrate communication across separate application processes. [Channels channel-layer documentation](https://channels.readthedocs.io/en/stable/topics/channel_layers.html)

Run fast tests during each phase and the real-infrastructure scenarios once those components exist. Use transaction-capable tests for locking and explicitly execute/capture commit callbacks where appropriate. Never treat a passing eager/synchronous task test as proof of real broker delivery.

## 6. What the future README should contain

- Prerequisites and exact dependency installation/startup commands for the implemented environment.
- Environment setup, migrations, demo seed, and how to sign in with generated demo accounts.
- One walkthrough for each role, plus incoming/outgoing webhook examples.
- How to start only core services or the complete worker/scheduler setup.
- Test commands and measured query counts before/after optimization.
- How to trigger duplicate events, competing claims, broker outage, and failed-delivery recovery.
- Known limitations: one team, immutable ownership, best-effort live hints, bounded webhook retries, and no production deployment guarantee.

Keep future work separate from implemented features. These three documents are the implementation blueprint; the application remains to be built.
