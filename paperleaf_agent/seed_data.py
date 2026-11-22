"""Made-up seed data for PaperLeaf Books (practice only, never real customers)."""

BOOKS = [
    ("The Midnight Library", "Matt Haig", "Fiction", 399, "New", 12),
    ("Atomic Habits", "James Clear", "Self-help", 449, "New", 20),
    ("The Alchemist", "Paulo Coelho", "Fiction", 299, "New", 25),
    ("Sapiens", "Yuval Noah Harari", "Non-fiction", 599, "New", 8),
    ("The God of Small Things", "Arundhati Roy", "Fiction", 349, "New", 10),
    ("Wings of Fire", "A. P. J. Abdul Kalam", "Biography", 250, "New", 15),
    ("Malgudi Days", "R. K. Narayan", "Fiction", 220, "New", 18),
    ("The White Tiger", "Aravind Adiga", "Fiction", 320, "New", 9),
    ("Train to Pakistan", "Khushwant Singh", "Fiction", 275, "New", 7),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Finance", 350, "New", 14),
    ("Ikigai", "Hector Garcia", "Self-help", 299, "New", 16),
    ("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "Children", 499, "New", 11),
    ("The Hobbit", "J. R. R. Tolkien", "Fantasy", 450, "New", 9),
    ("A Brief History of Time", "Stephen Hawking", "Science", 399, "New", 6),
    ("NCERT Mathematics Class 10", "NCERT", "Textbook", 150, "New", 40),
    ("Concepts of Physics Vol 1", "H. C. Verma", "Textbook", 520, "New", 13),
    ("Python Crash Course", "Eric Matthes", "Technology", 1999, "New", 5),
    ("The Pragmatic Programmer", "Hunt & Thomas", "Technology", 2499, "New", 4),
    ("Gitanjali", "Rabindranath Tagore", "Poetry", 199, "New", 12),
    ("Chanakya's Chant", "Ashwin Sanghi", "Fiction", 299, "Like New", 3),
    ("The Palace of Illusions", "Chitra Banerjee Divakaruni", "Fiction", 260, "Like New", 2),
    ("Godan", "Munshi Premchand", "Fiction", 150, "Good", 4),
    ("Discovery of India", "Jawaharlal Nehru", "History", 280, "Good", 2),
    ("The Immortals of Meluha", "Amish Tripathi", "Fantasy", 230, "Like New", 5),
    ("India After Gandhi", "Ramachandra Guha", "History", 650, "New", 6),
    ("Panchatantra Stories", "Vishnu Sharma", "Children", 180, "New", 20),
    ("The Monk Who Sold His Ferrari", "Robin Sharma", "Self-help", 240, "Good", 3),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Non-fiction", 420, "Like New", 4),
    ("Cosmos", "Carl Sagan", "Science", 480, "New", 5),
    ("Sherlock Holmes: Complete Stories", "Arthur Conan Doyle", "Mystery", 550, "New", 7),
]

CUSTOMERS = [
    ("Aarav Mehta", "aarav.mehta@example.com", "Mumbai"),
    ("Diya Nair", "diya.nair@example.com", "Kochi"),
    ("Rohan Iyer", "rohan.iyer@example.com", "Bengaluru"),
    ("Sneha Kulkarni", "sneha.kulkarni@example.com", "Pune"),
    ("Kabir Singh", "kabir.singh@example.com", "Delhi"),
    ("Ananya Das", "ananya.das@example.com", "Kolkata"),
]

# (order_id, customer_id, status, payment, placed_at, delivered_at, [(book_id, qty)])
ORDERS = [
    ("PL-1001", 1, "Delivered", "UPI", "2026-11-02 10:15", "2026-11-05 16:40", [(1, 1), (2, 1)]),
    ("PL-1002", 1, "Shipped", "Credit card", "2026-11-18 09:05", None, [(4, 1)]),
    ("PL-1003", 2, "Delivered", "Cash on delivery", "2026-11-04 18:30", "2026-11-09 12:10", [(3, 2)]),
    ("PL-1004", 2, "Placed", "UPI", "2026-11-21 20:45", None, [(12, 1), (26, 1)]),
    ("PL-1005", 3, "Delivered", "Net banking", "2026-10-28 11:00", "2026-11-01 15:20", [(17, 1), (18, 1)]),
    ("PL-1006", 3, "Returned", "UPI", "2026-10-20 13:25", "2026-10-24 10:00", [(16, 1)]),
    ("PL-1007", 4, "Shipped", "Debit card", "2026-11-19 08:50", None, [(8, 1), (9, 1), (10, 1)]),
    ("PL-1008", 4, "Cancelled", "UPI", "2026-11-12 17:10", None, [(13, 1)]),
    ("PL-1009", 5, "Delivered", "Cash on delivery", "2026-11-08 12:00", "2026-11-12 14:30", [(15, 3)]),
    ("PL-1010", 5, "Placed", "UPI", "2026-11-22 09:30", None, [(21, 1), (22, 1)]),
    ("PL-1011", 6, "Delivered", "Credit card", "2026-11-06 19:20", "2026-11-10 11:45", [(25, 1), (29, 1)]),
    ("PL-1012", 6, "Shipped", "UPI", "2026-11-20 14:15", None, [(5, 1)]),
]
