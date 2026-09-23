# FusionOS - Manual do Usuário & Guia de Recursos

Bem-vindo ao **FusionOS** — o sistema operacional projetado para unir a fluidez estética do macOS, a produtividade e compatibilidade do Windows e a solidez do Linux.

---

## 1. Atalhos Rápidos Essenciais

| Atalho | O que faz no FusionOS | Inspiração |
| :--- | :--- | :--- |
| **`Alt + Espaço`** (ou `Win + Espaço`) | Abre a **Busca Global Centralizada (Spotlight)** para abrir apps, arquivos ou fazer contas. | macOS Spotlight / Raycast |
| **`Win + E`** | Abre o **Gerenciador de Arquivos (Dolphin)**. | Windows |
| **`Win + V`** | Abre o **Histórico de Área de Transferência** (copiar e colar avançado). | Windows 11 |
| **`Win + Tab`** | Visão geral de todas as janelas abertas (**Mission Control**). | macOS & Windows |
| **`Win + Setas`** | Encaixa a janela na metade esquerda, direita, maximiza ou minimiza (**Aero Snap**). | Windows 11 |
| **`Win + L`** | Bloqueia a tela instantaneamente. | Windows |

---

## 2. Gestos no Touchpad (Notebooks)

O FusionOS roda 100% sobre o servidor gráfico **Wayland**, proporcionando animações 1:1 com resposta direta ao movimento dos seus dedos:

* **Deslizar 3 dedos para os lados:** Alterna suavemente entre as suas áreas de trabalho virtuais.
* **Deslizar 3 dedos para cima:** Abre o *Mission Control* (todas as janelas espalhadas na tela).
* **Pinça com 4 dedos:** Abre a grade de aplicativos instalados.

---

## 3. Como usar o Alternador de Estilo ("Chameleon Engine")

Você não precisa ficar preso a um único visual. Para mudar a aparência do sistema:
1. Abra o menu ou clique no ícone **Alternador de Estilo FusionOS** no dock/barra.
2. Selecione o modo desejado:
   * **Modo Mac (Padrão):** Barra superior com relógio e menu global + Dock flutuante inferior.
   * **Modo Windows 11:** Barra inferior unificada com Menu Iniciar centralizado e área de notificações.
   * **Modo Gamer & Foco:** Painéis ocultos para dar 100% da tela para o seu jogo ou software de trabalho.
3. A mudança ocorre **instantaneamente**, sem reiniciar nem fechar seus programas.

---

## 4. Executando Jogos e Programas do Windows (`.exe` e `.msi`)

### Para Programas Comuns (.exe / .msi):
1. Dê um **duplo clique** no arquivo `.exe` ou `.msi` baixado.
2. Uma janela inteligente do FusionOS aparecerá perguntando:
   * **Executar com Wine Direto:** Para programas rápidos ou instaladores simples.
   * **Abrir no Bottles (Recomendado para apps complexos):** Cria uma "garrafa" segura e isolada (ótimo para suítes de escritório, ferramentas de design ou programas antigos).

### Para Jogos da Epic Games, GOG e Amazon:
* Abra o aplicativo **Heroic Games Launcher** (já pré-instalado).
* Faça login com a sua conta da Epic Games ou GOG.
* Clique em instalar qualquer jogo da sua biblioteca. O FusionOS cuidará automaticamente de configurar a versão ideal do Wine/Proton.

### Para Jogos da Steam:
* Abra a **Steam** nativa.
* Todos os jogos da sua biblioteca Windows estão liberados para download automático através da camada **Proton-GE**.

---

## 5. Sistema de Restauração "À Prova de Falhas"

Se por qualquer motivo uma atualização de driver ou instalação acidental desestabilizar o computador:
1. Reinicie o computador.
2. No menu inicial de inicialização (GRUB), selecione a opção **"FusionOS Snapshots"**.
3. Escolha o ponto de restauração anterior (criado automaticamente minutos antes).
4. O sistema iniciará instantaneamente no estado anterior, como se nada tivesse acontecido.

