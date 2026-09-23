// ==============================================================================
// FusionOS - Windows 11 Layout Generator for KDE Plasma 6
// Proposito: Cria a barra de tarefas inferior centralizada estilo Windows 11
// ==============================================================================

// 1. Remove paineis antigos
var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}

// 2. Cria a Barra de Tarefas Inferior Centralizada
var winPanel = new Panel();
winPanel.location = "bottom";
winPanel.height = 44;
winPanel.floating = true; // Floating taskbar moderno

// Espacador esquerdo para centralizar os icones
winPanel.addWidget("org.kde.plasma.panelspacer");

// Botao Iniciar
winPanel.addWidget("org.kde.plasma.kickoff");

// Lupa de Busca
winPanel.addWidget("org.kde.plasma.krunner");

// Visao de Tarefas (Task View / Desktops virtuais)
winPanel.addWidget("org.kde.plasma.pager");

// Gerenciador de Tarefas centralizado
var taskManager = winPanel.addWidget("org.kde.plasma.icontasks");
taskManager.currentConfigGroup = ["General"];
taskManager.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:com.heroicgameslauncher.hgl.desktop",
    "applications:steam.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:fusion-layout-switcher.desktop"
]);

// Espacador direito para empurrar o systemtray para o canto direito
winPanel.addWidget("org.kde.plasma.panelspacer");

// Bandeja do Sistema e Notificacoes (lado direito)
winPanel.addWidget("org.kde.plasma.systemtray");

// Relogio Digital
var clock = winPanel.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");

// Botao "Mostrar Area de Trabalho" (no extremo canto direito)
winPanel.addWidget("org.kde.plasma.showdesktop");

