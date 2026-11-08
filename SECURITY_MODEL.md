# FoodWise security threat model

## Scope and evidence
- **User-confirmed scope:** `MRSHAKILS/FoodWise-AI-Powered-Food-Management-Sustainability-Platform`, whole repository, default branch, Normal effort. The user confirmed a public service with real user data, no demo-only security exceptions, and priorities of user accounts/sessions and household/dietary/consumption data.
- No root security-model document was found. Implementation details below are inferred from the checked-out code and repository-authored documentation; inferences alone must not change scanner severity. User-confirmed assumptions are explicitly labeled.
- No infrastructure code or related infrastructure repository was found in the inspected repository and repository-name searches. The user confirmed there is no infrastructure repository and this repository alone is in scope. Production topology, TLS termination, database exposure, media storage, and hosting access controls are unverified.
- README describes planned full-stack functionality. Current implementation takes precedence: custom app models are empty, most data views are placeholders, and AI/OCR dependencies do not establish an implemented AI service.

## System overview and trust boundaries
A Django monolith renders browser pages and uses Django authentication, database-backed sessions, and a local SQLite configuration. Internet/browser input crosses into Django routes; Django crosses into its database and filesystem. Third-party CDN JavaScript executes in the application's browser origin. Operators control runtime configuration and deployment, which are not captured in infrastructure-as-code here.

### Stable components
| Component | Code covered | Boundary and role |
|---|---|---|
| Web UI | `templates/`, `static/`, app-specific `templates/`, `package.json`, `package-lock.json` | Untrusted browser inputs, rendered HTML, forms, and third-party browser scripts. |
| Identity | `users/` | Login/logout, sessions, profile pages, and development test-login flow. |
| Food Management | `food/` | Inventory and consumption routes; custom models and persistence are currently placeholders. |
| Content | `resources/` | Resource listing, category, detail, and recommendation pages; currently placeholder data views. |
| Uploads | `uploads/` | Receipt/image forms and list/detail/delete/link routes; server-side upload processing is currently a placeholder. |
| Runtime | `Platform/`, `manage.py`, `requirements.txt` | Django middleware, admin routing, database, settings, Python dependencies, and WSGI/ASGI entry points. |

## Entry points and reachability
- **User-confirmed deployment assumption:** a public service with real user data. `/`, `/users/login/`, `/users/register/`, and routable feature pages must be assessed as internet-facing unless deployment evidence establishes restrictions.
- `Platform/urls.py` exposes `/admin/`, `/dashboard/`, `/users/`, `/food/`, `/resources/`, and `/uploads/`.
- `users/views.py` uses Django authentication for credential login; profile and profile-edit views require authentication. Dashboard permits either an authenticated user or a test-login session flag. A routed test-login view sets that flag on POST. This is observed behavior, **not an accepted risk**.
- Food, content, and upload view functions mostly render templates or redirect; absence of login decorators does not by itself demonstrate disclosure or modification of real records.
- Form values, route parameters, cookies, and future file bodies are untrusted. Current upload template provides a file input, but its view does not yet process files.
- Web UI loads Tailwind, GSAP, and Swiper from external CDNs (`templates/base.html`, `templates/home.html`, and login-related templates). CDN trust is distinct from application-server trust.
- Django admin is an operator surface protected by framework authentication/authorization; actual staff accounts and network restrictions are unknown.
- No implemented API, background worker, OCR pipeline, LLM call, or external model integration was found in the inspected routing/views. README future plans and dependencies are not proof those surfaces are live.

## Assets and sensitivity
**User-confirmed priorities:** user accounts and sessions; household, dietary, and consumption data. The user did not designate an always-critical severity; scanner-confirmed impact and exploitability still determine priority.

