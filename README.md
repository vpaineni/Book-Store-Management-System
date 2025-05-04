# Book-Store-Management-System

## Project Overview
The Bookstore Management System is a web application designed to streamline the operations of an online bookstore. This system allows both customers and administrators to interact with the platform, manage book inventories, place orders, and write reviews. The application leverages MongoDB as the database backend for storing books, users, orders, and reviews.

## Features
- User Authentication: Users can log in as either customers or administrators.
- Book Search: Customers can search for books by genre, author, or publisher.
- Order Management: Customers can place orders, and administrators can manage them.
- Review Management: Customers can add reviews for books.
- Admin Features: Admins can add, delete, and update book records, as well as manage orders.

## Technologies Used
1. Python: The backend logic is implemented using Python.
2. Streamlit: Used for building the web-based user interface.
3. MongoDB: A NoSQL database for storing book, user, order, and review data.
4. PyMongo: Python library used to interact with MongoDB.

## Project Structure
final.py: The main Python code for running the application. This file contains the logic for user authentication, book management, order processing, and review handling.

data.json: Contains the initial dataset for MongoDB to populate the database with books, users, and other necessary data.

## Setup Instructions
### Prerequisites
1. MongoDB: Make sure you have MongoDB installed and running locally.
2. Python 3.x: Ensure Python 3.x is installed on your machine.

### Installation
1. Clone this repository
2. Install required Python libraries
3. Set up MongoDB
4. Create a new database named BookstoreDB in MongoDB
5. Import the data from .json file into the appropriate collections (Books, Users, Orders, Reviews)
6. Run the application

### MongoDB Setup
1. Database Name: BookstoreDB
2. Collections:
   - Books: Stores details about each book.
   - Users: Stores information about users, including customers and administrators.
   - Orders: Captures order details.
   - Reviews: Stores reviews for books.

## Application Usage
1. Customers can:
   - Browse and search for books.
   - Place orders for books.
   - Write and view reviews for books.

2. Admins can:
   - Add, delete, and update books in the inventory.
   - Manage orders placed by customers.
   - View and manage customer reviews.

## Future Enhancements
- Integration with a payment gateway to allow users to complete purchases.
- Implementation of a recommendation system based on user activity and book reviews.
- Addition of more granular user roles for content and inventory management.
