APP_STYLESHEET = """
            QMainWindow, QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }

            /* path bar */
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 10px;
                color: #cdd6f4;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }

            /* all buttons base */
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #45475a;
                border: 1px solid #89b4fa;
            }
            QPushButton:pressed {
                background-color: #89b4fa;
                color: #1e1e2e;
            }

            /* browse button accent */
            QPushButton#browse_button {
                background-color: #89b4fa;
                color: #1e1e2e;
                font-weight: 600;
                border: none;
            }
            QPushButton#browse_button:hover {
                background-color: #b4befe;
            }

            /* delete button danger */
            QPushButton#delete_button {
                background-color: #f38ba8;
                color: #1e1e2e;
                font-weight: 600;
                border: none;
            }
            QPushButton#delete_button:hover {
                background-color: #eba0ac;
            }

            /* tree widget */
            QTreeWidget {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 8px;
                alternate-background-color: #1e1e2e;
                gridline-color: #313244;
            }
            QTreeWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #313244;
            }
            QTreeWidget::item:selected {
                background-color: #313244;
                color: #89b4fa;
            }
            QTreeWidget::item:hover {
                background-color: #2a2a3d;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #6c7086;
                border: none;
                border-bottom: 1px solid #313244;
                padding: 6px 4px;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 11px;
            }

            /* savings label */
            QLabel#savings_label {
                color: #a6e3a1;
                font-size: 13px;
                font-weight: 600;
                padding: 4px 0px;
            }

            /* path label */
            QLabel {
                color: #6c7086;
                font-size: 13px;
            }

            QTreeWidget::indicator {
            width: 16px;
                height: 16px;
            }
            QTreeWidget::indicator:checked {
                background-color: #89b4fa;
                border: 2px solid #89b4fa;
                border-radius: 3px;
            }
            QTreeWidget::indicator:unchecked {
                background-color: transparent;
                border: 2px solid #45475a;
                border-radius: 3px;
            }
        """