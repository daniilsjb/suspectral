from PySide6.QtCore import QSize, Qt, Slot
from PySide6.QtGui import QActionGroup, QAction
from PySide6.QtWidgets import QToolBar, QWidget, QApplication

from suspectral.tool.manager import ToolManager
from suspectral.tool.tool import Tool
from suspectral.view.image.image_view import ImageView
from suspectral.theme_icon import ThemeIcon


class ToolbarView(QToolBar):
    """
    Toolbar widget providing tool selection and image manipulation actions.

    Parameters
    ----------
    image : ImageView
        The image view instance whose transformations can be controlled.
    tools : ToolManager
        The manager that handles the state and switching of interactive tools.
    parent : QWidget or None, optional
        The parent widget of the toolbar, by default None.
    """

    def __init__(self, *,
                 image: ImageView,
                 tools: ToolManager,
                 parent: QWidget | None = None):
        super().__init__("Toolbar", parent)

        self._tools = tools
        self._group = QActionGroup(self)
        self._group.setExclusive(True)
        self._group.triggered.connect(self._select_tool)

        self._add_tools()
        self.addSeparator()
        self._add_actions(image)

        scheme = QApplication.styleHints().colorScheme()
        highlight_color = "#3b82f6" if scheme == Qt.ColorScheme.Dark else "#bfdbfe"

        self.setToolTip("Toolbar")
        self.setIconSize(QSize(20, 20))
        self.setMovable(False)
        self.setEnabled(False)
        self.setFloatable(False)
        self.setStyleSheet(f"""
            QToolButton:checked {{
                background-color: {highlight_color};
                border-radius: 4px;
                border: none;
            }}
        """)

    def _add_tools(self):
        self._add_tool(
            name="None",
            icon="cursor.svg",
            tool=self._tools.none,
            checked=True,
        )
        self._add_tool(
            name="Pan",
            icon="drag.svg",
            tool=self._tools.pan,
        )
        self._add_tool(
            name="Inspect",
            icon="hand-point.svg",
            tool=self._tools.inspect,
        )
        self._add_tool(
            name="Select Area",
            icon="select.svg",
            tool=self._tools.area,
        )
        self._add_tool(
            name="Zoom",
            icon="zoom.svg",
            tool=self._tools.zoom,
        )

    def _add_tool(self, name: str, icon: str, tool: Tool, checked: bool = False):
        action = QAction(ThemeIcon(icon), name, self)
        action.setData(tool)

        action.setCheckable(True)
        action.setChecked(checked)

        self._group.addAction(action)
        self.addAction(action)

    def _add_actions(self, image: ImageView):
        self._add_action(
            name="Rotate Left",
            icon="rotate-left.svg",
            slot=lambda: image.rotate_left(),
        )
        self._add_action(
            name="Rotate Right",
            icon="rotate-right.svg",
            slot=lambda: image.rotate_right(),
        )
        self._add_action(
            name="Flip Horizontal",
            icon="flip-horizontal.svg",
            slot=lambda: image.flip_horizontally(),
        )
        self._add_action(
            name="Flip Vertical",
            icon="flip-vertical.svg",
            slot=lambda: image.flip_vertically(),
        )
        self._add_action(
            name="Zoom In",
            icon="zoom-in.svg",
            slot=lambda: image.zoom_in(),
        )
        self._add_action(
            name="Zoom Out",
            icon="zoom-out.svg",
            slot=lambda: image.zoom_out(),
        )

    def _add_action(self, name: str, icon: str, slot):
        action = QAction(ThemeIcon(icon), name, self)
        action.triggered.connect(slot)
        self.addAction(action)

    @Slot()
    def _select_tool(self, action: QAction):
        tool: Tool = action.data()
        self._tools.set(tool)
