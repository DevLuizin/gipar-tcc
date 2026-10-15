# ADR-006: Arquitetura do Sistema de Temas e Autoatendimento de Perfil

**Status:** Aprovada  
**Data:** 2026-10-15  
**Decisores:** Luiz  
**Requisitos Relacionados:** REQ-003  

---

## 1. Contexto do Problema

O GIPAR já apresenta os itens "Meu Perfil" e "Configurações" no menu do usuário, mas as rotas ainda não existem. O usuário não possui autoatendimento para atualizar dados cadastrais ou senha, e o sistema não invalida JWTs anteriores quando uma credencial muda.

A interface utiliza o Padrão Institucional GIPAR, que deve ser preservado. O sistema também necessita de temas opcionais persistidos entre dispositivos. Foi necessário decidir os contratos de perfil, a forma de personalização do avatar, a estratégia de temas, a persistência e a invalidação simples de tokens.

## 2. Decisão Adotada

### 2.1 Separação de rotas

Serão criadas duas páginas protegidas por autenticação:

- `/perfil`: dados pessoais, avatar predefinido e credenciais;
- `/configuracoes`: temas visuais e informações do sistema.

### 2.2 Contratos específicos de API

O modelo genérico `Usuario` não será reutilizado no autoatendimento. Serão criados DTOs Pydantic independentes para:

- resposta do perfil autenticado;
- atualização de nome, nome de exibição, e-mail e avatar;
- alteração de senha;
- atualização do tema.

Os DTOs de autoatendimento não aceitarão `tipo_usuario`, `ativo` ou hash de senha. O ID do usuário será obtido exclusivamente do JWT validado.

### 2.3 Avatar predefinido

O usuário poderá escolher somente entre avatares locais, predefinidos e versionados no frontend. O banco armazenará uma chave curta na coluna `avatar`.

Não haverá upload de fotografia, armazenamento Base64, `multipart/form-data` ou coluna de avatar na listagem administrativa de usuários. Na ausência de escolha, permanece o fallback com a inicial do nome.

### 2.4 Motor de temas

Serão suportados quatro temas:

1. Padrão Institucional GIPAR;
2. Dark Mode;
3. Ocean Blue;
4. Alto Contraste.

O Padrão Institucional GIPAR reproduzirá a aparência já existente, sem redesenho. A implementação usará tokens semânticos em CSS e `data-theme` no elemento raiz. Os componentes serão migrados para os tokens antes da aplicação das três paletas alternativas.

O MySQL será a fonte oficial da preferência para permitir continuidade entre dispositivos. O `localStorage` usará chave por usuário apenas como cache de inicialização. Depois da autenticação, o valor do banco prevalece e reconcilia o cache.

Conformidade com WCAG não será presumida pela escolha de cores: somente será declarada após medição objetiva dos contrastes nos quatro temas.

### 2.5 Segurança de e-mail, senha e sessão

- Alterar o e-mail exige a senha atual porque o e-mail é a credencial utilizada no login;
- O novo e-mail deve possuir formato válido e ser único;
- A nova senha deve ter no mínimo 8 caracteres, com pelo menos uma letra e um número, e confirmação idêntica;
- E-mail e senha são validados com o hash `argon2` existente;
- O JWT passa a carregar `token_version`;
- O backend compara a versão do token com `usuario.token_version` durante a autenticação;
- Alterar e-mail ou senha incrementa `token_version`, invalidando todos os JWTs anteriores do usuário;
- Após sucesso, o frontend encerra a sessão local, explica a necessidade de reautenticação e redireciona para `/login`.

Essa abordagem foi escolhida por ser persistente, compatível com múltiplas instâncias e mais simples que manter uma blacklist individual de tokens.

### 2.6 Evolução do banco

O `docker/mysql/init.sql` será atualizado para instalações novas. Bancos existentes receberão uma migration SQL versionada em `docker/mysql/migrations/`, aplicada e validada explicitamente contra o MySQL containerizado.

## 3. Alternativas Consideradas

### Alternativa A: página única com abas

- **Vantagem:** menos rotas.
- **Desvantagem:** mistura identidade e preferências e não acompanha os dois itens já existentes no menu.
- **Decisão:** rejeitada.

### Alternativa B: upload de fotografia ou Base64 no MySQL

- **Vantagem:** personalização livre.
- **Desvantagens:** exige validação de arquivo, limite de tamanho, armazenamento, limpeza, proteção contra conteúdo inválido e maior tráfego.
- **Decisão:** rejeitada em favor de avatares predefinidos.

### Alternativa C: somente Padrão e Dark Mode

- **Vantagem:** menor esforço inicial.
- **Desvantagem:** não atende ao catálogo de quatro opções aprovado para o requisito.
- **Decisão:** rejeitada; os três temas alternativos serão entregues juntos, após a criação dos tokens semânticos.

### Alternativa D: persistência somente em `localStorage`

- **Vantagem:** não altera o banco.
- **Desvantagem:** a preferência não acompanha o usuário em outros navegadores ou dispositivos.
- **Decisão:** rejeitada.

### Alternativa E: logout somente no navegador

- **Vantagem:** não altera a validação JWT.
- **Desvantagem:** cópias anteriores do token permanecem válidas até a expiração.
- **Decisão:** rejeitada em favor de `token_version`.

## 4. Consequências e Impactos

### Consequências positivas

- Contratos de perfil não expõem senha nem permitem alteração de privilégios;
- Alterações de credencial invalidam sessões anteriores em todos os dispositivos;
- A solução de avatar permanece simples e sem armazenamento de arquivos enviados pelo usuário;
- O tema acompanha o usuário entre dispositivos;
- O visual institucional atual permanece como padrão e fallback;
- Migrations versionadas cobrem bancos existentes sem depender da recriação do volume.

### Consequências negativas e trade-offs

- A validação de cada requisição autenticada passa a consultar usuário ativo e `token_version` no banco;
- A adoção real de temas exige substituir gradualmente cores fixas por tokens semânticos em vários componentes;
- Os quatro temas aumentam a matriz de testes visuais e responsivos;
- A migration precisa ser aplicada explicitamente nos ambientes que já possuem volume MySQL.

## 5. Fora do Escopo

- Upload de fotografias;
- Avatar na tabela administrativa de usuários;
- Preferências, leitura ou persistência de notificações (`RN-007`);
- Correção de segurança de `/listar_usuarios`, registrada como pendência ao final do plano de implementação.

## 6. Rastreabilidade e Conformidade

- **Requisito:** REQ-003
- **Regras de negócio:** RN-006, RN-013, RN-014
- **Plano de implementação:** `docs/plano-implementacao-perfil-configuracoes.md`
- **Banco:** `docker/mysql/init.sql` e migration futura em `docker/mysql/migrations/`
- **Backend previsto:** DTOs de perfil, `api/routers/usuarios.py`, `gerenciador_db/usuario.py` e validação JWT
- **Frontend previsto:** `ThemeContext`, páginas de perfil/configurações, `AuthContext`, `MenuUsuario`, `Avatar`, rotas e tokens CSS
- **Validação:** testes de contrato, autorização, revogação, migração, responsividade e contraste medido
