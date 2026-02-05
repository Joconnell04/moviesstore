# Movies Store

A full-featured e-commerce web application built with Django that allows users to browse, review, and purchase movies. The platform includes a shopping cart system, user authentication, and a petition feature for requesting new movies to be added to the store.

## Project Overview

This project was developed as a Django-based web application to provide a complete online movie store experience. Users can browse a catalog of movies, read and write reviews, manage a shopping cart, place orders, and participate in community petitions for adding new movies to the store.

## Key Features

### Movie Browsing and Search
- Browse complete movie catalog with detailed information
- Search functionality to find movies by title
- Individual movie pages displaying price, description, and image
- User reviews and ratings visible on each movie page

### User Authentication System
- User registration with validation
- Secure login and logout functionality
- Password validation following Django best practices
- Session management for authenticated users

### Shopping Cart
- Add movies to cart with quantity selection
- View cart contents with price calculations
- Modify cart quantities or clear entire cart
- Session-based cart storage that persists across page visits

### Order Management
- Complete checkout process for authenticated users
- Order history tracking for each user
- Detailed order information including items and total cost
- Order confirmation display after successful purchase

### Review System
- Authenticated users can write reviews for movies
- Edit and delete own reviews
- View all reviews for a specific movie
- Top comments page showing most recent reviews across all movies

### Petition Feature
- Community-driven feature for requesting new movies
- Users can create petitions for movies they want added
- Yes voting system for showing support
- View all active petitions with vote counts
- One vote per user per petition enforcement

### Checkout Feedback
- Post-purchase feedback collection
- Optional user identification for feedback
- Public feedback viewing page
- Anonymous feedback support

## System Architecture

### Application Structure

The project follows Django's MTV (Model-Template-View) architecture and is organized into five main Django apps:

#### 1. Home App
Handles the main landing page, about page, and feedback functionality. Serves as the entry point for the application.

#### 2. Movies App
Core functionality for movie management and reviews:
- Movie model storing product information (name, price, description, image)
- Review model with foreign keys to both Movie and User
- Views for listing, searching, and displaying individual movies
- CRUD operations for reviews with authentication checks

#### 3. Accounts App
Manages user authentication and account features:
- Custom user creation forms with enhanced validation
- Login and logout views
- Order history page for viewing past purchases
- Integration with Django's built-in User model

#### 4. Cart App
Implements shopping cart functionality:
- Session-based cart storage
- Order and Item models for purchase tracking
- Cart total calculation utilities
- Add to cart, view cart, and checkout views

#### 5. Petitions App
Community feature for movie requests:
- Petition model for storing movie requests
- PetitionVote model with unique constraint per user
- Class-based views (ListView, DetailView, CreateView)
- Vote counting and display logic

### Database Schema

The application uses SQLite for development with the following key models:

**Movie**
- Primary model for the store catalog
- Fields: id, name, price, description, image
- Referenced by Review and Item models

**Review**
- Links movies with user comments
- Fields: id, comment, date, movie_id (FK), user_id (FK)
- Cascade deletion when movie or user is deleted

**Order**
- Represents completed purchases
- Fields: id, total, date, user_id (FK)
- Parent model for order items

**Item**
- Individual items within an order
- Fields: id, price, quantity, order_id (FK), movie_id (FK)
- Captures price at time of purchase

**Petition**
- Movie requests from users
- Fields: title, proposed_movie_title, reason, created_by (FK), created_at
- Parent model for petition votes

**PetitionVote**
- Individual votes on petitions
- Fields: petition_id (FK), voter_id (FK), yes, voted_at
- Unique constraint on (petition, voter) pair

**CheckoutFeedback**
- Post-purchase customer feedback
- Fields: name (optional), message, created
- Independent model for feedback collection

### Design Patterns and Principles

**Separation of Concerns**: Each Django app handles a specific domain of functionality, making the codebase modular and maintainable.

**DRY Principle**: Template inheritance using base.html reduces code duplication across views. Utility functions like calculate_cart_total centralize business logic.

**Authentication Decorators**: The @login_required decorator ensures proper access control for sensitive operations like purchasing and reviewing.

**Session Management**: Cart data is stored in Django sessions, allowing guest browsing while maintaining cart state before authentication.

**Foreign Key Relationships**: Database integrity is maintained through proper use of foreign keys with appropriate on_delete behaviors (CASCADE).

**Template Inheritance**: Base templates provide consistent layout and navigation across the application.

**Class-Based Views**: The petitions app demonstrates the use of Django's class-based views (ListView, DetailView, CreateView) for cleaner, more reusable code.

**Atomic Operations**: Database constraints like unique_together prevent duplicate votes and maintain data integrity.

## Technology Stack

- **Backend Framework**: Django 5.0
- **Database**: SQLite (development)
- **Template Engine**: Django Template Language
- **Authentication**: Django's built-in authentication system
- **Static Files**: Django static files management
- **Media Storage**: Local filesystem for uploaded images

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd moviesstore
```

2. Install dependencies:
```bash
pip install django pillow
```

3. Apply database migrations:
```bash
python manage.py migrate
```

4. Create a superuser for admin access:
```bash
python manage.py createsuperuser
```

5. Run the development server:
```bash
python manage.py runserver
```

6. Access the application at `http://localhost:8000`

### Admin Panel

Access the Django admin interface at `http://localhost:8000/admin` to manage:
- Movies (add, edit, delete)
- Users and authentication
- Orders and order items
- Reviews
- Petitions and votes
- Feedback entries

## URL Structure

- `/` - Home page
- `/movies/` - Movie catalog
- `/movies/<id>/` - Individual movie details
- `/movies/<id>/review/create/` - Create review
- `/movies/<id>/review/<review_id>/edit/` - Edit review
- `/movies/<id>/review/<review_id>/delete/` - Delete review
- `/movies/top-comments/` - Recent reviews
- `/accounts/login/` - User login
- `/accounts/signup/` - User registration
- `/accounts/logout/` - User logout
- `/accounts/orders/` - Order history
- `/cart/` - Shopping cart
- `/cart/add/<id>/` - Add to cart
- `/cart/purchase/` - Checkout
- `/cart/clear/` - Clear cart
- `/petitions/` - List all petitions
- `/petitions/<pk>/` - Petition details
- `/petitions/create/` - Create new petition
- `/petitions/<pk>/vote/` - Vote on petition
- `/about/` - About page
- `/feedback/` - View feedback
- `/feedback/submit/` - Submit feedback
- `/admin/` - Admin panel

## Security Considerations

- Secret key should be changed in production
- DEBUG mode should be disabled in production
- ALLOWED_HOSTS should be configured for production deployment
- Password validators enforce strong password requirements
- CSRF protection enabled via middleware
- Login requirements enforced on sensitive operations
- User authorization checks prevent unauthorized modifications

## Future Enhancements

Potential improvements for the application:
- Payment gateway integration for real transactions
- Email notifications for order confirmations
- Advanced search with filters (price range, genre)
- Movie ratings system (star ratings)
- Wishlist functionality
- User profiles with avatars
- Administrative dashboard for sales analytics
- RESTful API for mobile app integration
- Social media sharing for movies and petitions
- Pagination for movie listings

## Development Notes

The project uses Django's default SQLite database for development. For production deployment, consider migrating to PostgreSQL or MySQL for better performance and scalability.

Static files are configured to be served from the `moviesstore/static/` directory during development. In production, use a proper static file server or CDN.

Media files (movie images) are stored in the `media/` directory. Ensure proper permissions and backup strategies for production environments.

## License

This project is for educational purposes.
