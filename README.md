# Role-Based E-Commerce Platform

Full Stack Developer Internship Task — a complete role-based e-commerce web application demonstrating database design, JWT authentication, backend-enforced authorization, product CRUD with image upload, search/filtering, wishlist, cart, Razorpay test-mode payments, and role-specific dashboards.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Main Features](#2-main-features)
3. [Roles and Permissions](#3-roles-and-permissions)
4. [Technology Stack](#4-technology-stack)
5. [System Architecture](#5-system-architecture)
6. [Project Folder Structure](#6-project-folder-structure)
7. [Database Collections](#7-database-collections)
8. [Authentication](#8-authentication)
9. [Role-Based Access Control](#9-role-based-access-control)
10. [Product CRUD](#10-product-crud)
11. [Cloudinary Image Upload](#11-cloudinary-image-upload)
12. [Search and Filters](#12-search-and-filters)
13. [Wishlist](#13-wishlist)
14. [Cart](#14-cart)
15. [Razorpay Test Payment](#15-razorpay-test-payment)
16. [Order Management](#16-order-management)
17. [Admin Dashboard](#17-admin-dashboard)
18. [Sales Person Dashboard](#18-sales-person-dashboard)
19. [User Dashboard](#19-user-dashboard)
20. [Local Installation](#20-local-installation)
21. [Backend Setup](#21-backend-setup)
22. [Frontend Setup](#22-frontend-setup)
23. [MongoDB Setup](#23-mongodb-setup)
24. [Cloudinary Setup](#24-cloudinary-setup)
25. [Razorpay Setup](#25-razorpay-setup)
26. [Environment Variables](#26-environment-variables)
27. [Running the Application](#27-running-the-application)
28. [API Overview](#28-api-overview)
29. [Test Credentials](#29-test-credentials)
30. [Screenshots](#30-screenshots)
31. [Deployment](#31-deployment)
32. [Feature Completion Summary](#32-feature-completion-summary)
33. [Known Limitations](#33-known-limitations)

---

## 1. Project Overview

Minishopping  is a three-role e-commerce platform built as an internship evaluation project. It has a Flask + MongoDB REST API backend and a React + Vite + Tailwind frontend, with real Cloudinary image uploads and a real Razorpay test-mode checkout flow. Every permission boundary (who can edit which product, who can see which order, who can access which dashboard) is enforced on the backend — the frontend only hides UI for a better user experience.

## 2. Main Features

- JWT authentication with bcrypt password hashing
- Three roles: `ADMIN`, `SALES_PERSON`, `USER`, each with a dedicated dashboard
- Product CRUD with backend-enforced ownership (a seller can only edit/delete their own products; admins can act on any product)
- Cloudinary image upload — only the resulting URL is stored in MongoDB, never raw image bytes
- Server-side product search, category filter, and min/max price filter
- Wishlist (duplicate-safe) and cart (quantity management, stock validation) backed by MongoDB
- Razorpay test-mode checkout with a backend-computed trusted amount and backend signature verification — an order is only created after the signature is verified
- Role-scoped order visibility and admin order-status management
- Responsive Tailwind UI with loading/empty/error states throughout

## 3. Roles and Permissions

| Action | ADMIN | SALES_PERSON | USER |
|---|---|---|---|
| Browse / search / filter products | ✅ | ✅ | ✅ |
| Wishlist, cart, checkout | ❌ | ❌ | ✅ |
| View own orders | — | — | ✅ |
| Create product | ✅ (any) | ✅ (own) | ❌ |
| Edit / delete product | ✅ (any) | ✅ (own only) | ❌ |
| View orders containing own products | — | ✅ | — |
| View all orders | ✅ | ❌ | ❌ |
| Update order status | ✅ | ❌ | ❌ |
| Manage users / change roles | ✅ | ❌ | ❌ |
| View platform-wide stats | ✅ | ❌ (own stats only) | ❌ (own summary only) |

A `SALES_PERSON` who tries to edit or delete another seller's product via a direct API call is blocked with `403 Forbidden` by the backend — this is verified by an automated test (`test_sales_person_cannot_edit_others_product`, `test_sales_person_cannot_delete_others_product`).

## 4. Technology Stack

**Frontend:** React 18, Vite 5, Tailwind CSS 3, React Router 6, Axios
**Backend:** Python 3.11, Flask 3, Flask-Cors, PyMongo
**Database:** MongoDB
**Auth:** PyJWT, bcrypt
**Image Upload:** Cloudinary
**Payments:** Razorpay (Test Mode)
**Testing:** pytest + mongomock (backend), manual browser verification (frontend)
**Deployment target:** Render (backend), Vercel (frontend)

## 5. System Architecture

```
┌─────────────────┐        HTTPS/JSON        ┌──────────────────────┐
│  React (Vite)    │ ───────────────────────▶ │   Flask REST API      │
│  Vercel-hosted   │ ◀─────────────────────── │   Render-hosted       │
└─────────────────┘        JWT in header      └──────────┬────────────┘
                                                            │
                                    ┌───────────────────────┼───────────────────────┐
                                    │                        │                        │
                              ┌─────▼─────┐          ┌──────▼──────┐          ┌──────▼──────┐
                              │  MongoDB   │          │  Cloudinary  │          │  Razorpay    │
                              │  (Atlas)   │          │  (images)    │          │  (test mode) │
                              └────────────┘          └──────────────┘          └──────────────┘
```

The frontend never talks to MongoDB, Cloudinary, or Razorpay directly. Every write goes through the Flask API, which is the single point of authentication, authorization, validation, and trusted-amount calculation.

## 6. Project Folder Structure

```
ecommerce-internship-task/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/            # (reserved for static assets)
│   │   ├── components/        # Navbar, ProductCard, Modal, forms, states, etc.
│   │   ├── context/            # AuthContext, CartContext, WishlistContext, ToastContext
│   │   ├── hooks/              # (reserved for custom hooks; state currently lives in Context)
│   │   ├── layouts/            # MainLayout, DashboardLayout
│   │   ├── pages/               # public/, user/, sales/, admin/ pages
│   │   ├── routes/             # ProtectedRoute, RoleRoute
│   │   ├── services/            # one Axios-based module per API resource
│   │   ├── utils/               # format.js, roles.js, loadRazorpayScript.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── __init__.py          # app factory, blueprint + error handler registration
│   │   ├── config.py             # environment-based configuration
│   │   ├── extensions.py         # Mongo / Cloudinary / Razorpay client setup
│   │   ├── models/                # collection accessors + serializers
│   │   ├── routes/                # Flask blueprints (thin, delegate to controllers)
│   │   ├── controllers/           # request handling + business logic
│   │   ├── middleware/            # authenticate_user, require_role, etc.
│   │   ├── services/               # cloudinary_service.py, razorpay_service.py
│   │   ├── utils/                  # security (JWT/bcrypt), responses, object_id
│   │   └── validators/             # input validation
│   ├── tests/                      # 61 pytest tests (mongomock-isolated)
│   ├── run.py
│   ├── seed.py                     # creates the 3 test accounts + sample products
│   ├── requirements.txt
│   ├── .env.example
│   └── Procfile
│
├── README.md
├── IMPLEMENTATION_REPORT.md
└── .gitignore
```

## 7. Database Collections

**users** — `_id, name, email (unique), password_hash, role, created_at, updated_at`. `password_hash` is never returned by any API response.

**products** — `_id, name, description, price, category, image_url, owner_id, owner_name, stock, created_at, updated_at`. `image_url` is always a Cloudinary URL; no raw image bytes are ever stored.

**carts** — `_id, user_id (unique), items: [{product_id, quantity}]`. One cart document per user.

**wishlists** — `_id, user_id (unique), products: [product_id]`. `$addToSet` is used server-side so duplicates are structurally impossible.

**orders** — `_id, user_id, customer_name, items: [{product_id, seller_id, product_name, quantity, price, subtotal}], total_amount, razorpay_order_id, razorpay_payment_id, payment_status, order_status, created_at, updated_at`. Each item snapshots the product name/price/seller at order time, so order history stays accurate even if the product is later edited or deleted.

**pending_payments** (internal) — a short-lived record created when a Razorpay order is created and consumed when the payment is verified, so the real `orders` document is only ever built from a trusted, server-computed snapshot rather than trusting the client at verification time.

## 8. Authentication

- **Register** (`POST /api/auth/register`) — validates name/email/password, hashes the password with bcrypt, creates a `USER`-role account, returns a JWT.
- **Login** (`POST /api/auth/login`) — looks up the user by email, verifies the password against the bcrypt hash, returns a JWT containing the user id (`sub`) and `role`.
- **Session restore** (`GET /api/auth/me`) — the frontend calls this on load if a token is present, so a page refresh doesn't lose the session; an invalid/expired token clears it and returns to a logged-out state.
- **Logout** — client-side only (JWT is stateless): the token is removed from `localStorage`.
- Passwords are never stored or returned in plaintext; `password_hash` is stripped from every serialized user.

## 9. Role-Based Access Control

Authorization is enforced **only** on the backend. Frontend route guards (`ProtectedRoute`, `RoleRoute`) exist purely to redirect users to the right page and hide irrelevant navigation — they are a UX convenience, not a security boundary. A malicious client that skips the UI entirely and calls the API directly is still blocked by the same middleware every real request goes through:

- `authenticate_user` — validates the JWT, attaches the current user to the request, returns `401` for a missing/invalid/expired token.
- `require_role(*roles)` / `require_admin` / `require_sales_person` / `require_admin_or_sales` — return `403` if the authenticated user's role isn't allowed.
- Product ownership is re-checked inside the controller on every write (`PUT`/`DELETE /api/products/<id>`): an `ADMIN` may act on any product, a `SALES_PERSON` only on a product whose `owner_id` matches their own id.

## 10. Product CRUD

- `GET /api/products`, `GET /api/products/<id>` — public, no auth required.
- `POST /api/products` — `ADMIN` or `SALES_PERSON` only; accepts either `multipart/form-data` with an `image` file (uploaded to Cloudinary) or JSON with an `image_url`.
- `PUT /api/products/<id>`, `DELETE /api/products/<id>` — `ADMIN` (any product) or the owning `SALES_PERSON` only; any other caller gets `403`.

## 11. Cloudinary Image Upload

Flow: frontend sends the image file as `multipart/form-data` → Flask validates extension (`png/jpg/jpeg/gif/webp`) and size (≤5MB) → uploads the file stream directly to Cloudinary via `cloudinary.uploader.upload` → Cloudinary returns a `secure_url` → **only that URL string** is written to the `products.image_url` field in MongoDB. No image bytes ever touch MongoDB or the local filesystem.

The integration code itself is implemented and unit/integration tested (extension/size validation, error handling, and an end-to-end `/api/products` multipart request confirming only a URL string lands in MongoDB — see `backend/tests/test_cloudinary.py`) by mocking the Cloudinary network boundary. **A real upload against a live Cloudinary account has not been performed in this environment** because no `CLOUDINARY_*` credentials are configured — see [Known Limitations](#33-known-limitations).

## 12. Search and Filters

`GET /api/products` accepts:
- `search` — case-insensitive regex match against `name` and `description`
- `category` — exact (case-insensitive) category match
- `minPrice` / `maxPrice` — numeric range filter on `price`
- filters combine (`?search=shirt&category=Apparel&minPrice=100&maxPrice=1000`)

The frontend always re-queries this endpoint on every filter change — it never filters an already-loaded product list client-side.

## 13. Wishlist

`GET/POST /api/wishlist`, `DELETE /api/wishlist/<product_id>` — all require authentication and are scoped to the requesting user via their JWT. Adding an already-wishlisted product is a no-op (`$addToSet` server-side, and the frontend also skips the redundant request client-side).

## 14. Cart

`GET/POST /api/cart`, `PUT/DELETE /api/cart/<product_id>` — one cart per user, quantity increases/decreases/direct-set all validate against current product stock (`409 Conflict` if insufficient), and the response always includes computed `item_count`, `subtotal`, and `total`.

## 15. Razorpay Test Payment

1. User clicks **Pay Now** on the Checkout page.
2. Frontend calls `POST /api/payment/create-order` (no amount is sent).
3. Backend reads the user's cart from MongoDB, re-validates stock, and **computes the total from the current product prices in the database** — the amount the frontend displayed is never trusted or sent.
4. Backend creates a Razorpay order for that trusted amount and stores a snapshot (`pending_payments`) of exactly what is being purchased.
5. Frontend opens Razorpay Checkout using the amount/order id **returned by the backend**.
6. User completes the test-mode payment; Razorpay returns `razorpay_order_id`, `razorpay_payment_id`, `razorpay_signature`.
7. Frontend forwards those three values to `POST /api/payment/verify`.
8. Backend recomputes the HMAC-SHA256 signature itself and compares it — **only if it matches** does it create the real `orders` document (from the trusted snapshot, not from anything the frontend sent), decrement stock, and clear the cart.
9. An invalid/missing signature returns `400` and no order is created.

**Current limitation:** this flow is fully implemented on both ends and covered by backend tests (`test_payment.py`, including a mocked invalid-signature case that verifies no order is created), and was exercised manually in the browser up to the point where the backend genuinely calls the real Razorpay API — but no `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` are configured in this environment, so a complete real test-mode transaction has not been performed. See [Known Limitations](#33-known-limitations).

## 16. Order Management

- `GET /api/orders` — `USER` sees only their own orders; `SALES_PERSON` sees only orders containing at least one of their products (with only their own line items in the response); `ADMIN` sees everything.
- `GET /api/orders/<id>` — same scoping, `403` if the requester isn't entitled to see that order.
- `PUT /api/admin/orders/<id>/status` — `ADMIN` only; status is one of `Pending, Confirmed, Processing, Shipped, Delivered, Cancelled`.

## 17. Admin Dashboard

`GET /api/admin/stats` returns total users, total products, total (paid) orders, total sales, and the 5 most recent orders — all computed live from MongoDB. Admin also gets full product management (any seller), user management (role changes), and order management (status updates) pages.

## 18. Sales Person Dashboard

`GET /api/sales/stats` returns the count of the seller's own products, orders containing their products, units sold, and their own sales total — scoped entirely to `owner_id`/`seller_id` matching the logged-in seller, so one seller never sees another seller's numbers.

## 19. User Dashboard

Shows cart item count/total, wishlist count, order count, and recent orders — all pulled from the same real `GET /api/cart`, wishlist, and `GET /api/orders` endpoints the rest of the app uses.

## 20. Local Installation

Prerequisites: Python 3.11+, Node.js 18+, a MongoDB instance (local `mongod` or MongoDB Atlas).

```bash
git clone <your-fork-url>
cd ecommerce-internship-task
```

## 21. Backend Setup

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env      # Windows
# cp .env.example .env      # macOS/Linux
# then edit .env with your real MongoDB/Cloudinary/Razorpay values

python seed.py               # optional: creates 3 test accounts + sample products
python run.py                 # starts the API on http://localhost:5000
```

## 22. Frontend Setup

```bash
cd frontend
npm install
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
# VITE_API_URL=http://localhost:5000/api

npm run dev                   # starts Vite dev server on http://localhost:5173
```

## 23. MongoDB Setup

**Option A — MongoDB Atlas (recommended for deployment):**
1. Create a free cluster at [mongodb.com/cloud/atlas](https://mongodb.com/cloud/atlas).
2. Create a database user and note the username/password.
3. Under Network Access, allow your IP (or `0.0.0.0/0` for Render to reach it).
4. Copy the connection string into `MONGODB_URI` in `backend/.env`, e.g. `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/ecommerce_internship?retryWrites=true&w=majority`.

**Option B — Local MongoDB:** install MongoDB Community Server, run `mongod`, and use `MONGODB_URI=mongodb://localhost:27017` (the default).

No manual schema/collection creation is needed — collections and indexes are created automatically on first app startup (`_ensure_indexes()` in `app/__init__.py`).

## 24. Cloudinary Setup

1. Create a free account at [cloudinary.com](https://cloudinary.com).
2. From the Dashboard, copy your **Cloud name**, **API Key**, and **API Secret**.
3. Set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` in `backend/.env`.
4. No bucket/folder setup is required — the backend uploads into an `ecommerce_internship/products` folder automatically, which Cloudinary creates on first upload.

## 25. Razorpay Setup

1. Create a free account at [dashboard.razorpay.com](https://dashboard.razorpay.com) (Test Mode is enabled by default for new accounts).
2. Go to **Settings → API Keys** and generate a **Test Mode** key pair.
3. Set `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in `backend/.env`.
4. Set the same `RAZORPAY_KEY_ID` (public key only — never the secret) as `VITE_RAZORPAY_KEY_ID` in `frontend/.env`.
5. Use Razorpay's published test card `4111 1111 1111 1111`, any future expiry, any CVV, to complete a test payment.

## 26. Environment Variables

**backend/.env** (see `backend/.env.example`):

```
PORT=5000
FLASK_ENV=development

MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/ecommerce_internship?retryWrites=true&w=majority
MONGODB_DB_NAME=ecommerce_internship

JWT_SECRET=replace-with-a-long-random-secret
JWT_EXPIRES_HOURS=24

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=

CLIENT_URL=http://localhost:5173
```

**frontend/.env** (see `frontend/.env.example`):

```
VITE_API_URL=http://localhost:5000/api
VITE_RAZORPAY_KEY_ID=
```

Neither `.env` file is committed to Git (`.gitignore` excludes both); only the `.env.example` templates are tracked.

## 27. Running the Application

1. Start MongoDB (if running locally).
2. `cd backend && python run.py` → API on `http://localhost:5000`.
3. `cd frontend && npm run dev` → app on `http://localhost:5173`.
4. Optionally `python backend/seed.py` first to get the 3 test accounts and 3 sample products.

## 28. API Overview

All routes below are prefixed with `/api`. Protected routes require `Authorization: Bearer <token>`.

**Auth**
```
POST   /auth/register
POST   /auth/login
GET    /auth/me                         (auth)
```

**Products**
```
GET    /products                        (public; ?search=&category=&minPrice=&maxPrice=)
GET    /products/<id>                   (public)
POST   /products                        (ADMIN or SALES_PERSON)
PUT    /products/<id>                   (ADMIN, or owning SALES_PERSON)
DELETE /products/<id>                   (ADMIN, or owning SALES_PERSON)
```

**Wishlist**
```
GET    /wishlist                        (auth)
POST   /wishlist                        (auth)
DELETE /wishlist/<product_id>           (auth)
```

**Cart**
```
GET    /cart                            (auth)
POST   /cart                            (auth)
PUT    /cart/<product_id>               (auth)
DELETE /cart/<product_id>               (auth)
```

**Orders**
```
GET    /orders                          (auth; scoped by role)
GET    /orders/<id>                     (auth; scoped by role)
```

**Payment**
```
POST   /payment/create-order            (auth)
POST   /payment/verify                  (auth)
```

**Admin**
```
GET    /admin/users                     (ADMIN)
PUT    /admin/users/<id>/role           (ADMIN)
GET    /admin/orders                    (ADMIN)
PUT    /admin/orders/<id>/status        (ADMIN)
GET    /admin/stats                     (ADMIN)
```

**Sales**
```
GET    /sales/products                  (SALES_PERSON)
GET    /sales/orders                    (SALES_PERSON)
GET    /sales/stats                     (SALES_PERSON)
```

**Health**
```
GET    /health                          (public)
```

## 29. Test Credentials

Created by `python backend/seed.py` (safe to re-run; skips accounts that already exist):

| Role | Email | Password |
|---|---|---|
| ADMIN | admin@example.com | Admin@123 |
| SALES_PERSON | sales@example.com | Sales@123 |
| USER | user@example.com | User@1234 |

These are placeholder development credentials only — never real personal credentials, and not meant to be used in a production deployment.

## 30. Screenshots

_Not included in this submission. The application was verified interactively via automated browser testing during development (see IMPLEMENTATION_REPORT.md, Testing section) rather than captured as static images here._

## 31. Deployment

**Live Frontend URL:** Not deployed yet
**Live Backend URL:** Not deployed yet

### Backend → Render

1. Push this repository to GitHub.
2. In the Render dashboard: **New → Web Service**, connect the GitHub repo.
3. **Root Directory:** `backend`
4. **Runtime:** Python 3
5. **Build Command:** `pip install -r requirements.txt`
6. **Start Command:** `gunicorn run:app --bind 0.0.0.0:$PORT` (also defined in `backend/Procfile`)
7. **Environment variables** (Render → Environment tab) — set all of:
   `MONGODB_URI`, `MONGODB_DB_NAME`, `JWT_SECRET`, `JWT_EXPIRES_HOURS`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `CLIENT_URL` (set this to your deployed Vercel URL once known; Render provides `PORT` automatically — do not set it manually).
8. Deploy, then verify with `GET https://<your-render-url>/api/health` → `{"status": "ok"}`.

### Frontend → Vercel

1. In the Vercel dashboard: **Add New → Project**, import the same GitHub repo.
2. **Root Directory:** `frontend`
3. **Framework Preset:** Vite (build command `npm run build`, output directory `dist` — Vercel detects these automatically for a Vite project). `frontend/vercel.json` is already included with a catch-all rewrite to `index.html`, which is required so refreshing/deep-linking a client-side route like `/products` doesn't 404.
4. **Environment variables** (Vercel → Settings → Environment Variables):
   `VITE_API_URL` = `https://<your-render-backend-url>/api`
   `VITE_RAZORPAY_KEY_ID` = your Razorpay test key id
5. Deploy, then update `CLIENT_URL` on Render to the resulting Vercel URL (comma-separate multiple origins if needed) and redeploy the backend so CORS allows it.

Once both are live, replace the two "Not deployed yet" lines above with the real URLs.

## 32. Feature Completion Summary

| Feature | Status | Implementation |
|---|---|---|
| Authentication | ✅ Complete | JWT + bcrypt, register/login/me, verified by 9 passing tests |
| RBAC | ✅ Complete | `authenticate_user` + `require_role` family enforced on every protected route; 8 passing RBAC tests |
| Product CRUD | ✅ Complete | Full CRUD with search/category/price filters; 14 passing tests |
| Product Ownership | ✅ Complete | Backend-enforced per-request; verified cross-seller denial tests pass |
| Cloudinary | ⚠️ Implemented, not verified against a live account | Upload code path + error handling tested at the network boundary; needs real `CLOUDINARY_*` credentials to verify an actual account upload |
| Search | ✅ Complete | Regex search on name/description via query param |
| Filters | ✅ Complete | Category + min/max price, combinable |
| Wishlist | ✅ Complete | Duplicate-safe, scoped per user; 4 passing tests |
| Cart | ✅ Complete | Quantity management + stock validation; 6 passing tests |
| Razorpay | ⚠️ Implemented, real transaction not yet completed | Trusted server-side amount, backend signature verification, order-only-after-verification logic implemented and unit-tested with mocked signatures; a real end-to-end test-mode transaction requires valid `RAZORPAY_KEY_ID`/`SECRET`, not configured here |
| Orders | ✅ Complete | Role-scoped visibility (own / relevant / all); 8 passing tests |
| Admin Dashboard | ✅ Complete | Live stats + product/user/order management, verified manually in-browser |
| Sales Dashboard | ✅ Complete | Own-product-scoped stats, verified manually in-browser |
| User Dashboard | ✅ Complete | Cart/wishlist/order summary, verified manually in-browser |
| Responsive UI | ✅ Complete | Tailwind responsive utilities throughout; mobile hamburger nav; not verified at a real narrow viewport in this session (see Known Limitations) |
| Testing | ✅ Complete | 61/61 backend pytest tests passing; `npm run build` passes with 0 errors; manual browser walkthrough of all three roles |

## 33. Known Limitations

- **Razorpay:** no real test-mode transaction has been completed — `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` are not configured in this environment. The full flow (trusted backend amount, signature verification, order-only-after-verification, cart clearing) is implemented and covered by tests with mocked Razorpay responses, and was exercised live up to the real Razorpay API call, which failed cleanly (sanitized error shown to the user) because no credentials are set.
- **Cloudinary:** no real account upload has been verified — `CLOUDINARY_*` credentials are not configured. The upload code path is tested at the network boundary (extension/size validation, success/error handling, confirming only a URL is persisted to MongoDB).
- **Mobile responsive layout:** implemented with standard Tailwind responsive classes and a mobile hamburger nav, but not verified at an actual narrow browser viewport during this session due to a tooling constraint (the browser automation tool's window resize did not change the effective screenshot viewport in this environment).
- **No pagination** on the products list — acceptable at the current seed-data scale; would be a straightforward addition (`?page=`/`?limit=`) if the catalog grew significantly.
- **No automated frontend test suite** (e.g. Vitest/RTL) — frontend correctness was verified via a live manual browser walkthrough against the real backend rather than automated component tests.
- **Not yet deployed** — see [Deployment](#31-deployment) for the exact steps to deploy; this repository is deployment-ready but no live URLs exist yet.
