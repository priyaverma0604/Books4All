const booksData = [
    {
        title: "Introduction to Mathematics",
        author: "John Smith",
        condition: "Good",
        categories: ["Mathematics", "Grade: 6-8", "English"],
        publisher: "ABC Publishers",
        location: "Mumbai",
        quantity: 3
    },
    {
        title: "Basic Science for Elementary",
        author: "Sarah Johnson",
        condition: "New",
        categories: ["Science", "Grade: 3-5", "Hindi"],
        publisher: "XYZ Book Store",
        location: "Delhi",
        quantity: 5
    },
    {
        title: "History of India",
        author: "Rajesh Kumar",
        condition: "Fair",
        categories: ["History", "Grade: 9-10", "English"],
        publisher: "National Library",
        location: "Bangalore",
        quantity: 2
    },
    {
        title: "English Grammar",
        author: "Elizabeth Brown",
        condition: "Used",
        categories: ["Language", "Grade: 4-6", "English"],
        publisher: "City Book House",
        location: "Chennai",
        quantity: 8
    }
];

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.querySelector('.search-bar input');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            filterBooks(searchTerm);
        });
    }

    // Request book buttons
    const requestButtons = document.querySelectorAll('.request-btn');
    requestButtons.forEach(button => {
        button.addEventListener('click', function() {
            const bookTitle = this.closest('.book-card').querySelector('h3').textContent;
            requestBook(bookTitle);
        });
    });

    // View all books button
    const viewAllButton = document.querySelector('.view-all-btn');
    if (viewAllButton) {
        viewAllButton.addEventListener('click', function() {
            window.location.href = '#'; // Redirect to all books page
            alert('Redirecting to all available books...');
        });
    }
});

// Filter books based on search term
function filterBooks(searchTerm) {
    const bookCards = document.querySelectorAll('.book-card');
    
    if (searchTerm === '') {
        // If search is empty, show all books
        bookCards.forEach(card => {
            card.style.display = 'block';
        });
        return;
    }
    
    bookCards.forEach(card => {
        const title = card.querySelector('h3').textContent.toLowerCase();
        const author = card.querySelector('.author').textContent.toLowerCase();
        const tags = Array.from(card.querySelectorAll('.tag')).map(tag => tag.textContent.toLowerCase());
        
        if (title.includes(searchTerm) || 
            author.includes(searchTerm) || 
            tags.some(tag => tag.includes(searchTerm))) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Request book functionality
function requestBook(bookTitle) {
    // This would typically involve an API call or form submission
    console.log(Requesting book: ${bookTitle});
    alert(Your request for "${bookTitle}" has been received. We'll connect you with the donor soon!);
}

// Additional functionality could include:
// 1. User authentication
// 2. Book donation form
// 3. Book request form for schools
// 4. Donation tracking
// 5. Filtering by location, subject, grade, etc.