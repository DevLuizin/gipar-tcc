import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import LayoutUsuario from "../../layouts/usuario/LayoutUsuario";
import Avatar from "../../components/ui/Avatar";
import { AVATARES } from "../../constants/avatares.constants";
import { useAuth } from "../../contexts/AuthContext";
import {
  alterarMinhaSenha,
  atualizarMeuPerfil,
  buscarMeuPerfil,
} from "../../services/perfil/perfil.service";

const campoInicial = {
  nome: "",
  nome_exibicao: "",
  email: "",
  avatar: null,
  senha_atual: "",
};

export default function Perfil() {
  const navigate = useNavigate();
  const { usuario, atualizarUsuarioSessao, logout } = useAuth();
  const [perfil, setPerfil] = useState(campoInicial);
  const [senha, setSenha] = useState({
    senha_atual: "",
    nova_senha: "",
    confirmacao_senha: "",
  });
  const [carregando, setCarregando] = useState(true);
  const [salvando, setSalvando] = useState(false);
  const [mensagem, setMensagem] = useState(null);

  useEffect(() => {
    buscarMeuPerfil()
      .then((dados) => {
        setPerfil({ ...campoInicial, ...dados });
        atualizarUsuarioSessao({
          nome: dados.nome,
          nome_exibicao: dados.nome_exibicao,
          email: dados.email,
          avatar: dados.avatar,
          tema: dados.tema,
        });
      })
      .catch((erro) => setMensagem({ tipo: "erro", texto: erro.message }))
      .finally(() => setCarregando(false));
    // O carregamento ocorre apenas na entrada da página.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function alterarCampo(evento) {
    const { name, value } = evento.target;
    setPerfil((atual) => ({ ...atual, [name]: value }));
  }

  async function salvarPerfil(evento) {
    evento.preventDefault();
    setSalvando(true);
    setMensagem(null);
    try {
      const resultado = await atualizarMeuPerfil({
        nome: perfil.nome,
        nome_exibicao: perfil.nome_exibicao || null,
        email: perfil.email,
        avatar: perfil.avatar,
        senha_atual: perfil.senha_atual || null,
      });
      if (resultado.requer_novo_login) {
        logout();
        navigate("/login", { replace: true });
        return;
      }
      const atualizado = resultado.perfil;
      setPerfil({ ...campoInicial, ...atualizado });
      atualizarUsuarioSessao({
        nome: atualizado.nome,
        nome_exibicao: atualizado.nome_exibicao,
        email: atualizado.email,
        avatar: atualizado.avatar,
      });
      setMensagem({ tipo: "sucesso", texto: "Perfil atualizado com sucesso." });
    } catch (erro) {
      setMensagem({ tipo: "erro", texto: erro.message });
    } finally {
      setSalvando(false);
    }
  }

  async function salvarSenha(evento) {
    evento.preventDefault();
    setSalvando(true);
    setMensagem(null);
    try {
      await alterarMinhaSenha(senha);
      logout();
      navigate("/login", { replace: true });
    } catch (erro) {
      setMensagem({ tipo: "erro", texto: erro.message });
      setSalvando(false);
    }
  }

  const emailAlterado = perfil.email !== usuario?.email;

  return (
    <LayoutUsuario titulo="Meu Perfil">
      <main className="gipar-page mx-auto flex w-full max-w-5xl flex-col gap-6 p-4 sm:p-6">
        {mensagem && (
          <div className={`rounded-lg border p-3 text-sm ${mensagem.tipo === "erro" ? "border-red-300 bg-red-50 text-red-700" : "border-green-300 bg-green-50 text-green-700"}`}>
            {mensagem.texto}
          </div>
        )}

        {carregando ? (
          <p className="text-gray-600">Carregando perfil...</p>
        ) : (
          <>
            <form onSubmit={salvarPerfil} className="gipar-surface grid gap-6 rounded-xl border border-gray-200 bg-white p-5 shadow-sm md:grid-cols-[220px_1fr]">
              <section>
                <h2 className="text-lg font-semibold text-gray-900">Avatar</h2>
                <div className="my-4 flex justify-center">
                  <Avatar nome={perfil.nome} avatar={perfil.avatar} tamanho={96} />
                </div>
                <div className="grid grid-cols-3 gap-2">
                  {AVATARES.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setPerfil((atual) => ({ ...atual, avatar: item.id }))}
                      className={`rounded-lg border p-2 ${perfil.avatar === item.id ? "border-blue-600 ring-2 ring-blue-200" : "border-gray-200"}`}
                      aria-label={`Selecionar ${item.nome}`}
                    >
                      <Avatar avatar={item.id} tamanho={42} />
                    </button>
                  ))}
                </div>
              </section>

              <section className="grid gap-4">
                <h2 className="text-lg font-semibold text-gray-900">Dados pessoais</h2>
                <label className="grid gap-1 text-sm text-gray-700">
                  Nome
                  <input className="gipar-input rounded-lg border border-gray-300 px-3 py-2" name="nome" value={perfil.nome} onChange={alterarCampo} required minLength={2} />
                </label>
                <label className="grid gap-1 text-sm text-gray-700">
                  Nome de exibição
                  <input className="gipar-input rounded-lg border border-gray-300 px-3 py-2" name="nome_exibicao" value={perfil.nome_exibicao || ""} onChange={alterarCampo} />
                </label>
                <label className="grid gap-1 text-sm text-gray-700">
                  E-mail
                  <input className="gipar-input rounded-lg border border-gray-300 px-3 py-2" name="email" type="email" value={perfil.email} onChange={alterarCampo} required />
                </label>
                <label className="grid gap-1 text-sm text-gray-700">
                  Perfil de acesso
                  <input className="gipar-input rounded-lg border border-gray-300 bg-gray-100 px-3 py-2" value={perfil.tipo_usuario || ""} disabled />
                </label>
                {emailAlterado && (
                  <div className="rounded-lg border border-blue-200 bg-blue-50 p-3 text-sm text-blue-800">
                    O e-mail é sua credencial de acesso. Informe a senha atual para confirmar a alteração; depois será necessário entrar novamente.
                  </div>
                )}
                {emailAlterado && (
                  <label className="grid gap-1 text-sm text-gray-700">
                    Senha atual
                    <input className="gipar-input rounded-lg border border-gray-300 px-3 py-2" name="senha_atual" type="password" value={perfil.senha_atual} onChange={alterarCampo} required />
                  </label>
                )}
                <button disabled={salvando} className="justify-self-start rounded-lg bg-[#1A6B74] px-4 py-2 font-medium text-white disabled:opacity-60">
                  Salvar perfil
                </button>
              </section>
            </form>

            <form onSubmit={salvarSenha} className="gipar-surface grid gap-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Alterar senha</h2>
                <p className="text-sm text-gray-600">Use pelo menos 8 caracteres, incluindo letras e números. A alteração encerra as sessões em todos os dispositivos.</p>
              </div>
              {[
                ["senha_atual", "Senha atual"],
                ["nova_senha", "Nova senha"],
                ["confirmacao_senha", "Confirmar nova senha"],
              ].map(([campo, rotulo]) => (
                <label key={campo} className="grid gap-1 text-sm text-gray-700 sm:max-w-md">
                  {rotulo}
                  <input
                    className="gipar-input rounded-lg border border-gray-300 px-3 py-2"
                    type="password"
                    value={senha[campo]}
                    onChange={(evento) => setSenha((atual) => ({ ...atual, [campo]: evento.target.value }))}
                    required
                  />
                </label>
              ))}
              <button disabled={salvando} className="justify-self-start rounded-lg bg-[#1A6B74] px-4 py-2 font-medium text-white disabled:opacity-60">
                Alterar senha
              </button>
            </form>
          </>
        )}
      </main>
    </LayoutUsuario>
  );
}
