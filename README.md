# 🌴 KeraRoutes - Kerala Transportation & Research Analytics Platform

<div align="center">
  <img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
  <img src="https://img.shields.io/badge/Material_UI-0081CB?style=for-the-badge&logo=mui&logoColor=white" alt="Material UI" />
</div>

<div align="center">
  <h3>🚌 Smart Transportation Analytics • 🍛 Local Food Discovery • 📊 Research Dashboard</h3>
  <p><em>A comprehensive platform for analyzing transportation patterns and food culture in Kerala, India</em></p>
</div>

---

## 🎯 Overview

**KeraRoutes** is a full-stack analytics platform designed to capture, analyze, and visualize transportation and food consumption patterns across Kerala. Built for researchers, urban planners, and policymakers, it provides real-time insights into mobility trends and local culinary preferences.

### 🌟 Key Features

- **📱 Mobile Data Collection**: Flutter app for seamless trip and food logging
- **🔍 Real-time Analytics**: Beautiful dashboard for researchers and scientists
- **🗺️ Location Intelligence**: GPS-based tracking and geo-analytics
- **🍽️ Food Culture Mapping**: Restaurant and cuisine type analysis
- **💰 Economic Insights**: Cost analysis for transportation and dining
- **📊 Data Visualization**: Interactive charts and statistical summaries

---

## 🏗️ Architecture

```
KeraRoutes/
├── 📱 mobile_app/          # Flutter mobile application
├── ⚡ backend/             # FastAPI backend server
├── 🖥️ research_dashboard/  # React web dashboard
├── 🗄️ database/           # Database setup and migrations
└── 📚 docs/               # Documentation
```

### 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Mobile App** | Flutter + Dart | Cross-platform data collection |
| **Backend API** | FastAPI + Python | RESTful API and data processing |
| **Database** | MongoDB | Document storage and analytics |
| **Cache** | Redis | Session management and caching |
| **Frontend** | React + TypeScript | Research dashboard |
| **UI Framework** | Material-UI | Consistent design system |

---

## 🚀 Quick Start

### Prerequisites

- **Flutter SDK** (≥3.0.0)
- **Python** (≥3.8)
- **Node.js** (≥16.0.0)
- **MongoDB** (≥5.0)
- **Redis** (≥6.0)

### 1. 🔧 Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### 2. 📱 Mobile App Setup

```bash
cd mobile_app
flutter pub get
flutter run
```

### 3. 🖥️ Research Dashboard Setup

```bash
cd research_dashboard
npm install
npm start
```

The dashboard will be available at `http://localhost:3000`

---

## 📊 API Endpoints

### 🚌 Transportation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/trips` | Log a new trip |
| `GET` | `/api/v1/trips` | Retrieve trip history |
| `GET` | `/api/v1/analytics/transport` | Transport analytics |

### 🍛 Food & Dining

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/food` | Log food experience |
| `GET` | `/api/v1/food` | Retrieve food entries |
| `GET` | `/api/v1/analytics/food` | Food analytics |

### 📈 Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/analytics/dashboard-summary` | Complete dashboard data |
| `GET` | `/api/v1/health` | API health check |

---

## 📱 Mobile App Features

<div align="center">
  <table>
    <tr>
      <td align="center">
        <h3>🗺️ Trip Tracking</h3>
        <p>GPS-based route logging with transport mode selection</p>
      </td>
      <td align="center">
        <h3>🍽️ Food Logging</h3>
        <p>Restaurant visits and cuisine type tracking</p>
      </td>
    </tr>
    <tr>
      <td align="center">
        <h3>📊 Personal Analytics</h3>
        <p>Individual statistics and insights</p>
      </td>
      <td align="center">
        <h3>🔍 Data Collection</h3>
        <p>Simple forms for quick data entry</p>
      </td>
    </tr>
  </table>
</div>

### Transport Modes Supported
- 🚌 **Public Bus**
- 🚗 **Auto Rickshaw**
- 🚇 **Train**
- 🚲 **Bicycle**
- 🚶 **Walking**
- 🚗 **Private Car**

---

## 🖥️ Research Dashboard

### 📊 Analytics Views

1. **Overview Dashboard**
   - Total trips and food entries
   - Economic spending analysis
   - Mode distribution charts

2. **Transportation Analytics**
   - Mode split visualization
   - Hourly travel patterns
   - Cost analysis by transport type

3. **Food Culture Analysis**
   - Restaurant visit patterns
   - Cuisine type preferences
   - Spending trends

4. **Regional Insights**
   - Geographic distribution
   - City-wise analytics
   - Route popularity

---

## 🗄️ Data Models

### Trip Schema
```json
{
  "_id": "ObjectId",
  "transport_mode": "bus | auto | train | bike | walking | car",
  "purpose": "work | shopping | leisure | education",
  "start_location": {
    "city": "string",
    "latitude": "number",
    "longitude": "number"
  },
  "end_location": {
    "city": "string", 
    "latitude": "number",
    "longitude": "number"
  },
  "cost": "number",
  "number_of_people": "number",
  "created_at": "ISO8601"
}
```

### Food Schema
```json
{
  "_id": "ObjectId",
  "restaurant_name": "string",
  "cuisine_type": "kerala | north_indian | chinese | continental",
  "meal_type": "breakfast | lunch | dinner | snack",
  "total_cost": "number",
  "number_of_people": "number",
  "location": {
    "city": "string",
    "latitude": "number", 
    "longitude": "number"
  },
  "created_at": "ISO8601"
}
```

---

## 🛠️ Development

### 🔧 Environment Variables

Create `.env` files in respective directories:

**Backend (.env)**
```env
MONGODB_URL=mongodb://localhost:27017/natpac_transport
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
DEBUG=true
```

**Frontend (.env)**
```env
REACT_APP_API_BASE_URL=http://localhost:8000
```

### 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd research_dashboard && npm test

# Mobile app tests
cd mobile_app && flutter test
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### 📋 Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🎯 Roadmap

- [ ] **🤖 AI-powered route optimization**
- [ ] **🌍 Multi-language support**
- [ ] **📧 Automated report generation**
- [ ] **🔒 Advanced user authentication**
- [ ] **📱 Offline data collection**
- [ ] **🗺️ Interactive map visualizations**
- [ ] **📈 Predictive analytics**

---

## 👥 Team

<div align="center">
  <p><strong>Built with ❤️ for Kerala's sustainable transportation future</strong></p>
  
  <p>
    <a href="https://github.com/RitwikMittal">
      <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
    </a>
  </p>
</div>

---

## 📞 Support

- 📧 **Email**: [support@keraroutes.com](mailto:support@keraroutes.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/RitwikMittal/KeraRoutes/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/RitwikMittal/KeraRoutes/discussions)

---

<div align="center">
  <p><strong>⭐ Star this repository if you find it helpful!</strong></p>
  <p><em>Made with 🌴 in Kerala | Powered by Open Source</em></p>
</div>
