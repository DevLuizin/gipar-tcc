import LayoutUsuario from "../../layouts/usuario/LayoutUsuario";
import PopUpCadastrarEditarUsuario from "../../components/PopUpCadastrarEditarUsuario";
import Pesquisa from "../../components/Pesquisa/Pesquisa";
import TabulatorGipar from "../../components/tabulatorGipar";
import Botao from "../../components/Botao";
import PopUpExclusao from "../../components/PopUpExclusao";
import normalizarTexto from "../../utils/normalizarTexto";

import { useState, useEffect, useCallback, useMemo } from "react";
import { buscarUsuarios, criarUsuario, atualizarUsuario, inativarUsuario, reativarUsuario } from "../../services/usuarios/usuarios.service";

export default function Usuario() {
    const [popUpEditarUsuario, setPopUpEditarUsuario] = useState(false);
    const [popUpCadastrarUsuario, setPopUpCadastrarUsuario] = useState(false);
    const [popUpExclusao, setPopUpExclusao] = useState(false);

    const [termo, setTermo] = useState("");
    const [filtroPerfil, setFiltroPerfil] = useState(""); 
    const [filtroStatus, setFiltroStatus] = useState(""); 

    const [usuarioSelecionado, setUsuarioSelecionado] = useState(null);
    const [usuarios, setUsuarios] = useState([]);

    const colunas = useMemo(() => [
        { titulo: "Nome", chave: "nome", prioridadeResponsiva: 0 },
        { titulo: "Email", chave: "email", prioridadeResponsiva: 3 },
        { titulo: "Perfil", chave: "tipo_usuario", prioridadeResponsiva: 2 },
        {
            titulo: "Status",
            chave: "ativo",
            tipo: "status",
            prioridadeResponsiva: 1,
            formatarValor: (valor) =>
                valor === true || valor === 1 || valor === "true" || valor === "1"
                    ? "Ativo"
                    : "Inativo",
        },
    ], []);

    const carregarUsuarios = useCallback(async () => {
        try {
            const dados = await buscarUsuarios();
            console.log("📦 Usuários carregados:", dados);
            setUsuarios(Array.isArray(dados) ? dados : []);
        } catch (erro) {
            console.error("❌ Erro ao carregar usuários:", erro);
            setUsuarios([]);
        }
    }, []);

    useEffect(() => {
        carregarUsuarios();
    }, [carregarUsuarios]);

    const salvarUsuario = async (dadosDoFormulario) => {
        try {
            if (usuarioSelecionado) {
                await atualizarUsuario(usuarioSelecionado.id, dadosDoFormulario);
            } else {
                await criarUsuario(dadosDoFormulario);
            }
            await carregarUsuarios();
            fecharPopUp();
            alert("✅ Usuário salvo com sucesso!");
        } catch (erro) {
            console.error("❌ Erro ao salvar usuário:", erro);
            alert("Erro ao salvar usuário: " + (erro.message || ""));
        }
    };

    const excluirUsuario = async () => {
        if (usuarioSelecionado) {
            try {
                console.log("🗑️ Inativando usuário:", usuarioSelecionado.id);
                await inativarUsuario(usuarioSelecionado.id);
                await carregarUsuarios();
                fecharPopUp();
                alert("✅ Usuário inativado com sucesso!");
            } catch (erro) {
                console.error("❌ Erro ao inativar usuário:", erro);
                alert("Erro ao inativar usuário: " + (erro.message || ""));
            }
        }
    };

    const reativarUsuarioHandler = async (usuario) => {
        try {
            console.log("🔄 Reativando usuário:", usuario.id);
            await reativarUsuario(usuario.id);
            await carregarUsuarios();
            alert("✅ Usuário reativado com sucesso!");
        } catch (erro) {
            console.error("❌ Erro ao reativar usuário:", erro);
            alert("Erro ao reativar usuário: " + (erro.message || ""));
        }
    };

    const fecharPopUp = () => {
        setPopUpExclusao(false);
        setPopUpEditarUsuario(false);
        setPopUpCadastrarUsuario(false);
        setUsuarioSelecionado(null);
    };

    const usuariosFiltrados = useMemo(() => {
        const termoNormalizado = normalizarTexto(termo);

        return usuarios.filter((usuario) => {
            const bateTexto =
                normalizarTexto(usuario.nome).includes(termoNormalizado) ||
                normalizarTexto(usuario.email).includes(termoNormalizado);

            const batePerfil = filtroPerfil === "" || usuario.tipo_usuario === filtroPerfil;

            // 🔴 CORREÇÃO: Quando filtroStatus está vazio, mostra TODOS
            let bateStatus = true;
            if (filtroStatus === "Ativo") {
                bateStatus = usuario.ativo === true || usuario.ativo === 1 || usuario.ativo === "true" || usuario.ativo === "1";
            } else if (filtroStatus === "Inativo") {
                bateStatus = usuario.ativo === false || usuario.ativo === 0 || usuario.ativo === "false" || usuario.ativo === "0";
            }

            return bateTexto && batePerfil && bateStatus;
        });
    }, [filtroPerfil, filtroStatus, termo, usuarios]);

    return (
        <section className="h-screen w-full flex flex-row">
            <LayoutUsuario titulo="Usuários">

                <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
                    <div className="w-full">
                        <Pesquisa
                            termo={termo}
                            setTermo={setTermo}
                            categoria={filtroPerfil}
                            setCategoria={setFiltroPerfil}
                            listaCategorias={["ADMINISTRADOR", "TECNICO", "COMUM"]}
                            placeholderCategoria="Todos os Perfis" 
                            status={filtroStatus}
                            setStatus={setFiltroStatus}
                            listaStatus={["Ativo", "Inativo"]}
                            placeholderStatus="Todos os Status"
                            placeholderTexto="Buscar por nome ou email..."
                            extras={
                                <div className="ml-auto">
                                    <Botao 
                                        onClick={() => setPopUpCadastrarUsuario(true)}
                                        type="button"
                                        estilo="novo"
                                        icone={true}
                                    >
                                        Cadastrar Usuário
                                    </Botao>
                                </div>
                            }
                        />
                    </div>

                    <div className="w-full">
                        <TabulatorGipar
                            colunas={colunas}
                            dados={usuariosFiltrados} 
                            onEditar={(usuario) => {
                                setUsuarioSelecionado(usuario);
                                setPopUpEditarUsuario(true);
                            }}
                            onDeletar={(usuario) => {
                                setUsuarioSelecionado(usuario);
                                setPopUpExclusao(true);
                            }}
                        />
                    </div>

                    {/* MODAIS */}
                    {popUpEditarUsuario && (
                        <>
                            <div className="fixed inset-0 bg-black/40 z-40" onClick={fecharPopUp} />
                            <div className="fixed inset-0 flex items-center justify-center z-50">
                                <PopUpCadastrarEditarUsuario DadosIniciais={usuarioSelecionado} cancelar={fecharPopUp} salvar={salvarUsuario} modoEdicao={true} />
                            </div>
                        </>
                    )}
                    {popUpCadastrarUsuario && (
                        <>
                            <div className="fixed inset-0 bg-black/40 z-40" onClick={fecharPopUp} />
                            <div className="fixed inset-0 flex items-center justify-center z-50">
                                <PopUpCadastrarEditarUsuario cancelar={fecharPopUp} salvar={salvarUsuario} modoEdicao={false} />
                            </div>
                        </>
                    )}
                    {popUpExclusao && (
                        <>
                            <div className="fixed inset-0 bg-black/40 z-40" onClick={fecharPopUp} />
                            <div className="fixed inset-0 flex items-center justify-center z-50">
                                <PopUpExclusao
                                    titulo="Confirmar Inativação"
                                    subtitulo="Deseja realmente inativar este usuário? Ele não poderá mais acessar o sistema, mas seus dados permanecerão no histórico."
                                    objeto={usuarioSelecionado ? usuarioSelecionado.nome : "Usuário"}
                                    confirmarExclusao={excluirUsuario}
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
