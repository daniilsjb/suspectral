from PySide6.QtCore import (
    QSize,
    Signal,
    Slot,
)
from PySide6.QtGui import (
    Qt,
    QAction,
    QActionGroup,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QIcon,
    QImage,
    QKeySequence,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QWidget,
)

from suspectral.help import HelpDialog
from suspectral.about import AboutDialog
from suspectral.license import LicenseDialog

from suspectral.exporter.exporter_clipboard import ClipboardExporter
from suspectral.exporter.exporter_csv import CsvExporter
from suspectral.exporter.exporter_matlab import MatlabExporter
from suspectral.exporter.exporter_numpy import NpyExporter

from suspectral.hypercube.hypercube import Hypercube
from suspectral.hypercube.hypercube_container import HypercubeContainer

from suspectral.image.tool.tool import Tool
from suspectral.image.tool.tool_cursor import CursorTool
from suspectral.image.tool.tool_drag import DragTool
from suspectral.image.tool.tool_inspect import InspectTool
from suspectral.image.tool.tool_select import SelectTool
from suspectral.image.tool.tool_zoom import ZoomTool

from suspectral.image.controls.image_controls import ImageControls
from suspectral.image.image_view import ImageView
from suspectral.metadata.metadata_controller import MetadataController
from suspectral.metadata.metadata_view import MetadataView
from suspectral.selection.selection_controller import SelectionController
from suspectral.selection.selection_view import SelectionView
from suspectral.spectral.spectral_plot_controller import SpectralPlotController
from suspectral.spectral.spectral_plot_view import SpectralPlotView
from suspectral.status.status_bar import StatusBar
from suspectral.status.status_bar_controller import StatusBarController
from suspectral.widget.theme_icon import ThemeIcon


