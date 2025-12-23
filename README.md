# Physical AI & Humanoid Robotics Educational Platform

This is an educational platform for learning about Physical AI and Humanoid Robotics, built with Docusaurus 3.x.

## Features

- Interactive textbook content
- AI-powered RAG chatbot for learning assistance
- User authentication with personalized profiles
- Personalized AI responses based on user experience and interests
- Modular curriculum structure
- Responsive design for all devices

## Installation

```bash
yarn
```

## Environment Variables

Create a `.env` file in the root directory based on `.env.example`:

```bash
BACKEND_URL=http://localhost:8000
```

The BACKEND_URL should point to your authentication and RAG backend service.

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Authentication System

The platform includes a comprehensive authentication system with:

- **User Registration**: New users can create accounts with email, password, and profile information
- **User Login**: Existing users can sign in with their credentials
- **Profile Management**: Users can set their software/hardware experience and interests
- **Session Management**: Automatic session timeout after 1 hour of inactivity
- **Personalized AI Responses**: The RAG chatbot provides customized responses based on user profiles
- **Responsive Design**: Authentication forms work on all device sizes (320px to 2560px)

### Profile Fields
- Software Experience: Beginner, Intermediate, Advanced
- Hardware/Robotics Experience: None, Basic, Advanced
- Interests: Robotics, AI, ML, Hardware Design, Software Development, IoT, Computer Vision, NLP, Autonomous Systems, Embedded Systems

The authentication system is integrated into the Docusaurus navbar and provides login/logout functionality with personalized experiences.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true yarn deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> yarn deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
