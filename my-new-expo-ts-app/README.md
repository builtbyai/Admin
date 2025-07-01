# SRLA Mobile - Patient Portal App

A React Native mobile application for Sentiment Sports Rehab LA patients to manage appointments, memberships, and access support.

## Features

- **Secure Authentication**: JWT-based login system
- **Dashboard**: Quick overview of appointments and membership status
- **Appointment Management**: View, book, and cancel appointments
- **Recovery Lounge Membership**: Subscribe and manage $100/month membership
- **AI Chat Support**: 24/7 chatbot assistance
- **Cross-Platform**: Works on both iOS and Android

## Prerequisites

- Node.js 14+ 
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (Mac only) or Android Emulator
- Expo Go app on your physical device (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-repo/srla-mobile.git
cd srla-mobile
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update `.env` with your API URL:
```
API_BASE_URL=http://localhost:8000/api
```

## Running the App

### Development

Start the Expo development server:
```bash
npm start
# or
expo start
```

This will open the Expo Dev Tools in your browser. From there you can:
- Press `a` to open in Android emulator
- Press `i` to open in iOS simulator
- Scan the QR code with Expo Go app on your phone

### Platform-specific commands:

```bash
# iOS
npm run ios

# Android
npm run android

# Web (experimental)
npm run web
```

## Project Structure

```
srla-mobile/
├── App.tsx                 # Main app entry point
├── src/
│   ├── components/        # Reusable components
│   ├── screens/          # Screen components
│   │   ├── LoginScreen.tsx
│   │   ├── DashboardScreen.tsx
│   │   ├── AppointmentsScreen.tsx
│   │   ├── MembershipScreen.tsx
│   │   └── ChatScreen.tsx
│   ├── services/         # API services
│   │   ├── api.ts
│   │   └── auth.ts
│   ├── types/           # TypeScript type definitions
│   └── utils/           # Utility functions
├── assets/              # Images, fonts, etc.
├── app.json            # Expo configuration
├── babel.config.js     # Babel configuration
├── tsconfig.json       # TypeScript configuration
└── package.json        # Dependencies
```

## API Integration

The app connects to the SRLA backend API. Key endpoints:

- `POST /api/auth/login` - User authentication
- `GET /api/appointments` - List appointments
- `GET /api/membership/status` - Check membership
- `POST /api/chat` - Send chat messages

## Building for Production

### iOS

1. Configure app.json with your bundle identifier
2. Run build command:
```bash
expo build:ios
```

### Android

1. Configure app.json with your package name
2. Run build command:
```bash
expo build:android
```

### Using EAS Build (Recommended)

1. Install EAS CLI:
```bash
npm install -g eas-cli
```

2. Configure your project:
```bash
eas build:configure
```

3. Build for both platforms:
```bash
eas build --platform all
```

## Testing

Run tests:
```bash
npm test
```

Run linter:
```bash
npm run lint
```

## Troubleshooting

### Common Issues

1. **Metro bundler issues**: Clear cache
```bash
expo start -c
```

2. **Dependencies issues**: Reset and reinstall
```bash
rm -rf node_modules
npm install
```

3. **iOS Simulator not opening**: Make sure Xcode is installed and configured

4. **Android Emulator not found**: Ensure Android Studio and emulator are properly set up

## Security Considerations

- All API calls use HTTPS in production
- Authentication tokens stored securely using AsyncStorage
- Sensitive data is never logged
- HIPAA compliance considerations implemented

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For technical support:
- Email: support@prsm.tech
- Documentation: [docs.prsm.tech/srla-mobile](https://docs.prsm.tech/srla-mobile)

## License

This software is proprietary and confidential. Unauthorized copying or distribution is prohibited.

© 2024 PRSM Tech. All rights reserved.
