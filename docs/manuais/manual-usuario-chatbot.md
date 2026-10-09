---
titulo: "Manual do Usuário — Chatbot GIPAR"
versao: "1.0"
data_revisao: "2026-10-09"
modulo: "Chatbot"
publico: "Alunos, professores, bolsistas, técnicos e administradores"
requisito: "REQ-001"
status: "Manual baseado na implementação atual"
---

# Manual do Usuário — Chatbot GIPAR

## 1. Apresentação

O **Chatbot GIPAR** é o assistente virtual do laboratório. Ele permite fazer perguntas em linguagem natural sobre o acervo e sobre o funcionamento do laboratório, sem que o usuário precise procurar manualmente em tabelas ou menus.

O assistente pode ajudar com:

- disponibilidade de equipamentos e componentes;
- quantidade disponível de um item;
- localização indicada para um item;
- regras e prazos de empréstimo;
- horário de funcionamento do laboratório;
- exemplos do que pode ser consultado.

> [!IMPORTANT]
> O chatbot é um canal de **consulta**. Ele não realiza reservas, empréstimos, devoluções, cadastros ou alterações no sistema.

## 2. Quem pode utilizar

O chatbot pode ser utilizado pelos usuários que acessam o sistema GIPAR, incluindo:

- alunos;
- professores;
- bolsistas;
- técnicos de laboratório;
- administradores.

As respostas são voltadas principalmente às dúvidas comuns de quem utiliza equipamentos e componentes do laboratório.

## 3. Como abrir o chatbot

1. Acesse o sistema GIPAR pelo navegador.
2. Localize o botão flutuante do assistente no canto inferior direito da tela.
3. Clique no botão com o ícone de robô.
4. A janela **Assistente do Laboratório** será aberta.
5. O cursor será posicionado no campo de mensagem.

Ao abrir o chatbot pela primeira vez, será exibida a saudação:

> Olá! Sou o assistente do laboratório. Como posso ajudar com os equipamentos hoje?

## 4. Elementos da janela

| Elemento | Função |
| :--- | :--- |
| Cabeçalho | Identifica o Assistente do Laboratório e apresenta o status visual do widget. |
| Área de mensagens | Exibe as perguntas do usuário e as respostas do assistente. |
| Campo de texto | Permite escrever uma pergunta. |
| Botão de envio | Envia a mensagem digitada. |
| Indicador “Consultando acervo...” | Informa que a pergunta está sendo processada. |
| Botão de lixeira | Apaga o histórico da conversa armazenado no navegador. |
| Botão `X` | Fecha a janela sem apagar o histórico. |

## 5. Como enviar uma pergunta

1. Clique no campo **“Pergunte sobre peças, horários ou regras...”**.
2. Digite uma pergunta curta e direta.
3. Pressione `Enter` ou clique no botão de envio.
4. Aguarde enquanto a mensagem **“Consultando acervo...”** estiver visível.
5. Leia a resposta apresentada pelo assistente.

Enquanto uma pergunta estiver sendo processada, o campo e o botão de envio permanecerão temporariamente desabilitados.

## 6. O que perguntar

### 6.1. Disponibilidade de item

Informe o nome do equipamento ou componente desejado.

Exemplos:

- “Tem Arduino Uno disponível?”
- “Tem multímetro livre?”
- “Tem cabo mini USB?”
- “Tem protoboard disponível?”
- “Tem sensor ultrassom?”
- “Está disponível o Arduino Mega 2560?”

Quando o item estiver disponível, a resposta informará seu nome e a quantidade registrada no catálogo.

Exemplo de resposta:

> Sim! Temos 6 unidades de 'Arduino Uno' disponíveis no laboratório.

> [!TIP]
> Para obter um resultado mais preciso, informe o modelo ou a variação do item, como “Arduino Uno”, “jumper macho x macho” ou “cabo mini USB”.

### 6.2. Quantidade disponível

Também é possível perguntar diretamente pela quantidade.

Exemplos:

- “Quantos jumpers macho x macho temos?”
- “Quantos Arduinos Uno estão disponíveis?”
- “Tem mais de um multímetro livre?”

A resposta utiliza a quantidade associada ao item identificado no catálogo do chatbot.

