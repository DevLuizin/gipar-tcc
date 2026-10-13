import LayoutUsuario from "../../layouts/usuario/LayoutUsuario.jsx";
import Pesquisa from "../../components/Pesquisa/Pesquisa";
import TabulatorGipar from "../../components/tabulatorGipar";
import normalizarTexto from "../../utils/normalizarTexto";
import { useState, useEffect, useCallback, useMemo } from "react";
import { buscarEquipamentos } from "../../services/Equipamentos/equipamentos.service";

const STATUS_EQUIVALENTES = {
    disponivel: ["disponivel"],
    emprestado: ["emprestado", "em uso"],
    "em manutencao": ["em manutencao", "manutencao"],
    inativo: ["inativo"],
};

export default function Equipamentos() {
    const [termo, setTermo] = useState("");
    const [categoria, setCategoria] = useState("");
    const [filtroStatus, setFiltroStatus] = useState("");
    const [equipamentos, setEquipamentos] = useState([]);

    const colunas = useMemo(() => [
        {
            titulo: "Nome",
            chave: "nome",
            campoSecundario: "descricao",
            prioridadeResponsiva: 0,
        },
        {
            titulo: "Patrimônio",
            chave: "codigo_patrimonio",
            chaveAlternativa: "patrimonio",
            prioridadeResponsiva: 2,
        },
        {
            titulo: "Categoria",
            chave: "nome_categoria",
            chaveAlternativa: "categoria",
            prioridadeResponsiva: 3,
        },
        { titulo: "Status", chave: "status", tipo: "status", prioridadeResponsiva: 1 },
    ], []);

    const carregarEquipamentos = useCallback(async () => {
        try {
            const dados = await buscarEquipamentos();
            setEquipamentos(dados);
        } catch (erro) {
            console.error(erro);
        }
    }, []);

    useEffect(() => {
        carregarEquipamentos();
    }, [carregarEquipamentos]);

    const equipamentosFiltrados = useMemo(() => {
        const termoNormalizado = normalizarTexto(termo);

        return equipamentos.filter((equipamento) => {
            // Puxando o codigo_patrimonio real do backend
            const patrimonio = normalizarTexto(equipamento.codigo_patrimonio || equipamento.patrimonio);
            const nomeEq = normalizarTexto(equipamento.nome);

            const bateTexto = nomeEq.includes(termoNormalizado) || patrimonio.includes(termoNormalizado);

            const cat = equipamento.nome_categoria || equipamento.categoria || "";
            const bateCategoria = categoria === "" || cat === categoria;

            const statusEquipamento = normalizarTexto(equipamento.status).replaceAll("_", " ");
            const statusFiltro = normalizarTexto(filtroStatus);
            const bateStatus = filtroStatus === "" ||
                STATUS_EQUIVALENTES[statusFiltro]?.includes(statusEquipamento);

            return bateTexto && bateCategoria && bateStatus;
        });
    }, [categoria, equipamentos, filtroStatus, termo]);

    return (
        <section className="h-screen w-full flex flex-row">
            <LayoutUsuario 
                tipoUsuario="estagiario" 
                titulo="Equipamentos" 
                cargo="Estagiário"       
                nome="Paulo Victor"
                notificacoes={[]}        
                onMarcarNotificacaoLida={() => console.log("Notificação marcada como lida")}
                onMarcarTodasNotificacoesLidas={() => console.log("Todas as notificações marcadas como lidas")}
                onLogout={() => console.log("logout")}
            >
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
                            listaStatus={["Disponível", "Emprestado", "Em Manutenção", "Inativo"]}
                            placeholderTexto="Buscar por nome ou patrimônio..."
                            placeholderCategoria="Todas as Categorias"
                            placeholderStatus="Todos os Status"
                        />
                    </div>

                    <div className="w-full">
                        <TabulatorGipar
                            colunas={colunas}
                            dados={equipamentosFiltrados} 
                        />
                    </div>
                </main>
            </LayoutUsuario>
        </section>  
    );
}
