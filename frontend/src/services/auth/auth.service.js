// ================================================================
// auth.service.js - GIPAR Frontend
// CORRIGIDO: Agora usa APENAS o FastAPI (porta 8000)
// ================================================================

// ================================================================
// 1. CONFIGURAÇÃO DAS URLs
// ================================================================

// 🔴 ÚNICA URL DA API - NUNCA usa 3001!
const API_BACKEND_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ================================================================
// 2. CONFIGURAÇÕES DE PERFIL E ROTAS
// ================================================================

const SESSION_KEY = "gipar_usuario";

export const HOME_POR_PERFIL = {
  adm: "/dashboard",
  estagiario: "/dashboard",
  professor: "/dashboard",
  aluno: "/alunoEmprestimos",
};

export const ROTAS_POR_PERFIL = {
  adm: [
    "/perfil",
    "/configuracoes",
    "/dashboard",
    "/equipamentos",
    "/equipamento",
    "/emprestimos",
    "/manutencoes",
    "/usuarios",
    "/relatorios",
    "/relatorios/equipamentos",
    "/relatorios/emprestimos",
    "/relatorios/usuarios",
    "/relatorios/manutencoes",
    "/relatorios/reservas",
    "/relatorios/categorias"
  ],
  estagiario: [
    "/perfil",
    "/configuracoes",
    "/dashboard",
    "/equipamentos",
    "/equipamento",
    "/EstagEquipamentos",
    "/EstagEmprestimos"
  ],
  professor: [
    "/perfil",
    "/configuracoes",
    "/dashboard",
    "/equipamentos",
    "/equipamento",
    "/manutencoes"
  ],
  aluno: [
    "/perfil",
    "/configuracoes",
    "/alunoEmprestimos",
    "/catalogo",
    "/equipamentos",
    "/equipamento"
  ],
};

// ================================================================
// 3. MAPEAMENTO DE PERFIS
// ================================================================

export function mapPerfilToRole(perfil) {
  const mapa = {
    admin: "adm",
    tecnico: "estagiario",
    comum: "aluno",
    ADMINISTRADOR: "adm",
    TECNICO: "estagiario",
    COMUM: "aluno"
  };
  return mapa[perfil] ?? "aluno";
}

// ================================================================
// 4. GERENCIAMENTO DE SESSÃO
// ================================================================

export function getSessao() {
  const dados = sessionStorage.getItem(SESSION_KEY);
  if (!dados) return null;

  try {
    return JSON.parse(dados);
  } catch {
    sessionStorage.removeItem(SESSION_KEY);
    return null;
  }
}

export function salvarSessao(usuario) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(usuario));
}

export function encerrarSessao() {
  sessionStorage.removeItem(SESSION_KEY);
}

export function getAccessToken() {
  const sessao = getSessao();
  console.log("🔑 Token obtido:", sessao?.access_token ? "Sim ✅" : "Não ❌");
  return sessao?.access_token ?? null;
}

// ================================================================
// 5. AUTENTICAÇÃO (LOGIN) - USANDO O FASTAPI
// ================================================================

export async function autenticar(identificador, senha) {
  const corpo = new URLSearchParams();
  corpo.set("username", identificador.trim().toLowerCase());
  corpo.set("password", senha);

  console.log("📤 Tentando login:", identificador);

  const resposta = await fetch(`${API_BACKEND_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: corpo,
  });

  if (!resposta.ok) {
    let mensagemErro = "E-mail/login ou senha incorretos.";
    try {
      const erro = await resposta.json();
      if (erro.detail) mensagemErro = erro.detail;
    } catch {
      // ignora
    }
    throw new Error(mensagemErro);
  }

  const dados = await resposta.json();
  const sessao = {
    id: dados.id,
    nome: dados.nome,
    nome_exibicao: dados.nome_exibicao,
    email: dados.email,
    perfil: dados.perfil,
    role: mapPerfilToRole(dados.perfil),
    tipo_usuario: dados.tipo_usuario,
    avatar: dados.avatar,
    tema: dados.tema || "institucional",
    access_token: dados.access_token,
  };

  salvarSessao(sessao);
  return sessao;
}

// ================================================================
// 6. USUÁRIOS - AGORA USA O FASTAPI
// ================================================================

export async function buscarUsuariosAtivos() {
  try {
    const token = getAccessToken();
    const headers = {
      "Content-Type": "application/json",
    };
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const resposta = await fetch(`${API_BACKEND_URL}/listar_usuarios`, {
      method: "GET",
      headers,
    });

    if (!resposta.ok) {
      throw new Error("Erro ao buscar usuários");
    }

    const resultado = await resposta.json();
    
    if (resultado.usuarios) {
      return resultado.usuarios;
    }
    
    if (Array.isArray(resultado)) {
      return resultado;
    }
    
    return [];
    
  } catch (error) {
    console.error("Erro ao buscar usuários:", error);
    throw new Error("Não foi possível carregar os usuários. Verifique se o backend está rodando.");
  }
}

// ================================================================
// 7. VERIFICAÇÃO DE PERMISSÃO
// ================================================================

export function usuarioTemAcesso(role, pathname) {
  const rotasPermitidas = ROTAS_POR_PERFIL[role] ?? [];
  return rotasPermitidas.some(
    (rota) => pathname === rota || pathname.startsWith(`${rota}/`)
  );
}

// ================================================================
// 8. FUNÇÕES AUXILIARES PARA O BACKEND
// ================================================================

export async function fetchAutenticado(endpoint, options = {}) {
  const token = getAccessToken();
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const resposta = await fetch(`${API_BACKEND_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || "Erro na requisição");
  }

  return resposta.json();
}

export const API_URL = API_BACKEND_URL;
