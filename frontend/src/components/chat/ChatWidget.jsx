import React, { useState, useEffect, useRef } from "react";
import { MessageSquare, Send, X, Bot, User, Trash2, Loader2 } from "lucide-react";
import { sendChatMessage } from "../../services/chat/chatService";

const STORAGE_KEY = "gipar_chat_history";

const INITIAL_MESSAGE = {
  id: "msg-initial",
  sender: "bot",
  text: "Olá! Sou o assistente do laboratório. Como posso ajudar com os equipamentos hoje?",
  time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
};

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch {
      // Fallback
    }
    return [INITIAL_MESSAGE];
  });

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Salva no localStorage sempre que as mensagens mudarem
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {
      // Ignora falhas de cota
    }
  }, [messages]);

  // Rola até o final das mensagens
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, isLoading]);

  // Foco no input ao abrir
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 150);
    }
  }, [isOpen]);

  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();
    const trimmed = inputMessage.trim();
    if (!trimmed || isLoading) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: "user",
      text: trimmed,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage("");
    setIsLoading(true);

    try {
      const data = await sendChatMessage(trimmed);
      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: "bot",
        text: data.reply || "Resposta recebida.",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        matched_item: data.matched_item,
        options: data.options,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err-${Date.now()}`,
        sender: "bot",
        text: "Desculpe, ocorreu uma instabilidade na conexão com o assistente. Tente novamente em instantes.",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([INITIAL_MESSAGE]);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignora
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      {/* Botão Flutuante (quando fechado) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group relative flex items-center justify-center w-14 h-14 bg-gradient-to-tr from-blue-600 to-indigo-600 text-white rounded-full shadow-lg hover:shadow-2xl hover:scale-105 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-300"
          title="Assistente do Laboratório"
          aria-label="Abrir chat do laboratório"
        >
          <Bot className="w-7 h-7 transition-transform group-hover:rotate-12 duration-200" />
          <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-white"></span>
          </span>
        </button>
      )}

      {/* Janela do Chat (quando aberta) */}
      {isOpen && (
        <div className="flex flex-col w-[380px] max-w-[calc(100vw-2rem)] h-[520px] max-h-[calc(100vh-4rem)] bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden transition-all duration-300 animate-in fade-in slide-in-from-bottom-5">
          {/* Cabeçalho */}
          <div className="flex items-center justify-between px-4 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-sm">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center w-9 h-9 bg-white/10 rounded-full border border-white/20">
                <Bot className="w-5 h-5 text-white" />
                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-400 border-2 border-indigo-700 rounded-full"></span>
              </div>
              <div>
                <h3 className="font-semibold text-sm leading-tight">Assistente do Laboratório</h3>
                <p className="text-[11px] text-blue-100 flex items-center gap-1">
                  <span>GIPAR</span> • <span className="text-emerald-300 font-medium">Disponível</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1 text-white/80">
              <button
                onClick={handleClearHistory}
                className="p-1.5 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                title="Limpar histórico da conversa"
                aria-label="Limpar conversa"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                title="Fechar janela"
                aria-label="Fechar chat"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Área de Mensagens */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50 text-slate-800 text-sm">
            {messages.map((msg) => {
              const isUser = msg.sender === "user";
              return (
                <div
                  key={msg.id}
                  className={`flex items-end gap-2 ${isUser ? "justify-end" : "justify-start"}`}
                >
                  {!isUser && (
                    <div className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-100 text-blue-600 shrink-0">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`relative max-w-[82%] px-3.5 py-2.5 rounded-2xl shadow-sm leading-relaxed ${
                      isUser
                        ? "bg-blue-600 text-white rounded-br-sm"
                        : "bg-white text-slate-800 border border-slate-200/80 rounded-bl-sm"
                    }`}
                  >
                    <div className="whitespace-pre-wrap font-normal break-words">
                      {msg.text}
                    </div>
                    <span
                      className={`block text-[10px] mt-1 text-right ${
                        isUser ? "text-blue-100" : "text-slate-400"
                      }`}
                    >
                      {msg.time}
                    </span>
                  </div>

                  {isUser && (
                    <div className="flex items-center justify-center w-7 h-7 rounded-full bg-slate-200 text-slate-600 shrink-0">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })}

            {/* Indicador de Digitação */}
            {isLoading && (
              <div className="flex items-center gap-2">
                <div className="flex items-center justify-center w-7 h-7 rounded-full bg-blue-100 text-blue-600 shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-white border border-slate-200 px-3.5 py-2.5 rounded-2xl rounded-bl-sm shadow-sm flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                  <span className="w-1.5 h-1.5 bg-blue-600 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                  <span className="text-xs text-slate-400 ml-1">Consultando acervo...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Campo de Entrada de Mensagem */}
          <form
            onSubmit={handleSendMessage}
            className="p-3 bg-white border-t border-slate-200 flex items-center gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Pergunte sobre peças, horários ou regras..."
              disabled={isLoading}
              className="flex-1 px-3.5 py-2 text-sm bg-slate-100 border border-transparent rounded-xl focus:bg-white focus:border-blue-500 focus:outline-none transition-all disabled:opacity-60 text-slate-800 placeholder-slate-400"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              className="flex items-center justify-center w-9 h-9 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-xl transition-all shadow-sm shrink-0 focus:outline-none focus:ring-2 focus:ring-blue-400"
              title="Enviar mensagem"
              aria-label="Enviar"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
