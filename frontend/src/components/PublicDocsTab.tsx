import { useState } from 'react';
import { Globe, Terminal, Loader2, AlertCircle, Search, FileText, ChevronRight, BookOpen } from 'lucide-react';
import { scrapeOdoo, scrapePromptingGuide } from '../api';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

const PublicDocsTab = () => {
    const [activeTool, setActiveTool] = useState<'odoo' | 'prompting'>('odoo');
    const [url, setUrl] = useState('');
    const [markdown, setMarkdown] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [status, setStatus] = useState('');

    const handleScrape = async () => {
        setIsLoading(true);
        setStatus('Initializing scraping task...');
        setMarkdown('');

        try {
            // Simulate progress for better UX
            const steps = ['Analyzing source architecture...', 'Bypassing basic rate limits...', 'Parsing content tree...', 'Converting to markdown...'];
            let i = 0;
            const timer = setInterval(() => {
                if (i < steps.length) setStatus(steps[i++]);
                else clearInterval(timer);
            }, 1200);

            const response = activeTool === 'odoo'
                ? await scrapeOdoo(url)
                : await scrapePromptingGuide(url);

            clearInterval(timer);

            if (response.success) {
                setMarkdown(response.markdown_content);
                setStatus('Extraction Complete');
            } else {
                setStatus(`Error: ${response.message || 'Scraping failed'}`);
            }
        } catch (err: any) {
            setStatus(`Error: ${err.response?.data?.detail || err.message || 'An error occurred'}`);
        } finally {
            setIsLoading(false);
        }
    };

    const tools = [
        {
            id: 'odoo',
            label: 'Odoo 18 Docs',
            icon: <Globe className="w-5 h-5 text-blue-500" />,
            desc: 'Official Odoo ERP documentation extraction.',
            placeholder: 'https://www.odoo.com/documentation/18.0/...'
        },
        {
            id: 'prompting',
            label: 'Prompting Guide',
            icon: <Terminal className="w-5 h-5 text-orange-500" />,
            desc: 'PromptingGuide.ai content retrieval.',
            placeholder: 'https://www.promptingguide.ai/...'
        }
    ];

    return (
        <div className="space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight mb-1">Public Document Scraper</h1>
                    <p className="text-secondary text-sm font-medium">Extract content from open documentation platforms without authentication.</p>
                </div>
                <div className="px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-xl text-blue-500 text-sm font-bold shadow-sm flex items-center gap-2">
                    <BookOpen className="w-4 h-4" />
                    Public Access
                </div>
            </div>

            <div className="bento-grid">
                {/* Tool Selector */}
                <div className="md:col-span-1 space-y-4">
                    {tools.map((tool) => {
                        const isActive = activeTool === tool.id;
                        return (
                            <button
                                key={tool.id}
                                onClick={() => { setActiveTool(tool.id as any); setUrl(''); setMarkdown(''); setStatus(''); }}
                                className={cn(
                                    "w-full bento-item text-left transition-all duration-300 group relative overflow-hidden",
                                    isActive ? "ring-2 ring-primary border-primary bg-primary/5 shadow-xl shadow-primary/10" : "hover:border-primary/30"
                                )}
                            >
                                <div className="flex items-center gap-4 relative z-10">
                                    <div className={cn("p-3 rounded-2xl transition-all", isActive ? "bg-primary/20" : "bg-secondary/5 group-hover:bg-secondary/10")}>
                                        {tool.icon}
                                    </div>
                                    <div className="flex-1">
                                        <h4 className="font-bold text-sm tracking-tight">{tool.label}</h4>
                                        <p className="text-[10px] text-secondary font-bold uppercase tracking-wider">{tool.desc}</p>
                                    </div>
                                    <ChevronRight className={cn("w-4 h-4 text-secondary transition-all", isActive ? "translate-x-0 opacity-100" : "-translate-x-2 opacity-0 group-hover:translate-x-0 group-hover:opacity-100")} />
                                </div>
                                {isActive && (
                                    <motion.div
                                        layoutId="active-glow"
                                        className="absolute -bottom-8 -right-8 w-16 h-16 bg-primary/20 blur-2xl rounded-full"
                                    />
                                )}
                            </button>
                        );
                    })}
                </div>

                {/* Scraper Input Card */}
                <div className="md:col-span-2 bento-item shadow-2xl bg-surface/30 border-2">
                    <div className="flex items-center gap-3 mb-8">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <Search className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <h3 className="font-bold text-lg tracking-tight">Source Parameters</h3>
                            <p className="text-secondary text-xs font-semibold uppercase tracking-wider">Configure public target URL</p>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="relative group">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 p-1 bg-secondary/10 rounded-md">
                                <Globe className="w-4 h-4 text-secondary group-focus-within:text-primary transition-colors" />
                            </div>
                            <input
                                type="url"
                                placeholder={tools.find(t => t.id === activeTool)?.placeholder}
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                className="w-full bg-surface border-2 border-border rounded-2xl py-4 pl-14 pr-4 font-mono text-sm focus:outline-none focus:border-primary/50 focus:ring-4 focus:ring-primary/5 transition-all placeholder:text-secondary/50"
                            />
                        </div>

                        <div className="flex items-center justify-between gap-4">
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
                                                status.includes('Error') ? "text-red-500" : "text-primary/70"
                                            )}
                                        >
                                            {isLoading ? <Loader2 className="w-3 h-3 animate-spin" /> :
                                                status.includes('Error') ? <AlertCircle className="w-3 h-3" /> : null}
                                            {status}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>

                            <button
                                onClick={handleScrape}
                                disabled={isLoading || !url}
                                className="btn-primary flex items-center gap-2 py-3 px-10 shadow-xl shadow-primary/10"
                            >
                                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
                                <span className="font-bold uppercase tracking-wider text-xs">Execute Scrape</span>
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Markdown Preview Overlay */}
            <AnimatePresence>
                {markdown && (
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 30 }}
                        className="relative z-10"
                    >
                        <article className="bento-item p-0 overflow-hidden flex flex-col h-[600px] border-2 border-border bg-surface/40 backdrop-blur-xl">
                            <div className="px-6 py-4 border-b border-border flex justify-between items-center bg-surface/50">
                                <div className="flex items-center gap-3">
                                    <FileText className="w-4 h-4 text-primary" />
                                    <span className="font-bold text-sm">Extracted Data</span>
                                    <div className="px-2 py-0.5 bg-green-500/10 text-green-500 text-[10px] font-bold uppercase rounded-full tracking-widest">Active Result</div>
                                </div>
                                <button
                                    onClick={() => navigator.clipboard.writeText(markdown)}
                                    className="text-xs font-bold uppercase tracking-widest text-secondary hover:text-primary transition-colors"
                                >
                                    Copy Raw Markdown
                                </button>
                            </div>
                            <div className="flex-1 overflow-y-auto p-8 font-mono text-sm leading-relaxed text-secondary/80 custom-scrollbar">
                                <pre className="whitespace-pre-wrap">{markdown}</pre>
                            </div>
                        </article>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default PublicDocsTab;