### 6.3. Termos genéricos e escolha entre opções

Algumas palavras podem representar vários itens. Por exemplo:

- “arduino”;
- “jumper”;
- “cabo”;
- “sensor”.

Quando forem encontradas várias opções, o assistente poderá listar até cinco correspondências com suas quantidades e perguntar qual delas o usuário deseja.

Exemplo:

> Temos as seguintes opções de 'jumper' no acervo:
>
> - Jumper fêmea x fêmea: 20 unidades disponíveis
> - Jumper macho x macho: 30 unidades disponíveis
> - Jumper macho x fêmea: 15 unidades disponíveis
>
> Qual dessas opções você precisa?

Depois da lista, envie uma nova mensagem com o nome mais específico, por exemplo:

> Jumper macho x fêmea

As quantidades mostradas acima são apenas ilustrativas. O chatbot utiliza os valores presentes no catálogo carregado pelo sistema.

### 6.4. Localização de item

Exemplos:

- “Onde fica a estação de solda?”
- “Onde está o osciloscópio?”
- “Em qual armário fica o multímetro?”
- “Onde encontro a Ponte H?”

No funcionamento atual, a resposta de localização utiliza a indicação padrão **“Armário Geral do Laboratório”**, juntamente com a quantidade disponível. Caso seja necessário localizar uma gaveta, bancada ou armário específico, confirme a posição com o técnico responsável.

### 6.5. Regras de empréstimo

Exemplos:

- “Como funciona o empréstimo?”
- “Posso levar o multímetro para casa?”
- “Qual o prazo de devolução?”
- “Preciso de autorização do professor?”
- “Aluno pode levar kit de robótica para fora?”
- “O que acontece se eu atrasar a entrega?”

As regras atualmente configuradas são:

#### Materiais de bancada

- componentes e ferramentas de bancada devem ser retirados mediante cadastro;
- a devolução deve ocorrer no mesmo dia;
- o horário limite configurado para devolução é `17h45`.

#### Materiais para TCC ou projetos de extensão

- kits de desenvolvimento, como Arduino, ESP e sensores, podem ser emprestados por até sete dias;
- é necessário termo assinado;
- é necessária autorização do professor orientador.

#### Atrasos

- atrasos podem gerar suspensão temporária de novos empréstimos;
- a suspensão permanece até a regularização do item pendente.

> [!NOTE]
> As regras podem ser atualizadas pela coordenação. Em situações excepcionais ou quando houver divergência, prevalece a orientação do responsável pelo laboratório.

### 6.6. Horário de funcionamento

Exemplos:

- “Qual o horário do laboratório?”
- “Que horas o laboratório abre?”
- “Que horas o laboratório fecha?”
- “O laboratório abre no sábado?”
- “Até que horas posso devolver o material?”

O horário atualmente configurado é:

| Informação | Horário |
| :--- | :--- |
| Dias de funcionamento | Segunda a sexta-feira |
| Abertura | `08h00` |
| Fechamento | `18h00` |
| Limite indicado para devolução de material de bancada | `17h45` |

O chatbot apresenta o horário cadastrado. Ele não verifica feriados, suspensões extraordinárias ou alterações temporárias de expediente.

### 6.7. Ajuda

Caso não saiba como começar, envie uma destas mensagens:

- “Ajuda”
- “O que você faz?”
- “O que posso consultar aqui?”
- “Me dê exemplos de perguntas”

O assistente apresentará os tipos de consulta disponíveis.

### 6.8. Saudações e despedidas

O chatbot também reconhece mensagens simples, como:

- “Olá”;
- “Bom dia”;
- “Boa tarde”;
- “Obrigado”;
- “Valeu”;
- “Tchau”.

## 7. Como o nome do item é identificado

O chatbot normaliza o texto e procura nomes semelhantes no catálogo. Isso permite reconhecer alguns casos com:

- letras maiúsculas ou minúsculas diferentes;
- ausência de acentos;
- palavras adicionais na pergunta;
- pequenos erros de digitação;
- ordem diferente das palavras.

Exemplos de variações que podem ser compreendidas:

