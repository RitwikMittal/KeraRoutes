import React, { useState, useEffect } from 'react';
import './App.css';

// Simple Chart Components
const StatCard: React.FC<{ title: string; value: string | number; icon: string }> = ({ title, value, icon }) => {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <h3>{value}</h3>
        <p>{title}</p>
      </div>
    </div>
  );
};

const BarChart: React.FC<{ data: Record<string, number>; title: string }> = ({ data, title }) => {
  const entries = Object.entries(data || {});
  const maxValue = Math.max(...entries.map(([_, value]) => value));
  
  return (
    <div className="bar-chart">
      <h4>{title}</h4>
      <div className="bars-container">
        {entries.map(([key, value]) => (
          <div key={key} className="bar-item">
            <div className="bar-label">{key.toUpperCase()}</div>
            <div className="bar-wrapper">
              <div 
                className="bar-fill" 
                style={{ width: `${(value / maxValue) * 100}%` }}
              ></div>
            </div>
            <div className="bar-value">{value}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [tripsData, setTripsData] = useState<any[]>([]);
  const [foodData, setFoodData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Load analytics summary
      const analyticsResponse = await fetch(`${API_BASE_URL}/api/v1/analytics/dashboard-summary`);
      const analyticsResult = await analyticsResponse.json();
      
      if (analyticsResult.success) {
        setAnalyticsData(analyticsResult.data);
      }

      // Load trips data
      const tripsResponse = await fetch(`${API_BASE_URL}/api/v1/trips`);
      const tripsResult = await tripsResponse.json();
      
      if (tripsResult.success) {
        setTripsData(tripsResult.data);
      }

      // Load food data
      const foodResponse = await fetch(`${API_BASE_URL}/api/v1/food`);
      const foodResult = await foodResponse.json();
      
      if (foodResult.success) {
        setFoodData(foodResult.data);
      }

    } catch (err) {
      setError(`Failed to load data: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <h2>🔬 Loading NATPAC Research Dashboard...</h2>
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>❌ Connection Error</h2>
          <p>{error}</p>
          <p>Make sure the FastAPI backend is running on http://localhost:8000</p>
          <button onClick={loadDashboardData} className="retry-btn">
            🔄 Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const overview = analyticsData?.overview || {};
  const transportAnalysis = analyticsData?.transport_analysis || {};
  const foodAnalysis = analyticsData?.food_analysis || {};

  return (
    <div className="app">
      {/* Header */}
      <header className="dashboard-header">
        <h1>🔬 NATPAC Smart Transportation Research Dashboard</h1>
        <p>Real-time Kerala Travel & Food Consumption Analytics</p>
        <button onClick={loadDashboardData} className="refresh-btn">
          🔄 Refresh Data
        </button>
      </header>

      {/* Key Metrics */}
      <section className="metrics-section">
        <h2>📊 Key Metrics Overview</h2>
        <div className="stats-grid">
          <StatCard 
            title="Total Trips Recorded" 
            value={overview.total_trips || 0} 
            icon="🚌" 
          />
          <StatCard 
            title="Food Entries Logged" 
            value={overview.total_food_entries || 0} 
            icon="🍽️" 
          />
          <StatCard 
            title="Transport Spending" 
            value={`₹${overview.total_transport_spending || 0}`} 
            icon="💸" 
          />
          <StatCard 
            title="Food Spending" 
            value={`₹${overview.total_food_spending || 0}`} 
            icon="🍛" 
          />
          <StatCard 
            title="Combined Spending" 
            value={`₹${overview.total_combined_spending || 0}`} 
            icon="💰" 
          />
          <StatCard 
            title="Avg Trip Cost" 
            value={`₹${transportAnalysis.avg_trip_cost || 0}`} 
            icon="🎯" 
          />
        </div>
      </section>

      {/* Transport Analysis */}
      <section className="analysis-section">
        <h2>🚌 Transportation Mode Analysis</h2>
        <div className="charts-grid">
          <BarChart 
            data={transportAnalysis.mode_distribution || {}} 
            title="Transport Mode Usage" 
          />
        </div>
      </section>

      {/* Recent Data Tables */}
      <section className="data-section">
        <div className="data-grid">
          {/* Recent Trips */}
          <div className="data-table">
            <h3>🗺️ Recent Trip Data ({tripsData.length} total)</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Mode</th>
                    <th>Route</th>
                    <th>Cost</th>
                    <th>People</th>
                    <th>Purpose</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {tripsData.slice(0, 5).map((trip, index) => (
                    <tr key={index}>
                      <td className="transport-mode">{trip.transport_mode?.toUpperCase()}</td>
                      <td>{trip.start_location?.city} → {trip.end_location?.city}</td>
                      <td>₹{trip.cost || 0}</td>
                      <td>{trip.number_of_people}</td>
                      <td>{trip.purpose}</td>
                      <td>{new Date(trip.created_at).toLocaleTimeString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recent Food Entries */}
          <div className="data-table">
            <h3>🍽️ Recent Food Data ({foodData.length} total)</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Restaurant</th>
                    <th>Cuisine</th>
                    <th>Meal</th>
                    <th>Cost</th>
                    <th>People</th>
                    <th>Time</th>
                  </tr>
                </thead>
                <tbody>
                  {foodData.slice(0, 5).map((food, index) => (
                    <tr key={index}>
                      <td className="restaurant-name">{food.restaurant_name}</td>
                      <td>{food.cuisine_type?.toUpperCase()}</td>
                      <td>{food.meal_type}</td>
                      <td>₹{food.total_cost || 0}</td>
                      <td>{food.number_of_people}</td>
                      <td>{new Date(food.created_at).toLocaleTimeString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* Research Insights */}
      <section className="insights-section">
        <h2>🧪 Research Insights for NATPAC Scientists</h2>
        <div className="insights-grid">
          <div className="insight-card">
            <h4>💡 Transportation Patterns</h4>
            <ul>
              <li>Most popular transport mode: {Object.entries(transportAnalysis.mode_distribution || {})
                .sort(([,a], [,b]) => (b as number) - (a as number))[0]?.[0] || 'N/A'}</li>
              <li>Average cost per trip: ₹{transportAnalysis.avg_trip_cost || 0}</li>
              <li>Total trips recorded: {overview.total_trips || 0}</li>
            </ul>
          </div>
          
          <div className="insight-card">
            <h4>🍛 Food Consumption Patterns</h4>
            <ul>
              <li>Average meal cost: ₹{foodAnalysis.avg_meal_cost || 0}</li>
              <li>Restaurants visited: {foodAnalysis.total_restaurants_visited || 0}</li>
              <li>Total food entries: {overview.total_food_entries || 0}</li>
            </ul>
          </div>
          
          <div className="insight-card">
            <h4>💰 Economic Impact</h4>
            <ul>
              <li>Total tourism spending: ₹{overview.total_combined_spending || 0}</li>
              <li>Transport share: {overview.total_transport_spending && overview.total_combined_spending ? 
                ((overview.total_transport_spending / overview.total_combined_spending) * 100).toFixed(1) : 0}%</li>
              <li>Food share: {overview.total_food_spending && overview.total_combined_spending ? 
                ((overview.total_food_spending / overview.total_combined_spending) * 100).toFixed(1) : 0}%</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>🌴 Kerala Smart Transportation Research Dashboard | Real-time data collection for tourism and mobility analysis</p>
        <p>Last updated: {new Date().toLocaleString()}</p>
      </footer>
    </div>
  );
};

export default App;
