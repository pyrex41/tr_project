# Legal Document Analysis - Frontend

A modern, type-safe Elm frontend for analyzing legal documents with AI-powered insights.

**🌐 Live Demo:** [https://tr-project.fly.dev](https://tr-project.fly.dev)

## 🚀 Features

### **Dashboard**
- Real-time statistics (Total Orders, Experts, Exclusion Rate, Citations, Word Count, Daubert Analysis)
- AI-discovered insights with confidence scores
- Interactive charts (bar and pie charts using elm-charts)
- Quick search with keyword/semantic toggle

### **Search**
- Keyword and semantic search modes
- Real-time results with relevance scoring
- Rich result cards with metadata, expert names, and insights
- Click-through navigation to order details

### **Order Detail**
- **Overview Tab**: Case summary, ruling type, expert field, methodologies, exclusion grounds
- **Analysis Tab**: Key findings, strategic implications, citation context
- **Full Text Tab**: Complete document text with readable formatting
- **Citations Tab**: All citations with type and context
- **Quotes Tab**: Notable quotes with copy functionality

## 🛠️ Tech Stack

- **Elm 0.19.1** - Type-safe functional language for robust UIs
- **Vite 7.2.2** - Lightning-fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS via CDN
- **elm-charts 5.0.0** - SVG-based charts
- **elm-json-decode-pipeline** - Elegant JSON decoding

## 📦 Project Structure

```
frontend/
├── src/
│   ├── Main.elm                 # Application entry point, routing
│   ├── Types.elm                # Shared types and JSON decoders
│   ├── Api.elm                  # Backend API integration
│   ├── Components/              # Reusable UI components
│   │   ├── Layout.elm
│   │   ├── SearchBar.elm
│   │   ├── StatCard.elm
│   │   ├── OrderCard.elm
│   │   ├── QuoteCard.elm
│   │   ├── Chart.elm
│   │   └── Modal.elm
│   └── Pages/                   # Feature pages
│       ├── Dashboard.elm
│       ├── Search.elm
│       └── OrderDetail.elm
├── index.html                   # HTML entry point
├── vite.config.js              # Vite configuration
├── elm.json                     # Elm dependencies
└── package.json                 # Node dependencies
```

## 🏃 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Elm 0.19.1 (`npm install -g elm`)

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Building for Production

```bash
# Create optimized production build
npm run build

# Preview production build
npm run preview
```

## 🔌 Backend Integration

The frontend expects a backend API at `http://localhost:8000` with the following endpoints:

- `GET /api/stats` - Dashboard statistics
- `GET /api/insights` - AI-discovered insights
- `POST /api/search/keyword` - Keyword search
- `POST /api/search/semantic` - Semantic search
- `GET /api/orders` - Paginated order list
- `GET /api/orders/:id` - Order details

API configuration can be set via the `VITE_API_BASE_URL` environment variable.

## 📊 Build Stats

- **Bundle Size**: 116.08 KB (37.17 KB gzipped)
- **Build Time**: ~500ms
- **Zero console errors**
- **100% type-safe** - All data validated through Elm's type system

## 🎨 Styling

The application uses Tailwind CSS via CDN for rapid development with a professional Westlaw-inspired color scheme:

- **Primary**: Blue-900 (#1e3a8a)
- **Secondary**: Blue-800 (#1e40af)
- **Accent**: Blue-500 (#3b82f6)

Responsive breakpoints:
- Mobile: < 768px
- Desktop: >= 768px

## 🧪 Type Safety

All API responses are decoded through Elm's type system:
- JSON decoders ensure runtime safety
- Compiler catches type mismatches at build time
- RemoteData pattern for loading states
- Exhaustive pattern matching prevents bugs

## 🚦 Routing

- `/` - Dashboard
- `/search` - Search page
- `/order/:id` - Order detail page

## 📝 Development Notes

- **Hot Module Replacement**: Full HMR support via Vite
- **Type Errors**: Elm compiler provides helpful error messages
- **No Runtime Exceptions**: Elm guarantees no runtime errors
- **Immutable State**: All state updates are pure functions

## 🔮 Future Enhancements

- Pagination for search results
- Advanced filters (date range, expert field, ruling type)
- Export functionality (PDF, CSV)
- Saved searches and bookmarks
- Real-time clipboard support for quotes
- Accessibility improvements (ARIA labels, keyboard navigation)
- Unit tests with elm-test
- E2E tests with Cypress

## 📄 License

Part of the TR Project legal document analysis system.
