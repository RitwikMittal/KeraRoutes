import React, { useState, useEffect } from 'react';
import {
  Container,
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
  SelectChangeEvent,
  Grid,
  Chip,
  Avatar,
  IconButton,
  Divider,
  useTheme,
  alpha
} from '@mui/material';
import {
  TrendingUp,
  DirectionsBus,
  EcoFriendly,
  People,
  Timeline,
  Assessment,
  Map,
  Restaurant,
  Refresh,
  DirectionsCar,
  Train,
  DirectionsWalk,
  TwoWheeler
} from '@mui/icons-material';
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
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts';

import { useApi } from '../hooks/useApi';
import LiveTripsMap from '../components/maps/LiveTripsMap';
import { formatNumber, formatCurrency } from '../utils/formatters';

interface DashboardOverview {
  total_users: number;
  total_trips: number;
  total_distance_km: number;
  total_emissions_saved_kg: number;
  active_users_last_7_days: number;
  avg_trip_duration_minutes: number;
  popular_transport_mode: string;
  total_food_entries: number;
}

interface ModeSplit {
  mode: string;
  count: number;
  percentage: number;
}

interface TemporalPattern {
  hour: number;
  trips: number;
  avg_duration: number;
}

const CHART_COLORS = ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2', '#00796b'];

const getModeIcon = (mode: string) => {
  switch (mode.toLowerCase()) {
    case 'bus': return <DirectionsBus />;
    case 'car': return <DirectionsCar />;
    case 'train': return <Train />;
    case 'walk': return <DirectionsWalk />;
    case 'bike': return <TwoWheeler />;
    default: return <DirectionsBus />;
  }
};

