# Sala de Espera - Sistema de Apresentação

Um sistema web simples para apresentar slides, planilhas, sites e imagens com controle de tempo de exibição, similar a uma tela de sala de espera, incluindo opção de feed RSS na parte inferior como nos jornais.

## Funcionalidades

### 📺 Apresentação de Conteúdo
- **Imagens**: Exibe imagens de URLs
- **Sites**: Exibe páginas web em iframe
- **Slides**: Exibe apresentações em PDF
- **Planilhas**: Exibe planilhas online

### ⏱️ Controle de Tempo
- Configuração personalizada de duração para cada item
- Reprodução automática com transição entre conteúdos
- Controles de play/pause e pular para próximo

### 📰 Feed RSS
- Exibição de notícias em formato marquee na parte inferior
- Suporte a feeds RSS externos
- Animação contínua estilo jornal

### ⚙️ Interface de Configuração
- Painel lateral para adicionar e gerenciar conteúdo
- Lista visual dos itens adicionados
- Configuração fácil de RSS

## Como Usar

### 1. Iniciando o Sistema
```bash
cd sala-espera
pnpm install
pnpm run dev --host
```

### 2. Adicionando Conteúdo
1. Clique no botão de configurações (⚙️) no canto superior direito
2. Na aba "Conteúdo":
   - Selecione o tipo de conteúdo (Imagem, Site, Slide, Planilha)
   - Insira a URL do conteúdo
   - Adicione um título (opcional)
   - Configure a duração em segundos
   - Clique em "Adicionar"

### 3. Configurando RSS
1. Na aba "RSS":
   - Insira a URL do feed RSS
   - Clique em "Carregar RSS"
   - As notícias aparecerão na parte inferior da tela

### 4. Controlando a Apresentação
- **Play/Pause**: Inicia ou pausa a apresentação automática
- **Pular**: Avança para o próximo item
- **Configurações**: Abre/fecha o painel de configuração

## Exemplos de URLs

### Imagens
```
https://picsum.photos/800/600
https://via.placeholder.com/800x600
```

### Sites
```
https://www.google.com
https://www.wikipedia.org
```

### Slides (PDF)
```
https://exemplo.com/apresentacao.pdf
```

### Planilhas
```
https://docs.google.com/spreadsheets/d/ID/edit#gid=0
```

### Feeds RSS
```
https://rss.cnn.com/rss/edition.rss
https://feeds.bbci.co.uk/news/rss.xml
```

## Tecnologias Utilizadas

- **React**: Framework frontend
- **Tailwind CSS**: Estilização
- **shadcn/ui**: Componentes de interface
- **rss-parser**: Parsing de feeds RSS
- **Vite**: Build tool

## Estrutura do Projeto

```
sala-espera/
├── src/
│   ├── components/ui/     # Componentes de interface
│   ├── App.jsx           # Componente principal
│   ├── App.css           # Estilos personalizados
│   └── main.jsx          # Ponto de entrada
├── public/               # Arquivos estáticos
├── package.json          # Dependências
└── README.md            # Este arquivo
```

## Recursos Avançados

### Responsividade
- Interface adaptável para desktop e mobile
- Painel de configurações otimizado para diferentes tamanhos de tela

### Tratamento de Erros
- Fallback para imagens que não carregam
- Dados de exemplo quando RSS falha
- Validação de URLs

### Animações
- Transições suaves entre conteúdos
- Animação marquee para RSS
- Estados de loading

## Personalização

### Modificando Estilos
Edite o arquivo `src/App.css` para personalizar:
- Cores do tema
- Velocidade da animação do RSS
- Layout dos componentes

### Adicionando Novos Tipos de Conteúdo
1. Adicione o novo tipo no enum do select
2. Implemente a renderização no método `renderContent()`
3. Adicione validação se necessário

## Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se as URLs estão acessíveis
3. Verifique o console do navegador para erros

## Licença

Este projeto é de uso livre para fins educacionais e comerciais.

