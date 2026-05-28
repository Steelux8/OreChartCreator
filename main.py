from PyQt6.QtWidgets import QApplication
import sys

# Import the dialog and your main app class
from modpack_selection_dialog import ModpackSelectionDialog # pyright: ignore[reportMissingImports]
from ore_chart_creator import OreChartApp  # Your main window class

MODPACKS = ["Enigmatica", "GTNH"]

def main():
    app = QApplication(sys.argv)

    # Show modpack selection dialog
    dialog = ModpackSelectionDialog(MODPACKS)
    if dialog.exec():  # .exec() blocks until user selects and hits "Continue"
        selected_modpack = dialog.selected_modpack
        print(f"[INFO] User selected modpack: {selected_modpack}")

        # Pass it into your main window class
        assert selected_modpack is not None, "No modpack selected!"
        window = OreChartApp(modpack=selected_modpack)
        window.show()
        sys.exit(app.exec())
    else:
        print("[INFO] User cancelled modpack selection.")
        sys.exit(0)

if __name__ == "__main__":
    main()
