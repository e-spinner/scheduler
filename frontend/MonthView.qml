import QtQuick 6.2
import QtQuick.Controls 6.2

Rectangle {
    width: 600
    height: 600
    color: "#F0F4F8"

    property date currentDate: new Date()  // Tracks the current date
    property date today: new Date()
    property int firstDay: 0               // First day of the month (Sunday = 0)
    property int totalDays: 0              // Number of days in the month

    Column {
        anchors.fill: parent
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter

        // Month Navigation
        Row {
            width: parent.width
            spacing: 10

            Button {
                text: "<"
                onClicked: {
                    currentDate.setMonth(currentDate.getMonth() - 1)
                    updateCalendar()
                }
            }

            Text {
                text: currentDate.toLocaleDateString(Qt.locale(), "MMMM yyyy")
                font.bold: true
                font.pointSize: 20

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: console.log("Navigate to Year View")  // Future Implementation
                }
            }

            Button {
                text: ">"
                onClicked: {
                    currentDate.setMonth(currentDate.getMonth() + 1)
                    updateCalendar()
                }
            }

            Button {
                text: "Today"
                onClicked: {
                    currentDate = today
                    updateCalendar()
                }
            }
        }

        // Calendar Grid
        Grid {
            id: calendarGrid
            columns: 7
            spacing: 5
            width: parent.width

            Repeater {
                model: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
                Rectangle {
                    width: parent.width / 7 - 5
                    height: 40
                    color: "#90CAF9"
                    Text {
                        text: modelData
                        anchors.centerIn: parent
                        font.bold: true
                    }
                }
            }

            Repeater {
                model: 42  // Full grid size for month layout

                Rectangle {
                    width: parent.width / 7 - 5
                    height: 80
                    color: index >= firstDay && index < firstDay + totalDays
                            ? "#E3F2FD"
                            : "#CFD8DC"
                    border.color: "gray"

                    Text {
                        text: index >= firstDay && index < firstDay + totalDays
                              ? index - firstDay + 1
                              : ""
                        anchors.top: parent.top
                        anchors.left: parent.left
                        anchors.margins: 5
                    }

                    // Hover Effect
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onEntered: parent.color = index >= firstDay && index < firstDay + totalDays
                                ? "#BBDEFB"
                                : "#CFD8DC"
                        onExited: parent.color = index >= firstDay && index < firstDay + totalDays
                                ? "#E3F2FD"
                                : "#CFD8DC"

                        onClicked: console.log("Navigate to Week View - Day", index - firstDay + 1)
                    }

                    // Event Display
                    Rectangle {
                        width: parent.width * 0.8
                        height: 20
                        color: "#4CAF50"
                        anchors.bottom: parent.bottom
                        anchors.horizontalCenter: parent.horizontalCenter
                        visible: checkEventExists(index - firstDay + 1) // Integrated logic
                    }
                }
            }
        }
    }

    function updateCalendar() {
        const firstDayDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
        firstDay = firstDayDate.getDay()
        totalDays = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate()
    }

    // Mock function to demonstrate displaying events (replace with real logic)
    function checkEventExists(day) {
        // Example: Sample data for event logic
        const sampleEvents = [3, 7, 15, 21, 30]
        return sampleEvents.includes(day)
    }

    Component.onCompleted: updateCalendar()
}
