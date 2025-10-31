import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Leaderboard from './pages/Leaderboard';
import ModelComparison from './pages/ModelComparison';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        {/* Navigation */}
        <nav className="bg-white shadow-lg">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex justify-between h-16">
              <div className="flex space-x-8">
                <Link
                  to="/"
                  className="flex items-center px-3 text-gray-700 hover:text-blue-600"
                >
                  <span className="font-bold text-xl">Model Evaluation Toolbox</span>
                </Link>
                <Link
                  to="/"
                  className="flex items-center px-3 text-gray-700 hover:text-blue-600"
                >
                  Dashboard
                </Link>
                <Link
                  to="/leaderboard"
                  className="flex items-center px-3 text-gray-700 hover:text-blue-600"
                >
                  Leaderboard
                </Link>
                <Link
                  to="/comparison"
                  className="flex items-center px-3 text-gray-700 hover:text-blue-600"
                >
                  Compare Models
                </Link>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leaderboard" element={<Leaderboard />} />
            <Route path="/comparison" element={<ModelComparison />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
