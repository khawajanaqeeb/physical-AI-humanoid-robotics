# RAG Chatbot Frontend

This is the frontend for the Phase 2 RAG Chatbot System, built with Docusaurus 3.x and a custom React chat widget plugin.

## Quick Start

### Installation

```bash
npm install
```

### Development

```bash
npm start
```

This starts the Docusaurus development server at http://localhost:3000.

### Build

```bash
npm run build
```

Generates static content into the `build` directory.

### Deployment

The built site can be deployed to any static hosting service:

- **Vercel**: Automatic deployment from GitHub
- **Netlify**: Drag-and-drop or Git integration
- **GitHub Pages**: Built-in Docusaurus support

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
REACT_APP_API_URL=http://localhost:8000
```

For production, set `REACT_APP_API_URL` to your backend API URL.

## Chat Widget Plugin

The RAG chatbot is implemented as a custom Docusaurus plugin located in `plugins/rag-chatbot/`.

### Features

- **Floating Chat Button**: Always visible in bottom-right corner
- **Session Management**: UUID per browser tab (sessionStorage)
- **Real-time Answers**: Powered by backend RAG pipeline
- **Citations**: Clickable links to exact textbook sections
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Mode Support**: Matches Docusaurus theme

### Components

- `ChatWidget.jsx`: Floating button
- `ChatModal.jsx`: Chat interface and message list
- `Citation.jsx`: Citation link component
- `useSession.js`: Session ID management
- `useChatMessages.js`: Message state management
- `api/client.js`: Backend API communication

## Directory Structure

```
frontend/
├── docs/                    # Markdown documentation files
├── src/                     # Docusaurus source files
│   ├── components/          # React components
│   └── css/                 # Global styles
├── plugins/
│   └── rag-chatbot/         # Custom chat widget plugin
│       ├── components/      # React components
│       ├── hooks/           # Custom hooks
│       ├── api/             # API client
│       ├── chatWidget.js    # Plugin entry point
│       └── index.js         # Plugin definition
├── static/                  # Static assets
├── docusaurus.config.js     # Docusaurus configuration
├── sidebars.js              # Sidebar configuration
└── package.json             # Dependencies
```

## Customization

### Theme Colors

Edit `src/css/custom.css` to customize the color scheme.

### Chat Widget Styling

Edit component CSS files in `plugins/rag-chatbot/components/`:

- `ChatWidget.css`: Floating button styles
- `ChatModal.css`: Modal and message styles
- `Citation.css`: Citation link styles

### API Integration

Configure the backend URL in `.env`:

```env
REACT_APP_API_URL=https://your-api-domain.com
```

## Troubleshooting

### Chat widget not appearing

1. Check that the plugin is loaded in `docusaurus.config.js`
2. Verify `chatWidget.js` is rendering correctly
3. Check browser console for errors

### API requests failing

1. Verify backend server is running
2. Check `REACT_APP_API_URL` in `.env`
3. Ensure CORS is configured on backend

### Citations not navigating

1. Verify Docusaurus heading IDs match citation anchors
2. Check URL format: `/docs/page-name#heading-id`
3. Test navigation in production build

## Learn More

- [Docusaurus Documentation](https://docusaurus.io)
- [React Documentation](https://react.dev)
- Backend API: See `../backend/README.md`
