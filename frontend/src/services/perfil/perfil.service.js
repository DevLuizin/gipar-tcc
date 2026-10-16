import { apiGet, apiPut } from "../api.config";

const ENDPOINTS = {
  PERFIL: "/usuarios/me",
  SENHA: "/usuarios/me/senha",
  TEMA: "/usuarios/me/tema",
};

export function buscarMeuPerfil() {
  return apiGet(ENDPOINTS.PERFIL);
}

export function atualizarMeuPerfil(dados) {
  return apiPut(ENDPOINTS.PERFIL, dados);
}

export function alterarMinhaSenha(dados) {
  return apiPut(ENDPOINTS.SENHA, dados);
}

export function atualizarMeuTema(tema) {
  return apiPut(ENDPOINTS.TEMA, { tema });
}
