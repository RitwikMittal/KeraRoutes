import React, { useState, useEffect } from 'react';
import {
  Container,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Button,
  Stack
} from '@mui/material';
import {
  TrendingUp,
  DirectionsBus,
  Nature,
  People
} from '@mui/icons-material';

interface DashboardData {
  success: boolean;
  data: {
    overview: {
      total_trips: number;
      total_food_entries: number;
      total_transport_spending: number;
      total_food_spending: number;
      total_combined_spending: number;
    };
    transport_analysis: {
      mode_distribution: Record<string, number>;
      avg_trip_cost: number;
    };
    food_analysis: {
      avg_meal_cost: number;
      total_restaurants_visited: number;
    };
  };
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://192.168.29.117:8000/api/v1/analytics/dashboard-summary');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const result = await response.json();
      console.log('API Response:', result); // Debug log
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert 
          severity="error" 
          action={
            <Button color="inherit" size="small" onClick={fetchDashboardData}>
              Retry
            </Button>
          }
        >
          Error loading dashboard: {error}
        </Alert>
      </Container>
    );
  }

  if (!data || !data.success) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="info">No data available</Alert>
      </Container>
    );
  }

  const { overview, transport_analysis, food_analysis } = data.data;
  
  // Convert mode_distribution to array format for display
  const modeSplit = Object.entries(transport_analysis.mode_distribution).map(([mode, count]) => ({
    mode,
    count,
    percentage: Math.round((count / overview.total_trips) * 100)
  }));

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" mb={4}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold" color="primary">
            Kerala Transport Analytics
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Real-time insights into transportation and food patterns
          </Typography>
        </Box>
        <Button variant="contained" onClick={fetchDashboardData} startIcon={<TrendingUp />}>
          Refresh Data
        </Button>
      </Stack>

      {/* Stats Cards */}
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={3} mb={4}>
        <Card sx={{ flex: 1, borderRadius: 2 }} elevation={2}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="primary.main">
                  {overview.total_trips + overview.total_food_entries}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Entries
                </Typography>
              </Box>
              <People fontSize="large" color="primary" />
            </Stack>
          </CardContent>
        </Card>
        
        <Card sx={{ flex: 1, borderRadius: 2 }} elevation={2}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="success.main">
                  {overview.total_trips}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Trips
                </Typography>
              </Box>
              <DirectionsBus fontSize="large" color="success" />
            </Stack>
          </CardContent>
        </Card>
        
        <Card sx={{ flex: 1, borderRadius: 2 }} elevation={2}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="info.main">
                  ₹{overview.total_transport_spending}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Transport Spending
                </Typography>
              </Box>
              <TrendingUp fontSize="large" color="info" />
            </Stack>
          </CardContent>
        </Card>
        
        <Card sx={{ flex: 1, borderRadius: 2 }} elevation={2}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h4" fontWeight="bold" color="warning.main">
                  ₹{transport_analysis.avg_trip_cost.toFixed(0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Avg Trip Cost
                </Typography>
              </Box>
              <Nature fontSize="large" color="warning" />
            </Stack>
          </CardContent>
        </Card>
      </Stack>

      {/* Transport Modes */}
      <Card sx={{ borderRadius: 2, mb: 4 }} elevation={2}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Transport Mode Distribution
          </Typography>
          <Stack spacing={2}>
            {modeSplit.map((mode, index) => (
              <Box key={index}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>
                    {mode.mode}
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {mode.percentage}% ({mode.count} trips)
                  </Typography>
                </Stack>
                <Box sx={{ 
                  width: '100%', 
                  height: 8, 
                  bgcolor: 'grey.200', 
                  borderRadius: 1,
                  overflow: 'hidden'
                }}>
                  <Box sx={{ 
                    width: `${mode.percentage}%`, 
                    height: '100%', 
                    bgcolor: 'primary.main',
                    transition: 'width 0.3s ease'
                  }} />
                </Box>
              </Box>
            ))}
          </Stack>
        </CardContent>
      </Card>

      {/* Analysis Summary */}
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
        {/* Transport Analysis */}
        <Card sx={{ flex: 1, borderRadius: 2 }} elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              Transport Analysis
            </Typography>
            <Stack spacing={2}>
              <Box sx={{ p: 2, border: 1, borderColor: 'grey.200', borderRadius: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  Total Trips
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {overview.total_trips} trips recorded
                </Typography>
              </Box>
              <Box sx={{ p: 2, border: 1, borderColor: 'grey.200', borderRadius: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  Average Cost per Trip
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ₹{transport_analysis.avg_trip_cost.toFixed(2)}
                </Typography>
              </Box>
              <Box sx={{ p: 2, border: 1, borderColor: 'grey.200', borderRadius: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  Total Transport Spending
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ₹{overview.total_transport_spending}
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>

        {/* Food Analysis */}
        <Card sx={{ flex: 1, borderRadius: 2 }} elevation={2}>
          <CardContent>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              Food Analysis
            </Typography>
            <Stack spacing={2}>
              <Box sx={{ p: 2, border: 1, borderColor: 'grey.200', borderRadius: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  Food Entries
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {overview.total_food_entries} entries recorded
                </Typography>
              </Box>
              <Box sx={{ p: 2, border: 1, borderColor: 'grey.200', borderRadius: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  Restaurants Visited
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {food_analysis.total_restaurants_visited} restaurants
                </Typography>
              </Box>
              <Box sx={{ p: 2, border: 1, borderColor: 'grey.200', borderRadius: 1 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  Food Spending
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  ₹{overview.total_food_spending}
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </Container>
  );
};

export default Dashboard;
