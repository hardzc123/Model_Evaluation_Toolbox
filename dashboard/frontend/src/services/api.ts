import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface LeaderboardEntry {
  model_id: string;
  model_name: string;
  provider: string;
  accuracy?: number;
  latency_ms?: number;
  cost_per_request?: number;
  quality_score?: number;
  cost_efficiency?: number;
  capabilities?: string[];
  last_evaluated?: string;
}

export interface ModelInfo {
  model_id: string;
  model_name: string;
  provider: string;
  context_window?: number;
  max_output_tokens?: number;
  capabilities?: string[];
  input_price_per_1k?: number;
  output_price_per_1k?: number;
  latest_accuracy?: number;
  latest_latency_ms?: number;
  latest_quality_score?: number;
}

export interface OverviewStats {
  total_models: number;
  total_evaluations: number;
  num_providers: number;
  providers: string[];
}

export const apiService = {
  // Leaderboard
  getLeaderboard: async (
    sortBy: string = 'accuracy',
    order: string = 'desc',
    provider?: string,
    limit: number = 50
  ): Promise<LeaderboardEntry[]> => {
    const params: any = { sort_by: sortBy, order, limit };
    if (provider) params.provider = provider;

    const response = await api.get('/leaderboard', { params });
    return response.data;
  },

  // Models
  getModels: async (provider?: string): Promise<ModelInfo[]> => {
    const params = provider ? { provider } : {};
    const response = await api.get('/models', { params });
    return response.data;
  },

  getModel: async (modelId: string): Promise<ModelInfo> => {
    const response = await api.get(`/models/${modelId}`);
    return response.data;
  },

  compareModels: async (modelIds: string[], metrics: string[]): Promise<any> => {
    const response = await api.post('/models/compare', { model_ids: modelIds, metrics });
    return response.data;
  },

  // Statistics
  getOverviewStats: async (): Promise<OverviewStats> => {
    const response = await api.get('/stats/overview');
    return response.data;
  },

  // Health check
  healthCheck: async (): Promise<any> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
