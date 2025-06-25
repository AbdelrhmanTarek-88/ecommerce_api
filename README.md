# E-Commerce API Project

## Overview

This project is a fully functional e-commerce API built using **Django REST Framework (DRF)**. It provides a backend for an online store with features like user authentication, product management, order processing, favorites, cart management. The API is designed to be scalable, secure, and easy to integrate with a frontend application.

### Features

- **Authentication & Authorization**: JWT-based authentication for secure user access.
- **User Management**: Register, login, update profiles, and manage user roles (admin/users).
- **Product Management**: Create, update, delete, and review products (admin and authenticated users).
- **Order Management**: Create orders, track order status, and manage payments.
- **Favorites & Cart**: Add/remove products to favorites and cart for a seamless shopping experience.
- **API Testing**: Comprehensive test suite with sample requests and responses in `/docs/` or `/swager/`.

## Tech Stack

- **Backend Framework**: Django REST Framework
- **Database**: SQLite (default, can be configured for PostgreSQL)
- **Authentication**: Django JWT (JSON Web Tokens)

- **Dependencies**: Python 3.9+, Django 4.2+, DRF 3.14+

## Installation

Follow these steps to set up the project locally:

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtualenv (recommended)
- ecommerce-api/
- │
- ├── authn/ # Authentication module
- ├── users/ # User management module
- ├── products/ # Product management module
- ├── orders/ # Order processing module
- ├── favorites/ # Favorites management module
- ├── cart_item/ # Cart management module
- ├── docs/ # API documentation
- ├── manage.py # Django management script
- └── requirements.txt # Project dependencies

## Environment Variables (.env)

- Create a `.env` file in the root directory of the project and define the following variables:

- You can switch between **development** and **production** modes by setting the `ENVIRONMENT` variable

```env

- SECRET_KEY=your-secret-key
- DATABASE_URL=sqlite:///db.sqlite3
- ALLOWED_HOSTS=127.0.0.1,localhost
- CORS_ALLOWED_ORIGINS=https://your-frontend-site.com,http://localhost:3000
- ENVIRONMENT=production

```

- If you want to test the project with **production environment**, make sure to run the following command:

```bash
python manage.py collectstatic
python manage.py runserver --insecure

```

## API Endpoints

### The API is organized into the following modules:

- Test: Swager (All APIs)
- Authentication: /api/authn/ (e.g., login, register, refresh token)
- Users: /api/users/ (e.g., profile management, user details)
- Products: /api/products/ (e.g., product listing, reviews)
- Orders: /api/orders/ (e.g., create order, track order status)
- Favorites: /api/favorites/ (e.g., add/remove favorites)
- Cart: /api/cart/ (e.g., manage cart items)
