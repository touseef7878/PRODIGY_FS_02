# Employee Management System

A full-stack web application for managing employee records with CRUD operations, authentication, and a responsive user interface.

## 🌟 Features

### Backend
- JWT Authentication for secure admin login
- Complete CRUD operations for employees
- Advanced search and filtering capabilities
- File upload with validation and thumbnail generation
- Pagination for efficient data handling
- RESTful API with Swagger documentation

### Frontend
- Responsive design for all device sizes
- Modern UI with clean aesthetics
- Dashboard with employee statistics
- Real-time search with debounced requests
- Drag-and-drop profile picture uploads

## 🛠️ Technology Stack

**Backend**: Python 3.8+, Flask, SQLAlchemy, Flask-JWT-Extended  
**Frontend**: HTML5, CSS3, Vanilla JavaScript  
**Database**: SQLite (default), PostgreSQL/MySQL (production)

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/touseef7878/PRODIGY_FS_02.git
   cd PRODIGY_FS_02
   ```

2. **Run the development server**
   ```bash
   npm install
   npm run dev
   ```

This will automatically:
- Set up a Python virtual environment
- Install all dependencies
- Initialize the database
- Start both backend and frontend servers

The application will be available at:
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/api/docs

## 🔐 Default Admin Credentials

After initialization, log in with:
- **Username**: `admin`
- **Email**: `admin@prodigyinfotec.com`
- **Password**: `ProdigyAdmin2024!`

⚠️ **Important**: Change the default password after first login.

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login` - Admin login
- `POST /api/auth/refresh` - Refresh access token

### Employees
- `GET /api/employees` - Get all employees
- `GET /api/employees/{id}` - Get employee by ID
- `POST /api/employees` - Create new employee
- `PUT /api/employees/{id}` - Update employee
- `DELETE /api/employees/{id}` - Delete employee

## 📁 Project Structure

```
employee-management-system/
├── backend/          # Flask API server
├── frontend/         # Client-side application
├── scripts/          # Utility scripts
├── .env.example      # Environment variables template
└── dev-server.js     # Development server
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Support

For support, create an issue in the repository.

---

**Made with ❤️ by Touseef**