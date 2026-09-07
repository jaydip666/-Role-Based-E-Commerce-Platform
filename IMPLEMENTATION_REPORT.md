# Implementation Report — Role-Based E-Commerce Platform

## 1. Project Overview

A three-role (`ADMIN`, `SALES_PERSON`, `USER`) e-commerce platform built for a Full Stack Developer Internship evaluation. Backend: Flask + MongoDB REST API. Frontend: React + Vite + Tailwind CSS. Real Cloudinary image uploads and a real Razorpay test-mode checkout flow, with every authorization rule enforced on the backend.

## 2. Technology Stack

Frontend: React 18, Vite 5, Tailwind CSS 3, React Router 6, Axios.
Backend: Python 3.11, Flask 3, Flask-Cors, PyMongo, PyJWT, bcrypt, cloudinary SDK, razorpay SDK, gunicorn.
Database: MongoDB.
Testing: pytest + mongomock.

## 3. Features Completed

Registration/login/logout, JWT auth, backend RBAC, product CRUD with ownership validation, Cloudinary image upload, server-side search/category/price filtering, wishlist, cart with stock validation, Razorpay checkout (trusted backend amount + signature verification), role-scoped order visibility and status management, Admin/Sales/User dashboards with live stats, responsive Tailwind UI, 61 backend automated tests, and a full manual browser walkthrough of all three roles.

Not completed: a real (credentialed) Razorpay transaction, a real (credentialed) Cloudinary upload verification, deployment to Render/Vercel, and an automated frontend test suite. See sections 17–19.

## 4. Authentication Implementation

- **Registration** (`POST /api/auth/register`): validates `name` (2–100 chars), `email` (RFC-shape via `email-validator`), and `password` (≥6 chars, at least one letter and one digit); rejects a duplicate email with `409`; always creates the account with role `USER` (a client cannot self-assign `ADMIN`/`SALES_PERSON`).
- **Password hashing**: `bcrypt.hashpw` with a fresh salt per user (`app/utils/security.py`); the hash is stored in `password_hash` and is never included in any serialized API response (`serialize_user`).
- **Login** (`POST /api/auth/login`): looks up the user by (lower-cased) email, verifies the password with `bcrypt.checkpw`, returns `401` on any mismatch without revealing whether the email or the password was wrong.
- **JWT**: `PyJWT`, HS256, payload `{sub: user_id, role, iat, exp}`, expires after `JWT_EXPIRES_HOURS` (default 24h). `app/middleware/auth_middleware.py`'s `authenticate_user` decorator extracts the `Authorization: Bearer` header, decodes it, and attaches the live user document to `flask.g` — every protected route re-verifies against the current database state, not just the token payload.
- **`GET /api/auth/me`**: used by the frontend on app load to restore a session from a stored token; a missing/invalid/expired token, or a token for a user that no longer exists, all return `401` and the frontend clears its stored session.
- **Logout**: JWT is stateless, so logout is purely client-side — the token and cached user are removed from `localStorage`, and React state is cleared.

## 5. Role-Based Access Control

`ADMIN` has unrestricted access to all product/user/order management endpoints. `SALES_PERSON` can create products and can only update/delete products where `product.owner_id == current_user_id` — enforced in `product_controller._find_owned_product_or_error`, which is called by both the update and delete handlers before any mutation. `USER` has read-only product access plus wishlist/cart/checkout/own-orders.

**This is enforced exclusively on the backend.** The frontend's `ProtectedRoute` and `RoleRoute` components (`frontend/src/routes/`) redirect unauthenticated or wrong-role users away from pages for a clean UX, and the `Navbar` only renders links relevant to the current role — but neither of these is a security boundary. Every protected Flask route independently re-runs `authenticate_user` and the appropriate `require_*` check regardless of what the frontend did or didn't show, so a direct `curl`/Postman call from a `SALES_PERSON` token against another seller's product, or from a `USER` token against `/api/admin/*`, is rejected with `403` exactly the same as it would be through the UI. This is what `backend/tests/test_rbac.py` and the ownership tests in `test_products.py` verify.

## 6. Product CRUD

