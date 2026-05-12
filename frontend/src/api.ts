import axios from 'axios';

const API_URL = 'http://localhost:8002';

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

export const login = async (username: string, password: string) => {
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

export const scrape = async (categoryUrl: string) => {
    const response = await api.post('/scrape', { category_url: categoryUrl });
    return response.data;
};

export const scrapeOdoo = async (url: string) => {
    const response = await api.post('/scrape-odoo', { url });
    return response.data;
};

export const scrapePromptingGuide = async (url: string) => {
    const response = await api.post('/scrape-prompting-guide', { url });
    return response.data;
};

export const scrapeIsamsDeveloper = async (url: string) => {
    const response = await api.post('/scrape-isams-developer', { url });
    return response.data;
};

export const scrapeToddle = async (url: string) => {
    const response = await api.post('/scrape-toddle', { url });
    return response.data;
};

export const scrapeFlexischools = async (url: string) => {
    const response = await api.post('/scrape-flexischools', { url });
    return response.data;
};

export const scrapePowerschool = async (url: string, role: string, headless: boolean = true) => {
    const response = await api.post('/scrape-powerschool', { url, role, headless });
    return response.data;
};

export const scrapeClasslink = async (url: string, topic: string) => {
    const response = await api.post('/scrape-classlink', { url, topic });
    return response.data;
};

export const scrapeFreshservice = async (url: string, topic: string) => {
    const response = await api.post('/scrape-freshservice', { url, topic });
    return response.data;
};

export const scrapeJamf = async (url: string) => {
    const response = await api.post('/scrape-jamf', { url });
    return response.data;
};

export const scrapeCanvas = async (url: string, category: string) => {
    const response = await api.post('/scrape-canvas', { url, category });
    return response.data;
};

export const scrapeSeqta = async (url: string, category: string, headless: boolean = true) => {
    const response = await api.post('/scrape-seqta', { url, category, headless });
    return response.data;
};
