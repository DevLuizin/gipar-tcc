import { useState } from "react";
import { Check } from "lucide-react";
import LayoutUsuario from "../../layouts/usuario/LayoutUsuario";
import { useTheme } from "../../contexts/ThemeContext";

export default function Configuracoes() {
  const { tema, temas, selecionarTema } = useTheme();
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  async function escolher(temaId) {
    setErro("");
    setSalvando(true);
    try {
      await selecionarTema(temaId);
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setSalvando(false);
    }
  }

  return (
    <LayoutUsuario titulo="Configurações">
      <main className="gipar-page mx-auto flex w-full max-w-5xl flex-col gap-5 p-4 sm:p-6">
        <section className="gipar-surface rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Tema da interface</h2>
          <p className="mt-1 text-sm text-gray-600">Sua escolha é salva no perfil e acompanha você em outros dispositivos.</p>
          {erro && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{erro}</p>}

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {temas.map((opcao) => {
              const selecionado = tema === opcao.id;
              return (
                <button
                  key={opcao.id}
                  type="button"
                  disabled={salvando}
                  onClick={() => escolher(opcao.id)}
                  className={`theme-card relative rounded-xl border p-4 text-left transition ${selecionado ? "border-blue-600 ring-2 ring-blue-200" : "border-gray-200 hover:border-gray-400"}`}
                >
                  {selecionado && <Check className="absolute right-4 top-4 h-5 w-5 text-blue-600" />}
                  <span className={`mb-3 block h-14 rounded-lg theme-preview theme-preview-${opcao.id}`} />
                  <strong className="block text-gray-900">{opcao.nome}</strong>
                  <span className="mt-1 block pr-6 text-sm text-gray-600">{opcao.descricao}</span>
                </button>
              );
            })}
          </div>
        </section>
      </main>
    </LayoutUsuario>
  );
}
