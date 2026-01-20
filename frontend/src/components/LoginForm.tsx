import { useState } from 'react';
import { launchLogin, checkAuth, checkHealth } from '../api';
import { Lock, ExternalLink, CheckCircle2, RefreshCw, AlertCircle, Terminal } from 'lucide-react';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

interface LoginFormProps {
    onLoginSuccess: () => void;
}

const LoginForm = ({ onLoginSuccess }: LoginFormProps) => {
    const [step, setStep] = useState<'initial' | 'checking'>('initial');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [healthStatus, setHealthStatus] = useState<'idle' | 'checking' | 'ok' | 'fail'>('idle');

    const handleCheckHealth = async () => {
        setHealthStatus('checking');
        try {
            await checkHealth();
            setHealthStatus('ok');
            setTimeout(() => setHealthStatus('idle'), 3000);
        } catch (err) {
            setHealthStatus('fail');
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
        <div className="max-w-2xl mx-auto py-12">
            <div className="bento-item p-10 shadow-2xl shadow-primary/5 bg-gradient-to-br from-surface to-surface/90">
                <div className="flex flex-col items-center text-center">
                    <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mb-6 ring-1 ring-primary/20">
                        <Lock className="w-8 h-8 text-primary" />
                    </div>
                    <h2 className="text-3xl font-bold tracking-tight mb-2">Secure Authentication</h2>
                    <p className="text-secondary max-w-sm font-medium mb-10">
                        iSAMS requires manual authentication. Launch the controlled browser instance to continue.
                    </p>
                </div>

                <div className="space-y-6">
                    {step === 'initial' ? (
                        <div className="space-y-4">
                            <button
                                onClick={handleLaunch}
                                disabled={loading}
                                className="w-full btn-primary py-5 text-lg flex items-center justify-center gap-3 shadow-blue-500/20 shadow-xl"
                            >
                                {loading ? (
                                    <RefreshCw className="animate-spin w-5 h-5" />
                                ) : (
                                    <ExternalLink className="w-5 h-5" />
                                )}
                                <span>Initialize Secure Browser</span>
                            </button>

                            <div className="flex items-center justify-center pt-2">
                                <button
                                    onClick={handleCheckHealth}
                                    className={cn(
                                        "flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all border",
                                        healthStatus === 'idle' && "text-secondary hover:text-foreground border-border bg-secondary/5",
                                        healthStatus === 'checking' && "text-blue-500 border-blue-500/20 bg-blue-500/5",
                                        healthStatus === 'ok' && "text-green-500 border-green-500/20 bg-green-500/5",
                                        healthStatus === 'fail' && "text-red-500 border-red-500/20 bg-red-500/5"
                                    )}
                                >
                                    {healthStatus === 'checking' ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Terminal className="w-3 h-3" />}
                                    {healthStatus === 'idle' && "DEBUG: CHECK BACKEND"}
                                    {healthStatus === 'checking' && "CONNECTING..."}
                                    {healthStatus === 'ok' && "SYSTEM ONLINE"}
                                    {healthStatus === 'fail' && "SYSTEM OFFLINE"}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="space-y-4"
                        >
                            <div className="p-6 bg-accent/5 border border-accent/20 rounded-2xl flex items-start gap-4">
                                <AlertCircle className="w-6 h-6 text-accent shrink-0 mt-0.5" />
                                <div>
                                    <p className="font-bold text-accent text-sm mb-1 uppercase tracking-tight">Required Action</p>
                                    <p className="text-foreground/80 text-sm leading-relaxed">
                                        Open the browser window that just appeared. Log in to iSAMS normally, then return here to verify your session.
                                    </p>
                                </div>
                            </div>

                            <button
                                onClick={handleVerify}
                                disabled={loading}
                                className="w-full bg-green-500 text-white font-bold py-5 rounded-2xl shadow-xl shadow-green-500/20 hover:bg-green-600 active:scale-95 transition-all flex items-center justify-center gap-3"
                            >
                                {loading ? (
                                    <RefreshCw className="animate-spin w-5 h-5" />
                                ) : (
                                    <CheckCircle2 className="w-5 h-5" />
                                )}
                                <span>Verify Active Session</span>
                            </button>

                            <button
                                onClick={() => setStep('initial')}
                                className="w-full text-secondary hover:text-foreground font-bold text-xs uppercase tracking-widest py-3 transition-colors"
                            >
                                Cancel authentication
                            </button>
                        </motion.div>
                    )}

                    <AnimatePresence>
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: -10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500 text-sm font-semibold"
                            >
                                <AlertCircle className="w-4 h-4" />
                                {error}
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            <p className="mt-8 text-center text-secondary/60 text-[10px] uppercase font-bold tracking-[0.2em]">
                Secure Session Management &bull; AES-256 Encrypted
            </p>
        </div>
    );
};

export default LoginForm;
