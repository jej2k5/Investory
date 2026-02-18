import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, Shield, Users, DollarSign, Search, BarChart3, Sparkles, ArrowRight, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from './contexts/AuthContext';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const StockApp = () => {
  const { token } = useAuth();
  const [symbol, setSymbol] = useState('');
  const [stockData, setStockData] = useState(null);
  const [valuation, setValuation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('search');
  const [stocksTableData, setStocksTableData] = useState([]);
  const [tableLoading, setTableLoading] = useState(false);
  const [tableError, setTableError] = useState(null);
  const [sortKey, setSortKey] = useState('updated_at');
  const [sortDirection, setSortDirection] = useState('desc');
  const [watchlistSaving, setWatchlistSaving] = useState(false);
  const [watchlistMessage, setWatchlistMessage] = useState(null);
  
  // User inputs for analysis
  const [meaningScore, setMeaningScore] = useState(0);
  const [moatScore, setMoatScore] = useState(0);
  const [managementScore, setManagementScore] = useState(0);
  const [marginScore, setMarginScore] = useState(0);

  const fetchStockData = async (stockSymbol) => {
    setLoading(true);
    setError(null);
    setWatchlistMessage(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/stocks/${stockSymbol}`);
      if (!response.ok) throw new Error('Stock not found');
      
      const data = await response.json();
      setStockData(data);
      
      // Calculate valuation
      const avgGrowth = (
        data.growth_rates.book_value +
        data.growth_rates.eps +
        data.growth_rates.cash_flow +
        data.growth_rates.sales +
        data.growth_rates.roic
      ) / 5;
      
      const valuationResponse = await fetch(
        `${API_BASE_URL}/valuation?current_price=${data.current_metrics.price}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            current_eps: data.current_metrics.eps,
            growth_rate: avgGrowth,
            pe_ratio: data.current_metrics.pe_ratio || avgGrowth * 2
          })
        }
      );
      
      const valuationData = await valuationResponse.json();
      setValuation(valuationData);
      setActiveView('analysis');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (symbol.trim()) {
      fetchStockData(symbol.toUpperCase());
    }
  };

  const evaluateMoat = () => {
    if (!stockData) return null;
    const rates = Object.values(stockData.growth_rates);
    const allAbove10 = rates.every(r => r >= 10);
    return {
      pass: allAbove10,
      avg: rates.reduce((a, b) => a + b, 0) / rates.length
    };
  };

  const getOverallScore = () => {
    const scores = [meaningScore, moatScore, managementScore, marginScore].filter(s => s > 0);
    if (scores.length === 0) return 0;
    return scores.reduce((a, b) => a + b, 0) / scores.length;
  };

  const fetchStocksTableData = async () => {
    setTableLoading(true);
    setTableError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/watchlist`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        throw new Error(errorPayload?.detail || 'Unable to load watchlist');
      }

      const data = await response.json();
      const items = Array.isArray(data) ? data : data.items || data.results || [];

      const normalizedRows = items.map((item) => ({
        symbol: item.symbol || item.stock_symbol || '--',
        company_name: item.company_name || item.company || '--',
        target_buy_price: item.target_buy_price ?? item.mos_price ?? null,
        target_sell_price: item.target_sell_price ?? item.sticker_price ?? null,
        alert_enabled: item.alert_enabled ?? item.alert ?? false,
        moat_score: item.moat_score ?? null,
        moat_assessment: item.moat_assessment ?? null,
        has_wide_moat: item.has_wide_moat ?? null,
        updated_at: item.updated_at || item.created_at || null,
      }));

      setStocksTableData(normalizedRows);
    } catch (err) {
      setTableError(err.message);
    } finally {
      setTableLoading(false);
    }
  };


  const addStockToWatchlist = async () => {
    if (!stockData) return;

    setWatchlistSaving(true);
    setWatchlistMessage(null);

    const moatEvaluation = evaluateMoat();
    const payload = {
      symbol: stockData.symbol,
      company_name: stockData.company_name,
      target_buy_price: valuation?.mos_price ?? null,
      target_sell_price: valuation?.sticker_price ?? null,
      alert_enabled: true,
      moat_score: moatScore > 0 ? moatScore : null,
      moat_assessment: moatEvaluation
        ? (moatEvaluation.pass ? 'WIDE MOAT' : 'WEAK MOAT')
        : null,
      has_wide_moat: moatEvaluation?.pass ?? null,
      book_value_growth: stockData.growth_rates?.book_value ?? null,
      eps_growth: stockData.growth_rates?.eps ?? null,
      cash_flow_growth: stockData.growth_rates?.cash_flow ?? null,
      sales_growth: stockData.growth_rates?.sales ?? null,
      roic: stockData.growth_rates?.roic ?? null,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/watchlist`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-Auth-Token': token,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        const detail = errorPayload?.detail || 'Unable to add stock to watchlist';
        throw new Error(detail);
      }

      const savedItem = await response.json();
      const normalizedRow = {
        symbol: savedItem.symbol || savedItem.stock_symbol || payload.symbol,
        company_name: savedItem.company_name || savedItem.company || payload.company_name,
        target_buy_price: savedItem.target_buy_price ?? savedItem.mos_price ?? payload.target_buy_price,
        target_sell_price: savedItem.target_sell_price ?? savedItem.sticker_price ?? payload.target_sell_price,
        alert_enabled: savedItem.alert_enabled ?? savedItem.alert ?? payload.alert_enabled,
        moat_score: savedItem.moat_score ?? payload.moat_score,
        moat_assessment: savedItem.moat_assessment ?? payload.moat_assessment,
        has_wide_moat: savedItem.has_wide_moat ?? payload.has_wide_moat,
        updated_at: savedItem.updated_at || savedItem.created_at || new Date().toISOString(),
      };

      setStocksTableData((prev) => {
        const remaining = prev.filter((row) => row.symbol !== normalizedRow.symbol);
        return [normalizedRow, ...remaining];
      });
      setWatchlistMessage({ type: 'success', text: `${payload.symbol} added to watchlist` });
    } catch (err) {
      setWatchlistMessage({ type: 'error', text: err.message });
    } finally {
      setWatchlistSaving(false);
    }
  };

  useEffect(() => {
    if (activeView === 'table') {
      fetchStocksTableData();
    }
  }, [activeView]);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
      return;
    }

    setSortKey(key);
    setSortDirection(key === 'updated_at' ? 'desc' : 'asc');
  };

  const sortedStocksTableData = [...stocksTableData].sort((a, b) => {
    const direction = sortDirection === 'asc' ? 1 : -1;

    if (sortKey === 'updated_at') {
      const aTime = a.updated_at ? new Date(a.updated_at).getTime() : 0;
      const bTime = b.updated_at ? new Date(b.updated_at).getTime() : 0;
      return (aTime - bTime) * direction;
    }

    const aValue = (a[sortKey] || '').toString().toUpperCase();
    const bValue = (b[sortKey] || '').toString().toUpperCase();
    return aValue.localeCompare(bValue) * direction;
  });

  const formatCurrency = (value) => {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return '--';
    return `$${Number(value).toFixed(2)}`;
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* View Navigation */}
      <div className="mb-6 flex gap-2">
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveView('search')}
          className={`px-6 py-2.5 rounded-xl font-semibold transition-all ${
            activeView === 'search'
              ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/50'
              : 'bg-white/5 text-white/60 hover:bg-white/10'
          }`}
        >
          Search
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveView('analysis')}
          disabled={!stockData}
          className={`px-6 py-2.5 rounded-xl font-semibold transition-all ${
            activeView === 'analysis' && stockData
              ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/50'
              : 'bg-white/5 text-white/60 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed'
          }`}
        >
          Analysis
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setActiveView('table')}
          className={`px-6 py-2.5 rounded-xl font-semibold transition-all ${
            activeView === 'table'
              ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/50'
              : 'bg-white/5 text-white/60 hover:bg-white/10'
          }`}
        >
          Stocks
        </motion.button>
      </div>

      {/* Main Content */}
      <div>
          <AnimatePresence mode="wait">
            {activeView === 'search' && (
              <motion.div
                key="search"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="max-w-2xl mx-auto"
              >
                {/* Hero Section */}
                <div className="text-center mb-12">
                  <motion.h2 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-5xl font-bold text-white mb-4 tracking-tight"
                  >
                    Find Wonderful Companies
                    <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500">
                      At Attractive Prices
                    </span>
                  </motion.h2>
                  <motion.p 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="text-xl text-white/60 max-w-xl mx-auto"
                  >
                    Analyze stocks using Phil Town's proven Four Ms framework
                  </motion.p>
                </div>

                {/* Search Form */}
                <motion.form
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  onSubmit={handleSearch}
                  className="mb-8"
                >
                  <div className="relative">
                    <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-white/40" size={24} />
                    <input
                      type="text"
                      value={symbol}
                      onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                      placeholder="Enter stock symbol (e.g., AAPL)"
                      className="w-full pl-16 pr-6 py-6 bg-white/5 border border-white/10 rounded-2xl text-white text-xl placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent backdrop-blur-xl transition-all"
                    />
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      type="submit"
                      disabled={loading || !symbol.trim()}
                      className="absolute right-2 top-1/2 -translate-y-1/2 px-8 py-3 bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-bold rounded-xl hover:shadow-lg hover:shadow-emerald-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="animate-spin" size={20} />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          Analyze
                          <ArrowRight size={20} />
                        </>
                      )}
                    </motion.button>
                  </div>
                </motion.form>

                {error && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-red-500/10 border border-red-500/20 rounded-2xl backdrop-blur-xl"
                  >
                    <p className="text-red-400 text-center font-medium">{error}</p>
                  </motion.div>
                )}

                {/* Features */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="grid grid-cols-2 gap-4 mt-12"
                >
                  {[
                    { icon: TrendingUp, title: 'Meaning', desc: 'Circle of competence' },
                    { icon: Shield, title: 'Moat', desc: 'Competitive advantage' },
                    { icon: Users, title: 'Management', desc: 'Owner-oriented' },
                    { icon: DollarSign, title: 'Margin', desc: '50% safety buffer' },
                  ].map((feature, idx) => (
                    <motion.div
                      key={feature.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.5 + idx * 0.1 }}
                      className="p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-xl hover:bg-white/10 transition-all group"
                    >
                      <feature.icon className="text-emerald-400 mb-3 group-hover:scale-110 transition-transform" size={32} />
                      <h3 className="text-white font-bold text-lg mb-1">{feature.title}</h3>
                      <p className="text-white/50 text-sm">{feature.desc}</p>
                    </motion.div>
                  ))}
                </motion.div>
              </motion.div>
            )}

            {activeView === 'table' && (
              <motion.div
                key="table"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="max-w-6xl mx-auto"
              >
                <div className="p-6 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
                  <div className="flex items-center justify-between mb-6">
                    <div>
                      <h2 className="text-3xl font-bold text-white">Stock Watchlist</h2>
                      <p className="text-white/60">Track your target buy/sell levels at a glance.</p>
                    </div>
                    <button
                      onClick={fetchStocksTableData}
                      className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white/80 hover:bg-white/10 transition-all"
                    >
                      Refresh
                    </button>
                  </div>

                  {tableError && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl backdrop-blur-xl"
                    >
                      <p className="text-red-400 text-center font-medium">{tableError}</p>
                    </motion.div>
                  )}

                  <div className="overflow-x-auto rounded-2xl border border-white/10">
                    <table className="min-w-full divide-y divide-white/10">
                      <thead className="bg-white/5">
                        <tr>
                          {[
                            { label: 'Symbol', key: 'symbol' },
                            { label: 'Company', key: 'company_name' },
                            { label: 'Target Buy', key: null },
                            { label: 'Target Sell', key: null },
                            { label: 'Alert', key: null },
                            { label: 'Moat', key: null },
                            { label: 'Last Updated', key: 'updated_at' },
                          ].map((column) => (
                            <th
                              key={column.label}
                              onClick={() => column.key && handleSort(column.key)}
                              className={`px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-white/60 ${column.key ? 'cursor-pointer hover:text-white' : ''}`}
                            >
                              <span className="inline-flex items-center gap-2">
                                {column.label}
                                {column.key === sortKey && (
                                  <span className="text-emerald-400">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                                )}
                              </span>
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/10 bg-white/5">
                        {tableLoading ? (
                          <tr>
                            <td colSpan={7} className="px-4 py-12 text-center text-white/70">
                              <span className="inline-flex items-center gap-2">
                                <Loader2 className="animate-spin" size={18} />
                                Loading stocks...
                              </span>
                            </td>
                          </tr>
                        ) : sortedStocksTableData.length === 0 ? (
                          <tr>
                            <td colSpan={7} className="px-4 py-12 text-center text-white/50">No stocks yet.</td>
                          </tr>
                        ) : (
                          sortedStocksTableData.map((row) => (
                            <tr key={`${row.symbol}-${row.updated_at || 'na'}`} className="hover:bg-white/10 transition-colors">
                              <td className="px-4 py-3 text-white font-semibold">{row.symbol}</td>
                              <td className="px-4 py-3 text-white/80">{row.company_name}</td>
                              <td className="px-4 py-3 text-emerald-400">{formatCurrency(row.target_buy_price)}</td>
                              <td className="px-4 py-3 text-blue-300">{formatCurrency(row.target_sell_price)}</td>
                              <td className="px-4 py-3 text-white/70">
                                {row.alert_enabled ? (
                                  <span className="inline-flex items-center gap-1 text-emerald-400"><CheckCircle size={14} />On</span>
                                ) : (
                                  <span className="inline-flex items-center gap-1 text-white/50"><XCircle size={14} />Off</span>
                                )}
                              </td>
                              <td className="px-4 py-3 text-white/70">
                                <div className="flex flex-col gap-1">
                                  <span className="text-emerald-300 font-medium">{row.moat_score ? `${row.moat_score}/5` : '--'}</span>
                                  <span className={`${row.has_wide_moat ? 'text-emerald-400' : 'text-white/50'} text-xs`}>
                                    {row.moat_assessment || (row.has_wide_moat === null ? '--' : row.has_wide_moat ? 'WIDE MOAT' : 'WEAK MOAT')}
                                  </span>
                                </div>
                              </td>
                              <td className="px-4 py-3 text-white/60">
                                {row.updated_at ? new Date(row.updated_at).toLocaleDateString() : '--'}
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </motion.div>
            )}


            {activeView === 'analysis' && stockData && (
              <motion.div
                key="analysis"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                {/* Stock Header */}
                <div className="mb-8 p-8 bg-gradient-to-br from-white/10 to-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h2 className="text-4xl font-bold text-white mb-2">{stockData.symbol}</h2>
                      <p className="text-2xl text-white/70 mb-1">{stockData.company_name}</p>
                      <div className="flex gap-3">
                        <span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-lg text-sm font-medium">
                          {stockData.sector}
                        </span>
                        <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-sm font-medium">
                          {stockData.industry}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-white/50 mb-1">Current Price</div>
                      <div className="text-4xl font-bold text-white mb-4">
                        ${stockData.current_metrics.price.toFixed(2)}
                      </div>
                      <button
                        onClick={addStockToWatchlist}
                        disabled={watchlistSaving}
                        className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 rounded-xl text-emerald-300 font-semibold hover:bg-emerald-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
                      >
                        {watchlistSaving ? (
                          <>
                            <Loader2 className="animate-spin" size={16} />
                            Saving...
                          </>
                        ) : (
                          <>
                            <BarChart3 size={16} />
                            Add to Watchlist
                          </>
                        )}
                      </button>
                    </div>
                  </div>


                  {watchlistMessage && (
                    <div className={`mb-6 p-4 rounded-2xl border backdrop-blur-xl flex items-center gap-2 ${
                      watchlistMessage.type === 'success'
                        ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                        : 'bg-red-500/10 border-red-500/20 text-red-300'
                    }`}>
                      <AlertCircle size={18} />
                      <span className="font-medium">{watchlistMessage.text}</span>
                    </div>
                  )}

                  {/* Key Metrics Grid */}
                  <div className="grid grid-cols-4 gap-4">
                    {[
                      { label: 'EPS', value: `$${stockData.current_metrics.eps.toFixed(2)}` },
                      { label: 'P/E Ratio', value: stockData.current_metrics.pe_ratio.toFixed(1) },
                      { label: 'ROE', value: `${(stockData.current_metrics.roe * 100).toFixed(1)}%` },
                      { label: 'Profit Margin', value: `${(stockData.current_metrics.profit_margin * 100).toFixed(1)}%` },
                    ].map((metric) => (
                      <div key={metric.label} className="p-4 bg-white/5 rounded-xl">
                        <div className="text-white/50 text-sm mb-1">{metric.label}</div>
                        <div className="text-white font-bold text-xl">{metric.value}</div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* The Four Ms Analysis */}
                <div className="grid grid-cols-2 gap-6 mb-8">
                  {/* Moat Card */}
                  <div className="p-8 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
                    <div className="flex items-center gap-3 mb-6">
                      <Shield className="text-emerald-400" size={32} />
                      <div>
                        <h3 className="text-2xl font-bold text-white">Moat Analysis</h3>
                        <p className="text-white/50 text-sm">10-year growth rates</p>
                      </div>
                    </div>

                    <div className="space-y-4">
                      {[
                        { label: 'Book Value', value: stockData.growth_rates.book_value },
                        { label: 'EPS', value: stockData.growth_rates.eps },
                        { label: 'Cash Flow', value: stockData.growth_rates.cash_flow },
                        { label: 'Sales', value: stockData.growth_rates.sales },
                        { label: 'ROIC', value: stockData.growth_rates.roic },
                      ].map((rate) => (
                        <div key={rate.label} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                          <span className="text-white/70">{rate.label}</span>
                          <div className="flex items-center gap-2">
                            <span className={`font-bold text-lg ${rate.value >= 10 ? 'text-emerald-400' : 'text-red-400'}`}>
                              {rate.value.toFixed(1)}%
                            </span>
                            {rate.value >= 10 ? (
                              <CheckCircle className="text-emerald-400" size={20} />
                            ) : (
                              <XCircle className="text-red-400" size={20} />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>

                    {evaluateMoat() && (
                      <div className={`mt-6 p-4 rounded-xl ${evaluateMoat().pass ? 'bg-emerald-500/20 border border-emerald-500/30' : 'bg-red-500/20 border border-red-500/30'}`}>
                        <div className="flex items-center gap-2">
                          {evaluateMoat().pass ? (
                            <CheckCircle className="text-emerald-400" size={24} />
                          ) : (
                            <XCircle className="text-red-400" size={24} />
                          )}
                          <div>
                            <div className={`font-bold ${evaluateMoat().pass ? 'text-emerald-400' : 'text-red-400'}`}>
                              {evaluateMoat().pass ? 'WIDE MOAT ✓' : 'WEAK MOAT ✗'}
                            </div>
                            <div className="text-white/60 text-sm">
                              Average: {evaluateMoat().avg.toFixed(1)}%
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Margin of Safety Card */}
                  {valuation && (
                    <div className="p-8 bg-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
                      <div className="flex items-center gap-3 mb-6">
                        <DollarSign className="text-emerald-400" size={32} />
                        <div>
                          <h3 className="text-2xl font-bold text-white">Valuation</h3>
                          <p className="text-white/50 text-sm">Margin of Safety</p>
                        </div>
                      </div>

                      <div className="space-y-4">
                        <div className="p-4 bg-white/5 rounded-xl">
                          <div className="text-white/50 text-sm mb-1">Sticker Price</div>
                          <div className="text-3xl font-bold text-white">
                            ${valuation.sticker_price.toFixed(2)}
                          </div>
                        </div>

                        <div className="p-4 bg-emerald-500/20 rounded-xl">
                          <div className="text-emerald-400 text-sm mb-1 font-medium">MOS Buy Price (50% off)</div>
                          <div className="text-3xl font-bold text-emerald-400">
                            ${valuation.mos_price.toFixed(2)}
                          </div>
                        </div>

                        <div className="p-4 bg-white/5 rounded-xl">
                          <div className="text-white/50 text-sm mb-1">Current Price</div>
                          <div className="text-3xl font-bold text-white">
                            ${valuation.current_price.toFixed(2)}
                          </div>
                        </div>
                      </div>

                      <div className={`mt-6 p-6 rounded-xl ${
                        valuation.recommendation.includes('BUY') ? 'bg-emerald-500/20 border border-emerald-500/30' :
                        valuation.recommendation.includes('WAIT') ? 'bg-yellow-500/20 border border-yellow-500/30' :
                        'bg-red-500/20 border border-red-500/30'
                      }`}>
                        <div className="text-center">
                          <div className={`text-2xl font-bold mb-2 ${
                            valuation.recommendation.includes('BUY') ? 'text-emerald-400' :
                            valuation.recommendation.includes('WAIT') ? 'text-yellow-400' :
                            'text-red-400'
                          }`}>
                            {valuation.recommendation}
                          </div>
                          <div className="text-white/60 text-sm">
                            Trading at {valuation.discount_percentage.toFixed(0)}% of intrinsic value
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* User Scoring Section */}
                <div className="p-8 bg-gradient-to-br from-white/10 to-white/5 border border-white/10 rounded-3xl backdrop-blur-xl">
                  <h3 className="text-2xl font-bold text-white mb-6">Your Four Ms Assessment</h3>
                  
                  <div className="grid grid-cols-4 gap-6 mb-6">
                    {[
                      { label: 'Meaning', icon: TrendingUp, score: meaningScore, setScore: setMeaningScore },
                      { label: 'Moat', icon: Shield, score: moatScore, setScore: setMoatScore },
                      { label: 'Management', icon: Users, score: managementScore, setScore: setManagementScore },
                      { label: 'Margin', icon: DollarSign, score: marginScore, setScore: setMarginScore },
                    ].map((item) => (
                      <div key={item.label} className="p-6 bg-white/5 rounded-2xl">
                        <div className="flex items-center gap-2 mb-4">
                          <item.icon className="text-emerald-400" size={20} />
                          <span className="text-white font-semibold">{item.label}</span>
                        </div>
                        <div className="flex gap-2">
                          {[1, 2, 3, 4, 5].map((value) => (
                            <button
                              key={value}
                              onClick={() => item.setScore(value)}
                              className={`w-full h-12 rounded-lg font-bold transition-all ${
                                item.score >= value
                                  ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/50'
                                  : 'bg-white/5 text-white/30 hover:bg-white/10'
                              }`}
                            >
                              {value}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {getOverallScore() > 0 && (
                    <div className="p-6 bg-white/10 rounded-2xl text-center">
                      <div className="text-white/60 text-sm mb-2">Overall Score</div>
                      <div className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-blue-500 mb-2">
                        {getOverallScore().toFixed(1)} / 5.0
                      </div>
                      <div className={`text-lg font-semibold ${
                        getOverallScore() >= 4 ? 'text-emerald-400' :
                        getOverallScore() >= 3 ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {getOverallScore() >= 4 ? 'STRONG BUY' :
                         getOverallScore() >= 3 ? 'HOLD' :
                         'PASS'}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
      </div>
    </div>
  );
};

export default StockApp;
