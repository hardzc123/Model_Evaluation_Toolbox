import React, { useEffect, useState } from 'react';
import { apiService, LeaderboardEntry } from '../services/api';

const Leaderboard: React.FC = () => {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('accuracy');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [providerFilter, setProviderFilter] = useState<string>('');
  const [providers, setProviders] = useState<string[]>([]);

  useEffect(() => {
    // Extract unique providers from entries
    const uniqueProviders = Array.from(new Set(entries.map(e => e.provider)));
    setProviders(uniqueProviders);
  }, [entries]);

  useEffect(() => {
    fetchLeaderboard();
  }, [sortBy, order, providerFilter]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await apiService.getLeaderboard(
        sortBy,
        order,
        providerFilter || undefined
      );
      setEntries(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load leaderboard:', err);
      setLoading(false);
    }
  };

  const handleSort = (metric: string) => {
    if (sortBy === metric) {
      setOrder(order === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(metric);
      setOrder('desc');
    }
  };

  const formatValue = (value: number | undefined, type: string) => {
    if (value === undefined || value === null) return 'N/A';

    switch (type) {
      case 'percentage':
        return `${(value * 100).toFixed(2)}%`;
      case 'ms':
        return `${value.toFixed(2)} ms`;
      case 'cost':
        return `$${value.toFixed(6)}`;
      case 'efficiency':
        return value.toFixed(2);
      default:
        return value.toFixed(4);
    }
  };

  const SortIcon = ({ metric }: { metric: string }) => {
    if (sortBy !== metric) return <span className="text-gray-400">⇅</span>;
    return order === 'desc' ? <span>↓</span> : <span>↑</span>;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-600">Loading leaderboard...</div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Model Leaderboard</h1>
        <button
          onClick={fetchLeaderboard}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Provider
            </label>
            <select
              value={providerFilter}
              onChange={(e) => setProviderFilter(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">All Providers</option>
              {providers.map((provider) => (
                <option key={provider} value={provider}>
                  {provider}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rank
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Model
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Provider
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('accuracy')}
                >
                  <div className="flex items-center gap-1">
                    Accuracy <SortIcon metric="accuracy" />
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('latency_ms')}
                >
                  <div className="flex items-center gap-1">
                    Latency <SortIcon metric="latency_ms" />
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('cost_per_request')}
                >
                  <div className="flex items-center gap-1">
                    Cost/Request <SortIcon metric="cost_per_request" />
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('quality_score')}
                >
                  <div className="flex items-center gap-1">
                    Quality <SortIcon metric="quality_score" />
                  </div>
                </th>
                <th
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('cost_efficiency')}
                >
                  <div className="flex items-center gap-1">
                    Efficiency <SortIcon metric="cost_efficiency" />
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {entries.map((entry, index) => (
                <tr key={entry.model_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {index + 1}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {entry.model_name}
                    </div>
                    <div className="text-sm text-gray-500">{entry.model_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {entry.provider}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatValue(entry.accuracy, 'percentage')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatValue(entry.latency_ms, 'ms')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatValue(entry.cost_per_request, 'cost')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatValue(entry.quality_score, 'percentage')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatValue(entry.cost_efficiency, 'efficiency')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {entries.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No models found. Run some evaluations to populate the leaderboard.
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">Metrics Explanation</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li><strong>Accuracy:</strong> Percentage of correct predictions on evaluation dataset</li>
          <li><strong>Latency:</strong> Average response time in milliseconds</li>
          <li><strong>Cost/Request:</strong> Average cost per API request in USD</li>
          <li><strong>Quality:</strong> Text generation quality score (BLEU/ROUGE/BERTScore)</li>
          <li><strong>Efficiency:</strong> Quality per dollar ratio (higher is better)</li>
        </ul>
      </div>
    </div>
  );
};

export default Leaderboard;
