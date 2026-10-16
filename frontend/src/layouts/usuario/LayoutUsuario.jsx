import { useEffect, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import BarraLateral from "../../components/BarraLateral";
import Cabecalho from "../../components/Cabecalho";
import { useAuth } from "../../contexts/AuthContext";

/**
 * Layout padrão das telas autenticadas.
 *
 * Modo auth (padrão): páginas admin passam apenas `titulo` e `children`.
 * O layout resolve nome, perfil, role e logout via useAuth().
 *
 * Modo legado (TEMPORÁRIO): páginas de Estagiário e Aluno ainda passam
 * nome, cargo, tipoUsuario e onLogout. Remover após migrar esses perfis.
 * Ver docs/autenticacao.md
 */
export default function LayoutUsuario({
  tipoUsuario,
  titulo,
  cargo,
  nome,
  notificacoes = [],
  onMarcarNotificacaoLida,
  onMarcarTodasNotificacoesLidas,
  onLogout,
  children,
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const { usuario, logout } = useAuth();
  const [menuMobileAberto, setMenuMobileAberto] = useState(false);

  // TODO(migracao): remover modo legado quando Estagiário e Aluno migrarem.
  const modoLegado = nome !== undefined;

  useEffect(() => {
    setMenuMobileAberto(false);
  }, [location.pathname]);

  function handleLogoutAuth() {
    logout();
    navigate("/login");
  }

  if (!modoLegado && !usuario) {
    return <Navigate to="/login" replace />;
  }

  const dadosSidebar = modoLegado
    ? {
        userRole: tipoUsuario,
        nomeUsuario: nome,
        cargoUsuario: cargo,
        onLogoutHandler: onLogout,
      }
    : {
        userRole: usuario.role,
        nomeUsuario: usuario.nome_exibicao || usuario.nome,
        cargoUsuario: usuario.perfil,
        avatarUsuario: usuario.avatar,
        onLogoutHandler: handleLogoutAuth,
      };

  return (
    <section className="flex h-[100dvh] w-full min-h-0 overflow-hidden">
      <BarraLateral
        userRole={dadosSidebar.userRole}
        nomeUsuario={dadosSidebar.nomeUsuario}
        cargoUsuario={dadosSidebar.cargoUsuario}
        avatarUsuario={dadosSidebar.avatarUsuario}
        onLogout={dadosSidebar.onLogoutHandler}
        mobileAberto={menuMobileAberto}
        onFecharMobile={() => setMenuMobileAberto(false)}
      />
      <div className="flex min-h-0 min-w-0 flex-1 flex-col bg-gray-100">
        <Cabecalho
          titulo={titulo}
          nome={dadosSidebar.nomeUsuario}
          avatar={dadosSidebar.avatarUsuario}
          notificacoes={notificacoes}
          onMarcarNotificacaoLida={onMarcarNotificacaoLida}
          onMarcarTodasNotificacoesLidas={onMarcarTodasNotificacoesLidas}
          onLogout={dadosSidebar.onLogoutHandler}
          onAbrirMenuMobile={() => setMenuMobileAberto(true)}
          onPerfil={() => navigate("/perfil")}
          onConfiguracoes={() => navigate("/configuracoes")}
        />
        <div className="min-h-0 flex-1 overflow-y-auto overflow-x-hidden w-full">
          {children}
        </div>
      </div>
    </section>
  );
}
