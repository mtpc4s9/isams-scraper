import React, { useState } from 'react';
import LoginForm from './components/LoginForm';
import ScraperTool from './components/ScraperTool';
import PreviewPane from './components/PreviewPane';
import { Database, ShieldCheck } from 'lucide-react';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [markdown, setMarkdown] = useState('');
  const [articles, setArticles] = useState<any[]>([]);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleScrapeSuccess = (md: string, arts: any[]) => {
    setMarkdown(md);
    setArticles(arts);
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center py-12 px-4 relative overflow-hidden">
      {/* Background Ambient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-primary/20 rounded-full blur-[120px] -z-10 animate-pulse-slow" />

      <header className="mb-12 text-center relative z-10">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 bg-surface border border-white/10 rounded-xl shadow-lg shadow-primary/20">
            <Database className="w-8 h-8 text-primary" />
          </div>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-gray-200 to-gray-400 mb-4 tracking-tight">
          iSAMS Documentation Scraper
        </h1>
        <p className="text-secondary text-lg max-w-2xl mx-auto">
          Securely extract and format knowledge base articles for RAG ingestion.
        </p>
      </header>

      <main className="w-full max-w-5xl relative z-10">
        {!isAuthenticated ? (
          <LoginForm onLoginSuccess={handleLoginSuccess} />
        ) : (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full text-green-400 text-sm font-medium">
                <ShieldCheck className="w-4 h-4" />
                Session Authenticated
              </div>
            </div>

            <ScraperTool onScrapeSuccess={handleScrapeSuccess} />

            {markdown && (
              <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                <PreviewPane markdown={markdown} />
              </div>
            )}
          </div>
        )}
      </main>

      <footer className="mt-16 text-secondary text-sm text-center">
        <p>&copy; 2025 iSAMS Scraper Tool. Local Secure Environment.</p>
      </footer>
    </div>
  );
}

export default App;
