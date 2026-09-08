Role-Based E-Commerce Platform

A full-stack e-commerce platform with role-based access control, product management, secure test payments, and order management.

1. Project Overview

This project is a full-stack role-based e-commerce web application developed as part of a Full Stack Developer Internship Task.

The application supports three roles:

Admin – manages products, users, roles, orders, and sales information.

Sales Person – manages only their own products and views orders containing their products.

User – browses products, searches and filters products, uses wishlist and cart, makes payments, and views personal orders.

The application integrates Cloudinary for product images and Razorpay Test Mode for payment processing.

2. Key Features

User registration and login

JWT authentication

bcrypt password hashing

Backend role-based access control

Product CRUD and ownership validation

Product search and filters

Cloudinary image upload

Wishlist

Shopping cart and quantity management

Razorpay Test Mode payment

Payment signature verification

Order creation and order history

Admin user and role management

User and Sales Person profile update

Password show/hide toggle

Admin, Sales Person, and User dashboards

Sales Person My Sales calculation

3. Technology Stack

Layer

Technology

Purpose

Frontend

React.js

User interface

Frontend Tool

Vite

Development and production build

Styling

Tailwind CSS

Responsive UI

Language

JavaScript

Frontend logic

Backend

Python + Flask

REST APIs and business logic

Database

MongoDB

Application data

Database Driver

PyMongo

MongoDB connection

Authentication

JWT

Secure authentication

Password Security

bcrypt

Password hashing

Image Storage

Cloudinary

Product image storage

Payment

Razorpay Test Mode

Payment testing

Backend Hosting

Render

Backend deployment

Frontend Hosting

Vercel

Frontend deployment

Version Control

Git + GitHub

Source code management

4. Project Architecture

User
  |
  v
React + Vite + Tailwind CSS
  |
  | REST API
  v
Flask Backend
  |
  +---- JWT Authentication
  +---- Role-Based Access Control
  +---- Product APIs
  +---- Cart & Wishlist APIs
  +---- Payment APIs
  |
  v
MongoDB

External Services:
  +---- Cloudinary -> Product Images
  +---- Razorpay -> Test Payments

The frontend communicates with the Flask backend through REST APIs. The backend handles authentication, role permissions, business logic, products, cart, wishlist, payments, and orders. MongoDB stores application data. Cloudinary stores product images and Razorpay handles Test Mode payments.

5. User Roles and Permissions

Role

Main Permissions

Admin

Manage products, users and roles, view/update all orders, and view sales information

Sales Person

Add, edit, and delete only their own products; view orders containing their products; view their sales

User

Browse, search/filter, wishlist, cart, payment, own orders, and own profile update

Role restrictions are enforced on the backend, not only by hiding frontend buttons.

6. Authentication

The application uses JWT-based authentication and bcrypt password hashing.

User enters email and password
        |
        v
Backend checks user
        |
        v
Password verified using bcrypt
        |
        v
JWT token generated
        |
        v
Frontend stores authentication state
        |
        v
Protected pages and APIs can be accessed

Passwords are not stored as plain text.

7. Product Management

The application provides Product CRUD:

Create

Read

Update

Delete

Admin can manage all products. A Sales Person can manage only their own products. Backend ownership validation prevents a Sales Person from modifying another seller's product.

Cloudinary Image Flow

Select Image
    ↓
Frontend
    ↓
Flask Backend
    ↓
Cloudinary
    ↓
Image URL returned
    ↓
Only URL stored in MongoDB

The raw image file is not stored in MongoDB.

8. Search, Filters, Wishlist and Cart

Search & Filters: Users can search products and filter available products.

Wishlist: Users can add, remove, and view wishlist products.

Cart: Users can add products, update quantities, remove items, and view the total amount.

9. Razorpay Payment

Razorpay Test Mode is used.

Cart
  ↓
Checkout
  ↓
Backend creates Razorpay order
  ↓
Razorpay Checkout
  ↓
Test payment
  ↓
Backend verifies payment signature
  ↓
Application order created
  ↓
Cart cleared

The final application order is created only after successful payment verification. No real money is used because Test Mode is enabled.

10. Order Management

Users can view their own orders.

Sales Persons can view orders containing their own products.

Admins can view all orders and update order status.

Typical status flow:

Pending → Confirmed → Processing → Shipped → Delivered

An order can also be marked as Cancelled when applicable.

11. User Management

Admin can view registered users and manage their roles.

The application also supports safe profile management. Users and Sales Persons can update their own profile information.

Sensitive information such as password hashes and service secrets is never displayed.

12. Dashboards

Admin Dashboard

Products

Users

Orders

Sales information

Sales Person Dashboard

Own products

Product management

Related orders

My Sales

User Dashboard

Profile

