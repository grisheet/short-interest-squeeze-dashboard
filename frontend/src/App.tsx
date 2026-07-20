import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import TickerDetail from './components/TickerDetail';

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <Router basename={import.meta.env.BASE_URL}>
      <div className="flex h-screen bg-gray-950 text-gray-100 overflow-hidden">
        <Sidebar open={sidebarOpen} />
        <div className="flex flex-col flex-1 overflow-hidden">
          <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
          <main className="flex-1 overflow-auto p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/ticker/:symbol" element={<TickerDetail />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