| Forma digitada | Possível identificação |
| :--- | :--- |
| `arduino uno` | Arduino Uno |
| `ardúino uno` | Arduino Uno |
| `multimetro` | Multímetro |
| `cabo usb mini` | Cabo Mini USB |

O limiar mínimo configurado para aceitar uma correspondência é de **75% de similaridade**. Mesmo assim, a identificação não é garantida para toda abreviação ou erro de digitação.

## 8. Como interpretar as respostas

### Item disponível

> Sim! Temos 5 unidades de 'Cabo Mini USB' disponíveis no laboratório.

Significa que o item foi identificado, está marcado como disponível e possui quantidade maior que zero no catálogo utilizado pelo chatbot.

### Item indisponível

> Item indisponível no momento.

Significa que o item foi identificado, mas seu estado ou quantidade não permite apresentá-lo como disponível.

### Item não cadastrado

> Item não cadastrado no acervo.

Significa que o chatbot não encontrou uma correspondência suficiente para a consulta. Antes de concluir que o laboratório não possui o item:

1. confira a grafia;
2. retire palavras desnecessárias;
3. tente o nome mais comum do item;
4. informe o modelo, se souber;
5. consulte o catálogo do sistema ou um técnico.

### Várias opções encontradas

O chatbot encontrou mais de um item semelhante. Digite novamente o nome completo de uma das opções apresentadas.

### Solicitação não compreendida

> Não compreendi sua solicitação. Posso te ajudar com a disponibilidade de componentes, regras de empréstimo ou horários do laboratório.

Reescreva a pergunta usando uma frase curta e um dos formatos apresentados neste manual.

### Instabilidade de conexão

> Desculpe, ocorreu uma instabilidade na conexão com o assistente. Tente novamente em instantes.

Essa mensagem indica que o navegador não conseguiu obter uma resposta válida do serviço do chatbot.

## 9. Histórico da conversa

O histórico é armazenado localmente no navegador utilizado.

- Fechar a janela pelo botão `X` não apaga a conversa.
- Reabrir o chatbot no mesmo navegador normalmente restaura as mensagens anteriores.
- O histórico não deve ser considerado um registro oficial de atendimento.
- O histórico não acompanha automaticamente o usuário para outro navegador ou dispositivo.
- Sair da conta não garante a remoção das mensagens armazenadas no navegador.

### Como apagar o histórico

1. Abra a janela do chatbot.
2. Clique no botão com o ícone de lixeira, no cabeçalho.
3. A conversa será apagada.
4. A mensagem inicial do assistente será exibida novamente.

## 10. Privacidade e uso responsável

Não envie pelo chatbot:

- senhas;
- tokens de acesso;
- documentos pessoais;
- dados bancários;
- informações médicas;
- informações pessoais de terceiros;
- dados sigilosos de projetos ou pesquisas.

Use o chatbot apenas para dúvidas relacionadas ao acervo e ao funcionamento do laboratório.

Como o histórico fica armazenado no navegador, apague a conversa ao terminar quando estiver utilizando um computador compartilhado.

## 11. Limitações atuais

O chatbot:

- não realiza empréstimos, reservas ou devoluções;
- não altera cadastros ou quantidades;
- não substitui a autorização do técnico ou professor responsável;
- não confirma automaticamente se o laboratório está aberto naquele exato momento;
- não considera feriados ou mudanças excepcionais de horário;
- não mantém contexto avançado de conversas longas;
- pode solicitar que o usuário escolha entre itens semelhantes;
- pode não reconhecer abreviações muito curtas ou erros de digitação extensos;
- utiliza um catálogo carregado a partir do banco de dados pelo serviço do chatbot;
- pode apresentar informação desatualizada até que o catálogo seja recarregado, caso um item tenha sido alterado recentemente;
- apresenta atualmente uma localização padrão, que deve ser confirmada com o técnico quando for necessária uma posição física específica.

## 12. Boas práticas para obter respostas melhores

- Faça uma pergunta por vez.
- Utilize frases curtas.
- Informe o nome do item.
- Acrescente o modelo ou tipo quando houver várias versões.
- Evite usar somente siglas, especialmente se forem ambíguas.
- Se receber várias opções, repita exatamente o nome desejado.
- Confirme informações críticas com o responsável pelo laboratório.

