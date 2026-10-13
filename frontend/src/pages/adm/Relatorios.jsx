import { useCallback, useEffect, useMemo, useState } from "react";
import { Download, Eye, FileText } from "lucide-react";
import LayoutUsuario from "../../layouts/usuario/LayoutUsuario";
import CaixaSelecao from "../../components/CaixadeSelecao/CaixadeSelecao";
import DataSelecao from "../../components/DataSelecao/DataSelecao";
import Botao from "../../components/Botao";
import Pesquisa from "../../components/Pesquisa/Pesquisa";
import TabulatorGipar from "../../components/tabulatorGipar";
import EstadoVazio from "../../components/EstadoVazio/EstadoVazio";
import normalizarTexto from "../../utils/normalizarTexto";
import { TIPOS_RELATORIO } from "../../constants/relatorios.constants";
import {
  buscarDadosRelatorio,
  exportarRelatorio,
  obterConfigRelatorio,
  obterLabelTipoRelatorio,
} from "../../services/relatorios/relatorios.service";

export default function Relatorios() {
  const [tipoRelatorio, setTipoRelatorio] = useState("emprestimos");
  const [dataInicial, setDataInicial] = useState("");
  const [dataFinal, setDataFinal] = useState("");
  const [dadosPreview, setDadosPreview] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [exportando, setExportando] = useState("");
  const [erro, setErro] = useState("");
  const [previewGerada, setPreviewGerada] = useState(false);
  const [tipoRelatorioPreview, setTipoRelatorioPreview] = useState("emprestimos");
  const [termoPreview, setTermoPreview] = useState("");

  const configAtual = obterConfigRelatorio(tipoRelatorio);
  const labelRelatorio = obterLabelTipoRelatorio(tipoRelatorioPreview);
  const ocupado = carregando || Boolean(exportando);

  const colunasPreview = useMemo(() => {
    const config = obterConfigRelatorio(tipoRelatorioPreview);

    return config.colunas.map((coluna, indice) => ({
      ...coluna,
      tipo: coluna.chave === "status" ? "status" : undefined,
      prioridadeResponsiva:
        coluna.chave === "nome" || coluna.chave === "equipamento"
          ? 0
          : indice + 1,
    }));
  }, [tipoRelatorioPreview]);

  const dadosPreviewFiltrados = useMemo(() => {
    const termoNormalizado = normalizarTexto(termoPreview);
    if (!termoNormalizado) return dadosPreview;

    return dadosPreview.filter((registro) =>
      colunasPreview.some((coluna) =>
        normalizarTexto(registro[coluna.chave]).includes(termoNormalizado)
      )
    );
  }, [colunasPreview, dadosPreview, termoPreview]);

  const validarPeriodo = useCallback(() => {
    if (dataInicial && dataFinal && dataInicial > dataFinal) {
      setErro("A data inicial não pode ser posterior à data final.");
      return false;
    }
    return true;
  }, [dataInicial, dataFinal]);

  const gerarPreview = useCallback(async () => {
    if (!validarPeriodo()) return;

    setErro("");
    setCarregando(true);

    try {
      const dados = await buscarDadosRelatorio({
        tipo: tipoRelatorio,
        dataInicial,
        dataFinal,
      });
      setDadosPreview(dados);
      setTipoRelatorioPreview(tipoRelatorio);
      setPreviewGerada(true);
    } catch (error) {
      setDadosPreview([]);
      setPreviewGerada(false);
      setErro(
        error?.message ||
          "Não foi possível gerar a pré-visualização. Tente novamente."
      );
    } finally {
      setCarregando(false);
    }
  }, [tipoRelatorio, dataInicial, dataFinal, validarPeriodo]);

  const handleExportar = useCallback(
    async (formato) => {
      if (!validarPeriodo()) return;

      setErro("");
      setExportando(formato);

      try {
        await exportarRelatorio({
          tipo: tipoRelatorio,
          formato,
          dataInicial,
          dataFinal,
        });
      } catch (error) {
        setErro(
          error?.message ||
            `Não foi possível exportar o relatório em ${formato.toUpperCase()}.`
        );
      } finally {
        setExportando("");
      }
    },
    [tipoRelatorio, dataInicial, dataFinal, validarPeriodo]
  );

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    gerarPreview();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <LayoutUsuario titulo="Relatórios">
      <main className="flex-1 overflow-y-auto p-4 sm:p-6">
        <div className="mx-auto grid w-full max-w-7xl grid-cols-1 gap-4 xl:grid-cols-[minmax(280px,360px)_1fr] xl:gap-6">
          <article className="flex flex-col gap-5 rounded-xl border border-gray-200 bg-white p-4 shadow-sm sm:p-5">
            <header className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-[#1A6B74]" aria-hidden="true" />
              <h2 className="text-base font-semibold text-[#111827] sm:text-lg">
                Gerar Relatório
              </h2>
            </header>

            <CaixaSelecao
              label="Tipo de Relatório"
              id="tipo-relatorio"
              placeholder="Selecione o tipo"
              value={tipoRelatorio}
              onChange={(event) => setTipoRelatorio(event.target.value)}
              opcoes={TIPOS_RELATORIO}
            />

            <div className="flex flex-col gap-3">
              <span className="text-sm font-medium text-[#111827]">
                Período {configAtual.aceitaPeriodo ? "(opcional)" : "(não aplicável)"}
              </span>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <DataSelecao
                  id="data-inicial"
                  label="Data Inicial"
                  value={dataInicial}
                  onChange={(event) => setDataInicial(event.target.value)}
                  disabled={!configAtual.aceitaPeriodo || ocupado}
                />
                <DataSelecao
                  id="data-final"
                  label="Data Final"
                  value={dataFinal}
                  onChange={(event) => setDataFinal(event.target.value)}
                  disabled={!configAtual.aceitaPeriodo || ocupado}
                />
              </div>
              {!configAtual.aceitaPeriodo && (
                <p className="text-xs text-gray-500">
                  Este relatório não utiliza filtro de período.
                </p>
              )}
            </div>

            {erro && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                {erro}
              </div>
            )}

            <div className="flex flex-col gap-3">
              <div className="w-full [&_button]:w-full">
                <Botao estilo="novo" onClick={gerarPreview} disabled={ocupado}>
                  <Eye className="h-4 w-4" aria-hidden="true" />
                  {carregando ? "Carregando..." : "Pré-visualizar"}
                </Botao>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Botao
                  estilo="cancelar"
                  onClick={() => handleExportar("pdf")}
                  disabled={ocupado}
                >
                  <Download className="h-4 w-4" aria-hidden="true" />
                  {exportando === "pdf" ? "Exportando..." : "PDF"}
                </Botao>
                <button
                  type="button"
                  onClick={() => handleExportar("csv")}
                  disabled={ocupado}
                  className="flex h-[38px] items-center justify-center gap-2 rounded-lg bg-orange-500 px-3 text-sm font-medium text-white transition-colors hover:bg-orange-600 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <Download className="h-4 w-4" aria-hidden="true" />
                  {exportando === "csv" ? "Exportando..." : "CSV"}
                </button>
              </div>
            </div>
          </article>

          <article className="flex min-h-[320px] flex-col gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm sm:p-5">
            <header>
              <h2 className="text-base font-semibold text-[#111827] sm:text-lg">
                Pré-visualização: {labelRelatorio}
              </h2>
            </header>

            {carregando && (
              <div className="flex flex-1 items-center justify-center py-12 text-sm text-gray-500">
                <div className="mr-3 h-6 w-6 animate-spin rounded-full border-2 border-[#1A6B74] border-t-transparent" />
                Gerando pré-visualização...
              </div>
            )}

            {!carregando && previewGerada && dadosPreview.length === 0 && (
              <EstadoVazio mensagem="Nenhum registro encontrado para os filtros selecionados." />
            )}

            {!carregando && previewGerada && dadosPreview.length > 0 && (
              <>
                <Pesquisa
                  termo={termoPreview}
                  setTermo={setTermoPreview}
                  placeholderTexto="Buscar na pré-visualização..."
                />
                <TabulatorGipar
                  colunas={colunasPreview}
                  dados={dadosPreviewFiltrados}
                />
              </>
            )}
          </article>
        </div>
      </main>
    </LayoutUsuario>
  );
}
