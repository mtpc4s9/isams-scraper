import React from 'react';
import { cn } from '../lib/utils';
import { motion } from 'framer-motion';

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
        <div className="flex gap-1 p-1 bg-secondary/10 border border-border rounded-xl w-fit">
            {tabs.map((tab) => {
                const isActive = activeTabId === tab.id;
                return (
                    <button
                        key={tab.id}
                        onClick={() => onTabChange(tab.id)}
                        className={cn(
                            "relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-bold transition-all duration-200",
                            isActive ? "text-primary" : "text-secondary hover:text-foreground"
                        )}
                    >
                        {isActive && (
                            <motion.div
                                layoutId="subtab-active"
                                className="absolute inset-0 bg-surface border border-border rounded-lg shadow-sm"
                                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                            />
                        )}
                        <span className="relative z-10 flex items-center gap-2">
                            {tab.icon}
                            {tab.label}
                        </span>
                    </button>
                );
            })}
        </div>
    );
};

export default SubTabNavigation;
