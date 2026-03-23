import axios from 'axios';

// Ensure base URL always ends with /api/v1 so requests hit the correct backend routes.
// Handles both: "https://example.onrender.com" and "https://example.onrender.com/api/v1"
const rawBase = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_URL = rawBase.replace(/\/+$/, '').endsWith('/api/v1')
    ? rawBase.replace(/\/+$/, '')
    : `${rawBase.replace(/\/+$/, '')}/api/v1`;

const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const generatePodcast = async (attribution, voice = null, language = "both", customPrompt = null) => {
    try {
        const payload = { name: attribution, language };
        if (voice) payload.voice_agent = voice;
        if (customPrompt != null && String(customPrompt).trim() !== '') payload.custom_prompt = String(customPrompt).trim();
        const response = await apiClient.post('/generate', payload);
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        const data = error.response?.data;
        const detail = data?.detail;
        if (typeof detail === 'string') throw detail;
        if (Array.isArray(detail) && detail.length > 0) throw detail[0]?.msg ?? detail[0];
        if (data?.error) throw data.error;
        if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
            throw 'Cannot reach the backend. Is it running on port 8000? Start it with: cd backend && uvicorn app.main:app --reload';
        }
        throw error.message || 'Failed to generate podcast. Please try again.';
    }
};

export const getAgentInfo = async () => {
    const response = await apiClient.get('/agent-info');
    return response.data;
};

export const getAgentInstruction = async (date = 'yesterday', attribution = 'Smart Finance Agent') => {
    const response = await apiClient.get('/agent-instruction', {
        params: { date, attribution }
    });
    return response.data;
};

export const getFinancialNews = async (limit = 25) => {
    const response = await apiClient.get('/financial-news', { params: { limit } });
    return response.data;
};

/** Fetch all published podcasts (shared list for all users). */
export const getPodcasts = async () => {
    const response = await apiClient.get('/podcasts');
    return response.data;
};

/** Publish a podcast to the shared list so everyone can see it. */
export const publishPodcast = async (payload) => {
    const response = await apiClient.post('/podcasts', payload);
    return response.data;
};

export default apiClient;
