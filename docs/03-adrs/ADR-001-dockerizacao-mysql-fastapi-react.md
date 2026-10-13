# ADR-001: Dockerização do Ecossistema GIPAR com MySQL, FastAPI e React/Nginx

**Status:** Aprovada  
**Data:** 2026-10-04  
**Decisores:** Luiz, Crescencio   
**Requisitos Relacionados:** REQ-001, REQ-002, REQ-003  

---

## 1. Contexto do Problema
O GIPAR é composto por três camadas distintas: banco de dados MySQL, backend FastAPI (Python) e frontend SPA React (Vite). A execução do sistema dependia de configurações locais manuais de ambiente em cada máquina de desenvolvedor (versões de Python, Node e instâncias locais de MySQL), gerando inconsistências de dependências, erros de CORS e dificuldades para deploy em servidores de homologação e produção.

## 2. Decisão Adotada
Implementar a containerização completa da aplicação utilizando Docker e Docker Compose, organizada em três serviços integrados em uma rede interna (`gipar-network`):
1. **`gipar-mysql`:** Banco de dados MySQL 8.0 com inicialização automática de schema e carga através do script `docker/mysql/init.sql`. Porta 3306 isolada para a rede interna, sendo exposta no host apenas via `docker-compose.override.yml` para desenvolvimento.
2. **`gipar-backend`:** Container Python 3.11-slim executando FastAPI com Uvicorn, conectado ao MySQL pelo hostname de serviço `gipar-mysql`.
3. **`gipar-frontend`:** Build estático multi-stage do React 19 servido pelo Nginx Alpine, configurado com proxy reverso em `/api/` para encaminhar chamadas da API diretamente ao container do backend na porta 8000.

## 3. Alternativas Consideradas
### Alternativa A: Manter Execução Manual Local (Python venv + Node local + MySQL nativo)
- **Vantagens:** Não requer Docker instalado na máquina local.
- **Desvantagens:** Alto índice de falhas de ambiente entre desenvolvedores, complexidade no deploy em servidor e ausência de reprodutibilidade.
- **Motivo do descarte:** Incompatível com as boas práticas de engenharia de software e deploy institucional.

### Alternativa B: Backend servindo os arquivos estáticos do Frontend no mesmo container
- **Vantagens:** Um container a menos.
- **Desvantagens:** Acoplamento desnecessário, perda de performance no tráfego estático e sobrecarga desnecessária na CPU do Python.
- **Motivo do descarte:** A separação de responsabilidades com Nginx otimiza entrega de assets e segurança.

## 4. Consequências e Impactos
### Consequências Positivas
- Subida do ambiente completo com um único comando: `docker compose up -d --build`.
- Eliminação completa de problemas de CORS em produção graças ao proxy reverso do Nginx.
- Isolamento seguro da porta do banco de dados MySQL.
- Preservação persistente dos dados do banco via volume nomeado `mysql_data`.

### Consequências Negativas / Trade-offs
- Exige Docker Engine instalado e configurado na máquina de desenvolvimento e no servidor.
- Maior consumo de memória RAM inicial se comparado à execução de processos isolados.

## 5. Rastreabilidade e Conformidade
- **Implementação:** [`docker-compose.yml`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/docker-compose.yml), [`docker-compose.override.yml`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/docker-compose.override.yml), [`frontend/nginx.conf`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/frontend/nginx.conf), [`docker/mysql/init.sql`](file:///c:/Users/Luiz/Documents/BSI/TCC/Projeto/cepedi-capacita04-grupo3/docker/mysql/init.sql).
- **Diagramas:** `docs/02-diagramas/arquitetura/C4-gipar-containers.md`.
