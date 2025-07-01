# SRLA Backend API

Backend API for the SRLA Patient Portal mobile and web applications.

## Features

- RESTful API with Express.js
- MySQL database with Sequelize ORM
- JWT authentication
- Real-time messaging with Socket.io
- Email notifications
- SMS notifications with Twilio
- File upload support
- Rate limiting and security headers
- Comprehensive logging

## Prerequisites

- Node.js 14+
- MySQL 5.7+
- npm or yarn

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

4. Create MySQL database:
   ```sql
   CREATE DATABASE srla_db;
   ```

5. Run migrations:
   ```bash
   npm run migrate
   ```

## Running the Server

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm start
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh-token` - Refresh JWT token
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password
- `GET /api/auth/verify-email/:token` - Verify email address

### Users
- `GET /api/users/profile` - Get current user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/upload-avatar` - Upload profile picture

### Appointments
- `GET /api/appointments` - Get user appointments
- `POST /api/appointments` - Create new appointment
- `PUT /api/appointments/:id` - Update appointment
- `DELETE /api/appointments/:id` - Cancel appointment

### Messages
- `GET /api/messages` - Get user messages
- `POST /api/messages` - Send new message
- `GET /api/messages/:id` - Get message thread

### Documents
- `GET /api/documents` - Get user documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/:id/download` - Download document
- `DELETE /api/documents/:id` - Delete document

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/:id/read` - Mark notification as read
- `DELETE /api/notifications/:id` - Delete notification

## Testing

Run tests:
```bash
npm test
```

## Deployment

1. Set production environment variables
2. Build and start:
   ```bash
   NODE_ENV=production npm start
   ```

## License

MIT
