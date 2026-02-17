import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import PasswordChange from './components/PasswordChange';
import UserManagement from './components/UserManagement';
import StockApp from './StockApp';
import { motion } from 'framer-motion';
import { LogOut, User, Users, Shield } from 'lucide-react';

const AppContent = () => {
  const { isAuthenticated, requiresPasswordChange, user, logout, loading, isAdmin } = useAuth();
  const [currentView, setCurrentView] = useState('stocks'); // 'stocks' or 'users'

  // Show loading screen while checking auth
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  // Show login if not authenticated
  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => {}} />;
  }

  // Show password change if required
  if (requiresPasswordChange) {
    return <PasswordChange isForced={true} onSuccess={() => window.location.reload()} />;
  }

  // Authenticated user interface with navigation
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Top Navigation Bar */}
      <div className="border-b border-white/10 backdrop-blur-xl bg-white/5">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-white/60">Welcome,</span>
              <div className="flex items-center gap-2 px-4 py-2 bg-white/10 rounded-xl">
                {user?.role === 'admin' ? (
                  <Shield className="text-purple-400" size={18} />
                ) : (
                  <User className="text-blue-400" size={18} />
                )}
                <span className="text-white font-semibold">{user?.username}</span>
                {user?.role === 'admin' && (
                  <span className="px-2 py-0.5 bg-purple-500/30 text-purple-300 text-xs rounded font-medium">
                    ADMIN
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Navigation Buttons */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setCurrentView('stocks')}
                className={`px-4 py-2 rounded-xl font-semibold transition-all ${
                  currentView === 'stocks'
                    ? 'bg-emerald-500 text-white'
                    : 'bg-white/5 text-white/60 hover:bg-white/10'
                }`}
              >
                Stock Analysis
              </motion.button>

              {isAdmin() && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setCurrentView('users')}
                  className={`px-4 py-2 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                    currentView === 'users'
                      ? 'bg-purple-500 text-white'
                      : 'bg-white/5 text-white/60 hover:bg-white/10'
                  }`}
                >
                  <Users size={18} />
                  User Management
                </motion.button>
              )}

              {/* Logout Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={logout}
                className="px-4 py-2 bg-red-500/20 text-red-400 rounded-xl font-semibold hover:bg-red-500/30 transition-all flex items-center gap-2"
              >
                <LogOut size={18} />
                Logout
              </motion.button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-6">
        {currentView === 'stocks' ? <StockApp /> : <UserManagement />}
      </main>
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;
