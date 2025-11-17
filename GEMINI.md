# Project Overview

This is a Django-based e-commerce backend application. It provides a comprehensive set of APIs for managing various aspects of an online store, including:

*   **User Authentication:** Secure user registration, login, profile management, and logout using JWT.
*   **Product and Inventory Management:** APIs for creating, listing, retrieving, updating, and deleting products and categories, with features like pagination, searching, and low-stock alerts.
*   **Order Management:** Functionality for creating new orders, listing user-specific orders, retrieving order details, updating order statuses (admin only), and cancelling pending orders.
*   **Activity Logging & Audit Trail:** A system to log significant user and system actions, providing an audit trail for various activities.
*   **Analytics & Reports:** APIs for dashboard overviews, sales analytics (daily, weekly, monthly), top-selling products, revenue trends, and order status distribution.
*   **Cron Jobs:** Scheduled background tasks for daily sales aggregation, low stock alerts, and pending order reminders.

The project leverages Django Rest Framework for building robust RESTful APIs, Django Simple JWT for secure authentication, and Django APScheduler for efficient scheduling of background tasks.

## Building and Running

The project uses `uv` for dependency management and running commands.

*   **Install dependencies:**
    ```bash
    uv sync
    ```

*   **Apply database migrations:**
    ```bash
    uv run python manage.py migrate
    ```

*   **Create a superuser (admin):**
    ```bash
    uv run python manage.py createsuperuser
    ```

*   **Run the development server:**
    ```bash
    uv run python manage.py runserver
    ```
    The server will start, and the scheduled jobs will also be initialized.

## Development Conventions

*   **API Framework:** Django Rest Framework is used for building RESTful APIs.
*   **API Views:** All API endpoints are implemented using `rest_framework.views.APIView` directly, with manual handling of serialization, validation, and responses, rather than relying on DRF's generic views.
*   **Authentication:** JWT (JSON Web Tokens) authentication is implemented using `djangorestframework-simplejwt`.
*   **Custom User Model:** A custom `UserProfile` model extends Django's `AbstractUser` to include additional user-specific fields.
*   **Activity Logging:** A custom `ActivityLog` model and a `log_activity` utility function are used to record significant user and system actions, providing an audit trail.
*   **Cron Jobs:** Background tasks (daily sales aggregation, low stock alerts, pending order reminders) are scheduled using `django-apscheduler` and defined in `analytics/jobs.py`. These jobs are initialized when the Django app is ready.
*   **Database:** PostgreSQL is used as the primary database.
*   **Environment Variables:** Sensitive information and database credentials are managed using environment variables loaded via `python-dotenv`.
