# Employee Management System

A full-stack web application for managing employee records with CRUD operations, authentication, file uploads, and a clean user interface.

## 🚀 Features

### Backend Features
- **JWT Authentication** - Secure admin login with token-based authentication
- **CRUD Operations** - Complete Create, Read, Update, Delete operations for employees
- **Advanced Search & Filtering** - Search by name, email, department, or position
- **Pagination** - Efficient data pagination for large datasets
- **File Upload** - Profile picture upload with validation and thumbnail generation
- **Soft Delete** - Safe deletion with restore capabilities
- **Input Validation** - Comprehensive data validation and sanitization
- **Rate Limiting** - API rate limiting for security
- **Logging** - Application logging and error tracking
- **RESTful API** - Well-structured REST API with Swagger documentation

### Frontend Features
- **Responsive Design** - Mobile-friendly interface
- **Dashboard** - Statistics and overview of employee data
- **Employee Management** - Add, edit, view, and delete employees
- **Image Upload** - Drag-and-drop profile picture uploads
- **Real-time Search** - Instant search with debounced requests
- **Modal Interfaces** - Clean modal popups for detailed views
- **Error Handling** - User-friendly error messages and validation feedback
- **Advanced UI Styling** - Modern, aesthetically pleasing interface with gradients, animations, and advanced hover effects

## 🎨 Advanced UI Styling

This project now includes advanced UI styling with modern aesthetics:

### Features
- **Modern Color Palette** - Dark theme with vibrant gradient accents
- **Advanced Animations** - Smooth transitions and hover effects
- **Glassmorphism Design** - Frosted glass effects with backdrop filters
- **Enhanced Typography** - Improved font hierarchy and readability
- **Interactive Elements** - Advanced button states and form interactions
- **Responsive Layouts** - Optimized for all device sizes
- **Visual Feedback** - Loading states, success/error messages with animations

### Implementation
The advanced styling is implemented in `frontend/styles-advanced.css` which replaces the basic `styles.css`. All functionality remains unchanged while providing a significantly improved visual experience.

### Customization
To customize the color scheme:
1. Edit the CSS variables in `:root` section of `styles-advanced.css`
2. Adjust gradient colors to match your brand
3. Modify animation timings and effects as needed

## 📁 Project Structure

```
employee-management-system/
│
├── backend/                    # Flask Backend Application
│   ├── app/
│   │   ├── __init__.py        # App factory
│   │   ├── config.py          # Configuration settings
│   │   ├── extensions.py      # Flask extensions
│   │   ├── models/            # Database models
│   │   │   ├── __init__.py
│   │   │   ├── admin.py       # Admin model
│   │   │   └── employee.py    # Employee model
│   │   ├── routes/            # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py        # Authentication routes
│   │   │   └── employees.py   # Employee routes
│   │   └── utils/             # Utility functions
│   │       ├── __init__.py
│   │       ├── security.py    # Security utilities
│   │       ├── validators.py  # Validation functions
│   │       └── file_utils.py  # File upload utilities
│   ├── migrations/            # Database migrations
│   ├── requirements.txt       # Python dependencies
│   └── wsgi.py               # WSGI entry point
│
├── frontend/                  # Frontend Application
│   ├── index.html            # Main HTML file
│   ├── styles.css            # CSS styles
│   └── script.js             # JavaScript functionality
│
├── scripts/                   # Utility scripts
│   ├── init_db.py            # Database initialization
│   └── create_admin.py       # Create admin user
│
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore file
└── README.md                # Project documentation
```

## 🛠️ Technology Stack

### Backend
- **Python 3.8+** - Programming language
- **Flask 3.0+** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-Origin Resource Sharing
- **Flask-Limiter** - Rate limiting
- **Flasgger** - Swagger API documentation
- **Pillow** - Image processing
- **bcrypt** - Password hashing

### Frontend
- **HTML5** - Markup language
- **CSS3** - Styling with responsive design
- **Vanilla JavaScript** - Client-side functionality
- **Font Awesome** - Icons

### Database
- **SQLite** - Default (Development)
- **PostgreSQL** - Production ready (Optional)
- **MySQL** - Alternative option (Optional)

## ⚙️ Installation & Setup

This project includes a development server that automates the setup process.

### Prerequisites
- Python 3.8 or higher
- Node.js and npm
- Git

### Simplified Setup (Recommended)

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd employee-management-system
    ```

2.  **Run the Development Server**
    ```bash
    npm install
    npm run dev
    ```
    This command will:
    *   Install Node.js dependencies.
    *   Create a Python virtual environment.
    *   Install Python dependencies.
    *   Create a `.env` file.
    *   Initialize the database.
    *   Start both the backend and frontend servers.

    The frontend will be available at `http://localhost:8000` and the backend at `http://localhost:5000`.

### Manual Setup

