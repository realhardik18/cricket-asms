import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard'; // Optional, if you have a dashboard after login

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Default route */}
          <Route path="/" element={<Login />} />

          {/* Register route */}
          <Route path="/register" element={<Register />} />

          {/* Login route */}
          <Route path="/login" element={<Login />} />

          {/* Dashboard route (optional, redirect here after successful login) */}
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
