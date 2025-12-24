import React, { useState } from 'react';
import { scrape, scrapeIsamsDeveloper } from '../api';
import { Search, Loader2, FileText, CheckCircle } from 'lucide-react';

interface ScraperToolProps {
    onScrapeSuccess: (markdown: string, articles: any[]) => void;
    scraperType?: 'isams' | 'isams-developer';
}

const ScraperTool: React.FC<ScraperToolProps> = ({ onScrapeSuccess, scraperType = 'isams' }) => {
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('');

    const handleScrape = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setStatus('Initializing scraper...');
        try {
            // Simulate progress updates
            setTimeout(() => setStatus('Navigating to documentation...'), 1000);
            setTimeout(() => setStatus('Extracting content...'), 3000);

            const response = scraperType === 'isams'
                ? await scrape(url)
                : await scrapeIsamsDeveloper(url);

            if (response.success) {
                setStatus('Processing content...');
                // For isams-developer, 'articles' might be empty or different structure, 
                // but we primarily care about markdown_content
                onScrapeSuccess(response.markdown_content, response.articles || []);
                setStatus('Completed!');
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
        <div className="glass-card p-6 rounded-2xl mb-8">
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Search className="text-accent" />
                <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                    Target Category
                </span>
            </h3>
            <form onSubmit={handleScrape} className="flex gap-4">
                <input
                    type="url"
                    placeholder="https://support.isams.com/hc/en-us/categories/..."
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="flex-1 bg-surface/50 border border-white/10 rounded-xl py-3 px-4 text-white placeholder-secondary focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                    required
                />
                <button
                    type="submit"
                    disabled={loading}
                    className="bg-surface hover:bg-white/10 border border-white/10 text-white font-medium py-3 px-6 rounded-xl transition-all disabled:opacity-50 flex items-center gap-2"
                >
                    {loading ? <Loader2 className="animate-spin" /> : <FileText />}
                    {loading ? 'Processing' : 'Extract'}
                </button>
            </form>

            {status && (
                <div className={`mt-4 flex items-center gap-2 text-sm ${status.includes('Error') ? 'text-red-400' : 'text-accent'}`}>
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : status.includes('Error') ? null : <CheckCircle className="w-4 h-4" />}
                    {status}
                </div>
            )}
        </div>
    );
};

export default ScraperTool;
