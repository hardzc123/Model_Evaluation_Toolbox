import React, { useEffect, useState } from 'react';
import { apiService, OverviewStats } from '../services/api';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await apiService.getOverviewStats();
        setStats(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard statistics');
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-xl text-gray-600">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-1">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Models
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats?.total_models || 0}
                </dd>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-1">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Total Evaluations
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats?.total_evaluations || 0}
                </dd>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-1">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Providers
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {stats?.num_providers || 0}
                </dd>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-1">
                <dt className="text-sm font-medium text-gray-500 truncate">
                  Status
                </dt>
                <dd className="mt-1 text-3xl font-semibold text-green-600">
                  Healthy
                </dd>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Providers List */}
      {stats && stats.providers && stats.providers.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Supported Providers
          </h2>
          <div className="flex flex-wrap gap-2">
            {stats.providers.map((provider) => (
              <span
                key={provider}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
              >
                {provider}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Quick Links */}
      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Quick Links
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/leaderboard"
            className="block p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-lg mb-2">View Leaderboard</h3>
            <p className="text-gray-600 text-sm">
              See model rankings across different metrics
            </p>
          </a>
          <a
            href="/comparison"
            className="block p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
          >
            <h3 className="font-semibold text-lg mb-2">Compare Models</h3>
            <p className="text-gray-600 text-sm">
              Side-by-side comparison of multiple models
            </p>
          </a>
          <div className="block p-4 border border-gray-200 rounded-lg bg-gray-50">
            <h3 className="font-semibold text-lg mb-2">Documentation</h3>
            <p className="text-gray-600 text-sm">
              Learn how to use the evaluation toolbox
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
