import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { opportunities } from '../api';
import { Flame, Droplet, WindIcon, Thermometer } from 'lucide-react';

const STATUS_COLUMNS = ['Qualificação', 'Prospecção', 'Proposta', 'Negociação'];

const temperatureColors = {
  'Frio': 'bg-blue-100 text-blue-800 border-blue-300',
  'Morno': 'bg-yellow-100 text-yellow-800 border-yellow-300',
  'Quente': 'bg-orange-100 text-orange-800 border-orange-300',
  'Fervendo': 'bg-red-100 text-red-800 border-red-300'
};

const temperatureIcons = {
  'Frio': <Droplet size={16} />,
  'Morno': <WindIcon size={16} />,
  'Quente': <Thermometer size={16} />,
  'Fervendo': <Flame size={16} />
};

export default function Kanban() {
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

  const getOpportunitiesByStatus = (status) => {
    return opps.filter(opp => opp.status === status);
  };

  const getDaysSinceInteraction = (date) => {
    const lastInteraction = new Date(date);
    return Math.floor((new Date() - lastInteraction) / (1000 * 60 * 60 * 24));
  };

  if (loading) return <div className="flex items-center justify-center h-screen">Carregando...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">Cooper CRM Lite - Kanban</h1>
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
            >
              Dashboard
            </button>
            <button
              onClick={() => navigate('/kanban')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg"
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

      {/* Kanban Board */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {STATUS_COLUMNS.map(status => (
            <div key={status} className="bg-gray-100 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center justify-between">
                {status}
                <span className="bg-blue-600 text-white text-xs rounded-full px-2 py-1">
                  {getOpportunitiesByStatus(status).length}
                </span>
              </h3>

              <div className="space-y-3">
                {getOpportunitiesByStatus(status).map(opp => {
                  const daysSince = getDaysSinceInteraction(opp.last_interaction_date);
                  const isFree = daysSince > 90;

                  return (
                    <div
                      key={opp.id}
                      className={`bg-white rounded-lg p-4 shadow-sm border-2 ${
                        isFree ? 'border-red-500 animate-pulse' : 'border-transparent'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900 text-sm line-clamp-2">
                          {opp.razao_social}
                        </h4>
                        {isFree && (
                          <span className="text-red-600 text-xs bg-red-50 px-2 py-1 rounded">
                            LIVRE
                          </span>
                        )}
                      </div>

                      <p className="text-xs text-gray-600 mb-2">
                        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(opp.valor_estimado)}
                      </p>

                      {opp.temperatura && (
                        <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs border ${temperatureColors[opp.temperatura]}`}>
                          {temperatureIcons[opp.temperatura]}
                          {opp.temperatura}
                        </div>
                      )}

                      <div className="mt-2 text-xs text-gray-500">
                        {daysSince === 0 ? 'Hoje' : `${daysSince} dias sem contato`}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
