import { useState } from 'react';
import LoginForm from './LoginForm';
import ScraperTool from './ScraperTool';
import PreviewPane from './PreviewPane';
import SubTabNavigation from './SubTabNavigation';
import { ShieldCheck, User, Code, GraduationCap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const LoginRequiredTab = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [markdown, setMarkdown] = useState('');
    const [activeSubTab, setActiveSubTab] = useState<'user' | 'developer' | 'toddle'>('user');

    const handleLoginSuccess = () => {
        setIsAuthenticated(true);
    };

    const handleScrapeSuccess = (md: string) => {
        setMarkdown(md);
    };

    const subTabs = [
        { id: 'user', label: 'User Documents', icon: <User className="w-4 h-4" /> },
        { id: 'developer', label: 'Developer Documents', icon: <Code className="w-4 h-4" /> },
        { id: 'toddle', label: 'Toddle Support', icon: <GraduationCap className="w-4 h-4" /> }
    ];

    return (
        <div className="w-full">
            <AnimatePresence mode="wait">
                {!isAuthenticated ? (
                    <motion.div
                        key="login-form"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        transition={{ duration: 0.4 }}
                    >
                        <LoginForm onLoginSuccess={handleLoginSuccess} />
                    </motion.div>
                ) : (
                    <motion.div
                        key="scraper-content"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-8"
                    >
                        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                            <div>
                                <h1 className="text-2xl font-bold tracking-tight mb-1">iSAMS Documentation Scraper</h1>
                                <p className="text-secondary text-sm font-medium">Extract structured content from iSAMS official documentation.</p>
                            </div>
                            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-xl text-green-500 text-sm font-bold shadow-sm">
                                <ShieldCheck className="w-4 h-4" />
                                Session Active
                            </div>
                        </div>

                        <div className="bento-grid">
                            <div className="md:col-span-3 bento-item bg-surface/50 border-dashed border-2 flex items-center justify-between py-4">
                                <span className="text-sm font-semibold text-secondary uppercase tracking-widest pl-2">Select Target System</span>
                                <SubTabNavigation
                                    tabs={subTabs}
                                    activeTabId={activeSubTab}
                                    onTabChange={(id) => {
                                        setActiveSubTab(id as any);
                                        setMarkdown(''); // Clear preview when switching
                                    }}
                                />
                            </div>

                            <div className="md:col-span-3">
                                <ScraperTool
                                    onScrapeSuccess={handleScrapeSuccess}
                                    scraperType={activeSubTab === 'user' ? 'isams' : activeSubTab === 'developer' ? 'isams-developer' : 'toddle'}
                                />
                            </div>
                        </div>

                        {markdown && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                            >
                                <PreviewPane markdown={markdown} />
                            </motion.div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default LoginRequiredTab;
