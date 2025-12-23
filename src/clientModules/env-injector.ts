// Inject environment variables at runtime
if (typeof window !== 'undefined') {
  (window as any).__ENV__ = {
    API_URL: process.env.NEXT_PUBLIC_API_URL,
  };
}