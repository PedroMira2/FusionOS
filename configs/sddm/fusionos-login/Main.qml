import QtQuick 2.15
import QtQuick.Controls 2.15
import QtGraphicalEffects 1.15
import SddmComponents 2.0

Item {
    id: root
    anchors.fill: parent

    Rectangle {
        id: background
        anchors.fill: parent
        
        RadialGradient {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#0D0F1A" }
                GradientStop { position: 1.0; color: "#0A0C14" }
            }
        }
    }
    
    FastBlur {
        anchors.fill: background
        source: background
        radius: 32
    }
    
    Column {
        id: clock
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 40
        spacing: 5
        
        Text {
            id: timeText
            text: Qt.formatTime(new Date(), "hh:mm")
            font.family: "Inter"
            font.pixelSize: 72
            color: "#E8ECF5"
            anchors.right: parent.right
            
            Timer {
                interval: 1000
                running: true
                repeat: true
                onTriggered: timeText.text = Qt.formatTime(new Date(), "hh:mm")
            }
        }
        
        Text {
            id: dateText
            text: Qt.formatDate(new Date(), "dddd, d MMMM")
            font.family: "Inter"
            font.pixelSize: 18
            color: "#9CA3AF"
            anchors.right: parent.right
            
            Timer {
                interval: 60000
                running: true
                repeat: true
                onTriggered: dateText.text = Qt.formatDate(new Date(), "dddd, d MMMM")
            }
        }
    }
    
    Rectangle {
        id: loginPanel
        width: 420
        height: 520
        anchors.centerIn: parent
        color: "#1A1D2799"
        radius: 20
        border.color: "#2E3452"
        border.width: 1
        layer.enabled: true
        
        Column {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 20
            
            Column {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                
                Item {
                    width: 60
                    height: 60
                    anchors.horizontalCenter: parent.horizontalCenter
                    
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "#5B8BFF"
                        opacity: 0.8
                        x: 0
                        y: 10
                    }
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "#9D5BFF"
                        opacity: 0.8
                        x: 20
                        y: 10
                    }
                }
                
                Text {
                    text: "FusionOS"
                    font.family: "Inter"
                    font.pixelSize: 28
                    font.bold: true
                    color: "#E8ECF5"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
                
                Text {
                    text: "Make it yours."
                    font.family: "Inter"
                    font.pixelSize: 14
                    font.italic: true
                    color: "#6B7280"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
            
            Item { height: 10; width: 1 } // Spacer
            
            TextField {
                id: usernameInput
                width: parent.width
                height: 48
                placeholderText: "Nome de utilizador"
                color: "#E8ECF5"
                font.family: "Inter"
                font.pointSize: 11
                
                background: Rectangle {
                    color: "#0D0F1A"
                    radius: 10
                    border.color: usernameInput.focus ? "#5B8BFF" : "#2E3452"
                    border.width: 1
                }
            }
            
            TextField {
                id: passwordInput
                width: parent.width
                height: 48
                placeholderText: "Palavra-passe"
                echoMode: TextInput.Password
                color: "#E8ECF5"
                font.family: "Inter"
                font.pointSize: 11
                
                background: Rectangle {
                    color: "#0D0F1A"
                    radius: 10
                    border.color: passwordInput.focus ? "#5B8BFF" : "#2E3452"
                    border.width: 1
                }
                
                onAccepted: sddm.login(usernameInput.text, passwordInput.text, sessionSelector.currentIndex)
            }
            
            Rectangle {
                id: loginButtonBackground
                width: parent.width
                height: 48
                radius: 10
                color: loginArea.pressed ? "#3A60D9" : (loginArea.containsMouse ? "#4A7AEE" : "#5B8BFF")
                
                Text {
                    text: "Entrar"
                    anchors.centerIn: parent
                    color: "white"
                    font.family: "Inter"
                    font.pixelSize: 14
                    font.weight: Font.SemiBold
                }
                
                MouseArea {
                    id: loginArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: sddm.login(usernameInput.text, passwordInput.text, sessionSelector.currentIndex)
                }
            }
            
            ComboBox {
                id: sessionSelector
                width: parent.width
                model: sessionModel
                textRole: "name"
                currentIndex: sessionModel.lastIndex
                
                background: Rectangle {
                    color: "#0D0F1A"
                    radius: 10
                    border.color: "#2E3452"
                    border.width: 1
                }
                
                contentItem: Text {
                    text: sessionSelector.displayText
                    color: "#E8ECF5"
                    font.family: "Inter"
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                    leftPadding: 12
                }
            }
        }
        
        Rectangle {
            id: errorMessage
            width: parent.width - 40
            height: 40
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20
            anchors.horizontalCenter: parent.horizontalCenter
            color: "#22FF6B7A"
            border.color: "#FF6B7A"
            border.width: 1
            radius: 8
            visible: typeof sddm !== "undefined" ? false : false // In sddm env: sddm.loginFailed
            
            // Connect to SDDM login failure
            Connections {
                target: typeof sddm !== "undefined" ? sddm : null
                function onLoginFailed() {
                    errorMessage.visible = true;
                    passwordInput.text = "";
                }
            }
            
            Text {
                text: "Autenticação falhou"
                anchors.centerIn: parent
                color: "#FF6B7A"
                font.family: "Inter"
                font.pixelSize: 12
            }
        }
    }
    
    Text {
        id: hostnameText
        text: typeof sddm !== "undefined" ? sddm.hostName : "Localhost"
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.margins: 20
        font.family: "Inter"
        font.pixelSize: 14
        color: "#6B7280"
    }
}
