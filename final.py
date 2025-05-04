import streamlit as st
from datetime import date
from pymongo import MongoClient

# MongoDB connection URI
MONGO_URI = "mongodb://localhost:27017/"

# Create a MongoDB client
client = MongoClient(MONGO_URI)

# Access the database
db = client["BookstoreDB"]

# Access collections
books_collection = db["Books"]
orders_collection = db["Orders"]
reviews_collection = db["Reviews"]
users_collection = db["Users"]

# Fetch data
books_data = list(books_collection.find())
users_data = list(users_collection.find())
orders_data = list(orders_collection.find())
reviews_data = list(reviews_collection.find())

# Initialize session state if not already set
for key in ['user_type', 'user_id', 'user_name', 'authenticated', 'edit_mode', 'reset', 'submitted', 'add_mode', 'delete_mode']:
    if key not in st.session_state:
        st.session_state[key] = None

# Add the new 'creating_account' flag
if 'creating_account' not in st.session_state:
    st.session_state['creating_account'] = False

def handle_logout():
    """ Handle user logout """
    st.session_state['authenticated'] = False
    st.session_state['user_type'] = None
    st.session_state['user_id'] = None
    st.session_state['user_name'] = None
    st.session_state['reset'] = True
    st.session_state['edit_mode'] = False
    st.session_state['search'] = False
    st.session_state['order'] = False
    st.session_state['manage_books'] = False
    st.session_state['viewing_orders'] = False
    st.session_state['add_mode'] = False
    st.session_state['delete_mode'] = False
    st.session_state['submitted'] = False

def set_user_type(user_type):
    """ Set the type of user (Customer or Admin) """
    st.session_state['user_type'] = user_type
    st.session_state['authenticated'] = False

def login_user(user_id):
    """ Simulate a login function with different authentication for admins and customers """
    if authenticate_user(user_id, st.session_state['user_type']):
        st.session_state['user_id'] = user_id
        st.session_state['authenticated'] = True
        st.session_state['search'] = st.session_state['user_type'] == "Customer"
        st.session_state['order'] = st.session_state['user_type'] == "Customer"
        st.session_state['manage_books'] = st.session_state['user_type'] == "Admin"
        st.session_state['viewing_orders'] = False
        st.session_state['edit_mode'] = False
        st.session_state['add_mode'] = False
        st.session_state['delete_mode'] = False
    else:
        st.session_state['authenticated'] = False
        st.error("Invalid User ID")

def authenticate_user(user_id, user_type):
    """ Check user credentials based on type """
    user_id = int(user_id)
    user = users_collection.find_one({"UserID": user_id, "UserType": user_type})
    if user:
        st.session_state['user_name'] = user['Username']
        return True
    return False

def create_account(user_type):
    """ Function to create a new customer or admin account without using a form """
    st.session_state['creating_account'] = True
    # Input fields
    name = st.text_input("Name", key="name_input")
    email = st.text_input("Email", key="email_input")
    new_id = st.text_input("ID", key="id_input")
    
    # Submit button
    if st.button("Create Account", key="create_account_button"):
        if name and email and new_id:
            handle_account_creation(user_type, name, email, new_id)
        else:
            st.error("All fields are required.")

def handle_account_creation(user_type, name, email, new_id):
    """ Function to handle the account creation process """
    try:
        new_id = int(new_id)  # Convert new_id to integer
        if not users_collection.find_one({"UserID": new_id}):
            add_account(user_type, name, email, new_id)
        else:
            st.error("User ID already exists. Please choose a different ID.")
    except ValueError:
        st.error("Invalid ID. Please enter a numeric value.")

def add_account(user_type, name, email, new_id):
    """ Function to create a new customer or admin account """
    new_user = {
        "UserID": int(new_id),  # Ensure new_id is already an integer here
        "Username": name,
        "Email": email,
        "UserType": user_type
    }
    # Insert the new user into the database
    users_collection.insert_one(new_user)
    st.success(f"{user_type} account created successfully!")
    login_user(new_id)

