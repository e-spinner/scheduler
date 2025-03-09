import QtQuick 6.2
import QtQuick.Controls 6.2

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "Scheduler"

    StackView {
        id: stackView
        initialItem: "frontend/MonthView.qml"
        anchors.fill: parent
    }
}
