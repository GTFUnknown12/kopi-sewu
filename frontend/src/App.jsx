import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './lib/auth.jsx';
import Login from './pages/Login.jsx';
import AdminLayout from './layouts/AdminLayout.jsx';
import Dashboard from './pages/admin/Dashboard.jsx';
import StaffPortal from './pages/StaffPlaceholder.jsx';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Dashboard />} />
          </Route>
          <Route path="/staf" element={<StaffPortal />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
