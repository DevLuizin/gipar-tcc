import { useEffect, useRef } from "react";
import { TabulatorFull as Tabulator } from "tabulator-tables";
import "tabulator-tables/dist/css/tabulator.min.css";
import "./TabulatorGipar.css";

const CLASSES_STATUS = {
  ativo: "bg-blue-100 text-blue-700",
  atrasado: "bg-red-100 text-red-700",
  concluido: "bg-green-100 text-green-700",
  cancelado: "bg-gray-100 text-gray-600",
  disponivel: "bg-green-100 text-green-700",
  emprestado: "bg-blue-100 text-blue-700",
  em_uso: "bg-blue-100 text-blue-700",
  manutencao: "bg-orange-100 text-orange-700",
  em_manutencao: "bg-amber-100 text-amber-700",
  inativo: "bg-gray-100 text-gray-500",
};

const ROTULOS_STATUS = {
  DISPONIVEL: "Disponível",
  EMPRESTADO: "Emprestado",
  EM_USO: "Em uso",
  MANUTENCAO: "Manutenção",
  EM_MANUTENCAO: "Em manutenção",
  INATIVO: "Inativo",
};

function normalizarStatus(status) {
  return String(status ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
}

function criarBadgeStatus(status) {
  const chave = normalizarStatus(status);
  const badge = document.createElement("span");
  const classeCor = CLASSES_STATUS[chave] ?? "bg-gray-100 text-gray-700";

  badge.className = `inline-flex shrink-0 whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium ${classeCor}`;
  badge.textContent = ROTULOS_STATUS[String(status)] ?? String(status ?? "—");

  return badge;
}

function criarConteudoComDetalhe(valor, detalhe) {
  const container = document.createElement("div");
  const principal = document.createElement("span");

  container.className = "flex flex-col";
  principal.className = "font-medium text-gray-900";
  principal.textContent = String(valor ?? "—");
  container.appendChild(principal);

  if (detalhe) {
    const secundario = document.createElement("span");
    secundario.className = "mt-0.5 text-xs text-gray-500";
    secundario.textContent = String(detalhe);
    container.appendChild(secundario);
  }

  return container;
}

function criarBotaoAcao(acao, titulo, caminhoIcone, classe) {
  const botao = document.createElement("button");

  botao.type = "button";
  botao.dataset.acao = acao;
  botao.title = titulo;
  botao.setAttribute("aria-label", titulo);
  botao.className = `rounded-md p-1 transition-colors ${classe}`;
  botao.innerHTML = `
    <svg aria-hidden="true" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${caminhoIcone}"></path>
    </svg>
  `;

  return botao;
}

function criarAcoes(temEdicao, temExclusao) {
  const container = document.createElement("div");
  container.className = "flex items-center justify-center gap-3";

  if (temEdicao) {
    container.appendChild(
      criarBotaoAcao(
        "editar",
        "Editar",
        "M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z",
        "text-gray-500 hover:bg-gray-100 hover:text-gray-900"
      )
    );
  }

  if (temExclusao) {
    container.appendChild(
      criarBotaoAcao(
        "deletar",
        "Excluir",
        "M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16",
        "text-red-500 hover:bg-red-50 hover:text-red-700"
      )
    );
  }

  return container;
}

function obterValor(coluna, valor, linha) {
  if (coluna.formatarValor) {
    return coluna.formatarValor(valor, linha);
  }

  if ((valor === null || valor === undefined || valor === "") && coluna.chaveAlternativa) {
    return linha[coluna.chaveAlternativa];
  }

  return valor;
}

function mapearColunas(colunas, callbacksRef) {
  const colunasMapeadas = colunas.map((coluna, indice) => ({
    title: coluna.titulo,
    field: coluna.chave,
    headerSort: coluna.ordenavel !== false,
    hozAlign: coluna.align === "right" ? "right" : "left",
    cssClass: coluna.className,
    minWidth: coluna.larguraMinima ?? 120,
    responsive: coluna.prioridadeResponsiva ?? (indice === 0 ? 0 : indice),
    formatter: (cell) => {
      const linha = cell.getRow().getData();
      const valor = obterValor(coluna, cell.getValue(), linha);

      if (coluna.tipo === "status") {
        return criarBadgeStatus(valor);
      }

      if (coluna.campoSecundario) {
        return criarConteudoComDetalhe(valor, linha[coluna.campoSecundario]);
      }

      return String(valor ?? "—");
    },
  }));

  const temEdicao = Boolean(callbacksRef.current.onEditar);
  const temExclusao = Boolean(callbacksRef.current.onDeletar);

  if (temEdicao || temExclusao) {
    colunasMapeadas.push({
      title: "Ações",
      field: "_acoes",
      headerSort: false,
      hozAlign: "center",
      minWidth: 100,
      responsive: 0,
      formatter: () => criarAcoes(temEdicao, temExclusao),
      cellClick: (event, cell) => {
        event.stopPropagation();
        const botao = event.target.closest("button[data-acao]");
        const linha = cell.getRow().getData();

        if (botao?.dataset.acao === "editar") {
          callbacksRef.current.onEditar?.(linha);
        }

        if (botao?.dataset.acao === "deletar") {
          callbacksRef.current.onDeletar?.(linha);
        }
      },
    });
  }

  return colunasMapeadas;
}

export default function TabulatorGipar({
  colunas,
  dados,
  onEditar,
  onDeletar,
}) {
  const elementoRef = useRef(null);
  const tabelaRef = useRef(null);
  const tabelaProntaRef = useRef(false);
  const callbacksRef = useRef({ onEditar, onDeletar });
  const dadosRef = useRef(dados);

  useEffect(() => {
    callbacksRef.current = { onEditar, onDeletar };
  }, [onEditar, onDeletar]);

  useEffect(() => {
    let cancelado = false;
    let tabela = null;
    let tabelaConstruida = false;

    const iniciarTabela = () => {
      if (cancelado || !elementoRef.current) return;

      tabela = new Tabulator(elementoRef.current, {
        data: dadosRef.current,
        columns: mapearColunas(colunas, callbacksRef),
        index: "id",
        layout: "fitColumns",
        placeholder: "Nenhum dado encontrado.",
        pagination: true,
        paginationMode: "local",
        paginationSize: 10,
        paginationSizeSelector: [10, 25, 50, 100],
        paginationButtonCount: 3,
        paginationCounter: "rows",
        responsiveLayout: "collapse",
        responsiveLayoutCollapseStartOpen: false,
        rowHeader: {
          formatter: "responsiveCollapse",
          width: 32,
          minWidth: 32,
          hozAlign: "center",
          resizable: false,
          headerSort: false,
        },
        locale: "pt-br",
        langs: {
          "pt-br": {
            pagination: {
              page_size: "Registros por página",
              first: "Primeira",
              first_title: "Primeira página",
              last: "Última",
              last_title: "Última página",
              prev: "Anterior",
              prev_title: "Página anterior",
              next: "Próxima",
              next_title: "Próxima página",
              counter: {
                showing: "Mostrando",
                of: "de",
                rows: "registros",
                pages: "páginas",
              },
            },
          },
        },
      });

      tabelaRef.current = tabela;

      tabela.on("tableBuilt", () => {
        tabelaConstruida = true;

        if (cancelado) {
          tabela.destroy();
          return;
        }

        tabelaProntaRef.current = true;

        tabela
          .replaceData(dadosRef.current)
          .then(() => tabela.setPage(1))
          .catch((erro) => console.error("Erro ao iniciar o Tabulator:", erro));
      });
    };

    const inicializacaoId = window.setTimeout(iniciarTabela, 0);

    return () => {
      cancelado = true;
      window.clearTimeout(inicializacaoId);

      if (tabela && tabelaConstruida) {
        tabela.destroy();
      }

      if (tabelaRef.current === tabela) {
        tabelaRef.current = null;
        tabelaProntaRef.current = false;
      }
    };
  }, [colunas]);

  useEffect(() => {
    dadosRef.current = dados;

    const tabela = tabelaRef.current;
    if (!tabela || !tabelaProntaRef.current) return;

    tabela
      .replaceData(dados)
      .then(() => {
        if (tabelaRef.current === tabela) {
          return tabela.setPage(1);
        }
      })
      .catch((erro) => console.error("Erro ao atualizar o Tabulator:", erro));
  }, [dados]);

  return <div ref={elementoRef} className="tabulator-gipar w-full" />;
}
