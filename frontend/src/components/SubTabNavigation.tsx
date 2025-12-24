import React from 'react';

interface SubTab {
    id: string;
    label: string;
    icon?: React.ReactNode;
}

interface SubTabNavigationProps {
    tabs: SubTab[];
    activeTabId: string;
    onTabChange: (id: string) => void;
}

const SubTabNavigation: React.FC<SubTabNavigationProps> = ({ tabs, activeTabId, onTabChange }) => {
    return (
        <div className="flex gap-2 mb-6 p-1 bg-surface/30 border border-white/5 rounded-xl w-fit">
            {tabs.map((tab) => (
                <button
                    key={tab.id}
                    onClick={() => onTabChange(tab.id)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${activeTabId === tab.id
                            ? 'bg-primary/20 text-primary border border-primary/30 shadow-sm'
                            : 'text-secondary hover:text-foreground hover:bg-white/5 border border-transparent'
                        }`}
                >
                    {tab.icon}
                    {tab.label}
                </button>
            ))}
        </div>
    );
};

export default SubTabNavigation;
