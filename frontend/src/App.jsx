import { Navigate, Route, Routes } from 'react-router-dom';

// Importações das páginas
import Login from './pages/login/Login';
import Usuarios from './pages/adm/Usuarios.jsx';
import AdmDashboard from './pages/adm/admDashboard';
import DashboardEstagiario from './pages/estagiario/Dashboard';
import AdmEquipamentos from './pages/adm/equipamentos.jsx';
import EstagEquipamentos from './pages/estagiario/equipamentos.jsx';
import Manutencoes from './pages/adm/Manutencoes.jsx';
import Relatorios from './pages/adm/Relatorios.jsx';
import MeusEmprestimos from './pages/aluno/MeusEmprestimos.jsx';
import EmprestimosAdm from './pages/adm/Emprestimo.jsx';
import EstagEmprestimos from "./pages/estagiario/emprestimos.jsx";
import Catalogo from './pages/aluno/Catalogo.jsx';
import Perfil from './pages/perfil/Perfil.jsx';
import Configuracoes from './pages/configuracoes/Configuracoes.jsx';

// Importações de autenticação
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './contexts/AuthContext';
import ChatWidget from './components/chat/ChatWidget';


function RotaInicial() {
  const { isAuthenticated, homePath } = useAuth();
  return <Navigate to={isAuthenticated ? homePath : '/login'} replace />;
}

function DashboardRouter() {
  const { usuario } = useAuth();

  if (usuario?.role === 'estagiario') {
    return <DashboardEstagiario />;
  }

  return <AdmDashboard />;
}

export default function App() {
  return (
    <>
      <Routes>
        {/* Rotas Públicas */}
        <Route path="/" element={<RotaInicial />} />
        <Route path="/login" element={<Login />} />

        <Route
          path="/perfil"
          element={
            <ProtectedRoute>
              <Perfil />
            </ProtectedRoute>
          }
        />
        <Route
          path="/configuracoes"
          element={
            <ProtectedRoute>
              <Configuracoes />
            </ProtectedRoute>
          }
        />

        {/* Rotas Protegidas (Exigem Autenticação) */}
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <DashboardRouter />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/EstagEquipamentos" 
          element={
            <ProtectedRoute>
              <EstagEquipamentos />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/EstagEmprestimos" 
          element={
            <ProtectedRoute>
              <EstagEmprestimos />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/equipamentos" 
          element={
            <ProtectedRoute>
              <AdmEquipamentos />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/manutencoes" 
          element={
            <ProtectedRoute>
              <Manutencoes />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/usuarios" 
          element={
            <ProtectedRoute>
              <Usuarios />
            </ProtectedRoute>
          } 
        />
        <Route
          path="/relatorios"
          element={
            <ProtectedRoute>
              <Relatorios />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/alunoEmprestimos" 
          element={
            <ProtectedRoute>
              <MeusEmprestimos />
            </ProtectedRoute>
          } 
        />
        <Route
          path="/catalogo"
          element={
            <ProtectedRoute>
              <Catalogo />
            </ProtectedRoute>
          }
        />
        <Route 
          path="/emprestimos" 
          element={
            <ProtectedRoute>
              <EmprestimosAdm />
            </ProtectedRoute>
          } 
        />
      </Routes>

      {/* Widget Flutuante do Chatbot Inteligente (REQ-001) */}
      <ChatWidget />
    </>
  );
}
