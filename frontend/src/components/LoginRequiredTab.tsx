import React, { useState } from 'react';
import LoginForm from './LoginForm';
import ScraperTool from './ScraperTool';
import PreviewPane from './PreviewPane';
import { ShieldCheck } from 'lucide-react';

const LoginRequiredTab: React.FC = () => {
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
        <div className="w-full max-w-5xl mx-auto">
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
        </div>
    );
};

export default LoginRequiredTab;
