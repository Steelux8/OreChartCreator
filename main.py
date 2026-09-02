from PyQt6.QtWidgets import QApplication
import sys
import os

# Import the dialog and your main app class
from modpack_selection_dialog import ModpackSelectionDialog # pyright: ignore[reportMissingImports]
from ore_chart_creator import OreChartApp  # Your main window class

MODPACKS = ["Enigmatica", "GTNH"]

def setup_bundled_graphviz():
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    
    graphviz_bin = os.path.join(base_dir, "graphviz_bin")
    
    if os.path.exists(graphviz_bin):
        os.environ["PATH"] = graphviz_bin + os.pathsep + os.environ["PATH"]

def main():
    setup_bundled_graphviz()

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
