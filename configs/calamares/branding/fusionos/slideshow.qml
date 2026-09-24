import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: presentation
    anchors.fill: parent

    property int currentSlide: 0
    property var slides: [
        {
            title: "Bem-vindo ao FusionOS",
            subtitle: "Simplicidade e sofisticação em perfeita harmonia.",
            description: "O FusionOS foi projetado para quem busca a fluidez de um sistema moderno sem poluição visual. Uma experiência digital limpa, intuitiva e focada na sua produtividade.",
            tag: "NOVO DESIGN 1.0",
            icon: "✨"
        },
        {
            title: "Chameleon Layout Engine",
            subtitle: "A interface que se adapta ao seu estilo de trabalho.",
            description: "Alterne instantaneamente entre o estilo macOS com dock flutuante, a familiaridade do Windows 11 centralizado ou o modo Gamer com foco imersivo, com apenas um clique.",
            tag: "EXCLUSIVIDADE",
            icon: "🎨"
        },
        {
            title: "Performance Extrema para Jogos",
            subtitle: "Compatibilidade nativa com seus títulos favoritos.",
            description: "Equipado com GameMode, MangoHud, Wine Assist pré-configurado e áudio PipeWire de baixíssima latência. Jogue e produza sem limites.",
            tag: "ALTO DESEMPENHO",
            icon: "🎮"
        },
        {
            title: "Estabilidade e Proteção Total",
            subtitle: "Trabalhe com a tranquilidade que você merece.",
            description: "Com o sistema de arquivos Btrfs e ZRAM ativo por padrão, seus dados ficam protegidos com restauração instantânea e máxima eficiência de memória.",
            tag: "CONFIABILIDADE",
            icon: "🛡️"
        }
    ]

    Rectangle {
        anchors.fill: parent
        color: "#141728"

        // Circulos de brilho ambiente
        Rectangle {
            width: 320; height: 320; radius: 160
            x: parent.width - 240; y: -80
            color: "#5B8BFF"
            opacity: 0.08
        }
        Rectangle {
            width: 280; height: 280; radius: 140
            x: -80; y: parent.height - 200
            color: "#8B5CF6"
            opacity: 0.06
        }

        // Conteúdo central do slide
        Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - 100, 680)
            spacing: 20

            // Tag de destaque
            Rectangle {
                width: tagText.contentWidth + 24
                height: 30
                radius: 15
                color: "#1E243D"
                border.color: "#5B8BFF"
                border.width: 1

                Text {
                    id: tagText
                    anchors.centerIn: parent
                    text: slides[currentSlide].tag
                    font.family: "Inter, Segoe UI, sans-serif"
                    font.pixelSize: 11
                    font.bold: true
                    color: "#5B8BFF"
                }
            }

            // Ícone + Título
            Row {
                spacing: 16
                Text {
                    text: slides[currentSlide].icon
                    font.pixelSize: 42
                }
                Column {
                    spacing: 6
                    Text {
                        text: slides[currentSlide].title
                        font.family: "Inter, Segoe UI, sans-serif"
                        font.pixelSize: 32
                        font.bold: true
                        color: "#E8ECF5"
                    }
                    Text {
                        text: slides[currentSlide].subtitle
                        font.family: "Inter, Segoe UI, sans-serif"
                        font.pixelSize: 16
                        color: "#9CA3AF"
                    }
                }
            }

            // Descrição detalhada
            Text {
                width: parent.width
                text: slides[currentSlide].description
                font.family: "Inter, Segoe UI, sans-serif"
                font.pixelSize: 15
                lineHeight: 1.4
                wrapMode: Text.WordWrap
                color: "#CBD5E1"
            }

            // Indicadores de slide (bolinhas)
            Row {
                spacing: 8
                topPadding: 16
                Repeater {
                    model: slides.length
                    Rectangle {
                        width: index === currentSlide ? 24 : 8
                        height: 8
                        radius: 4
                        color: index === currentSlide ? "#5B8BFF" : "#2E3452"

                        Behavior on width {
                            NumberAnimation { duration: 250; easing.type: Easing.InOutQuad }
                        }
                        Behavior on color {
                            ColorAnimation { duration: 250 }
                        }
                    }
                }
            }
        }
    }

    // Transição automática de slides a cada 7 segundos
    Timer {
        interval: 7000
        running: true
        repeat: true
        onTriggered: {
            currentSlide = (currentSlide + 1) % slides.length
        }
    }
}
