# TodoList Application

A full-stack task management application built with FastAPI and React.

## 🚀 Deployed URLs

- **Frontend**: [https://todolist-sepia-seven-38.vercel.app](https://todolist-sepia-seven-38.vercel.app)
- **Backend API**: [https://todolist-production-454d.up.railway.app](https://todolist-production-454d.up.railway.app)
- **API Documentation**: [https://todolist-production-454d.up.railway.app/docs](https://todolist-production-454d.up.railway.app/docs)

## 🛠️ Technologies

### Backend
- **FastAPI**: Modern Python web framework
- **MongoDB**: NoSQL database for data storage
- **Motor**: Async MongoDB driver
- **JWT**: Token-based authentication
- **Pydantic**: Data validation
- **uvicorn**: ASGI server

### Frontend
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Chakra UI**: Component library
- **Axios**: HTTP client
- **React Router**: Navigation
- **Vite**: Build tool

## 📋 Prerequisites

- Python 3.10+
- Node.js 16+
- MongoDB
- Git

## ⚙️ Installation

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd todolist/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your MongoDB connection string and other configurations
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd ../frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env
# Set VITE_API_URL to your backend URL
```

4. Run development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🗄️ Database Structure

### Collections

#### Users
```json
{
  "_id": "ObjectId",
  "name": "string",
  "email": "string",
  "password": "string (hashed)",
  "created_at": "datetime"
}
```

#### Tasks
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "title": "string",
  "description": "string",
  "due_date": "datetime",
  "completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 🔒 API Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration
- Input validation with Pydantic

## 🌟 Features

- User authentication (signup/login)
- Create, read, update, and delete tasks
- Task filtering and pagination
- Real-time validation
- Responsive design
- Error handling and validation
- API documentation with Swagger UI

## 📝 Environment Variables

### Backend
```
MONGO_PUBLIC_URL=mongodb://your_mongodb_url
DATABASE_NAME=todolist
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend
```
VITE_API_URL=http://localhost:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
