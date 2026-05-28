import pandas as pd
import yaml
import re

def _coerce_number(val):
    """Return int if val is a whole number, else float."""
    x = float(str(val).replace(",", "").strip())
    return int(x) if x.is_integer() else x

def parse_sheet(excel_path, sheet_name="Platline"):
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    recipes = []
    default_group = "Fuel Processing"
    i = 0
    recipe_index = 1
    found_first = False

    while i < len(df):
        row = df.iloc[i]

        if isinstance(row[1], str) and re.match(r"\d{2}:", row[1].strip()):
            if found_first and row[1].strip().startswith("01:"):
                break
            found_first = True

            method = row[1].strip()

            # Get group (optional, from row below)
            group = default_group
            group_candidate = df.iloc[i + 1, 1] if i + 1 < len(df) else None
            if isinstance(group_candidate, str) and group_candidate.strip():
                match = re.search(r"\((.*?)\)", group_candidate.strip())
                group = match.group(1).strip() if match else group_candidate.strip()
                print(f"🔹 Group override: '{group}' (from '{group_candidate}')")
            else:
                print(f"🔸 No group override, using default: '{group}'")

            # Inputs and outputs start one row below the method (your sheet already leaves col C/D/E/F empty on the group row)
            base_row = i + 1

            inputs = []
            j = base_row
            while j < len(df):
                input_name = df.iloc[j, 2]
                input_amount = df.iloc[j, 3]
                if pd.isna(input_name) or str(input_name).strip() == "":
                    break
                try:
                    amount = _coerce_number(input_amount)
                    inputs.append({"item": str(input_name).strip(), "amount": amount})
                except Exception as e:
                    print(f"⚠️ Skipping invalid input on row {j+1}: {input_name} ({input_amount}) - {e}")
                j += 1

            outputs = []
            k = base_row
            while k < len(df):
                output_name = df.iloc[k, 4]
                output_amount = df.iloc[k, 5]
                if pd.isna(output_name) or str(output_name).strip() == "":
                    break
                try:
                    amount = _coerce_number(output_amount)
                    outputs.append({"item": str(output_name).strip(), "amount": amount})
                except Exception as e:
                    print(f"⚠️ Skipping invalid output on row {k+1}: {output_name} ({output_amount}) - {e}")
                k += 1

            recipes.append({
                "id": f"recipe_{recipe_index:02}",
                "inputs": inputs,
                "outputs": outputs,
                "method": method,
                "group": group
            })
            recipe_index += 1

            # Skip past max of input/output rows (group row is harmless because C–F are blank there)
            i = max(j, k)
        else:
            i += 1

    return recipes

def save_as_yaml_with_header(data, output_file, title="Diesel → CBD Processing"):
    yaml_structure = {
        "title": title,
        "steps": data
    }

    class InlineListDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow=True, indentless=indentless)

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(
            yaml_structure,
            f,
            allow_unicode=True,
            sort_keys=False,
            indent=2,
            Dumper=InlineListDumper,
            default_flow_style=False
        )

# Example usage
excel_path = "sources/GTNH Documentation Spreadsheets.xlsx"
output_file = "recipes/platline.yml"

recipes = parse_sheet(excel_path)
save_as_yaml_with_header(recipes, output_file)

print(f"✅ YAML file saved to {output_file}")
