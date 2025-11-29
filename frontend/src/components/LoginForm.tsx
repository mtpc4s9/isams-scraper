import React, { useState } from 'react';
import { launchLogin, checkAuth, checkHealth } from '../api';
import { Lock, ExternalLink, CheckCircle2, RefreshCw } from 'lucide-react';

interface LoginFormProps {
    onLoginSuccess: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLoginSuccess }) => {
    const [step, setStep] = useState<'initial' | 'checking'>('initial');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [healthStatus, setHealthStatus] = useState('');

    const handleCheckHealth = async () => {
        setHealthStatus('Checking connection...');
        try {
            await checkHealth();
            setHealthStatus('✅ Backend Connected');
            setTimeout(() => setHealthStatus(''), 3000);
        } catch (err) {
            setHealthStatus('❌ Backend Unreachable');
        }
    };

    const handleLaunch = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await launchLogin();
            if (response.success) {
                setStep('checking');
            } else {
                setError(response.message);
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to launch browser');
        } finally {
            setLoading(false);
        }
    };

    const handleVerify = async () => {
        setLoading(true);
        setError('');
        try {
            const response = await checkAuth();
            if (response.success) {
                onLoginSuccess();
            } else {
                setError(response.message || 'Authentication not detected');
            }
        } catch (err: any) {
            setError('Verification failed');
        } finally {
            setLoading(false);
        }
    };


    return (
        <div className="glass-card p-8 rounded-2xl w-full max-w-md mx-auto transform transition-all duration-500 hover:scale-[1.02] md:max-w-lg lg:max-w-xl">
            <div className="flex justify-center mb-6">
                <div className="p-4 bg-primary/20 rounded-full">
                    <Lock className="w-8 h-8 text-primary" />
                </div>
            </div>
            <h2 className="text-2xl font-bold text-center mb-2 text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
                Manual Authentication
            </h2>
            <p className="text-center text-secondary mb-8 text-sm">
                Launch the secure browser and log in with your credentials.
            </p>

            <div className="flex justify-center mb-4">
                <button
                    onClick={handleCheckHealth}
                    className="text-xs text-secondary hover:text-white underline"
                >
                    {healthStatus || "Test Backend Connection"}
                </button>
            </div>

            <div className="space-y-4">
                {step === 'initial' ? (
                    <button
                        onClick={handleLaunch}
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-primary to-accent hover:from-blue-600 hover:to-cyan-600 text-white font-bold py-4 rounded-xl shadow-lg shadow-primary/25 transform transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {loading ? (
                            <RefreshCw className="animate-spin w-5 h-5" />
                        ) : (
                            <ExternalLink className="w-5 h-5" />
                        )}
                        Launch Login Page
                    </button>
                ) : (
                    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4">
                        <div className="bg-yellow-500/10 border border-yellow-500/20 p-4 rounded-xl text-yellow-200 text-sm text-center">
                            Please log in to iSAMS in the opened Chrome window.
                        </div>
                        <button
                            onClick={handleVerify}
                            disabled={loading}
                            className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-green-500/25 transform transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <RefreshCw className="animate-spin w-5 h-5" />
                            ) : (
                                <CheckCircle2 className="w-5 h-5" />
                            )}
                            I have logged in
                        </button>
                        <button
                            onClick={() => setStep('initial')}
                            className="w-full text-secondary hover:text-white text-sm py-2"
                        >
                            Cancel / Retry
                        </button>
                    </div>
                )}

                {error && (
                    <div className="text-red-400 text-sm text-center bg-red-500/10 py-2 rounded-lg animate-in fade-in">
                        {error}
                    </div>
                )}
            </div>
        </div>
    );
};

export default LoginForm;