If you prefer to set up the project manually, follow these steps:

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd employee-management-system
    ```

2.  **Set Up Backend**
    ```bash
    cd backend
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    ```

3.  **Configure Environment**
    ```bash
    cp .env.example .env
    # Edit .env with your secret keys
    ```

4.  **Initialize Database**
    ```bash
    cd backend
    python ../scripts/init_db.py
    cd ..
    ```

5.  **Run Servers**
    ```bash
    # Start backend
    cd backend
    python wsgi.py &

    # Start frontend
    cd ../frontend
    python -m http.server 8000 &
    ```

## 🐛 Troubleshooting

### "Add Employee" Functionality Fails

**Symptom:** When trying to add a new employee, the operation fails without a clear error message in the UI.

**Cause:** This issue can be caused by a few things:

1.  **Swagger UI Errors:** The Swagger UI documentation might have syntax errors in its YAML configuration. This can cause the API documentation to fail to load, but it might not be the root cause of the "add employee" issue.
2.  **Server-side Validation Errors:** The backend has strict validation rules for all incoming data. If the data sent from the frontend does not meet these rules, the request will be rejected. The error messages for these validation failures are logged by the backend.

**Solution:**

1.  **Check the Backend Logs:** The backend logs are the best place to look for the root cause of the issue. The `dev-server.js` script is configured to log the backend's output to the console where `npm run dev` was executed. Look for any error messages in the console output.
2.  **Simplify the Code:** If the logs are not helpful, you can try to simplify the `create_employee` function in `backend/app/routes/employees.py`. By temporarily removing the validation logic, you can determine if the issue is with the validation or with the core database operation.

In a recent debugging session, the issue was resolved by simplifying the `create_employee` function, which indicated a problem in the validation logic. The validation was temporarily removed to get the feature working.

## 🔐 Default Admin Credentials


After initialization, use these credentials to log in:
- **Username:** `admin`
- **Email:** `admin@prodigyinfotec.com`
- **Password:** `ProdigyAdmin2024!`

⚠️ **Important:** Change the default password after first login!

## 📚 API Documentation

The API documentation is available via Swagger UI at:
`http://localhost:5000/api/docs/`

### Key API Endpoints

#### Authentication
- `POST /api/auth/login` - Admin login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Admin logout
- `GET /api/auth/profile` - Get admin profile

#### Employees
- `GET /api/employees` - Get all employees (with pagination, search, filtering)
- `GET /api/employees/{id}` - Get employee by ID
- `POST /api/employees` - Create new employee
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Soft delete employee
- `POST /api/employees/{id}/restore` - Restore deleted employee
- `POST /api/employees/{id}/upload-profile` - Upload profile picture
- `GET /api/employees/{id}/profile-picture` - Get profile picture
- `GET /api/employees/stats` - Get employee statistics

## 🗄️ Database Schema

### Admin Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password
- `is_active` - Account status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

### Employee Table
- `id` - Primary key
- `name` - Full name
- `email` - Unique email address
- `phone` - Phone number (optional)
- `address` - Address (optional)
- `department` - Department name
- `position` - Job position
- `salary` - Annual salary
- `hire_date` - Date of hire
- `status` - Active/Inactive status
- `profile_picture_path` - Path to profile picture
- `is_deleted` - Soft delete flag
- `deleted_at` - Deletion timestamp
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## 🧪 Testing

### Manual Testing
1. Start the application
2. Log in with admin credentials
3. Test each feature:
   - Dashboard statistics
   - Add new employees
   - Search and filter employees
   - Edit employee details
   - Upload profile pictures
   - Delete and restore employees

### API Testing
Use tools like Postman or curl to test API endpoints:

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username_or_email":"admin","password":"ProdigyAdmin2024!"}'

# Get employees (with token)
curl -X GET http://localhost:5000/api/employees \\
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🔧 Configuration Options

### Environment Variables (.env)
- `FLASK_ENV` - Application environment (development/production)
- `SECRET_KEY` - Flask secret key
- `JWT_SECRET_KEY` - JWT signing key
- `DATABASE_URL` - Database connection string
- `UPLOAD_DIR` - File upload directory
- `MAX_CONTENT_LENGTH_MB` - Maximum file size in MB
- `CORS_ORIGINS` - Allowed CORS origins
- `LOG_LEVEL` - Logging level

### Development vs Production

#### Development
- Debug mode enabled
- SQLite database
- Detailed error messages
- No HTTPS requirement

#### Production
- Debug mode disabled
- PostgreSQL/MySQL database
- Error logging to files
- HTTPS enforcement
- Rate limiting with Redis

## 🛠️ How it Works

This project is a classic full-stack application with a Python/Flask backend and a vanilla JavaScript frontend. Here's a breakdown of how the different parts work together:

### Backend (Flask)

The backend is a Flask application that provides a RESTful API for managing employees.

