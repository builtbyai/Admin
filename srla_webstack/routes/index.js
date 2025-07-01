const express = require('express');
const router = express.Router();

// Import route modules
const authRoutes = require('./auth');
const userRoutes = require('./users');
const appointmentRoutes = require('./appointments');
const messageRoutes = require('./messages');
const documentRoutes = require('./documents');
const notificationRoutes = require('./notifications');

// Mount routes
router.use('/auth', authRoutes);
router.use('/users', userRoutes);
router.use('/appointments', appointmentRoutes);
router.use('/messages', messageRoutes);
router.use('/documents', documentRoutes);
router.use('/notifications', notificationRoutes);

module.exports = router;
