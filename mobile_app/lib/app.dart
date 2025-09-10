import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'features/authentication/screens/login_screen.dart';
import 'features/trip_tracking/screens/trip_dashboard.dart';
import 'features/authentication/providers/auth_provider.dart';
import 'shared/themes/app_theme.dart';

class NatpacTransportApp extends StatelessWidget {
  const NatpacTransportApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NATPAC Smart Transport',
      theme: AppTheme.lightTheme,
      home: Consumer<AuthProvider>(
        builder: (context, authProvider, child) {
          if (authProvider.isAuthenticated) {
            return const TripDashboard();
          } else {
            return const LoginScreen();
          }
        },
      ),
      debugShowCheckedModeBanner: false,
    );
  }
}