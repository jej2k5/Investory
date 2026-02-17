import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, UserPlus, Loader2, AlertCircle, CheckCircle, Trash2, Shield, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const UserManagement = () => {
  const { token, user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Create user form state
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'user',
  });
  const [createLoading, setCreateLoading] = useState(false);
  const [createError, setCreateError] = useState('');
  const [createSuccess, setCreateSuccess] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/users`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setCreateError('');
    setCreateSuccess('');
    setCreateLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(newUser),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create user');
      }

      const createdUser = await response.json();
      setUsers([...users, createdUser]);
      setCreateSuccess(`User "${newUser.username}" created successfully!`);

      // Reset form
      setNewUser({
        username: '',
        email: '',
        password: '',
        full_name: '',
        role: 'user',
      });

      setTimeout(() => {
        setShowCreateForm(false);
        setCreateSuccess('');
      }, 2000);
    } catch (err) {
      setCreateError(err.message);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete user');
      }

      setUsers(users.filter((u) => u.id !== userId));
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="p-8 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold text-white flex items-center gap-3">
              <Users size={32} />
              User Management
            </h2>
            <p className="text-white/60 mt-2">Manage user accounts and permissions</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="px-6 py-3 bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-emerald-500/50 transition-all flex items-center gap-2"
          >
            <UserPlus size={20} />
            {showCreateForm ? 'Cancel' : 'Create User'}
          </motion.button>
        </div>

        {/* Create User Form */}
        <AnimatePresence>
          {showCreateForm && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8 overflow-hidden"
            >
              <div className="p-6 bg-white/10 border border-white/10 rounded-2xl">
                <h3 className="text-xl font-bold text-white mb-4">Create New User</h3>
                <form onSubmit={handleCreateUser} className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-white/70 text-sm font-medium mb-2">
                        Username *
                      </label>
                      <input
                        type="text"
                        value={newUser.username}
                        onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                        required
                        minLength={3}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        placeholder="johndoe"
                      />
                    </div>

                    <div>
                      <label className="block text-white/70 text-sm font-medium mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        value={newUser.email}
                        onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        placeholder="john@example.com"
                      />
                    </div>

                    <div>
                      <label className="block text-white/70 text-sm font-medium mb-2">
                        Password *
                      </label>
                      <input
                        type="password"
                        value={newUser.password}
                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                        required
                        minLength={8}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        placeholder="Min 8 characters"
                      />
                    </div>

                    <div>
                      <label className="block text-white/70 text-sm font-medium mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={newUser.full_name}
                        onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        placeholder="John Doe"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-white/70 text-sm font-medium mb-2">
                      Role *
                    </label>
                    <select
                      value={newUser.role}
                      onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                      className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>

                  {createError && (
                    <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-2 text-red-400">
                      <AlertCircle size={18} />
                      <span className="text-sm">{createError}</span>
                    </div>
                  )}

                  {createSuccess && (
                    <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-2 text-emerald-400">
                      <CheckCircle size={18} />
                      <span className="text-sm">{createSuccess}</span>
                    </div>
                  )}

                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    type="submit"
                    disabled={createLoading}
                    className="w-full px-6 py-3 bg-emerald-500 text-white font-bold rounded-xl hover:bg-emerald-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {createLoading ? (
                      <>
                        <Loader2 className="animate-spin" size={20} />
                        Creating...
                      </>
                    ) : (
                      <>
                        <UserPlus size={20} />
                        Create User
                      </>
                    )}
                  </motion.button>
                </form>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-2 text-red-400">
            <AlertCircle size={18} />
            <span className="text-sm">{error}</span>
          </div>
        )}

        {/* Users Table */}
        <div className="overflow-x-auto rounded-2xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-white/60">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-white/60">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-white/60">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-white/60">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-white/60">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-white/60">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10 bg-white/5">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-white/70">
                    <span className="inline-flex items-center gap-2">
                      <Loader2 className="animate-spin" size={18} />
                      Loading users...
                    </span>
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-white/50">
                    No users found
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="hover:bg-white/10 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-white font-semibold">{user.username}</div>
                        {user.full_name && (
                          <div className="text-white/50 text-sm">{user.full_name}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-white/80">
                      {user.email || <span className="text-white/30">—</span>}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1 px-3 py-1 rounded-lg text-sm font-medium ${
                          user.role === 'admin'
                            ? 'bg-purple-500/20 text-purple-300'
                            : 'bg-blue-500/20 text-blue-300'
                        }`}
                      >
                        {user.role === 'admin' ? <Shield size={14} /> : <User size={14} />}
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1 px-3 py-1 rounded-lg text-sm font-medium ${
                          user.is_active
                            ? 'bg-emerald-500/20 text-emerald-300'
                            : 'bg-red-500/20 text-red-300'
                        }`}
                      >
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-white/60 text-sm">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {user.id !== currentUser?.id && (
                        <motion.button
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.9 }}
                          onClick={() => handleDeleteUser(user.id)}
                          className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-all"
                          title="Delete user"
                        >
                          <Trash2 size={18} />
                        </motion.button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
