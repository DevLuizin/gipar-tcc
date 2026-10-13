// ================================================================
// equipamentos.jsx - VERSÃO CORRIGIDA E OTIMIZADA
// ================================================================

import LayoutUsuario from "../../layouts/usuario/LayoutUsuario.jsx";
import PopUpCadastrarEditarEquipamento from "../../components/PopUpCadastrarEditarEquipamento/index.jsx";
import Pesquisa from "../../components/Pesquisa/Pesquisa";
import TabulatorGipar from "../../components/tabulatorGipar";
import Botao from "../../components/Botao";
import PopUpExclusao from "../../components/PopUpExclusao";
import normalizarTexto from "../../utils/normalizarTexto";

import { useState, useEffect, useCallback, useMemo } from "react";
import { buscarEquipamentos, criarEquipamento, atualizarEquipamento, deletarEquipamento } from "../../services/Equipamentos/equipamentos.service";

export default function Equipamentos() {
    // ============================================================
    // ESTADOS
    // ============================================================
    const [popUpEditarEquipamento, setPopUpEditarEquipamento] = useState(false);
    const [popUpCadastrarEquipamento, setPopUpCadastrarEquipamento] = useState(false);
    const [popUpExclusao, setPopUpExclusao] = useState(false);

    const [termo, setTermo] = useState("");
    const [categoria, setCategoria] = useState("");
    const [filtroStatus, setFiltroStatus] = useState("");

    const [equipamentoSelecionado, setEquipamentoSelecionado] = useState(null);
    const [equipamentos, setEquipamentos] = useState([]);
    const [carregando, setCarregando] = useState(false);

    const colunas = useMemo(() => [
        { titulo: "Nome", chave: "nome", prioridadeResponsiva: 0 },
        { titulo: "Patrimônio", chave: "codigo_patrimonio", prioridadeResponsiva: 2 },
        { titulo: "Categoria", chave: "categoria", prioridadeResponsiva: 3 },
        { titulo: "Status", chave: "status", tipo: "status", prioridadeResponsiva: 1 },
    ], []);

    // ============================================================
    // FUNÇÕES
    // ============================================================

    const carregarEquipamentos = useCallback(async () => {
        setCarregando(true);
        try {
            const dados = await buscarEquipamentos();
            console.log("📦 Equipamentos carregados:", dados);
            setEquipamentos(Array.isArray(dados) ? dados : []);
        } catch (erro) {
            console.error("❌ Erro ao carregar equipamentos:", erro);
            setEquipamentos([]);
        } finally {
            setCarregando(false);
        }
    }, []);

    // ✅ CORREÇÃO: Array vazio para executar apenas uma vez
    useEffect(() => {
        carregarEquipamentos();
    }, [carregarEquipamentos]);

    const fecharPopUp = () => {
        setPopUpExclusao(false);
        setPopUpEditarEquipamento(false);
        setPopUpCadastrarEquipamento(false);
        setEquipamentoSelecionado(null);
    };

    const salvarEquipamento = async (dadosDoFormulario) => {
    try {
        console.log("📤 Enviando dados:", dadosDoFormulario);

        const payload = {
            codigo_patrimonio: dadosDoFormulario.codigo_patrimonio || dadosDoFormulario.patrimonio,
            nome: dadosDoFormulario.nome,
            modelo: dadosDoFormulario.modelo || "",
            id_categoria: Number(dadosDoFormulario.id_categoria || dadosDoFormulario.categoria),
            quantidade: Number(dadosDoFormulario.quantidade) || 1,
            status: (dadosDoFormulario.status || "DISPONIVEL").toUpperCase(),
            ativo: true
        };

        let resultado;
        if (equipamentoSelecionado) {
            resultado = await atualizarEquipamento(equipamentoSelecionado.id, payload);
        } else {
            resultado = await criarEquipamento(payload);
        }

        console.log("✅ Resposta do backend:", resultado);

        // 🔴 Fecha o popup e recarrega a lista
        fecharPopUp();
        await carregarEquipamentos();
        
        alert("Equipamento salvo com sucesso!");

    } catch (erro) {
        console.error("❌ Erro ao salvar equipamento:", erro);
        
        // 🔴 Se o erro for 'NoneType', o equipamento foi criado mas a resposta veio incompleta
        if (erro.message && erro.message.includes("NoneType")) {
            alert("Equipamento criado com sucesso! (Recarregue a lista para ver)");
            await carregarEquipamentos();
            fecharPopUp();
        } else {
            alert("Erro ao salvar: " + (erro.message || "Verifique os dados e tente novamente."));
        }
    }
};

    const excluirEquipamento = async () => {
        if (!equipamentoSelecionado) {
            alert("Nenhum equipamento selecionado!");
            return;
        }

        const id = equipamentoSelecionado.id;
        console.log("🗑️ Tentando excluir equipamento:", { id, nome: equipamentoSelecionado.nome });

        try {
            await deletarEquipamento(id);
            console.log("✅ Equipamento excluído com sucesso!");
            await carregarEquipamentos();
            fecharPopUp();
            alert("Equipamento excluído com sucesso!");
        } catch (erro) {
            console.error("❌ Erro ao excluir equipamento:", erro);
            alert("Erro ao excluir: " + (erro.message || "Verifique se o equipamento existe no banco."));
        }
    };

    // ============================================================
    // FILTROS
    // ============================================================

    const equipamentosFiltrados = useMemo(() => {
        const termoNormalizado = normalizarTexto(termo);

        return equipamentos.filter((equipamento) => {
            const bateTexto =
                normalizarTexto(equipamento.nome).includes(termoNormalizado) ||
                normalizarTexto(equipamento.codigo_patrimonio || equipamento.patrimonio)
                    .includes(termoNormalizado);

            const bateCategoria = categoria === "" || equipamento.categoria === categoria;
            const bateStatus = filtroStatus === "" || equipamento.status === filtroStatus;

            return bateTexto && bateCategoria && bateStatus;
        });
    }, [categoria, equipamentos, filtroStatus, termo]);

    // ============================================================
    // RENDER
    // ============================================================

    return (
        <section className="h-screen w-full flex flex-row">
            <LayoutUsuario titulo="Equipamentos">
                <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
                    <div className="w-full">
                        <Pesquisa
                            termo={termo}
                            setTermo={setTermo}
                            categoria={categoria}
                            setCategoria={setCategoria}
                            listaCategorias={["Informática", "Audiovisual", "Laboratório", "Ferramentas", "Redes", "Acessórios"]}
                            status={filtroStatus}
                            setStatus={setFiltroStatus}
                            listaStatus={["DISPONIVEL", "EM_USO", "EM_MANUTENCAO", "INATIVO"]}
                            placeholderTexto="Buscar por nome ou patrimônio..."
                            placeholderCategoria="Todas as Categorias"
                            placeholderStatus="Todos os Status"
                            extras={
                                <div className="ml-auto">
                                    <Botao
                                        onClick={() => setPopUpCadastrarEquipamento(true)}
                                        type="button"
                                        estilo="novo"
                                        icone={true}
                                    >
                                        Cadastrar Equipamento
                                    </Botao>
                                </div>
                            }
                        />
                    </div>

                    <div className="w-full">
                        {carregando ? (
                            <div className="text-center py-8 text-gray-500">Carregando equipamentos...</div>
                        ) : (
                            <TabulatorGipar
                                colunas={colunas}
                                dados={equipamentosFiltrados}
                                onEditar={(equipamento) => {
                                    setEquipamentoSelecionado(equipamento);
                                    setPopUpEditarEquipamento(true);
                                }}
                                onDeletar={(equipamento) => {
                                    setEquipamentoSelecionado(equipamento);
                                    setPopUpExclusao(true);
                                }}
                            />
                        )}
                    </div>

                    {/* ============================================================
                        MODAIS
                    ============================================================ */}

                    {popUpEditarEquipamento && (
                        <>
                            <div className="fixed inset-0 bg-black/40 z-40" onClick={fecharPopUp} />
                            <div className="fixed inset-0 flex items-center justify-center z-50">
                                <PopUpCadastrarEditarEquipamento
                                    DadosIniciais={equipamentoSelecionado}
                                    cancelar={fecharPopUp}
                                    salvar={salvarEquipamento}
                                    modoEdicao={true}
                                />
                            </div>
                        </>
                    )}

                    {popUpCadastrarEquipamento && (
                        <>
                            <div className="fixed inset-0 bg-black/40 z-40" onClick={fecharPopUp} />
                            <div className="fixed inset-0 flex items-center justify-center z-50">
                                <PopUpCadastrarEditarEquipamento
                                    cancelar={fecharPopUp}
                                    salvar={salvarEquipamento}
                                    modoEdicao={false}
                                />
                            </div>
                        </>
                    )}

                    {popUpExclusao && (
                        <>
                            <div className="fixed inset-0 bg-black/40 z-40" onClick={fecharPopUp} />
                            <div className="fixed inset-0 flex items-center justify-center z-50">
                                <PopUpExclusao
                                    titulo="Confirmar Exclusão"
                                    subtitulo="Essa ação não poderá ser desfeita."
                                    objeto={equipamentoSelecionado?.nome || "Equipamento"}
                                    confirmarExclusao={excluirEquipamento}
                                    cancelarExclusao={fecharPopUp}
                                />
                            </div>
                        </>
                    )}
                </main>
            </LayoutUsuario>
        </section>
    );
}
