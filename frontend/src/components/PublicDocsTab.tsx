import React, { useState } from 'react';
import { Globe, Terminal, Loader2, AlertCircle } from 'lucide-react';
import { scrapeOdoo, scrapePromptingGuide } from '../api';

const PublicDocsTab: React.FC = () => {
    const [activeTool, setActiveTool] = useState<'odoo' | 'prompting'>('odoo');
    const [url, setUrl] = useState('');
    const [markdown, setMarkdown] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleScrape = async () => {
        setIsLoading(true);
        setError('');
        setMarkdown('');

        try {
            let response;
            if (activeTool === 'odoo') {
                response = await scrapeOdoo(url);
            } else {
                response = await scrapePromptingGuide(url);
            }

            if (response.success) {
                setMarkdown(response.markdown_content);
            } else {
                setError(response.message || 'Scraping failed');
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full max-w-6xl mx-auto flex gap-6">
            {/* Sidebar */}
            <div className="w-64 flex-shrink-0 space-y-2">
                <button
                    onClick={() => { setActiveTool('odoo'); setUrl(''); setMarkdown(''); setError(''); }}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${activeTool === 'odoo'
                            ? 'bg-primary text-white shadow-lg shadow-primary/25'
                            : 'bg-surface hover:bg-surface/80 text-secondary hover:text-foreground'
                        }`}
                >
                    <Globe className="w-5 h-5" />
                    <span className="font-medium">Odoo 18 Docs</span>
                </button>
                <button
                    onClick={() => { setActiveTool('prompting'); setUrl(''); setMarkdown(''); setError(''); }}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 ${activeTool === 'prompting'
                            ? 'bg-primary text-white shadow-lg shadow-primary/25'
                            : 'bg-surface hover:bg-surface/80 text-secondary hover:text-foreground'
                        }`}
                >
                    <Terminal className="w-5 h-5" />
                    <span className="font-medium">Prompting Guide</span>
                </button>
            </div>

            {/* Main Content */}
            <div className="flex-1 glass-card rounded-2xl p-6 min-h-[500px] flex flex-col">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white mb-2">
                        {activeTool === 'odoo' ? 'Odoo 18 Documentation' : 'Prompting Guide'}
                    </h2>
                    <p className="text-secondary">
                        {activeTool === 'odoo'
                            ? 'Extract documentation from Odoo 18 official site.'
                            : 'Scrape prompting guides and resources.'}
                    </p>
                </div>

                <div className="flex gap-4 mb-6">
                    <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder={activeTool === 'odoo' ? "https://www.odoo.com/documentation/18.0/..." : "https://www.promptingguide.ai/..."}
                        className="flex-1 bg-background/50 border border-white/10 rounded-xl px-4 py-3 text-foreground placeholder-secondary focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all"
                    />
                    <button
                        onClick={handleScrape}
                        disabled={isLoading || !url}
                        className="px-6 py-3 bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-xl transition-all shadow-lg shadow-primary/25 flex items-center gap-2 min-w-[120px] justify-center"
                    >
                        {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Scrape'}
                    </button>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <p>{error}</p>
                    </div>
                )}

                {markdown && (
                    <div className="flex-1 bg-background/50 rounded-xl p-4 border border-white/5 overflow-y-auto font-mono text-sm text-secondary custom-scrollbar">
                        <div className="flex justify-between items-center mb-2 pb-2 border-b border-white/5">
                            <span className="text-xs uppercase tracking-wider font-semibold text-secondary/70">Markdown Output</span>
                            <button
                                onClick={() => navigator.clipboard.writeText(markdown)}
                                className="text-xs text-primary hover:text-primary/80 transition-colors"
                            >
                                Copy to Clipboard
                            </button>
                        </div>
                        <pre className="whitespace-pre-wrap">{markdown}</pre>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PublicDocsTab;
