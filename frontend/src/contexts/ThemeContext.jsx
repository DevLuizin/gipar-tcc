/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useEffect, useState } from "react";
import { useAuth } from "./AuthContext";
import { atualizarMeuTema } from "../services/perfil/perfil.service";
import { TEMAS } from "../constants/temas.constants";

const ThemeContext = createContext(null);

function chaveTema(usuarioId) {
  return `gipar_tema_${usuarioId}`;
}

export function ThemeProvider({ children }) {
  const { usuario, atualizarUsuarioSessao } = useAuth();
  const [selecao, setSelecao] = useState({ usuarioId: null, tema: null });
  const temaDoUsuario = usuario
    ? usuario.tema || localStorage.getItem(chaveTema(usuario.id)) || "institucional"
    : "institucional";
  const tema = selecao.usuarioId === usuario?.id && selecao.tema
    ? selecao.tema
    : temaDoUsuario;

  useEffect(() => {
    document.documentElement.dataset.theme = tema;
  }, [tema]);

  useEffect(() => {
    if (usuario?.id && usuario.tema) {
      localStorage.setItem(chaveTema(usuario.id), usuario.tema);
    }
  }, [usuario]);

  async function selecionarTema(novoTema) {
    const anterior = tema;
    setSelecao({ usuarioId: usuario?.id ?? null, tema: novoTema });
    if (!usuario) return;

    localStorage.setItem(chaveTema(usuario.id), novoTema);
    try {
      await atualizarMeuTema(novoTema);
      atualizarUsuarioSessao({ tema: novoTema });
    } catch (erro) {
      setSelecao({ usuarioId: usuario.id, tema: anterior });
      localStorage.setItem(chaveTema(usuario.id), anterior);
      throw erro;
    }
  }

  const valor = { tema, temas: TEMAS, selecionarTema };

  return <ThemeContext.Provider value={valor}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const contexto = useContext(ThemeContext);
  if (!contexto) {
    throw new Error("useTheme deve ser usado dentro de ThemeProvider.");
  }
  return contexto;
}
