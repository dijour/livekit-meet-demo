# Hedra Avatar App

A real-time avatar application built with Next.js frontend and Python LiveKit agent backend, featuring Hedra AI avatars and OpenAI integration.

## Overview

This project consists of two main components:
- **Frontend**: Next.js application for the user interface
- **Backend**: Python LiveKit agent for real-time communication and AI processing

## Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- pnpm (recommended) or npm
- Git

## Environment Setup

Before running the application, you'll need to set up your environment variables:

1. Copy the `.env.local` files and configure your API keys:
   - LiveKit API credentials
   - OpenAI API key
   - Hedra API credentials

## Quick Start

The easiest way to run both components is using the provided npm scripts:

```bash
# Start the frontend (Next.js app)
npm run start-app

# Start the backend (Python agent)
npm run start-agent
```

## Manual Setup

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   pnpm install
   # or
   npm install
   ```

3. Start the development server:
   ```bash
   pnpm dev
   # or
   npm run dev
   ```

The frontend will be available at `http://localhost:3000`

### Backend Setup

#### Option 1: Using Virtual Environment (Recommended)

A virtual environment is recommended to isolate Python dependencies:

1. Create a virtual environment (if not already created):
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. Navigate to the backend directory:
   ```bash
   cd backend
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the agent:
   ```bash
   python agent_worker.py start
   ```

#### Option 2: System-wide Installation (Optional)

If you prefer not to use a virtual environment:

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies directly:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the agent:
   ```bash
   python agent_worker.py start
   ```

## Key Dependencies

### Frontend
- Next.js - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- LiveKit React SDK - Real-time communication

### Backend
- LiveKit Agents - Real-time agent framework
- LiveKit Plugins (Hedra, OpenAI) - AI integrations
- aiohttp - Async HTTP client
- python-dotenv - Environment variable management

## Project Structure

```
hedra-test/
├── frontend/          # Next.js application
│   ├── app/          # Next.js app router
│   ├── components/   # React components
│   └── hooks/        # Custom React hooks
├── backend/          # Python LiveKit agent
│   ├── agent_worker.py    # Main agent script
│   ├── requirements.txt   # Python dependencies
│   └── assets/       # Static assets
├── venv/            # Python virtual environment
└── package.json     # Root package with scripts
```

## Development Workflow

1. Start both services:
   ```bash
   # Terminal 1: Start frontend
   npm run start-app
   
   # Terminal 2: Start backend
   npm run start-agent
   ```

2. The application will be running with:
   - Frontend: `http://localhost:3000`
   - Backend: LiveKit agent running in the background

## Environment Variables

Make sure to configure the following in your `.env.local` files:

- `LIVEKIT_URL` - Your LiveKit server URL
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret
- `OPENAI_API_KEY` - OpenAI API key
- `HEDRA_API_KEY` - Hedra API key

## Troubleshooting

### Virtual Environment Issues
- If you encounter permission issues, ensure the virtual environment is properly activated
- On Windows, you might need to run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell

### Dependency Issues
- For frontend: Try deleting `node_modules` and running `pnpm install` again
- For backend: Ensure you're using the correct Python version and virtual environment

### Port Conflicts
- Frontend runs on port 3000 by default
- If port 3000 is busy, Next.js will prompt you to use a different port

## Contributing

When contributing to this project:
1. Ensure both frontend and backend tests pass
2. Follow the existing code style
3. Update documentation as needed
4. Test with both virtual environment and system-wide Python installations

## License

This project is for testing and development purposes.