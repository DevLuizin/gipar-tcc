// ================================================================
// chatService.js — Cliente de API para o Chatbot Inteligente GIPAR
// ================================================================

import { API_BACKEND_URL, getAuthHeaders } from "../api.config";

/**
 * Envia uma mensagem do usuário para o backend FastAPI do Chatbot.
 * @param {string} message - Texto digitado pelo usuário.
 * @returns {Promise<{reply: string, intent: string, confidence: number, matched_item: object|null, options: array|null}>}
 */
export async function sendChatMessage(message) {
  // Se VITE_API_URL for "/api", a URL final será "/api/chat"
  // Se for "http://localhost:8000", chamará "/chat" ou "/api/chat"
  const baseUrl = API_BACKEND_URL.endsWith("/") ? API_BACKEND_URL.slice(0, -1) : API_BACKEND_URL;
  const endpoint = baseUrl.endsWith("/api") ? `${baseUrl}/chat` : `${baseUrl}/api/chat`;

  const response = await fetch(endpoint, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Falha na comunicação com o assistente do laboratório.");
  }

  return await response.json();
}