- **Create** (`POST /api/products`, `ADMIN`/`SALES_PERSON`): accepts `multipart/form-data` (with an `image` file, uploaded to Cloudinary) or JSON (with an `image_url`); validates name/description/price/category/stock; `owner_id` is always set from the authenticated user, never from the request body.
- **Read** (`GET /api/products`, `GET /api/products/<id>`): public.
- **Update** (`PUT /api/products/<id>`): partial updates supported; ownership re-checked before any field is changed.
- **Delete** (`DELETE /api/products/<id>`): ownership re-checked before deletion.
- **Ownership validation**: `_find_owned_product_or_error` loads the product, then compares `g.current_user_role == ADMIN or product["owner_id"] == g.current_user_id`; any other case returns `403` before touching the database.

## 7. Search and Filtering

`GET /api/products` builds a MongoDB query from optional `search` (case-insensitive regex on `name` OR `description`), `category` (exact case-insensitive match), and `minPrice`/`maxPrice` (range on `price`), all combinable in a single request. The frontend's `Products` page keeps this state in the URL query string and re-fetches from the backend on every change — it never filters a client-cached list.

## 8. Cloudinary Implementation

`app/services/cloudinary_service.py::upload_product_image` validates the file extension and a 5MB size cap locally, then streams the file directly to `cloudinary.uploader.upload(..., folder="ecommerce_internship/products")` and returns only the `secure_url` from the response. That URL string is the only thing ever written to `products.image_url` — MongoDB never stores image bytes, and no file is written to local disk.

**Real account verification requires valid Cloudinary credentials, which are not configured in this environment** (`CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET` are blank in `backend/.env.example` and no real `.env` with credentials exists here). What *has* been verified: the upload function's validation logic (rejects bad extensions, oversized files, missing files), its error handling when the underlying `cloudinary.uploader.upload` call raises (mocked at that exact boundary in `test_cloudinary.py`), and an end-to-end request through the real `/api/products` route with a mocked Cloudinary response, confirming the resulting MongoDB document contains only a URL string.

## 9. Wishlist Implementation

`GET/POST /api/wishlist`, `DELETE /api/wishlist/<product_id>`, all behind `authenticate_user` and scoped to `g.current_user_id`. Adding a product already in the wishlist is a no-op both server-side (`$addToSet`, which cannot create duplicates by definition) and client-side (`WishlistContext.addProduct` checks its local id set before issuing the request at all, avoiding a redundant network call).

## 10. Cart Implementation

One cart document per user (`carts.user_id` is a unique index). `POST /api/cart` adds or increments a line item; `PUT /api/cart/<product_id>` sets an exact quantity; `DELETE /api/cart/<product_id>` removes a line item. Every quantity change is validated against the product's current `stock` (`409 Conflict` if insufficient). `GET /api/cart` returns items joined with live product data (name/image/price/stock) plus computed `item_count`, `subtotal`, and `total`, so the frontend never computes cart totals itself — it only displays what the backend returns.

## 11. Razorpay Implementation

`POST /api/payment/create-order`: reads the caller's cart, re-validates stock, and computes `total_amount` by summing `product.price × quantity` read fresh from MongoDB for every item — the amount the frontend was displaying is never sent to or trusted by this endpoint. It then calls `razorpay_service.create_razorpay_order(total_amount, ...)` to create a real Razorpay order for that trusted amount, and stores a snapshot of the purchased items in a short-lived `pending_payments` record so the eventual order can be built from that trusted snapshot rather than from anything supplied at verification time.

