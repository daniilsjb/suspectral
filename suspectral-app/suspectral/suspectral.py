from PySide6.QtCore import Slot
from PySide6.QtGui import (
    Qt,
    QAction,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QIcon,
    QKeySequence,
)
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QWidget, QMessageBox,
)

from suspectral.about import AboutDialog
from suspectral.controller.image_controller import ImageController
from suspectral.controller.metadata_controller import MetadataController
from suspectral.controller.selection_controller import SelectionController
from suspectral.controller.spectral_controller import SpectralController
from suspectral.controller.status_controller import StatusController
from suspectral.exporter.exporter_clipboard import ClipboardExporter
from suspectral.exporter.exporter_csv import CsvExporter
from suspectral.exporter.exporter_matlab import MatlabExporter
from suspectral.exporter.exporter_numpy import NpyExporter
from suspectral.help import HelpDialog
from suspectral.license import LicenseDialog
from suspectral.model.hypercube import Hypercube, HypercubeDataMissing, HypercubeHeaderInvalid
from suspectral.model.hypercube_container import HypercubeContainer
from suspectral.tool.manager import ToolManager
from suspectral.tool.tool import Tool
from suspectral.view.image.image_options_view import ImageOptionsView
from suspectral.view.image.image_view import ImageView
from suspectral.view.metadata_view import MetadataView
from suspectral.view.selection_view import SelectionView
from suspectral.view.spectral_view import SpectralView
from suspectral.view.status_view import StatusView
from suspectral.view.toolbar_view import ToolbarView
from suspectral.widget.theme_icon import ThemeIcon


