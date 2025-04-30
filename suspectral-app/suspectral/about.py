from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class AboutDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setWindowTitle("About")
        self.resize(300, 200)

        pixmap = QPixmap(":/icons/suspectral.png") \
            .scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        logo = QLabel(self)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.resize(64, 64)

        version = QCoreApplication.applicationVersion()
        text = QLabel(
            f"<strong>Suspectral</strong>"
            f"<p>Copyright &copy; 2025 Daniils Buts</p>"
            f"<p>Software for visualization and analysis of hyperspectral imaging data.</p>"
            f"<p>Version {version}</p>",
            self,
        )

        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button.accepted.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(logo)
        layout.addWidget(text)
        layout.addWidget(button)
        self.setLayout(layout)
