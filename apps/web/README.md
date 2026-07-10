# OmniSight Frontend (Next.js)

## Structure

```
apps/web/
├── src/
│   ├── pages/        # Next.js pages
│   ├── components/   # React components
│   ├── hooks/        # Custom React hooks
│   ├── services/     # API client services
│   ├── stores/       # Zustand state management
│   ├── types/        # TypeScript type definitions
│   ├── utils/        # Utility functions
│   └── styles/       # CSS & Tailwind
├── public/           # Static assets
└── tests/            # Test files
```

## Starting Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start dev server:
   ```bash
   npm run dev
   ```

3. Open browser:
   ```
   http://localhost:3000
   ```

## Building for Production

```bash
npm run build
npm start
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking
- `npm run format` - Format code with Prettier
- `npm run test` - Run tests

## Technologies

- **Framework**: Next.js 14 with React 18
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios + SWR
- **Validation**: React Hook Form + Zod
- **Animations**: Framer Motion
- **Testing**: Jest + React Testing Library