class Suspectral(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Suspectral")
        self.setWindowIcon(QIcon(":/icons/suspectral.ico"))
        self.resize(1600, 900)

        self._model = HypercubeContainer()
        self._model.opened.connect(self._handle_hypercube_opened)
        self._model.closed.connect(self._handle_hypercube_closed)

        exporters = [
            ClipboardExporter(),
            MatlabExporter(),
            NpyExporter(),
            CsvExporter(),
        ]

        self._image_view = ImageView(self)
        self._image_controls_view = ImageOptionsView(self._model, self)
        self._image_controller = ImageController(
            image_options_view=self._image_controls_view,
            image_display_view=self._image_view,
            model=self._model,
            parent=self,
        )

        self._tools = ToolManager(
            exporters=exporters,
            view=self._image_view,
            model=self._model,
            parent=self,
        )

        self._status_view = StatusView(self)
        self._status_controller = StatusController(
            image=self._image_view,
            view=self._status_view,
            tools=self._tools,
            model=self._model,
            parent=self,
        )

        self._toolbar = ToolbarView(
            image=self._image_view,
            tools=self._tools,
            model=self._model,
            parent=self,
        )

        self._selection_view = SelectionView(self)
        self._selection_controller = SelectionController(
            view=self._selection_view,
            tools=self._tools,
            model=self._model,
            parent=self,
        )

        self._spectral_view = SpectralView(self._model, exporters, self)
        self._spectral_controller = SpectralController(
            view=self._spectral_view,
            tools=self._tools,
            model=self._model,
            parent=self,
        )

        self._metadata_view = MetadataView(self)
        self._metadata_controller = MetadataController(
            view=self._metadata_view,
            model=self._model,
            parent=self,
        )

        self._create_menubar()
        self._create_docks()

        self.addToolBar(self._toolbar)
        self.setStatusBar(self._status_view)
        self.setCentralWidget(self._image_view)

        self.centralWidget().setAcceptDrops(True)
        self.centralWidget().dragEnterEvent = self._handle_drag_enter
        self.centralWidget().dragMoveEvent = self._handle_drag_move
        self.centralWidget().dropEvent = self._handle_drop

    def _create_menubar(self):
        menu_bar = self.menuBar()

        def create_file_menu():
            menu = menu_bar.addMenu("&File")

            load_action = menu.addAction("Open")
            load_action.setIcon(ThemeIcon("folder-open.svg"))
            load_action.setShortcut("Ctrl+O")
            load_action.triggered.connect(self._handle_open)

            close_action = menu.addAction("Close")
            close_action.setIcon(ThemeIcon("trash.svg"))
            close_action.setShortcut("Ctrl+W")
            close_action.triggered.connect(self._handle_close)
            close_action.setEnabled(False)
            self._model.opened.connect(lambda: close_action.setEnabled(True))
            self._model.closed.connect(lambda: close_action.setEnabled(False))

            menu.addSeparator()

            copy_image_action = menu.addAction("Copy Image")
            copy_image_action.setIcon(ThemeIcon("copy.svg"))
            copy_image_action.triggered.connect(lambda: self._image_controller.copy_image())
            copy_image_action.setEnabled(False)
            self._model.opened.connect(lambda: copy_image_action.setEnabled(True))
            self._model.closed.connect(lambda: copy_image_action.setEnabled(False))

            save_image_action = menu.addAction("Save Image As...")
            save_image_action.setIcon(ThemeIcon("image.svg"))
            save_image_action.triggered.connect(lambda: self._image_controller.save_image())
            save_image_action.setEnabled(False)
            self._model.opened.connect(lambda: save_image_action.setEnabled(True))
            self._model.closed.connect(lambda: save_image_action.setEnabled(False))

            menu.addSeparator()

            exit_action = menu.addAction("&Exit")
            exit_action.setIcon(QIcon(ThemeIcon("exit.svg")))
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)

        def create_view_menu():
            menu = menu_bar.addMenu("&View")

            zoom_in_action = menu.addAction("Zoom In")
            zoom_in_action.setIcon(ThemeIcon("zoom-in.svg"))
            zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
            zoom_in_action.triggered.connect(lambda: self._image_view.zoom_in())

            zoom_out_action = menu.addAction("Zoom Out")
            zoom_out_action.setIcon(ThemeIcon("zoom-out.svg"))
            zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
            zoom_out_action.triggered.connect(lambda: self._image_view.zoom_out())

            zoom_fit_action = menu.addAction("Zoom Fit")
            zoom_fit_action.setIcon(ThemeIcon("zoom-fit.svg"))
            zoom_fit_action.setShortcut("Ctrl+1")
            zoom_fit_action.triggered.connect(lambda: self._image_view.zoom_fit())

            menu.addSeparator()

            rotate_left_action = menu.addAction("Rotate Left")
            rotate_left_action.setIcon(ThemeIcon("rotate-left.svg"))
            rotate_left_action.setShortcut("Ctrl+A")
            rotate_left_action.triggered.connect(lambda: self._image_view.rotate_left())

            rotate_right_action = menu.addAction("Rotate Right")
            rotate_right_action.setIcon(ThemeIcon("rotate-right.svg"))
            rotate_right_action.setShortcut("Ctrl+D")
            rotate_right_action.triggered.connect(lambda: self._image_view.rotate_right())

            menu.addSeparator()

            flip_v_action = menu.addAction("Flip Vertical")
            flip_v_action.setIcon(ThemeIcon("flip-vertical.svg"))
            flip_v_action.setShortcut("Ctrl+V")
            flip_v_action.triggered.connect(lambda: self._image_view.flip_vertically())

            flip_h_action = menu.addAction("Flip Horizontal")
            flip_h_action.setIcon(ThemeIcon("flip-horizontal.svg"))
            flip_h_action.setShortcut("Ctrl+H")
            flip_h_action.triggered.connect(lambda: self._image_view.flip_horizontally())

            for action in menu.actions():
                action.setEnabled(False)
                self._model.opened.connect(lambda _, it=action: it.setEnabled(True))
                self._model.closed.connect(lambda it=action: it.setEnabled(False))

        def create_help_menu():
            menu = menu_bar.addMenu("&Help")

            about_action = menu.addAction("About")
            about_action.triggered.connect(self._handle_about)

            help_action = menu.addAction("Help")
            help_action.setIcon(ThemeIcon("help.svg"))
            help_action.triggered.connect(self._handle_help)

            license_action = menu.addAction("License")
            license_action.setIcon(ThemeIcon("license.svg"))
            license_action.triggered.connect(self._handle_license)

        create_file_menu()
        create_view_menu()
        create_help_menu()

    def _create_docks(self):
        self.setDockOptions(
            QMainWindow.DockOption.AllowNestedDocks |
            QMainWindow.DockOption.AllowTabbedDocks)

        self._create_dock(
            name="Metadata",
            view=self._metadata_view,
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
        )
        self._create_dock(
            name="Selection",
            view=self._selection_view,
            area=Qt.DockWidgetArea.LeftDockWidgetArea,
        )
        self._create_dock(
            name="Spectral Plot",
            view=self._spectral_view,
            area=Qt.DockWidgetArea.RightDockWidgetArea,
        )
        self._create_dock(
            name="Image Controls",
            view=self._image_controls_view,
            area=Qt.DockWidgetArea.RightDockWidgetArea,
        )

    def _create_dock(self, name: str, view: QWidget, area: Qt.DockWidgetArea):
        dock = QDockWidget(name, self)
        dock.setWidget(view)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea |
            Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(area, dock)

    @Slot()
    def _select_tool(self, action: QAction):
        tool: Tool = action.data()
        self._tools.set(tool)

    @Slot()
    def _handle_about(self):
        dialog = AboutDialog(self)
        dialog.exec()

    @Slot()
    def _handle_help(self):
        dialog = HelpDialog(self)
        dialog.exec()

    @Slot()
    def _handle_license(self):
        dialog = LicenseDialog(self)
        dialog.exec()

    @Slot()
    def _handle_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Load Hypercube",
            filter="ENVI (*.hdr)"
        )

        if path:
            self._load_hypercube(path)

    @Slot()
    def _handle_close(self):
        self._model.close()

    @Slot()
    def _handle_hypercube_opened(self, hypercube: Hypercube):
        self.setWindowTitle(f"Suspectral - {hypercube.name}")

    @Slot()
    def _handle_hypercube_closed(self):
        self.setWindowTitle("Suspectral")

    @staticmethod
    def _handle_drag_enter(event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            if path.lower().endswith(".hdr"):
                event.accept()

    @staticmethod
    def _handle_drag_move(event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.accept()

    def _handle_drop(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            self._load_hypercube(path)

    def _load_hypercube(self, path: str):
        try:
            self._model.open(path)
        except HypercubeDataMissing:
            QMessageBox.critical(
                self,
                "Missing Data",
                "The data file associated with the selected header does not exist. "
                "Please, ensure that it is located in the same directory as the header "
                "and has either .raw, .img., or .dat extension."
            )
        except HypercubeHeaderInvalid:
            QMessageBox.critical(
                self,
                "Invalid Header",
                "The selected header does not follow the standard ENVI format. Please, "
                "ensure that the contents  of the header file contain all necessary fields."
            )