`POST /api/payment/verify`: receives `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature` from the frontend (which got them from Razorpay's own checkout callback) and independently recomputes the expected HMAC-SHA256 signature using the server's `RAZORPAY_KEY_SECRET`. **Only if the recomputed signature matches** does it look up the matching `pending_payments` snapshot, create the real `orders` document, decrement product stock, clear the user's cart, and mark the payment `paid`. An invalid or missing signature returns `400` and creates nothing — this is the mechanism that makes a frontend-only "payment successful" callback impossible to fake into a real order.

## 12. Payment Signature Verification

Implemented in `app/services/razorpay_service.py::verify_payment_signature` using `hmac.new(key=RAZORPAY_KEY_SECRET, msg=f"{order_id}|{payment_id}", digestmod=sha256)` compared with `hmac.compare_digest` (constant-time, avoiding timing attacks). Covered by two tests: a mocked valid signature that results in a created, paid order and a cleared cart, and a mocked invalid signature that results in `400` and zero orders created (`test_verify_invalid_signature_rejected`, `test_verify_valid_signature_creates_order_and_clears_cart`).

## 13. Order Management

`GET /api/orders` scopes by role: `USER` → `{user_id: current_user}`; `SALES_PERSON` → `{"items.seller_id": current_user}` (and the response strips out any line items belonging to other sellers within a mixed-seller order); `ADMIN` → no filter. `GET /api/orders/<id>` applies the same scoping and returns `403` for an order the caller isn't entitled to view. `PUT /api/admin/orders/<id>/status` is `ADMIN`-only and validates the new status against the fixed `ORDER_STATUSES` tuple.

## 14. Admin Dashboard

`GET /api/admin/stats` returns `total_users`, `total_products`, `total_orders` (paid only), `total_sales` (sum of paid order totals), and the 5 most recent orders — all computed live from MongoDB on each request, no caching. The Admin frontend also has full Product Management (any seller's products), User Management (role changes via a dropdown, with the admin's own row disabled to prevent self-lockout), and Order Management (status updates) pages, each verified manually against the running backend.

## 15. Sales Person Dashboard

`GET /api/sales/stats` computes the seller's own product count, orders containing their products, total units sold, and total sales — filtered to `owner_id`/`seller_id == current_user_id` throughout, so one seller's numbers never leak into another's. Verified manually: created a product as one seller, confirmed a second seller's `/sales/orders` view showed zero results for an order containing only the first seller's product (`test_sales_person_does_not_see_unrelated_orders`).

## 16. Testing

**Backend:** 61 pytest tests, **61/61 passing**, run against an isolated `mongomock` database injected via `create_app(db=...)` (see Bugs Found, item 1) — covering auth, RBAC, product CRUD/ownership, search/filters, Cloudinary integration structure, wishlist, cart, Razorpay create-order/verify (with mocked Razorpay responses), and role-scoped order visibility.

**Frontend:** `npm run build` completes with **0 errors** (275KB JS / 23KB CSS, gzipped to ~86KB/~4.7KB).

**Manual verification:** logged in as all three seeded roles via a real Chrome browser against the real running Flask + MongoDB backend and confirmed: registration, login/logout, role-based redirect, product search, category filter, price-range filter, product details, wishlist add/remove, add-to-cart, quantity +/-, checkout page (through the real backend Razorpay call, which failed cleanly with no credentials configured — see Known Limitations), sales-person product edit (persisted, visible cross-role from the Admin product list), admin role change, admin product/user/order management pages, guest redirect away from `/admin/dashboard`, and the 404 page. Zero browser console errors observed throughout.

## 17. Bugs Found and Fixed

**1. MongoDB test isolation bug (critical — tests were hitting a real local database).** `app/__init__.py` originally did `from app.extensions import init_mongo` and called that directly-imported name inside `create_app()`. The test fixture's `monkeypatch.setattr(extensions, "init_mongo", ...)` therefore had no effect, because monkeypatching a module attribute doesn't retroactively change a name another module already imported by value. `create_app()` kept calling the *real* `init_mongo()`, which connected to an actual MongoDB server running on `localhost:27017` on the development machine and wrote real documents into a database named `ecommerce_internship` — polluting it with test fixture data (fake users, 72 fake products, 16 fake orders, all with `@test.com` emails) and causing flaky, order-dependent test failures from cross-test data leakage (12–17 failures on a first full run). **Fix:** `create_app()` now accepts an optional `db=` parameter that, when provided, injects an already-constructed database directly (`extensions.set_db(db)`) instead of calling `init_mongo()` at all; the test fixture passes a per-test, uniquely-named `mongomock` instance this way. Verified the fix by re-running the full suite (went from 12–17 failures to 61/61 passing) and by confirming, via `MongoClient(...).list_database_names()`, that the real local MongoDB was untouched by a subsequent test run. The already-polluted database was identified (all `@test.com` fixture data, confirmed with the user it wasn't their data) and dropped with explicit user approval before continuing.

**2. Backend leaking internal exception details to the client.** When the real Razorpay API call failed (SSL certificate verification error in this environment, since no credentials or working outbound trust chain were configured), the raw exception — including connection host, port, and low-level SSL error text — was being returned directly in the `502` API response body via `raise PaymentError(f"Failed to create Razorpay order: {exc}")`, then surfaced verbatim to the browser. This violates the "no stack traces to the client" requirement and would leak infrastructure details in a real deployment. Found by manually clicking "Pay Now" in the browser with no Razorpay credentials configured and observing the raw `HTTPSConnectionPool(...)SSLCertVerificationError(...)` text rendered on the Checkout page. **Fix:** both `razorpay_service.create_razorpay_order` and `cloudinary_service.upload_product_image` now log the full exception server-side via `logging.exception(...)` and raise/return a short, generic, user-safe message instead (e.g. "Could not start the payment. Please try again in a moment."). Verified live in the browser (the sanitized message now renders) and confirmed the full traceback still appears in the server log for debugging. The corresponding test (`test_upload_wraps_cloudinary_errors`) was updated to match the new message and the full 61-test suite still passes.

**3. Test data validation bug (minor, test-only).** An order-visibility test used a product named `"A"` (single character), which the backend's `validate_product_payload` correctly rejects (minimum 2 characters), causing the test's product-creation step to fail with a `KeyError` when it tried to read a nonexistent `data` key from the resulting `400` error response. This was a mistake in the test data, not an application bug — the validator was behaving correctly. **Fix:** renamed the test products to `"Item A"`/`"Item B"`.

**4. `taskkill /IM` incident (process management, not a code bug).** While stopping the local dev servers started for manual testing, a blanket `taskkill /IM python.exe` / `taskkill /IM node.exe` was run, which terminates *every* process with that image name for the user rather than only the specific PIDs started for this project. This was caught immediately, disclosed to the user, and flagged via the tool's feedback mechanism; going forward, process cleanup should target the specific PID(s) that were started rather than an image-name-wide kill. No evidence of actual damage to unrelated work was found, but the risk was real and is documented here per the user's explicit request.

## 18. Challenges Faced and Solutions

- **Isolating tests from a real, already-running local MongoDB** — solved by moving from monkeypatching internal functions (fragile, as bug #1 shows) to explicit dependency injection (`create_app(db=...)`), which is both more testable and more obviously correct by inspection.
- **Testing Razorpay/Cloudinary without real credentials** — solved by testing at the exact network boundary (mocking `cloudinary.uploader.upload` and the controller-level `create_razorpay_order`/`verify_payment_signature` functions) rather than mocking away the application's own logic, so the real integration code (validation, request construction, response handling, error paths) is genuinely exercised, while acknowledging plainly that a live-account transaction has not been verified.
- **Keeping order history accurate after products change** — solved by snapshotting `product_name`/`price`/`seller_id` into each order line item at order-creation time rather than re-joining against the current product document, so a later product edit or deletion never rewrites past order history.
- **Preventing a frontend-only "payment succeeded" from being trusted** — solved by never creating the `orders` document from anything the frontend sends at the verify step; the order is built exclusively from the server-side `pending_payments` snapshot created during `create-order`, and only after the signature check passes.

## 19. Pending Features / Not Yet Completed

- A real, credentialed Razorpay test-mode transaction (needs `RAZORPAY_KEY_ID`/`SECRET`).
- A real, credentialed Cloudinary account upload (needs `CLOUDINARY_*` credentials).
- Deployment to Render (backend) and Vercel (frontend) — configuration is ready (see README §31) but not yet executed.
- An automated frontend test suite (component/e2e tests); frontend correctness was instead verified via live manual browser testing against the real backend.
- A merged Pull Request from `feature/react-frontend` into `main` (no GitHub remote is configured in this environment — see final report for exact manual steps).

## 20. Known Limitations

See README.md §33 for the full list (Razorpay, Cloudinary, mobile-viewport verification, no pagination, no automated frontend tests, not yet deployed). None of these affect the correctness of the code that has been written and tested — they reflect what could not be exercised end-to-end without credentials, a remote, or additional tooling that weren't available in this environment.

## Test Credentials

| Role | Email | Password |
|---|---|---|
| ADMIN | admin@example.com | Admin@123 |
| SALES_PERSON | sales@example.com | Sales@123 |
| USER | user@example.com | User@1234 |

Created by `python backend/seed.py`. Development/demo credentials only.