class Suspectral(QMainWindow):
    tool_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Suspectral")
        self.setWindowIcon(QIcon(":/icons/suspectral.ico"))
        self.resize(1600, 900)

        self._container = HypercubeContainer()
        self._container.opened.connect(self._handle_hypercube_opened)
        self._container.closed.connect(self._handle_hypercube_closed)

        self._exporters = [ClipboardExporter(), MatlabExporter(), CsvExporter(), NpyExporter()]

        self._tool_action_group = QActionGroup(self)
        self._tool_action_group.setExclusive(True)
        self._tool_action_group.triggered.connect(self._set_tool)

        self._init_image_view()
        self._tool_cursor = CursorTool(self._image_view)
        self._tool_drag = DragTool(self._image_view)
        self._tool_zoom = ZoomTool(self._image_view)
        self._tool_select = SelectTool(self._image_view, self._container, self._exporters)
        self._tool_inspect = InspectTool(self._image_view, self._container, self._exporters)

        self._tool = self._tool_cursor
        self._container.opened.connect(lambda: self._tool.activate())
        self._container.closed.connect(lambda: self._tool.deactivate())

        self._container.opened.connect(self._image_view.reset)
        self._container.closed.connect(self._image_view.reset)

        self._init_status_bar()
        self._init_metadata_view()
        self._init_spectral_plot()
        self._init_selection_view()
        self._init_image_controls()

        self._create_toolbar()
        self._create_menubar()
        self._create_docks()

        self.centralWidget().setAcceptDrops(True)
        self.centralWidget().dragEnterEvent = self._handle_drag_enter
        self.centralWidget().dragMoveEvent = self._handle_drag_move
        self.centralWidget().dropEvent = self._handle_drop

    def _init_status_bar(self):
        self._status_bar = StatusBar(self)
        self._status_bar_controller = StatusBarController(
            view=self._status_bar,
            model=self._container,
            parent=self,
        )

        self._image_view.cursor_moved_inside.connect(self._status_bar.update_cursor_status)
        self._image_view.cursor_moved_outside.connect(self._status_bar.update_cursor_status)
        self._tool_select.selection_moved.connect(self._status_bar.update_selection_status)
        self._tool_select.selection_stopped.connect(self._status_bar.update_selection_status)
        self._tool_select.selection_ended.connect(lambda: self._status_bar.update_selection_status(None))

        self.setStatusBar(self._status_bar)

    def _init_metadata_view(self):
        self._metadata_view = MetadataView(self)
        self._metadata_controller = MetadataController(
            view=self._metadata_view,
            model=self._container,
            parent=self,
        )

    def _init_spectral_plot(self):
        self._spectral_plot_view = SpectralPlotView(self._exporters, self)
        self._spectral_plot_controller = SpectralPlotController(
            view=self._spectral_plot_view,
            model=self._container,
            parent=self,
        )

        self.tool_changed.connect(self._spectral_plot_controller.handle_tool_changed)
        self._tool_inspect.pixel_clicked.connect(self._spectral_plot_controller.handle_pixel_clicked)
        self._tool_inspect.pixel_cleared.connect(self._spectral_plot_controller.handle_pixel_cleared)
        self._tool_select.selection_moved.connect(self._spectral_plot_controller.handle_selection_updated)
        self._tool_select.selection_ended.connect(self._spectral_plot_controller.handle_selection_updated)
        self._tool_select.selection_stopped.connect(self._spectral_plot_controller.handle_selection_updated)
        self._tool_select.selection_sampled.connect(self._spectral_plot_controller.handle_selection_sampled)

    def _init_selection_view(self):
        self._selection_view = SelectionView(self)
        self._selection_controller = SelectionController(
            view=self._selection_view,
            model=self._container,
            parent=self,
        )

        self.tool_changed.connect(self._selection_controller.handle_tool_changed)
        self._tool_inspect.pixel_clicked.connect(self._selection_controller.handle_pixel_clicked)
        self._tool_inspect.pixel_cleared.connect(self._selection_controller.handle_pixel_cleared)
        self._tool_select.selection_moved.connect(self._selection_controller.handle_selection_updated)
        self._tool_select.selection_ended.connect(self._selection_controller.handle_selection_updated)
        self._tool_select.selection_stopped.connect(self._selection_controller.handle_selection_updated)
        self._tool_select.selection_sampled.connect(self._selection_controller.handle_selection_sampled)

    def _init_image_controls(self):
        self._image_controls = ImageControls(self._container, self)
        self._container.opened.connect(self._image_controls.open)
        self._container.closed.connect(self._image_controls.close)
        self._image_controls.image_changed.connect(self._handle_image_changed)

    def _init_image_view(self):
        self._image_view = ImageView(self)
        self.setCentralWidget(self._image_view)

    @Slot()
    def _handle_image_changed(self, image: QImage):
        self._image_view.set_pixmap(QPixmap.fromImage(image))

    def _create_toolbar(self):
        toolbar = self.addToolBar("Toolbar")
        toolbar.setToolTip("Toolbar")
        toolbar.setIconSize(QSize(20, 20))

        toolbar.setMovable(False)
        toolbar.setEnabled(False)
        toolbar.setFloatable(False)

        if QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark:
            highlight = "#3b82f6"
        else:
            highlight = "#bfdbfe"

        toolbar.setStyleSheet(f"""
            QToolButton:checked {{
                background-color: {highlight};
                border-radius: 4px;
                border: none;
            }}
        """)

        self._container.opened.connect(lambda: toolbar.setEnabled(True))
        self._container.closed.connect(lambda: toolbar.setEnabled(False))

        def add_tool(name: str, icon: str, tool: Tool, checked: bool = False):
            action = QAction(ThemeIcon(icon), name, self)
            action.setData(tool)

            action.setCheckable(True)
            action.setChecked(checked)

            self._tool_action_group.addAction(action)
            toolbar.addAction(action)

        add_tool(
            name="No Tool",
            icon="cursor.svg",
            tool=self._tool_cursor,
            checked=True,
        )
        add_tool(
            name="Drag",
            icon="drag.svg",
            tool=self._tool_drag,
        )
        add_tool(
            name="Inspect",
            icon="hand-point.svg",
            tool=self._tool_inspect,
        )
        add_tool(
            name="Select Area",
            icon="select.svg",
            tool=self._tool_select,
        )
        add_tool(
            name="Zoom",
            icon="zoom.svg",
            tool=self._tool_zoom,
        )

        toolbar.addSeparator()

        def add_action(name: str, icon: str, slot):
            action = QAction(ThemeIcon(icon), name, self)
            action.triggered.connect(slot)
            toolbar.addAction(action)

        add_action(
            name="Rotate Left",
            icon="rotate-left.svg",
            slot=self._image_view.rotate_left,
        )
        add_action(
            name="Rotate Right",
            icon="rotate-right.svg",
            slot=self._image_view.rotate_right,
        )
        add_action(
            name="Flip Horizontal",
            icon="flip-horizontal.svg",
            slot=self._image_view.flip_horizontally,
        )
        add_action(
            name="Flip Vertical",
            icon="flip-vertical.svg",
            slot=self._image_view.flip_vertically,
        )
        add_action(
            name="Zoom In",
            icon="zoom-in.svg",
            slot=lambda: self._image_view.zoom_in(),
        )
        add_action(
            name="Zoom Out",
            icon="zoom-out.svg",
            slot=lambda: self._image_view.zoom_out(),
        )

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
            self._container.opened.connect(lambda: close_action.setEnabled(True))
            self._container.closed.connect(lambda: close_action.setEnabled(False))

            menu.addSeparator()

            copy_image_action = menu.addAction("Copy Image")
            copy_image_action.setIcon(ThemeIcon("copy.svg"))
            copy_image_action.triggered.connect(self._image_view.copy_image)
            copy_image_action.setEnabled(False)
            self._container.opened.connect(lambda: copy_image_action.setEnabled(True))
            self._container.closed.connect(lambda: copy_image_action.setEnabled(False))

            save_image_action = menu.addAction("Save Image As...")
            save_image_action.setIcon(ThemeIcon("image.svg"))
            save_image_action.triggered.connect(self._image_view.save_image)
            save_image_action.setEnabled(False)
            self._container.opened.connect(lambda: save_image_action.setEnabled(True))
            self._container.closed.connect(lambda: save_image_action.setEnabled(False))

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
            zoom_in_action.triggered.connect(lambda: self._image_view.zoom(factor=1.2))

            zoom_out_action = menu.addAction("Zoom Out")
            zoom_out_action.setIcon(ThemeIcon("zoom-out.svg"))
            zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
            zoom_out_action.triggered.connect(lambda: self._image_view.zoom(factor=1 / 1.2))

            zoom_fit_action = menu.addAction("Zoom Fit")
            zoom_fit_action.setIcon(ThemeIcon("zoom-fit.svg"))
            zoom_fit_action.setShortcut("Ctrl+1")
            zoom_fit_action.triggered.connect(self._image_view.zoom_fit)

            menu.addSeparator()

            rotate_left_action = menu.addAction("Rotate Left")
            rotate_left_action.setIcon(ThemeIcon("rotate-left.svg"))
            rotate_left_action.setShortcut("Ctrl+A")
            rotate_left_action.triggered.connect(self._image_view.rotate_left)

            rotate_right_action = menu.addAction("Rotate Right")
            rotate_right_action.setIcon(ThemeIcon("rotate-right.svg"))
            rotate_right_action.setShortcut("Ctrl+D")
            rotate_right_action.triggered.connect(self._image_view.rotate_right)

            menu.addSeparator()

            flip_v_action = menu.addAction("Flip Vertical")
            flip_v_action.setIcon(ThemeIcon("flip-vertical.svg"))
            flip_v_action.setShortcut("Ctrl+V")
            flip_v_action.triggered.connect(self._image_view.flip_vertically)

            flip_h_action = menu.addAction("Flip Horizontal")
            flip_h_action.setIcon(ThemeIcon("flip-horizontal.svg"))
            flip_h_action.setShortcut("Ctrl+H")
            flip_h_action.triggered.connect(self._image_view.flip_horizontally)

            for action in menu.actions():
                action.setEnabled(False)
                self._container.opened.connect(lambda _, it=action: it.setEnabled(True))
                self._container.closed.connect(lambda it=action: it.setEnabled(False))

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
            name="Spectral Plots",
            view=self._spectral_plot_view,
            area=Qt.DockWidgetArea.RightDockWidgetArea,
        )
        self._create_dock(
            name="Image Controls",
            view=self._image_controls,
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
    def _set_tool(self, action: QAction):
        tool: Tool = action.data()
        if self._tool is not tool:
            self._tool.deactivate()
            self._tool = tool
            self._tool.activate()
            self.tool_changed.emit()

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
            self._container.open(path)

    @Slot()
    def _handle_close(self):
        self._container.close()

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
            self._container.open(path)
