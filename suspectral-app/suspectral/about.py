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
    """
    A dialog window displaying information about the application.

    Shows the application logo, version, copyright, and a brief description.
    Provides a simple OK button to close the dialog.

    Parameters
    ----------
    parent : QWidget or None, optional
        The parent widget of the dialog, by default None.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.resize(300, 200)

        pixmap = QPixmap(":/icons/suspectral.png") \
            .scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        logo = QLabel(parent=self)
        logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.resize(50, 50)

        text = QLabel(
            f"<strong>Suspectral</strong>"
            f"<p>Copyright &copy; 2025 Daniils Buts</p>"
            f"<p>Software for visualization and extraction of hyperspectral imaging data.</p>"
            f"<p>Version {QCoreApplication.applicationVersion()}</p>",
            parent=self,
        )
        text.setWordWrap(True)
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        okay = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, parent=self)
        okay.accepted.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(logo)
        layout.addWidget(text)
        layout.addWidget(okay)
