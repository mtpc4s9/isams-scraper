import { Search, Bell, Settings } from 'lucide-react';

const TopNav: React.FC = () => {
    return (
        <header className="h-16 border-b border-border bg-surface/80 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-8">
            <div className="flex items-center gap-4 flex-1 max-w-xl">
                <div className="relative w-full group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-secondary group-focus-within:text-primary transition-colors" />
                    <input
                        type="text"
                        placeholder="Search tools, documentation, history..."
                        className="w-full bg-secondary/5 border border-border rounded-xl py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all"
                    />
                </div>
            </div>

            <div className="flex items-center gap-3">
                <button className="p-2 text-secondary hover:text-foreground hover:bg-secondary/10 rounded-lg transition-all">
                    <Bell className="w-5 h-5" />
                </button>
                <button className="p-2 text-secondary hover:text-foreground hover:bg-secondary/10 rounded-lg transition-all">
                    <Settings className="w-5 h-5" />
                </button>
                <div className="h-8 w-[1px] bg-border mx-2" />
                <button className="flex items-center gap-2 pl-2 pr-1 py-1 hover:bg-secondary/10 rounded-full transition-all">
                    <span className="text-sm font-semibold pr-1">Admin</span>
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold">
                        MT
                    </div>
                </button>
            </div>
        </header>
    );
};

export default TopNav;