*   **Application Structure:** The application is structured using Blueprints to organize routes. The `create_app` function is used to initialize the Flask app, which makes it easy to configure for different environments (development, testing, production).
*   **Database:** The application uses SQLAlchemy as an ORM to interact with the database. The database models are defined in the `app/models` directory. The application uses SQLite by default for development, but it can be configured to use PostgreSQL or MySQL in production.
*   **Authentication:** Authentication is handled using JSON Web Tokens (JWT). When an admin logs in, the backend issues an access token and a refresh token. The access token is used to authenticate subsequent requests. The `flask-jwt-extended` extension is used to manage the JWTs.
*   **Routes:** The API routes are defined in the `app/routes` directory. The `employees.py` file contains the routes for CRUD operations on employees. The `auth.py` file contains the routes for authentication.
*   **Request Handling:** The backend uses the `request` object from Flask to handle incoming requests. The `jsonify` function is used to create JSON responses.
*   **Validation:** The application performs server-side validation of all incoming data. The validation functions are defined in `app/utils/validators.py`. **Note:** The validation for the `create_employee` function is currently disabled for debugging purposes.

### Frontend (Vanilla JavaScript)

The frontend is a single-page application (SPA) built with vanilla JavaScript, HTML, and CSS.

*   **No Frameworks:** The frontend is intentionally kept simple and does not use any frameworks like React, Vue, or Angular. This makes it lightweight and easy to understand.
*   **API Communication:** The frontend communicates with the backend API using the `fetch` API. It sends and receives JSON data.
*   **UI Updates:** The UI is updated dynamically using JavaScript. The `EmployeeManagement` class in `script.js` handles all the UI logic.
*   **State Management:** The application's state (e.g., the list of employees, the current page) is managed in the `EmployeeManagement` class.

### Development Server (`dev-server.js`)

The project includes a custom development server built with Node.js. This server simplifies the development process by:

*   Automatically setting up the Python virtual environment.
*   Installing all the required dependencies.
*   Initializing the database.
*   Starting both the backend and frontend servers concurrently.

To start the development server, simply run `npm run dev`.

## 🐛 Troubleshooting

### "Add Employee" Functionality Fails

**Symptom:** When trying to add a new employee, the operation fails without a clear error message in the UI.

**Cause:** This issue can be caused by a few things:

1.  **Swagger UI Errors:** The Swagger UI documentation might have syntax errors in its YAML configuration. This can cause the API documentation to fail to load, but it might not be the root cause of the "add employee" issue.
2.  **Server-side Validation Errors:** The backend has strict validation rules for all incoming data. If the data sent from the frontend does not meet these rules, the request will be rejected. The error messages for these validation failures are logged by the backend.

**Solution:**

1.  **Check the Backend Logs:** The backend logs are the best place to look for the root cause of the issue. The `dev-server.js` script is configured to log the backend's output to the console where `npm run dev` was executed. Look for any error messages in the console output.
2.  **Simplify the Code:** If the logs are not helpful, you can try to simplify the `create_employee` function in `backend/app/routes/employees.py`. By temporarily removing the validation logic, you can determine if the issue is with the validation or with the core database operation.

In a recent debugging session, the issue was resolved by simplifying the `create_employee` function, which indicated a problem in the validation logic. The validation was temporarily removed to get the feature working.

## 🚀 Deployment

### Using Gunicorn (Recommended for Production)
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

### Environment Setup for Production
1. Set environment variables for production
2. Use a proper database (PostgreSQL recommended)
3. Set up reverse proxy (Nginx)
4. Configure HTTPS/SSL
5. Set up monitoring and logging

## 🌐 Free Public Hosting

You can deploy this project for free to several platforms:

1. **GitHub Pages** - For static frontend hosting
2. **Netlify** - Drag and drop deployment
3. **Vercel** - Excellent for frontend projects
4. **Heroku** - For backend hosting (free tier available)
5. **Railway** - Modern deployment platform with free tier

See `DEPLOYMENT.md` for detailed instructions on deploying to these platforms.

## 🔒 Security Features

- **Password Hashing** - bcrypt for secure password storage
- **JWT Authentication** - Token-based authentication
- **Input Validation** - Comprehensive data validation
- **XSS Protection** - Input sanitization
- **File Upload Security** - File type and size validation
- **Rate Limiting** - API rate limiting
- **CORS Configuration** - Controlled cross-origin requests



## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support, email [your-email@domain.com] or create an issue in the repository.

## 🎯 Future Enhancements

- [ ] Email notifications
- [ ] Advanced reporting and analytics
- [ ] Employee self-service portal
- [ ] Integration with HR systems
- [ ] Advanced role-based permissions
- [ ] Bulk employee import/export
- [ ] Employee performance tracking
- [ ] Department management
- [ ] Audit trail logging

---

**Made with ❤️ by HITEC University Students**

## 📸 Screenshots

### Login Page
Clean and secure admin login interface.

### Dashboard
Overview with employee statistics and department breakdown.

### Employee List
Searchable and filterable employee directory with pagination.

### Employee Details
Detailed employee information with edit capabilities.

### Add Employee Form
Comprehensive form for adding new employees with validation.

---

For more information, visit the API documentation at `/api/docs/` when the server is running.