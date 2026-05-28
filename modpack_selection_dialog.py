from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton

class ModpackSelectionDialog(QDialog):
    def __init__(self, modpack_list):
        super().__init__()
        self.setWindowTitle("Select Modpack")
        self.selected_modpack = None

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Choose a modpack to begin:"))

        self.combo = QComboBox()
        self.combo.addItems(modpack_list)
        layout.addWidget(self.combo)

        confirm_btn = QPushButton("Continue")
        confirm_btn.clicked.connect(self.accept)
        layout.addWidget(confirm_btn)

        self.setLayout(layout)

    def accept(self):
        self.selected_modpack = self.combo.currentText()
        super().accept()
