import React, { useEffect, useState } from 'react';
import { apiService, ModelInfo } from '../services/api';

const ModelComparison: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const data = await apiService.getModels();
      setModels(data);
    } catch (err) {
      console.error('Failed to load models:', err);
    }
  };

  const toggleModel = (modelId: string) => {
    if (selectedModels.includes(modelId)) {
      setSelectedModels(selectedModels.filter(id => id !== modelId));
    } else {
      if (selectedModels.length < 5) {
        setSelectedModels([...selectedModels, modelId]);
      }
    }
  };

  const compareModels = async () => {
    if (selectedModels.length < 2) {
      alert('Please select at least 2 models to compare');
      return;
    }

    try {
      setLoading(true);
      const data = await apiService.compareModels(
        selectedModels,
        ['accuracy', 'latency_ms', 'cost_per_request', 'quality_score']
      );
      setComparisonData(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to compare models:', err);
      setLoading(false);
    }
  };

  const getModelName = (modelId: string) => {
    const model = models.find(m => m.model_id === modelId);
    return model?.model_name || modelId;
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Compare Models</h1>

      {/* Model Selection */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Select Models (up to 5)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {models.map((model) => (
            <label
              key={model.model_id}
              className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition ${
                selectedModels.includes(model.model_id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-300'
              }`}
            >
              <input
                type="checkbox"
                checked={selectedModels.includes(model.model_id)}
                onChange={() => toggleModel(model.model_id)}
                className="mr-3 h-5 w-5 text-blue-600"
                disabled={
                  !selectedModels.includes(model.model_id) &&
                  selectedModels.length >= 5
                }
              />
              <div className="flex-1">
                <div className="font-semibold">{model.model_name}</div>
                <div className="text-sm text-gray-500">{model.provider}</div>
              </div>
            </label>
          ))}
        </div>

        <div className="mt-4 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {selectedModels.length} model(s) selected
          </div>
          <button
            onClick={compareModels}
            disabled={selectedModels.length < 2 || loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? 'Comparing...' : 'Compare Models'}
          </button>
        </div>
      </div>

      {/* Comparison Results */}
      {comparisonData && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Comparison Results</h2>

          {/* Comparison Table */}
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Model
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Provider
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Accuracy
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Latency (ms)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cost/Request
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Quality Score
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {comparisonData.models.map((model: any) => (
                  <tr key={model.model_id}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium">
                      {model.model_name || getModelName(model.model_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {model.provider}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {model.accuracy !== null && model.accuracy !== undefined
                        ? `${(model.accuracy * 100).toFixed(2)}%`
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {model.latency_ms !== null && model.latency_ms !== undefined
                        ? `${model.latency_ms.toFixed(2)} ms`
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {model.cost_per_request !== null && model.cost_per_request !== undefined
                        ? `$${model.cost_per_request.toFixed(6)}`
                        : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {model.quality_score !== null && model.quality_score !== undefined
                        ? `${(model.quality_score * 100).toFixed(2)}%`
                        : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Best Model Recommendations */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {comparisonData.models.length > 0 && (
              <>
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-900 mb-2">Best Accuracy</h3>
                  <p className="text-sm text-green-800">
                    {(() => {
                      const best = comparisonData.models.reduce((prev: any, curr: any) =>
                        (curr.accuracy || 0) > (prev.accuracy || 0) ? curr : prev
                      );
                      return best.model_name || getModelName(best.model_id);
                    })()}
                  </p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h3 className="font-semibold text-yellow-900 mb-2">Fastest</h3>
                  <p className="text-sm text-yellow-800">
                    {(() => {
                      const best = comparisonData.models.reduce((prev: any, curr: any) =>
                        (curr.latency_ms || Infinity) < (prev.latency_ms || Infinity) ? curr : prev
                      );
                      return best.model_name || getModelName(best.model_id);
                    })()}
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Most Cost-Effective</h3>
                  <p className="text-sm text-blue-800">
                    {(() => {
                      const best = comparisonData.models.reduce((prev: any, curr: any) =>
                        (curr.cost_per_request || Infinity) < (prev.cost_per_request || Infinity) ? curr : prev
                      );
                      return best.model_name || getModelName(best.model_id);
                    })()}
                  </p>
                </div>

                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <h3 className="font-semibold text-purple-900 mb-2">Best Quality</h3>
                  <p className="text-sm text-purple-800">
                    {(() => {
                      const best = comparisonData.models.reduce((prev: any, curr: any) =>
                        (curr.quality_score || 0) > (prev.quality_score || 0) ? curr : prev
                      );
                      return best.model_name || getModelName(best.model_id);
                    })()}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {!comparisonData && !loading && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600">
            Select at least 2 models above and click "Compare Models" to see the comparison.
          </p>
        </div>
      )}
    </div>
  );
};

export default ModelComparison;