Wishlist

Cart

Orders

My Sales counts the value of the Sales Person's own products, including correct handling of orders containing products from multiple sellers.

13. Security

JWT authentication

bcrypt password hashing

Backend RBAC

Product ownership validation

Protected APIs

Environment variables for secrets

Razorpay signature verification

.env files excluded from Git

Raw image files are not stored in MongoDB

14. Testing

The backend test suite covers authentication, RBAC, Product CRUD, ownership, search/filters, Cloudinary, wishlist, cart, Razorpay, and order visibility.

Verified backend result: 61/61 tests passed.

The frontend production build also completes successfully.

15. Setup and Installation

Backend

cd backend
python -m venv venv

Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Create backend/.env using the environment variables below and start the Flask server using the project's configured command.

Frontend

cd frontend
npm install
npm run dev

Create frontend/.env using the variables below.

16. Environment Variables

Backend .env

MONGO_URI=
JWT_SECRET=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
RAZORPAY_KEY_ID=
RAZORPAY_KEY_SECRET=
CORS_ORIGINS=

Frontend .env

VITE_API_URL=
VITE_RAZORPAY_KEY_ID=

A .env.example file is provided as a template.

Never commit real .env files, passwords, API keys, API secrets, or database credentials to GitHub.

17. Test Credentials

Role

Email

Password

Admin

admin@example.com

********

Sales Person

sales@example.com

********

User

user@example.com

********

Replace the masked passwords with the actual evaluation passwords before final submission if they are intended to be shared with the evaluator.

18. Feature Completion Summary

Feature

Implementation Summary

Authentication

JWT authentication with bcrypt password hashing

Role-Based Access

Backend-enforced permissions for Admin, Sales Person, and User

Product CRUD

Product creation, viewing, editing, and deletion with ownership validation

Cloudinary

Images are uploaded to Cloudinary and only image URLs are stored in MongoDB

Search & Filters

Product search and filtering through backend APIs

Wishlist

Users can add and remove products from their wishlist

Cart

Add, remove, and quantity update functionality

Razorpay

Test Mode payment with backend order creation and signature verification

Orders

Orders are created after successful payment verification

User Management

Admin can view users and manage their roles

Profile Update

Users and Sales Persons can update their own profiles

Dashboards

Separate dashboards for Admin, Sales Person, and User

My Sales

Sales Person sees sales generated from their own products

Testing

61/61 backend tests passed

19. Screenshots

Add 2–3 final screenshots before submission.

Recommended screenshots:

Admin Dashboard / User Management

Product Listing / Product Management

Order Management / Razorpay Checkout

Recommended folder:

docs/screenshots/

20. Live Application

Frontend — Vercel

[Add live Vercel URL after deployment]

Backend — Render

[Add live Render URL after deployment]

21. GitHub Workflow

The project uses Git and GitHub for version control.

Development was performed using a feature branch and merged into the main branch through a Pull Request.

main
  |
  +---- feature/react-frontend
              |
              v
         Development
              |
              v
        Pull Request
              |
              v
            Merge
              |
              v
            main

22. Future Improvements

AI Shopping Chatbot

An AI chatbot could help users find products, answer product questions, compare products, and provide shopping assistance.

AI Product Recommendation

A recommendation system could suggest products based on previous purchases, recently viewed products, wishlist items, cart items, categories, and similar products.

AI-Based Search

Users could search using natural language, for example:

I need headphones for gaming under ₹3,000.

The system could understand the requirement and show relevant products.

Product Comparison

Users could compare products by price, features, specifications, and ratings.

Voice Shopping Assistant

Users could search for products using voice commands.

Advanced Sales Analytics

The Admin dashboard could provide daily sales, monthly sales, revenue trends, best-selling products, and category statistics.

Order Tracking

Future versions could provide detailed order tracking from confirmation to delivery.

Notifications

Future notifications could include order confirmation, payment confirmation, status updates, and wishlist alerts.

These AI and advanced features are future improvements and are not claimed as current implemented features.

23. Known Limitations

Razorpay is configured in Test Mode for internship evaluation.

AI chatbot and AI recommendation features are not part of the current implementation.

Advanced real-time delivery tracking is not currently implemented.

Large-scale production features such as advanced caching and distributed services can be added in future versions.

24. Conclusion

The Role-Based E-Commerce Platform demonstrates a complete full-stack web application using React, Flask, and MongoDB.

It includes secure authentication, backend role-based access control, product CRUD, Cloudinary image uploads, search and filters, wishlist, shopping cart, Razorpay Test Mode payments, order management, user management, and role-specific dashboards.

The project can be extended in the future with AI-powered shopping assistance, product recommendations, natural-language search, voice shopping, advanced analytics, notifications, and real-time order tracking.
