import { Menu } from "lucide-react";
import TituloPagina from "../TituloPagina";
import DropdownNotificacoes from "../DropdownNotificacoes";
import MenuUsuario from "../MenuUsuario";

export default function Cabecalho({
  titulo,
  nome,
  avatar,
  notificacoes = [],
  onMarcarNotificacaoLida,
  onMarcarTodasNotificacoesLidas,
  onLogout,
  onAbrirMenuMobile,
  onPerfil,
  onConfiguracoes,
}) {
  const usaInteracao = typeof onLogout === "function";

  return (
    <header className="flex min-h-14 shrink-0 items-center justify-between gap-2 bg-white px-3 py-2 sm:gap-4 sm:px-6 sm:py-0">
      <div className="flex min-w-0 flex-1 items-center gap-2 sm:gap-3">
        {onAbrirMenuMobile && (
          <button
            type="button"
            onClick={onAbrirMenuMobile}
            className="rounded-lg p-2 text-gray-600 transition-colors hover:bg-gray-200/60 md:hidden"
            aria-label="Abrir menu"
          >
            <Menu className="h-5 w-5" />
          </button>
        )}
        <div className="min-w-0">
          <TituloPagina className="truncate">{titulo}</TituloPagina>
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1.5 sm:gap-4">
        {usaInteracao ? (
          <>
            <DropdownNotificacoes
              notificacoes={notificacoes}
              onMarcarLida={onMarcarNotificacaoLida}
              onMarcarTodasLidas={onMarcarTodasNotificacoesLidas}
            />

            <p className="hidden text-sm text-gray-600 lg:block">
              Bem-vindo, <span className="font-medium text-gray-900">{nome}</span>
            </p>

            <MenuUsuario
              nome={nome}
              avatar={avatar}
              onLogout={onLogout}
              onPerfil={onPerfil}
              onConfiguracoes={onConfiguracoes}
            />
          </>
        ) : (
          <p className="hidden text-sm text-gray-600 sm:block">
            Bem-vindo, <span className="font-medium text-gray-900">{nome}</span>
          </p>
        )}
      </div>
    </header>
  );
}
