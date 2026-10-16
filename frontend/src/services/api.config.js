// ================================================================
// api.config.js - Configuração central da API
// ================================================================

// URL base do backend (FastAPI)
export const API_BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Chave para armazenar a sessão no sessionStorage
export const SESSION_KEY = "gipar_usuario";

// ================================================================
// Funções auxiliares para requisições
// ================================================================

/**
 * Obtém o token JWT da sessão
 */
export function getAccessToken() {
  const dados = sessionStorage.getItem(SESSION_KEY);
  if (!dados) return null;
  try {
    const sessao = JSON.parse(dados);
    console.log("🔑 Token recuperado do sessionStorage:", sessao.access_token ? "Sim ✅" : "Não ❌");
    return sessao.access_token || null;
  } catch {
    return null;
  }
}

/**
 * Cria os headers padrão para requisições autenticadas
 */
export function getAuthHeaders(extraHeaders = {}) {
  const token = getAccessToken();
  const headers = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
    console.log("🔑 Requisição autenticada preparada.");
  } else {
    console.warn("⚠️ Nenhum token disponível para autenticação!");
  }

  return headers;
}

/**
 * Função genérica para requisições GET
 */
export async function apiGet(endpoint) {
  console.log("📤 GET", `${API_BACKEND_URL}${endpoint}`);
  const resposta = await fetch(`${API_BACKEND_URL}${endpoint}`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    console.error("❌ Erro na requisição GET:", erro);
    throw new Error(erro.detail || "Erro na requisição");
  }

  return resposta.json();
}

/**
 * Função genérica para requisições POST
 */
export async function apiPost(endpoint, dados) {
  console.log("📤 POST", `${API_BACKEND_URL}${endpoint}`, dados);
  try {
    const resposta = await fetch(`${API_BACKEND_URL}${endpoint}`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(dados),
    });

    if (!resposta.ok) {
      let mensagemErro = "Erro ao criar registro";
      try {
        const erro = await resposta.json();
        if (erro.detail) {
          if (Array.isArray(erro.detail)) {
            mensagemErro = erro.detail.map(e => 
              `${e.loc.join('.')}: ${e.msg}`
            ).join('; ');
          } else {
            mensagemErro = erro.detail;
          }
        }
      } catch {
        mensagemErro = `Erro ${resposta.status}: ${resposta.statusText}`;
      }
      throw new Error(mensagemErro);
    }

    return await resposta.json();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error("Erro desconhecido ao criar registro");
  }
}

/**
 * Função genérica para requisições PUT
 */
export async function apiPut(endpoint, dados) {
  console.log("📤 PUT", `${API_BACKEND_URL}${endpoint}`, dados);
  const resposta = await fetch(`${API_BACKEND_URL}${endpoint}`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(dados),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    console.error("❌ Erro na requisição PUT:", erro);
    throw new Error(erro.detail || "Erro ao atualizar registro");
  }

  return resposta.json();
}

/**
 * Função genérica para requisições PATCH
 */
export async function apiPatch(endpoint, dados = null) {
  console.log("📤 PATCH", `${API_BACKEND_URL}${endpoint}`, dados);
  const options = {
    method: "PATCH",
    headers: getAuthHeaders(),
  };

  if (dados) {
    options.body = JSON.stringify(dados);
  }

  const resposta = await fetch(`${API_BACKEND_URL}${endpoint}`, options);

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    console.error("❌ Erro na requisição PATCH:", erro);
    throw new Error(erro.detail || "Erro ao atualizar registro");
  }

  return resposta.json();
}

/**
 * Função genérica para requisições DELETE
 */
export async function apiDelete(endpoint) {
  console.log("📤 DELETE", `${API_BACKEND_URL}${endpoint}`);
  const resposta = await fetch(`${API_BACKEND_URL}${endpoint}`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    console.error("❌ Erro na requisição DELETE:", erro);
    throw new Error(erro.detail || "Erro ao excluir registro");
  }

  return resposta.json();
}
