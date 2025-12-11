import React, { useState } from 'react';
import LoginRequiredTab from './components/LoginRequiredTab';
import PublicDocsTab from './components/PublicDocsTab';
import { Database, Lock, Globe } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState<'login' | 'public'>('login');

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
          DocScraper Pro
        </h1>
        <p className="text-secondary text-lg max-w-2xl mx-auto">
          Unified documentation extraction tool for iSAMS, Odoo, and more.
        </p>
      </header>

      {/* Tab Navigation */}
      <div className="relative z-10 mb-8 p-1 bg-surface/50 border border-white/5 rounded-xl flex gap-1">
        <button
          onClick={() => setActiveTab('login')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all duration-200 ${activeTab === 'login'
              ? 'bg-primary text-white shadow-lg shadow-primary/25'
              : 'text-secondary hover:text-foreground hover:bg-white/5'
            }`}
        >
          <Lock className="w-4 h-4" />
          Login Required
        </button>
        <button
          onClick={() => setActiveTab('public')}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all duration-200 ${activeTab === 'public'
              ? 'bg-primary text-white shadow-lg shadow-primary/25'
              : 'text-secondary hover:text-foreground hover:bg-white/5'
            }`}
        >
          <Globe className="w-4 h-4" />
          Public Docs
        </button>
      </div>

      <main className="w-full relative z-10">
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          {activeTab === 'login' ? <LoginRequiredTab /> : <PublicDocsTab />}
        </div>
      </main>

      <footer className="mt-16 text-secondary text-sm text-center">
        <p>&copy; 2025 DocScraper Pro. Local Secure Environment.</p>
      </footer>
    </div>
  );
}

export default App;
