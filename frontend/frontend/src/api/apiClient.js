import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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
        const detail = error.response?.data?.detail;
        if (typeof detail === 'string') throw detail;
        if (Array.isArray(detail) && detail.length > 0) throw detail[0]?.msg ?? detail[0];
        if (error.response?.data?.error) throw error.response.data.error;
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

export default apiClient;
