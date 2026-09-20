# ==========================================
# Estágio 1: Build da aplicação React
# ==========================================
FROM node:22-alpine AS builder

WORKDIR /app

# Copia dependências do package.json
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o código fonte do frontend
COPY . .

# Argumento para URL da API em tempo de build (padrão: /api para usar o proxy reverso do Nginx)
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Executa o build de produção com Vite
RUN npm run build

# ==========================================
# Estágio 2: Servidor Web Nginx
# ==========================================
FROM nginx:alpine

# Remove página padrão do Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copia os arquivos compilados do estágio anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia a configuração customizada do Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
