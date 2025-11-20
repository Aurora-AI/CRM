import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { opportunities } from '../api';
import { TrendingUp, AlertCircle, DollarSign, Menu } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [opps, setOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadOpportunities();
  }, []);

  const loadOpportunities = async () => {
    try {
      const data = await opportunities.getAll();
      setOpps(data);
    } catch (error) {
      console.error(error);
      if (error.response?.status === 401) {
        navigate('/');
      }
    } finally {
      setLoading(false);
    }
  };

  const totalOpps = opps.length;
  const totalValue = opps.reduce((sum, opp) => sum + (opp.valor_estimado || 0), 0);
  
  // Calculate days since last interaction
  const oppsAtRisk = opps.filter(opp => {
    const lastInteraction = new Date(opp.last_interaction_date);
    const daysSince = Math.floor((new Date() - lastInteraction) / (1000 * 60 * 60 * 24));
    return daysSince > 85;
  }).length;

  // Chart data
  const statusCounts = {};
  opps.forEach(opp => {
    statusCounts[opp.status] = (statusCounts[opp.status] || 0) + 1;
  });
  const chartData = Object.entries(statusCounts).map(([name, value]) => ({
    name,
    value
  }));

  if (loading) return <div className="flex items-center justify-center h-screen">Carregando...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Cooper CRM Lite</h1>
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate('/kanban')}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
            >
              Kanban
            </button>
            <button
              onClick={() => {
                localStorage.removeItem('token');
                navigate('/');
              }}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Sair
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPIs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total de Oportunidades</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{totalOpps}</p>
              </div>
              <TrendingUp className="text-blue-600" size={40} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Valor em Pipeline</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(totalValue)}
                </p>
              </div>
              <DollarSign className="text-green-600" size={40} />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Oportunidades em Risco (&gt;85 dias)</p>
                <p className="text-3xl font-bold text-red-600 mt-2">{oppsAtRisk}</p>
              </div>
              <AlertCircle className="text-red-600" size={40} />
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Oportunidades por Status</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
