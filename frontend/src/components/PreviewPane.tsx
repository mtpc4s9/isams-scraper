import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Download, Copy, Check } from 'lucide-react';

interface PreviewPaneProps {
    markdown: string;
}

const PreviewPane: React.FC<PreviewPaneProps> = ({ markdown }) => {
    const [copied, setCopied] = React.useState(false);

    const handleDownload = () => {
        const blob = new Blob([markdown], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'isams_documentation.md';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(markdown);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!markdown) return null;

    return (
        <div className="glass-card rounded-2xl overflow-hidden flex flex-col h-[600px]">
            <div className="p-4 border-b border-white/10 flex justify-between items-center bg-surface/50">
                <h3 className="font-semibold text-gray-300">Generated Documentation</h3>
                <div className="flex gap-2">
                    <button
                        onClick={handleCopy}
                        className="p-2 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white"
                        title="Copy to Clipboard"
                    >
                        {copied ? <Check className="w-5 h-5 text-green-400" /> : <Copy className="w-5 h-5" />}
                    </button>
                    <button
                        onClick={handleDownload}
                        className="flex items-center gap-2 bg-primary/20 hover:bg-primary/30 text-primary px-4 py-2 rounded-lg transition-colors border border-primary/20"
                    >
                        <Download className="w-4 h-4" />
                        Download .md
                    </button>
                </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6 bg-[#0d1117]">
                <div className="prose prose-invert max-w-none prose-headings:text-gray-200 prose-p:text-gray-400 prose-a:text-blue-400 prose-code:text-pink-400">
                    <ReactMarkdown>{markdown}</ReactMarkdown>
                </div>
            </div>
        </div>
    );
};

export default PreviewPane;