Exemplos recomendados:

```text
Tem Arduino Uno disponível?
Quantos jumpers macho x macho temos?
Onde fica a estação de solda?
Qual o prazo para devolver um kit Arduino?
Até que horas posso devolver material de bancada?
```

Exemplos pouco específicos:

```text
Tem isso?
Onde fica?
Quero uma placa.
Preciso de cabo.
Está aberto?
```

## 13. Solução de problemas

### O botão do chatbot não aparece

1. Atualize a página.
2. Verifique se a aplicação terminou de carregar.
3. Confirme se o navegador é compatível e está atualizado.
4. Tente sair e entrar novamente no sistema.
5. Se o problema continuar, informe ao suporte qual navegador e dispositivo foram utilizados.

### A mensagem não é enviada

- verifique se o campo contém algum texto;
- aguarde a conclusão da pergunta anterior;
- confirme a conexão com a rede;
- atualize a página e tente novamente.

### O chatbot informa instabilidade

1. Aguarde alguns instantes.
2. Tente enviar novamente.
3. Verifique se outras funções do GIPAR estão funcionando.
4. Se a falha persistir, informe ao suporte o horário aproximado e a pergunta enviada, sem incluir dados sensíveis.

### O item correto não foi encontrado

- utilize o nome completo;
- retire palavras que não fazem parte do nome;
- tente sem acentos;
- informe o modelo;
- consulte o catálogo visual do GIPAR;
- procure o técnico responsável.

### A quantidade parece incorreta

O catálogo do chatbot pode precisar ser recarregado após uma alteração recente. Confirme a disponibilidade no catálogo principal ou com o técnico antes da retirada.

### A conversa antiga ainda aparece

Clique no botão de lixeira. Em computador compartilhado, sempre apague o histórico antes de encerrar o uso.

## 14. Perguntas frequentes

### O chatbot pode reservar um equipamento?

Não. Ele apenas fornece informações. Utilize o fluxo apropriado do GIPAR ou procure o responsável pelo laboratório.

### O chatbot pode registrar uma devolução?

Não. A devolução precisa ser registrada pelo fluxo operacional autorizado.

### Preciso escrever comandos especiais?

Não. Escreva perguntas comuns em português.

### Posso escrever sem acentos?

Sim. O texto é normalizado antes da identificação da intenção e do item.

### O chatbot entende erros de digitação?

Ele tolera alguns erros leves. A correspondência de itens exige no mínimo 75% de similaridade.

### As respostas substituem a orientação do técnico?

Não. O técnico ou responsável pelo laboratório deve ser consultado em caso de dúvida, divergência ou situação excepcional.

### Fechar o chatbot apaga as mensagens?

Não. Utilize o botão de lixeira para limpar o histórico.

### O histórico fica salvo na minha conta?

Não. Ele é armazenado localmente no navegador e não deve ser tratado como histórico oficial vinculado à conta.

## 15. Guia rápido

1. Abra o chatbot no canto inferior direito.
2. Digite uma pergunta curta.
3. Informe o item e, se possível, o modelo.
4. Envie a mensagem.
5. Se aparecerem várias opções, digite o nome completo da desejada.
6. Confirme com o técnico informações críticas ou recentemente alteradas.
7. Em computador compartilhado, apague o histórico ao terminar.

## 16. Referências e rastreabilidade

Este manual foi elaborado com base em:

- `REQ-001` — Chatbot de Atendimento e Consulta de Patrimônio;
- `RN-008` — tolerância a erros e desambiguação;
- `RN-009` — respostas baseadas no acervo;
- `RN-010` — respostas padronizadas para indisponibilidade e ausência;
- `RN-011` — regras e horários parametrizados;
- `ADR-002` — arquitetura NLP do chatbot;
- implementação do componente `ChatWidget`;
- implementação atual dos serviços de NLP, catálogo e atendimento.

## 17. Controle do documento

| Campo | Valor |
| :--- | :--- |
| Documento | Manual do Usuário — Chatbot GIPAR |
| Versão | 1.0 |
| Revisão | 09/10/2026 |
| Módulo | Chatbot |
| Requisito principal | REQ-001 |
| Público | Usuários do sistema GIPAR |

