import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Paper,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  ResponsiveContainer
} from 'recharts';

import { useApi } from '../hooks/useApi';
import LiveTripsMap from '../components/maps/LiveTripsMap';
import { formatNumber, formatCurrency } from '../utils/formatters';

interface DashboardOverview {
  total_users: number;
  active_users: number;
  total_trips: number;
  total_food_entries: number;
  data_quality: {
    avg_quality_score: number;
    high_quality_percentage: number;
  };
  user_engagement: {
    active_user_percentage: number;
  };
}

interface ModeSplit {
  mode: string;
  count: number;
  percentage: number;
  avg_distance_km: number;
  avg_cost: number;
}

interface TemporalPattern {
  time_period: any;
  trip_count: number;
  unique_users: number;
  most_common_mode: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82ca9d'];

export default function Dashboard() {
  const [tabValue, setTabValue] = useState(0);
  const [timeFilter, setTimeFilter] = useState(30);
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [modeSplit, setModeSplit] = useState<ModeSplit[]>([]);
  const [temporalPatterns, setTemporalPatterns] = useState<TemporalPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { get } = useApi();

  useEffect(() => {
    loadDashboardData();
  }, [timeFilter]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load all dashboard data
      const [overviewRes, modeSplitRes, temporalRes] = await Promise.all([
        get(`/analytics/dashboard/overview?days=${timeFilter}`),
        get(`/analytics/trips/mode-split?days=${timeFilter}`),
        get(`/analytics/trips/temporal-patterns?days=${timeFilter}&granularity=hour`)
      ]);

      setOverview(overviewRes.data);
      setModeSplit(modeSplitRes.data.mode_split || []);
      setTemporalPatterns(temporalRes.data.temporal_patterns || []);

    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleTimeFilterChange = (event: SelectChangeEvent<number>) => {
    setTimeFilter(event.target.value as number);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ margin: 2 }}>
        {error}
        <Button onClick={loadDashboardData} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          NATPAC Research Dashboard
        </Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Period</InputLabel>
          <Select
            value={timeFilter}
            label="Time Period"
            onChange={handleTimeFilterChange}
          >
            <MenuItem value={7}>Last 7 days</MenuItem>
            <MenuItem value={30}>Last 30 days</MenuItem>
            <MenuItem value={90}>Last 90 days</MenuItem>
            <MenuItem value={365}>Last year</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Overview Cards */}
      {overview && (
        <Grid container spacing={3} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Users
                </Typography>
                <Typography variant="h4" component="div">
                  {formatNumber(overview.total_users)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {overview.user_engagement.active_user_percentage}% active
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Trips
                </Typography>
                <Typography variant="h4" component="div">
                  {formatNumber(overview.total_trips)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Last {timeFilter} days
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Food Entries
                </Typography>
                <Typography variant="h4" component="div">
                  {formatNumber(overview.total_food_entries)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cultural data points
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Data Quality
                </Typography>
                <Typography variant="h4" component="div">
                  {(overview.data_quality.avg_quality_score * 100).toFixed(0)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {overview.data_quality.high_quality_percentage}% high quality
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs for different views */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} variant="fullWidth">
          <Tab label="Transport Analysis" />
          <Tab label="Live Tracking" />
          <Tab label="Food Analytics" />
          <Tab label="User Engagement" />
        </Tabs>
      </Paper>

      {/* Tab Content */}
      {tabValue === 0 && (
        <Grid container spacing={3}>
          {/* Mode Split Chart */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Transport Mode Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={modeSplit}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ mode, percentage }) => `${mode} (${percentage}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {modeSplit.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Hourly Patterns */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Hourly Trip Patterns
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={temporalPatterns}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="time_period.hour" 
                      tickFormatter={(hour) => `${hour}:00`}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(hour) => `${hour}:00 - ${hour + 1}:00`}
                    />
                    <Bar dataKey="trip_count" fill="#2E7D32" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>

          {/* Mode Statistics Table */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Detailed Transport Mode Statistics
                </Typography>
                <Box sx={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f5f5f5' }}>
                        <th style={{ padding: '12px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>
                          Mode
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>
                          Trip Count
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>
                          Percentage
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>
                          Avg Distance (km)
                        </th>
                        <th style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>
                          Avg Cost (₹)
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {modeSplit.map((mode, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                          <td style={{ padding: '12px', textTransform: 'capitalize' }}>
                            {mode.mode.replace('_', ' ')}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right' }}>
                            {formatNumber(mode.count)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right' }}>
                            {mode.percentage}%
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right' }}>
                            {mode.avg_distance_km.toFixed(1)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right' }}>
                            {formatCurrency(mode.avg_cost)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Real-time Trip Tracking
                </Typography>
                <Box sx={{ height: 500 }}>
                  <LiveTripsMap />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Food Consumption Analytics
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  Food analytics dashboard coming soon...
                </Typography>
                {/* Food analytics components would go here */}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  User Engagement Metrics
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  User engagement analytics coming soon...
                </Typography>
                {/* User engagement components would go here */}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}