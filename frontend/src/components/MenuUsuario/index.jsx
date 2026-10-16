import { useEffect, useRef, useState } from "react";
import { LogOut, Settings, User } from "lucide-react";
import Avatar from "../ui/Avatar";

export default function MenuUsuario({ nome, avatar, onLogout, onPerfil, onConfiguracoes }) {
  const [aberto, setAberto] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!aberto) {
      return undefined;
    }

    function handleCliqueFora(event) {
      if (!containerRef.current?.contains(event.target)) {
        setAberto(false);
      }
    }

    document.addEventListener("mousedown", handleCliqueFora);
    return () => document.removeEventListener("mousedown", handleCliqueFora);
  }, [aberto]);

  function handleAcao(callback) {
    setAberto(false);
    callback?.();
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setAberto((prev) => !prev)}
        className="rounded-full transition-opacity hover:opacity-80"
        aria-label="Menu do usuário"
        aria-expanded={aberto}
      >
        <Avatar nome={nome} avatar={avatar} tamanho={36} />
      </button>

      {aberto && (
        <div className="absolute right-0 top-full z-50 mt-2 w-[min(13rem,calc(100vw-1.5rem))] overflow-hidden rounded-xl border border-gray-200 bg-white py-1 shadow-lg sm:w-52">
          <div className="border-b border-gray-100 px-4 py-3">
            <p className="truncate text-sm font-medium text-gray-900">{nome}</p>
          </div>

          <button
            type="button"
            onClick={() => handleAcao(onPerfil)}
            className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
          >
            <User className="h-4 w-4 text-gray-400" />
            Meu Perfil
          </button>

          <button
            type="button"
            onClick={() => handleAcao(onConfiguracoes)}
            className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50"
          >
            <Settings className="h-4 w-4 text-gray-400" />
            Configurações
          </button>

          <div className="my-1 border-t border-gray-100" />

          <button
            type="button"
            onClick={() => handleAcao(onLogout)}
            className="flex w-full items-center gap-2 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50"
          >
            <LogOut className="h-4 w-4" />
            Sair
          </button>
        </div>
      )}
    </div>
  );
}
