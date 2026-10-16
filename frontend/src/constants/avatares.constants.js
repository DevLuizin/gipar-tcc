export const AVATARES = [
  { id: "robo-azul", simbolo: "🤖", fundo: "#2563EB", nome: "Robô azul" },
  { id: "robo-verde", simbolo: "🤖", fundo: "#059669", nome: "Robô verde" },
  { id: "robo-roxo", simbolo: "🤖", fundo: "#7C3AED", nome: "Robô roxo" },
  { id: "circuito-azul", simbolo: "⚡", fundo: "#0369A1", nome: "Circuito azul" },
  { id: "circuito-verde", simbolo: "⚡", fundo: "#0F766E", nome: "Circuito verde" },
  { id: "circuito-laranja", simbolo: "⚡", fundo: "#C2410C", nome: "Circuito laranja" },
];

export function obterAvatar(id) {
  return AVATARES.find((avatar) => avatar.id === id) ?? null;
}
