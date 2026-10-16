import { obterAvatar } from "../../../constants/avatares.constants";

function obterInicial(nome = "") {
  return nome.trim().charAt(0).toUpperCase() || "?";
}
export default function Avatar({ nome, avatar, tamanho = 36, className = "" }) {
  const tamanhoPx = typeof tamanho === "number" ? `${tamanho}px` : tamanho;
  const avatarSelecionado = obterAvatar(avatar);

  return (
    <span
      className={`inline-flex shrink-0 items-center justify-center rounded-full font-semibold text-white ${className}`}
      style={{
        width: tamanhoPx,
        height: tamanhoPx,
        fontSize: typeof tamanho === "number" ? tamanho * 0.45 : "1rem",
        backgroundColor: avatarSelecionado?.fundo || "#2563EB",
      }}
      aria-label={avatarSelecionado?.nome || `Avatar de ${nome}`}
    >
      {avatarSelecionado?.simbolo || obterInicial(nome)}
    </span>
  );
}