**Code-derived asset inventory:**
- Actual Django account credentials/hashes, authenticated sessions, administrator privileges, and application signing material are sensitive.
- Intended household profiles, dietary preferences, food inventory, and consumption history may reveal personal habits. Current custom app models do not persist them.
- Intended uploaded receipts/images may contain names, purchases, addresses, or other personal data. Current server-side processing is not implemented.
- Database integrity, deployment configuration, application availability, and any future external-service credentials/cost exposure matter. Do not assume payment data or regulated medical records are present.

## Relevant attackers
The user confirmed a public service with real user data and no demo-only security exceptions. Anonymous internet attackers and malicious users attempting access to others' real data are relevant; no attacker has been explicitly excluded. Specific capabilities below remain code-derived assumptions:
- Anonymous internet clients targeting exposed routes or configuration.
- Malicious authenticated users attempting cross-user access where real data operations exist.
- Malicious web content attempting browser-mediated requests or script injection.
- A compromised third-party script/dependency supply chain.
- Compromised ordinary user sessions; administrator/deployment-operator compromise has greater access but is not automatically an application exploit.
No attacker is excluded and no demo-only bypass is accepted unless the user explicitly says so.

## Existing controls and limitations
- `Platform/settings.py` enables Django SecurityMiddleware, SessionMiddleware, CsrfViewMiddleware, AuthenticationMiddleware, and XFrameOptionsMiddleware; template autoescaping follows the Django defaults unless overridden.
- Django password validators are configured. Login uses `authenticate()` and `login()`; logout uses Django `logout()`.
- Profile routes use `login_required`; visible login and upload forms include CSRF tokens. These are code-level controls, not proof every endpoint is protected.
- Checked-in runtime settings use SQLite, debug mode, an empty allowed-hosts list, and a literal signing-key assignment; actual deployed overrides are unknown. Do not reproduce signing material.
- Production hosting/TLS, cookie hardening, rate limits, backups, secret rotation, file limits, media isolation, and access logging are unverified. Deployment instructions in README are examples, not deployed controls.
- Empty models and TODO views limit demonstrated impact; distinguish currently reachable behavior from risks contingent on future implementation.
- The verified scan environment installs only the pinned current Django runtime and npm dependencies. Full Python requirements resolution fails because the two Google AI packages require incompatible google-ai-generativelanguage versions; unused AI/OCR packages are not installed. All repository files remain in scope. Django checks, migrations, and HTTP startup smoke checks passed; the test command discovers zero tests. This environment limitation is not accepted risk for findings in those dependency declarations.

## Accepted risk and exclusions
The user explicitly accepts no demo-only security exceptions. No other accepted risks or excluded attackers were supplied. No separate infrastructure repository is in scope by the user's choice; this does not make deployment-related application findings accepted risk. Do not invent working data flows from README aspirations.

## Reranking policy
Keep each finding's scanner severity, exploitability assessment, and confirmed reach unless a user-provided fact changes its relevance. A code-derived assumption moves nothing. Lower only for explicitly excluded attackers/assets/surfaces or accepted risk; raise rarely, only for a user-designated critical asset reached by a scanner-confirmed, sufficiently exploitable path. Never raise hard-to-exploit or unverified findings. Tag each finding with the stable Component above; cross-component findings use the primary root-cause component.

## Open questions
1. Which personal data is actually persisted in the deployed instance, given that checked-out custom app models remain empty?
2. What production hosting/network controls and runtime overrides are applied outside this repository?

The user selected Component-only finding tags and no infrastructure repository. No further answers are required to finalize this threat model.

## Sources
- `README.md`: intended feature set, development setup, planned data schema, and example Heroku/PythonAnywhere deployment.
- `Platform/settings.py`, `Platform/urls.py`: configured middleware, storage, runtime, and route exposure.
- `users/views.py`, `users/urls.py`: actual authentication, session, and test-login behavior.
- `food/`, `resources/`, `uploads/` views, URLs, models, and templates: current feature boundaries and placeholder persistence.
- `templates/base.html`, `templates/home.html`, `users/templates/users/login.html`: browser third-party scripts and forms.
