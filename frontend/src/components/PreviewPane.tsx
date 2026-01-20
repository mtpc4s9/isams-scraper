import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Download, Copy, Check, FileText } from 'lucide-react';

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
        <div className="bento-item p-0 overflow-hidden flex flex-col h-[700px] border-2 border-border shadow-2xl">
            <div className="px-6 py-4 border-b border-border flex justify-between items-center bg-surface/50 backdrop-blur-md">
                <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-primary/10 rounded-md">
                        <FileText className="w-4 h-4 text-primary" />
                    </div>
                    <h3 className="font-bold text-sm tracking-tight">Generated Output</h3>
                    <div className="px-2 py-0.5 bg-secondary/10 rounded-full text-[10px] font-bold text-secondary uppercase tracking-widest">Markdown</div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={handleCopy}
                        className="flex items-center gap-2 px-3 py-1.5 hover:bg-secondary/10 rounded-lg transition-all text-secondary hover:text-foreground font-bold text-xs uppercase tracking-wider border border-transparent hover:border-border"
                    >
                        {copied ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                        {copied ? 'Copied' : 'Copy'}
                    </button>
                    <button
                        onClick={handleDownload}
                        className="btn-primary flex items-center gap-2 py-2 px-4 text-xs font-bold uppercase tracking-widest shadow-lg shadow-primary/10"
                    >
                        <Download className="w-4 h-4" />
                        Download
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-8 bg-surface/30">
                <div className="max-w-4xl mx-auto">
                    <article className="prose prose-slate prose-invert max-w-none 
                        prose-headings:font-bold prose-headings:tracking-tight prose-headings:text-foreground
                        prose-p:text-secondary prose-p:leading-relaxed
                        prose-strong:text-foreground prose-strong:font-bold
                        prose-code:text-primary prose-code:bg-primary/5 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded-md prose-code:before:content-none prose-code:after:content-none
                        prose-pre:bg-secondary/5 prose-pre:border prose-pre:border-border prose-pre:rounded-2xl
                        prose-li:text-secondary
                        prose-img:rounded-2xl prose-img:border prose-img:border-border prose-img:shadow-xl">
                        <ReactMarkdown>{markdown}</ReactMarkdown>
                    </article>
                </div>
            </div>

            <div className="px-6 py-2 border-t border-border bg-surface/50 flex justify-between items-center">
                <p className="text-[10px] font-bold text-secondary/50 uppercase tracking-widest">
                    Character Count: {markdown.length.toLocaleString()}
                </p>
                <div className="flex gap-1">
                    {[1, 2, 3].map(i => <div key={i} className="w-1.5 h-1.5 rounded-full bg-border" />)}
                </div>
            </div>
        </div>
    );
};

export default PreviewPane;
