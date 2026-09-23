// ==============================================================================
// FusionOS - macOS Layout Generator for KDE Plasma 6
// Proposito: Cria a barra superior (Top Bar) e o Dock flutuante inferior estilo Mac
// ==============================================================================

// 1. Remove paineis antigos para evitar duplicacao
var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}

// 2. Cria a Barra Superior (Top Bar estilo macOS Sonoma/Sequoia)
var topBar = new Panel();
topBar.location = "top";
topBar.height = 28;
topBar.alignment = "center";
topBar.floating = false;

// Widgets da Barra Superior:
// - Lado Esquerdo: Menu FusionOS + Menu Global da Aplicacao (File, Edit, View...)
topBar.addWidget("org.kde.plasma.kickoff");
topBar.addWidget("org.kde.plasma.appmenu");

// - Espacador flexivel
topBar.addWidget("org.kde.plasma.panelspacer");

// - Centro: Relogio Digital
var clock = topBar.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");

// - Espacador flexivel
topBar.addWidget("org.kde.plasma.panelspacer");

// - Lado Direito: Bandeja do Sistema, Volume e Controle Rapido
topBar.addWidget("org.kde.plasma.systemtray");

// 3. Cria o Dock Flutuante Inferior (Estilo macOS Dock)
var dock = new Panel();
dock.location = "bottom";
dock.height = 54;
dock.alignment = "center";
dock.floating = true; // Floating Dock nativo do Plasma 6!
dock.hiding = "windowscover"; // Auto-ocultacao inteligente quando janelas encostam

// Widgets do Dock:
// Gerenciador de Tarefas apenas com icones (Icons-only Task Manager)
var taskManager = dock.addWidget("org.kde.plasma.icontasks");
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

// Lixeira no canto do dock
dock.addWidget("org.kde.plasma.trash");