def display_login_or_create():
    """ Display login or create account based on session state """
    if st.session_state['creating_account']:
        create_account(st.session_state['user_type'])
    else:
        user_id = st.text_input(f"Enter {st.session_state['user_type']} ID", type="password")
        if st.button("Login"):
            login_user(user_id)
        if st.button("Create Account"):
            st.session_state['creating_account'] = True

def update_profile(user_id, user_type, name, email):
    """ Update customer or admin profile information in MongoDB """
    users_collection.update_one(
        {"UserID": user_id, "UserType": user_type},
        {"$set": {"Username": name, "Email": email}}
    )
    st.session_state['user_name'] = name

st.markdown("""
    <style>
    .book-card {
        border: 2px solid #ccc;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .book-title {
        font-size: 1.5em;
        font-weight: bold;
    }
    .book-details {
        font-size: 1em;
        margin-bottom: 10px;
    }
    .order-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .order-card h4 {
        margin: 0 0 10px;
    }
    .order-card p {
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

def display_user_dashboard():
    """ Display user dashboard with options to edit profile, view books, and manage orders """
    
    if st.session_state.get('authenticated', False):
        user_profile = users_collection.find_one({"UserID": int(st.session_state['user_id']), "UserType": st.session_state['user_type']})
        st.sidebar.write(f"Welcome, {st.session_state['user_name']}")
        
        # Sidebar buttons
        if st.sidebar.button("Home", key="home_button"):
            st.session_state.update({
                'search': st.session_state['user_type'] == "Customer",
                'order': st.session_state['user_type'] == "Customer",
                'manage_books': st.session_state['user_type'] == "Admin",
                'viewing_orders': False,
                'edit_mode': False,
                'add_mode': False,
                'delete_mode': False,
                'reviews': False
            })
        
        if st.sidebar.button("Edit Profile", key="edit_profile_button"):
            st.session_state.update({
                'edit_mode': True,
                'search': False,
                'order': False,
                'manage_books': False,
                'viewing_orders': False,
                'add_mode': False,
                'delete_mode': False,
                'reviews': False
            })

        if st.sidebar.button("Manage Orders", key="manage_orders_button"):
            st.session_state.update({
                'viewing_orders': True,
                'search': False,
                'order': False,
                'manage_books': False,
                'edit_mode': False,
                'add_mode': False,
                'delete_mode': False,
                'reviews': False
            })
            manage_orders(st.session_state['user_id'])

        if st.sidebar.button("Reviews", key="reviews_button"):
            st.session_state.update({
                'reviews': True,
                'search': False,
                'order': False,
                'manage_books': False,
                'viewing_orders': False,
                'edit_mode': False,
                'add_mode': False,
                'delete_mode': False
            })

        if st.sidebar.button("Logout", key="logout_button"):
            handle_logout()
            return  # Exit the function early to prevent further rendering

        if st.session_state.get('edit_mode', False):
            new_name = st.text_input("Name", value=user_profile['Username'], key="name_input")
            new_email = st.text_input("Email", value=user_profile['Email'], key="email_input")
            if st.button("Save Changes", key="save_changes_button"):
                update_profile(int(st.session_state['user_id']), st.session_state['user_type'], new_name, new_email)
                st.session_state['edit_mode'] = False
                st.success("Profile updated successfully!")
            return  # Stop further rendering after editing profile

        # Display the Customer or Admin dashboard based on user type
        if st.session_state['user_type'] == "Customer":
            
            if st.session_state.get('search', False):
                search_term = st.text_input("Enter search term", key="search_term_input")
                search_by = st.radio("Search by", options=["genre", "author", "publisher"], key="search_by_radio")
                search_active = bool(search_term)

                if search_active:
                    search_results = search_books(search_term, search_by)
                    if search_results:
                        st.subheader("Search Results")
                        cols = st.columns(3)
                        for index, book in enumerate(search_results):
                            with cols[index % 3]:
                                st.markdown(f"""
                                    <div class="book-card">
                                        <div class="book-title">{book['title']}</div>
                                        <div class="book-details">Author: {book['author']}</div>
                                        <div class="book-details">Price: ${book['price']}</div>
                                        <div class="book-details">Genre: {book['genre']}</div>
                                        <div class="book-details">Published Year: {book['published_year']}</div>
                                        <div class="book-details">Publisher: {book['publisher']}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                if st.button("Order Book", key=f"order_{book['BookID']}_search"):
                                    order_book(st.session_state['user_id'], book['BookID'], book['price'])
                    else:
                        st.warning("No books found.")
                else:
                    cols = st.columns(3)
                    for index, book in enumerate(books_data):
                        with cols[index % 3]:
                            st.markdown(f"""
                                <div class="book-card">
                                    <div class="book-title">{book['title']}</div>
                                    <div class="book-details">Author: {book['author']}</div>
                                    <div class="book-details">Price: ${book['price']}</div>
                                    <div class="book-details">Genre: {book['genre']}</div>
                                    <div class="book-details">Published Year: {book['published_year']}</div>
                                    <div class="book-details">Publisher: {book['publisher']}</div>
                                </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"Order Book {book['BookID']}", key=f"order_{book['BookID']}_display"):
                                order_book(st.session_state['user_id'], book['BookID'], book['price'])

            if st.session_state.get('reviews', False):
                display_reviews(st.session_state['user_id'])
                add_review(st.session_state['user_id'])

        elif st.session_state['user_type'] == "Admin":
            if st.session_state.get('manage_books', False):
                st.subheader("Manage Books:")
                cols = st.columns(2)

                with cols[0]:
                    if st.button("Delete Books", key="delete_books_button"):
                        st.session_state['delete_mode'] = True
                        st.session_state['add_mode'] = False  # Ensure add mode is turned off

                with cols[1]:
                    if st.button("Add Books", key="add_books_button"):
                        st.session_state['add_mode'] = True
                        st.session_state['delete_mode'] = False  # Ensure delete mode is turned off

                if st.session_state.get('delete_mode', False):
                    delete_books()

                if st.session_state.get('add_mode', False):
                    add_book()
            
            if st.session_state.get('reviews', False):
                display_reviews(st.session_state['user_id'])

def search_books(search_term, search_by):
    """ Search for books based on search term and search by criteria """
    query = {search_by: {"$regex": search_term, "$options": "i"}}
    return list(books_collection.find(query))

def delete_books():
    """Function to delete books from the database"""
    for book in books_data:
        cols = st.columns([1, 2, 1])
        with cols[1]:
            st.write(f"Title: {book['title']} | Author: {book['author']}")
        with cols[2]:
            if st.button(f"Delete Book {book['BookID']}", key=str(book['BookID'])):
                # Delete book from MongoDB
                books_collection.delete_one({"BookID": book['BookID']})
                st.success("Book deleted successfully!")
                st.session_state["deleted"] = True

def add_book():
    """Function to add books to the database"""  
    st.subheader("Add Books")
    book_title = st.text_input("Title", key="book_title_input")
    book_author = st.text_input("Author", key="book_author_input")
    book_price = st.number_input("Price", value=0.0, step=0.01, key="book_price_input")
    book_genre = st.text_input("Genre", key="book_genre_input")
    book_year = st.number_input("Published Year", value=1950, key="book_year_input")
    book_publisher = st.text_input("Publisher", key="book_publisher_input")    
    if st.button("Add Book", key="add_book_button"):
        # Check for empty fields
        if not all([book_title, book_author, book_price, book_genre, 
                    book_year, book_publisher]):
            st.error("All fields must be filled!")
        # Check if the book already exists
        elif books_collection.find_one({"title": book_title}):
            st.error("A book with this title already exists!")
        else:
            new_book_id = books_collection.count_documents({}) + 1
            new_book = {
                "BookID": int(new_book_id),
                "title": book_title,
                "author": book_author,
                "price": book_price,
                "genre": book_genre,
                "published_year": int(book_year),
                "publisher": book_publisher
            }
            books_collection.insert_one(new_book)
            st.success(f"Book '{book_title}' added successfully!")

def manage_orders(user_id):
    """Function to manage orders based on user type"""
    st.header("Orders")
    # Create two columns for the grid layout
    cols = st.columns(2)

    if st.session_state['user_type'] == "Admin":
        orders = list(orders_collection.find())
        
    elif st.session_state['user_type'] == "Customer":
        user_id = int(user_id)
        orders = list(orders_collection.find({"UserID": user_id}))
        if not orders:
            st.write("No orders found.")  # Message if no orders are present
    
    for index, order in enumerate(orders):
        col = cols[index % 2]

        with col:
            st.markdown(f"""
                <div class="order-card">
                    <h4>Order ID: {order.get('OrderID', 'N/A')}</h4>
                    <p><strong>Book ID:</strong> {order.get('BookID', 'N/A')}</p>
                    <p><strong>Price:</strong> ${order.get('Price', 'N/A')}</p>
                    <p><strong>Order Date:</strong> {order.get('OrderDate', 'N/A')}</p>
                    <p><strong>Status:</strong> {order.get('OrderStatus', 'N/A')}</p>
                </div>
            """, unsafe_allow_html=True)

def order_book(user_id, book_id, price):
    """ Function to order a book """
    new_order_id = orders_collection.count_documents({}) + 1
    id = int(user_id)
    today = date.today()
    new_order = {
        "OrderID": new_order_id,
        "UserID": id,
        "OrderDate": today.strftime('%Y-%m-%d'),
        "BookID": book_id,
        "Price": price,
        "OrderStatus": 'Processing'
    }
    orders_collection.insert_one(new_order)  # Insert new order into MongoDB
    st.success("Book ordered successfully!")

def display_reviews(user_id):
    """ Display reviews for books """
    st.header("Book Reviews")
    user_id = int(user_id)
    book_ids = [book['BookID'] for book in books_data]
    reviews = list(reviews_collection.find({"BookID": {"$in": book_ids}}))
    
    if not reviews:
        st.write("No reviews available.")
    
    for review in reviews:
        book = books_collection.find_one({"BookID": review['BookID']})
        st.markdown(f"""
            <div class="order-card">
                <h4>Book: {book['title']}</h4>
                <p><strong>Rating:</strong> {review.get('Rating', 'N/A')}</p>
                <p><strong>Comment:</strong> {review.get('Comment', 'N/A')}</p>
                <p><strong>Date:</strong> {review.get('ReviewDate', 'N/A')}</p>
            </div>
        """, unsafe_allow_html=True)

def add_review(user_id):
    """ Add a review for a book """
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.subheader("Add Review")
    user_id = int(user_id)
    # Fetch books and display them with titles and IDs
    books = books_collection.find()
    book_options = [(book['title'], book['BookID']) for book in books]
    selected_book_title, selected_book_id = st.selectbox("Select Book", options=book_options, format_func=lambda x: f"{x[0]}")
    
    # Radio buttons for rating
    rating = st.radio("Rating", options=[1, 2, 3, 4, 5])
    
    # Text area for the comment
    comment = st.text_area("Comment")
    
    if st.button("Submit Review"):
        if selected_book_id and comment:
            new_review_id = reviews_collection.count_documents({}) + 1
            today = date.today()
            new_review = {
                "ReviewID": new_review_id,
                "BookID": selected_book_id,
                "UserID": user_id,
                "Rating": rating,
                "Comment": comment,
                "ReviewDate": today.strftime('%Y-%m-%d')
            }
            reviews_collection.insert_one(new_review)
            st.success("Review added successfully!")
        else:
            st.error("Please fill out all fields.")

# User Interface
st.title("Bookstore Management System")

# Check if the user is authenticated
if not st.session_state.get('authenticated', False):
    st.write("Select User Type")
    
    cols = st.columns(2)
    
    with cols[0]:
        st.button("Customer", on_click=set_user_type, args=("Customer",))
    with cols[1]:
        st.button("Admin", on_click=set_user_type, args=("Admin",))
    
    if st.session_state.get('user_type') in ["Customer", "Admin"]:
        st.subheader(f"{st.session_state['user_type']} Login")
        display_login_or_create()
else:
    display_user_dashboard()
