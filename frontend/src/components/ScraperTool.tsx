import React, { useState } from 'react';
import { scrape, scrapeIsamsDeveloper, scrapeToddle } from '../api';
import { Search, Loader2, FileText, CheckCircle, AlertCircle, Globe } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface ScraperToolProps {
    onScrapeSuccess: (markdown: string, articles: any[]) => void;
    scraperType?: 'isams' | 'isams-developer' | 'toddle';
}

const ScraperTool: React.FC<ScraperToolProps> = ({ onScrapeSuccess, scraperType = 'isams' }) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');

    const handleScrape = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setStatus('Initializing...');
        try {
            // Simulate progression
            const steps = [
                'Navigating to source...',
                'Parsing HTML structure...',
                'Extracting documentation body...',
                'Formatting to Markdown...'
            ];

            let i = 0;
            const timer = setInterval(() => {
                if (i < steps.length) setStatus(steps[i++]);
                else clearInterval(timer);
            }, 1500);

            const response = scraperType === 'isams'
                ? await scrape(url)
                : scraperType === 'isams-developer'
                    ? await scrapeIsamsDeveloper(url)
                    : await scrapeToddle(url);

            clearInterval(timer);

            if (response.success) {
                onScrapeSuccess(response.markdown_content, response.articles || []);
                setStatus('Extraction Successful');
            } else {
                setStatus(`Error: ${response.message}`);
            }
        } catch (err: any) {
            setStatus(`Error: ${err.response?.data?.detail || 'Scraping failed'}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bento-item bg-surface/30 backdrop-blur-sm border-2 border-border shadow-inner">
            <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-accent/10 rounded-lg">
                    <Globe className="w-5 h-5 text-accent" />
                </div>
                <div>
                    <h3 className="font-bold text-lg tracking-tight">Source Configuration</h3>
                    <p className="text-secondary text-xs font-semibold uppercase tracking-wider">Configure extraction parameters</p>
                </div>
            </div>

            <form onSubmit={handleScrape} className="space-y-4">
                <div className="relative group">
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 p-1 bg-secondary/10 rounded-md">
                        <Search className="w-4 h-4 text-secondary group-focus-within:text-primary transition-colors" />
                    </div>
                    <input
                        type="url"
                        placeholder={scraperType === 'toddle' ? 'Paste Toddle Collection URL (e.g., https://support.toddleapp.com/en/collections/...)' : 'Paste iSAMS Documentation URL here...'}
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        className="w-full bg-surface border-2 border-border rounded-2xl py-4 pl-14 pr-4 font-mono text-sm focus:outline-none focus:border-primary/50 focus:ring-4 focus:ring-primary/5 transition-all placeholder:text-secondary/50"
                        required
                    />
                </div>

                <div className="flex items-center justify-between gap-4 pt-2">
                    <div className="flex-1">
                        <AnimatePresence mode="wait">
                            {status && (
                                <motion.div
                                    key={status}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 10 }}
                                    className={cn(
                                        "flex items-center gap-2 text-xs font-bold uppercase tracking-widest",
                                        status.includes('Error') ? "text-red-500" : "text-primary"
                                    )}
                                >
                                    {loading ? <Loader2 className="w-3 h-3 animate-spin" /> :
                                        status.includes('Error') ? <AlertCircle className="w-3 h-3" /> :
                                            <CheckCircle className="w-3 h-3" />}
                                    {status}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary flex items-center gap-2 py-3 px-8 shadow-xl shadow-primary/10"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                        <span className="font-bold uppercase tracking-wider text-xs">Run Extraction Task</span>
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ScraperTool;
