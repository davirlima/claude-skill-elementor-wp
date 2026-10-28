# Skill Elementor + WordPress para o Claude

Uma skill que ensina o Claude a trabalhar em sites **WordPress feitos com Elementor / Elementor Pro** no padrão de uma agência: páginas refeitas com containers e **widgets oficiais**, header e rodapé no **Theme Builder**, **design system** no Kit do Elementor, **SEO com Rank Math**, **acessibilidade 100** no Lighthouse, imagens otimizadas em **WebP**, **animações** de entrada leves e **limpeza** segura do site.

Ela nasceu de um projeto real e guarda tanto o fluxo de trabalho quanto as armadilhas que só aparecem na prática: popup que perde as configurações ao salvar, cache de elementos que quebra animações, Wordfence bloqueando senha de aplicativo, Rank Math vendo "0 palavras" em páginas do Elementor, entre outras.

> *English: a Claude skill for building and maintaining Elementor/WordPress sites to an agency standard. Download `elementor-wordpress.skill` from Releases and upload it in Claude → Settings → Skills.*

---

## Como instalar

### 1. Baixe o arquivo da skill

1. Abra a página de **[Releases](https://github.com/davirlima/claude-skill-elementor-wp/releases/latest)** deste repositório.
2. Em **Assets**, baixe o arquivo **`elementor-wordpress.skill`**.

### 2. Envie para a sua conta do Claude

1. Acesse [claude.ai](https://claude.ai) e entre na sua conta.
2. Vá em **Configurações → Capacidades** (*Settings → Capabilities*) e procure a seção **Skills**.
3. Clique em **Enviar skill** (*Upload skill*) e escolha o arquivo `elementor-wordpress.skill` que você baixou.
4. Confira se a skill aparece ativada na lista.

Pronto. A skill fica salva na sua conta e passa a valer no Claude.ai e no **Claude Code** conectado à mesma conta. Se o Claude Code já estiver aberto, feche e abra de novo.

> Se a sua organização não permitir enviar skills, peça ao administrador do plano para liberar.

### Alternativa: só no Claude Code deste computador

1. Na mesma página de Releases, baixe o **`elementor-wordpress.zip`**.
2. Descompacte e coloque a pasta **`elementor-wordpress`** dentro da pasta de skills do Claude Code:
   - Windows: `C:\Users\<seu-usuário>\.claude\skills\`
   - macOS / Linux: `~/.claude/skills/`
3. A estrutura deve ficar `.../.claude/skills/elementor-wordpress/SKILL.md`.
4. Abra o Claude Code de novo.

---

## Como usar

Você não precisa chamar a skill pelo nome. Basta pedir algo sobre um site com Elementor, por exemplo:

- "Refaz a home desse cliente no padrão do Elementor, só com widgets oficiais."
- "Passa o header e o rodapé para o Theme Builder."
- "Organiza as cores e fontes do site no Kit do Elementor."
- "As páginas internas estão com nota baixa no Rank Math, o que está acontecendo?"
- "Otimiza as imagens da home para WebP com nomes bons para SEO."
- "Coloca animações de entrada sutis nas dobras."
- "Faz uma limpa nos rascunhos, modelos e mídias que não são usados."

No início de cada projeto, o Claude pergunta o que precisa: endereço do site, fontes e cores da marca, WhatsApp e mensagens de contato, e quais páginas entram no trabalho.

### Para o Claude mexer no site

Para trabalhar direto no site, o Claude precisa de acesso. A skill explica cada passo na hora, mas o resumo é:

1. No WordPress, crie uma **senha de aplicativo** para um usuário administrador (Usuários → Perfil → Senhas de aplicativo). O ideal é um usuário só para isso.
2. Conecte o **servidor MCP do Elementor** no Claude Code. O Claude te passa o comando pronto.
3. Se usar **Wordfence**, deixe as senhas de aplicativo permitidas para esse usuário.

A senha nunca é gravada na skill. O Claude a lê das variáveis de ambiente da sua máquina.

---

## O que a skill garante em cada entrega

- Só componentes oficiais do Elementor, do Elementor Pro e do WordPress.
- Containers, tokens globais do Kit, um H1 por página e títulos pensados para SEO.
- Backup antes de qualquer alteração e ações reversíveis: página antiga vira rascunho e o que é removido vai para a lixeira. Mídia só é apagada depois de um backup local.
- Conferência no site publicado, no desktop e no celular, com prints e Lighthouse. Quando a mudança não deveria alterar o visual, comparação pixel a pixel.
- Relatório claro do que mudou, do que foi testado e do que ficou para você fazer.

---

## O que vem no pacote

| Pasta | Conteúdo |
|---|---|
| `SKILL.md` | Padrão de qualidade, regras de segurança, fluxo de trabalho e definição de "pronto" |
| `references/` | Guias de consulta: conexão, armadilhas conhecidas, estrutura do Elementor, design system, padrões de página, SEO, acessibilidade, mídia, animações, limpeza |
| `scripts/` | Ferramentas que o Claude usa: cliente do WordPress, kit de componentes, aplicação de tokens, animações, texto para o Rank Math, auditoria de mídia, prints, comparação de imagens, checagens de página, conversão para WebP e Lighthouse |
| `evals/` | Casos de teste usados para validar a skill |

Para usar as ferramentas de navegador (prints, Lighthouse, WebP), o computador precisa ter Python, Node.js e o navegador Chromium. Se faltar algo, o Claude avisa e explica como resolver.

---

## Licença

MIT. Use, adapte e compartilhe à vontade.