const StatCard: React.FC<{
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
}> = ({ title, value, icon, color, subtitle }) => {
  const theme = useTheme();
  
  return (
    <Card 
      sx={{ 
        height: '100%',
        background: `linear-gradient(135deg, ${color} 0%, ${alpha(color, 0.8)} 100%)`,
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '100px',
          height: '100px',
          background: alpha('#fff', 0.1),
          borderRadius: '50%',
          transform: 'translate(30px, -30px)'
        }
      }}
    >
      <CardContent sx={{ position: 'relative', zIndex: 1 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Avatar sx={{ bgcolor: alpha('#fff', 0.2), color: 'white' }}>
            {icon}
          </Avatar>
          <Typography variant="h4" fontWeight="bold">
            {typeof value === 'number' ? formatNumber(value) : value}
          </Typography>
        </Box>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        {subtitle && (
          <Typography variant="body2" sx={{ opacity: 0.9 }}>
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [modeSplit, setModeSplit] = useState<ModeSplit[]>([]);
  const [temporalPatterns, setTemporalPatterns] = useState<TemporalPattern[]>([]);
  const [tabValue, setTabValue] = useState(0);
  const [timeFilter, setTimeFilter] = useState<number>(7);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const theme = useTheme();
  const { get } = useApi();

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      setError(null);

      const [overviewRes, modeSplitRes, temporalRes] = await Promise.all([
        get(`/analytics/dashboard/overview?days=${timeFilter}`),
        get(`/analytics/trips/mode-split?days=${timeFilter}`),
        get(`/analytics/trips/temporal-patterns?days=${timeFilter}&granularity=hour`)
      ]);

      setOverview(overviewRes.data as DashboardOverview);
      setModeSplit((modeSplitRes.data as any)?.mode_split || []);
      setTemporalPatterns((temporalRes.data as any)?.temporal_patterns || []);

    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleTimeFilterChange = (event: SelectChangeEvent<number>) => {
    setTimeFilter(event.target.value as number);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  useEffect(() => {
    loadDashboardData();
  }, [timeFilter]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="60vh">
          <CircularProgress size={60} thickness={4} />
          <Typography variant="h6" sx={{ mt: 2, color: 'text.secondary' }}>
            Loading Kerala Transport Analytics...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert 
          severity="error" 
          sx={{ borderRadius: 2 }}
          action={
            <Button 
              color="inherit" 
              size="small" 
              onClick={loadDashboardData}
              startIcon={<Refresh />}
            >
              Retry
            </Button>
          }
        >
          <Typography variant="h6">Failed to load dashboard</Typography>
          <Typography variant="body2">{error}</Typography>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box mb={4}>
        <Typography 
          variant="h3" 
          gutterBottom 
          sx={{ 
            fontWeight: 'bold',
            background: 'linear-gradient(45deg, #1976d2, #42a5f5)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Kerala Transport Analytics
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Real-time insights into Kerala's smart transportation ecosystem
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2} mt={2}>
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Time Period</InputLabel>
            <Select
              value={timeFilter}
              onChange={handleTimeFilterChange}
              label="Time Period"
            >
              <MenuItem value={1}>Last 24 hours</MenuItem>
              <MenuItem value={7}>Last 7 days</MenuItem>
              <MenuItem value={30}>Last 30 days</MenuItem>
              <MenuItem value={90}>Last 90 days</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={loadDashboardData} color="primary">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* Navigation Tabs */}
      <Paper sx={{ mb: 4, borderRadius: 2 }} elevation={2}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              fontSize: '1rem',
              fontWeight: 600
            }
          }}
        >
          <Tab icon={<Assessment />} label="Overview" iconPosition="start" />
          <Tab icon={<Timeline />} label="Trip Analysis" iconPosition="start" />
          <Tab icon={<Map />} label="Live Tracking" iconPosition="start" />
          <Tab icon={<Restaurant />} label="Food Analytics" iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Overview Tab */}
      {tabValue === 0 && overview && (
        <Box>
          {/* Stats Cards */}
          <Grid container spacing={3} mb={4}>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Total Users"
                value={overview.total_users}
                icon={<People />}
                color="#1976d2"
                subtitle="Active users in system"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Total Trips"
                value={overview.total_trips}
                icon={<DirectionsBus />}
                color="#388e3c"
                subtitle="Trips completed"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Distance Traveled"
                value={`${formatNumber(overview.total_distance_km)} km`}
                icon={<TrendingUp />}
                color="#f57c00"
                subtitle="Total distance covered"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="CO₂ Saved"
                value={`${formatNumber(overview.total_emissions_saved_kg)} kg`}
                icon={<EcoFriendly />}
                color="#00796b"
                subtitle="Environmental impact"
              />
            </Grid>
          </Grid>

          {/* Charts */}
          <Grid container spacing={3}>
            {/* Mode Split Chart */}
            <Grid item xs={12} md={6}>
              <Card sx={{ height: 400, borderRadius: 2 }} elevation={2}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <DirectionsBus color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6" fontWeight="bold">
                      Transport Mode Distribution
                    </Typography>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                      <Pie
                        data={modeSplit}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ mode, percentage }: any) => `${mode}\n${percentage}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="count"
                      >
                        {modeSplit.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
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
              <Card sx={{ height: 400, borderRadius: 2 }} elevation={2}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Timeline color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6" fontWeight="bold">
                      Hourly Trip Patterns
                    </Typography>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <ResponsiveContainer width="100%" height={280}>
                    <AreaChart data={temporalPatterns}>
                      <defs>
                        <linearGradient id="colorTrips" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#1976d2" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#1976d2" stopOpacity={0.1}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="hour" />
                      <YAxis />
                      <Tooltip />
                      <Area 
                        type="monotone" 
                        dataKey="trips" 
                        stroke="#1976d2" 
                        fillOpacity={1} 
                        fill="url(#colorTrips)" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>

            {/* Mode Statistics Table */}
            <Grid item xs={12}>
              <Card sx={{ borderRadius: 2 }} elevation={2}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Assessment color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6" fontWeight="bold">
                      Detailed Mode Statistics
                    </Typography>
                  </Box>
                  <Divider sx={{ mb: 2 }} />
                  <Grid container spacing={2}>
                    {modeSplit.map((mode, index) => (
                      <Grid item xs={12} sm={6} md={4} key={index}>
                        <Box 
                          p={2} 
                          border={1} 
                          borderColor="divider" 
                          borderRadius={1}
                          display="flex"
                          alignItems="center"
                          gap={2}
                        >
                          <Avatar sx={{ bgcolor: CHART_COLORS[index % CHART_COLORS.length] }}>
                            {getModeIcon(mode.mode)}
                          </Avatar>
                          <Box>
                            <Typography variant="h6" fontWeight="bold">
                              {mode.count}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {mode.mode}
                            </Typography>
                            <Chip 
                              label={`${mode.percentage}%`} 
                              size="small" 
                              color="primary" 
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Trip Analysis Tab */}
      {tabValue === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card sx={{ borderRadius: 2, minHeight: 400 }} elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Timeline color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    Advanced Trip Analytics
                  </Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Box textAlign="center" py={8}>
                  <Typography variant="h6" color="text.secondary">
                    Detailed trip analysis and patterns
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    Advanced analytics dashboard coming soon...
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Live Map Tab */}
      {tabValue === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card sx={{ borderRadius: 2 }} elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Map color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    Real-time Trip Tracking
                  </Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Box sx={{ height: 600, borderRadius: 1, overflow: 'hidden' }}>
                  <LiveTripsMap />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Food Analytics Tab */}
      {tabValue === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card sx={{ borderRadius: 2, minHeight: 400 }} elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Restaurant color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" fontWeight="bold">
                    Food Consumption Analytics
                  </Typography>
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Box textAlign="center" py={8}>
                  <Typography variant="h6" color="text.secondary">
                    Food logging insights and analytics
                  </Typography>
                  <Typography variant="body2" color="text.secondary" mt={1}>
                    Nutritional analysis and consumption patterns coming soon...
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Container>
  );
};

export default Dashboard;
