import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { LogOut, Menu, X } from "lucide-react";
import { menuByRole } from "../../config/menuItems";
import { BotaoBarraLateral } from "../BotaoBarraLateral";
import LogoClaro from "../ui/LogoClaro";
import Avatar from "../ui/Avatar";

export default function Sidebar({
  userRole,
  nomeUsuario = "Usuário",
  cargoUsuario = "",
  avatarUsuario,
  onLogout,
  mobileAberto = false,
  onFecharMobile,
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const currentMenu = menuByRole[userRole] || menuByRole.aluno;
  const [isCollapsed, setIsCollapsed] = useState(false);

  const menuExpandido = !isCollapsed || mobileAberto;

  function handleNavegacao(path) {
    navigate(path);
    onFecharMobile?.();
  }

  return (
    <>
      {mobileAberto && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          aria-label="Fechar menu"
          onClick={onFecharMobile}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex h-full shrink-0 flex-col bg-[#1A6B74] p-3 transition-all duration-300 md:relative md:z-auto md:translate-x-0 ${
          mobileAberto ? "translate-x-0" : "-translate-x-full"
        } ${isCollapsed ? "md:w-[72px]" : "md:w-56"} w-64 max-w-[85vw]`}
      >
        <div className="mb-3 flex shrink-0 items-center justify-end gap-1">
          <button
            type="button"
            onClick={onFecharMobile}
            className="flex h-8 w-8 items-center justify-center rounded-md text-white/80 transition-colors hover:bg-white/10 hover:text-white md:hidden"
            aria-label="Fechar menu"
          >
            <X className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden h-8 w-8 shrink-0 items-center justify-center rounded-md text-white/80 transition-colors hover:bg-white/10 hover:text-white md:flex"
            aria-label={isCollapsed ? "Expandir menu" : "Recolher menu"}
          >
            <Menu className="h-5 w-5" />
          </button>
        </div>

        <div className="mb-4 flex justify-center border-b border-white/10 px-1 pb-4">
          {menuExpandido ? (
            <LogoClaro largura={180} className="max-w-full" />
          ) : (
            <LogoClaro altura={28} />
          )}
        </div>

        <nav className="flex flex-1 flex-col gap-1 overflow-y-auto">
          {currentMenu.map((item) => (
            <BotaoBarraLateral
              key={item.path}
              label={item.label}
              icon={item.icon}
              isActive={location.pathname === item.path}
              onClick={() => handleNavegacao(item.path)}
              labelClass={menuExpandido ? "" : "sr-only"}
              isCollapsed={!menuExpandido}
            />
          ))}
        </nav>

        <div
          className={`mt-3 flex items-center gap-2 border-t border-white/10 pt-3 ${
            menuExpandido ? "" : "justify-center"
          }`}
        >
          <Avatar nome={nomeUsuario} avatar={avatarUsuario} tamanho={menuExpandido ? 36 : 32} />
          {menuExpandido && (
            <>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium text-white">{nomeUsuario}</p>
                {cargoUsuario && (
                  <p className="truncate text-xs text-white/70">{cargoUsuario}</p>
                )}
              </div>
              <button
                type="button"
                onClick={onLogout}
                className="rounded-md p-1.5 text-white/70 transition-colors hover:bg-white/10 hover:text-white"
                aria-label="Sair"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </>
          )}
        </div>
      </aside>
    </>
  );
}
