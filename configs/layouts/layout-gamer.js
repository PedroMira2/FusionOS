// ==============================================================================
// FusionOS - Gamer & Focus Minimal Layout Generator for KDE Plasma 6
// Proposito: Esconde paineis completamente ou deixa dock ultra-fino auto-ocultavel
// ==============================================================================

// 1. Remove paineis antigos
var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    allPanels[i].remove();
}

// 2. Cria um Dock Minimalista que so aparece ao encostar o mouse na borda inferior
var gamerDock = new Panel();
gamerDock.location = "bottom";
gamerDock.height = 42;
gamerDock.alignment = "center";
gamerDock.floating = true;
gamerDock.hiding = "autohide"; // Ocultacao total durante jogos e trabalho imersivo

var taskManager = gamerDock.addWidget("org.kde.plasma.icontasks");
taskManager.currentConfigGroup = ["General"];
taskManager.writeConfig("launchers", [
    "applications:com.heroicgameslauncher.hgl.desktop",
    "applications:steam.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:fusion-layout-switcher.desktop"
]);

gamerDock.addWidget("org.kde.plasma.systemtray");

