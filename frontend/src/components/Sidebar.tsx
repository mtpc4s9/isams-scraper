import React from 'react';
import { cn } from '../lib/utils';
import { Database, Lock, Globe, ChevronRight } from 'lucide-react';

interface SidebarProps {
    activeTab: 'login' | 'public';
    setActiveTab: (tab: 'login' | 'public') => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
    const menuItems = [
        { id: 'login', label: 'iSAMS Scraper', icon: Lock, description: 'Login required tools' },
        { id: 'public', label: 'Public Docs', icon: Globe, description: 'Open source documentation' },
    ];

    return (
        <aside className="w-72 bg-surface border-r border-border flex flex-col h-screen sticky top-0">
            <div className="p-6 flex items-center gap-3 border-b border-border">
                <div className="p-2 bg-primary/10 rounded-lg">
                    <Database className="w-6 h-6 text-primary" />
                </div>
                <div>
                    <h2 className="font-bold text-lg tracking-tight">DocScraper</h2>
                    <p className="text-xs text-secondary font-medium">v1.2.0 Pro</p>
                </div>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id as any)}
                            className={cn(
                                "w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 group text-left",
                                isActive
                                    ? "bg-primary text-white shadow-lg shadow-primary/20"
                                    : "text-secondary hover:bg-secondary/10 hover:text-foreground"
                            )}
                        >
                            <div className={cn(
                                "p-2 rounded-lg transition-colors",
                                isActive ? "bg-white/20" : "bg-secondary/10 group-hover:bg-secondary/20"
                            )}>
                                <Icon className="w-5 h-5" />
                            </div>
                            <div className="flex-1">
                                <p className="font-semibold text-sm">{item.label}</p>
                                <p className={cn("text-[10px]", isActive ? "text-white/70" : "text-secondary/70")}>
                                    {item.description}
                                </p>
                            </div>
                            {isActive && <ChevronRight className="w-4 h-4 text-white/50" />}
                        </button>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-border">
                <div className="p-4 bg-secondary/5 rounded-2xl border border-border">
                    <p className="text-xs font-semibold text-secondary mb-1 uppercase tracking-wider">System Status</p>
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-xs font-medium text-foreground">Backend Connected</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
