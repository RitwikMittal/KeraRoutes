import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './pages/DashboardSimple';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2E7D32', // Kerala green
    },
    secondary: {
      main: '#FF6B35', // Kerala orange
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Dashboard />
    </ThemeProvider>
  );
}

export default App;
