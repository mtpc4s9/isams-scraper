import { useState } from 'react';
import LoginRequiredTab from './components/LoginRequiredTab';
import PublicDocsTab from './components/PublicDocsTab';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import { AnimatePresence, motion } from 'framer-motion';

function App() {
  const [activeTab, setActiveTab] = useState<'login' | 'public'>('login');

  return (
    <div className="flex min-h-screen bg-background text-foreground selection:bg-primary/30 selection:text-primary">
      {/* Sidebar - Persistent */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <TopNav />

        <main className="flex-1 overflow-y-auto p-8 relative">
          {/* Ambient Background Glow for Content */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-[100px] -z-10" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent/5 rounded-full blur-[80px] -z-10" />

          <div className="max-w-6xl mx-auto w-full">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10, filter: 'blur(8px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                exit={{ opacity: 0, y: -10, filter: 'blur(8px)' }}
                transition={{ duration: 0.3, ease: 'easeInOut' }}
                className="w-full"
              >
                {activeTab === 'login' ? <LoginRequiredTab /> : <PublicDocsTab />}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>

        <footer className="p-4 border-t border-border bg-surface/50 text-center">
          <p className="text-secondary text-xs font-medium">
            &copy; 2025 DocScraper Pro &bull; Developed by Antigravity &bull; Local Secure Environment
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
