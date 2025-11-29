import axios from 'axios';

const API_URL = 'http://127.0.0.1:8001';

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const checkHealth = async () => {
    try {
        const response = await api.get('/');
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const login = async (username, password) => {
    const response = await api.post('/login', { username, password });
    return response.data;
};

export const launchLogin = async () => {
    const response = await api.post('/launch-login');
    return response.data;
};

export const checkAuth = async () => {
    const response = await api.get('/check-auth');
    return response.data;
};

export const scrape = async (categoryUrl) => {
    const response = await api.post('/scrape', { category_url: categoryUrl });
    return response.data;
};
