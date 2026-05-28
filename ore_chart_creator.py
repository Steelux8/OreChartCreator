import os
import sys
import yaml # type: ignore
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSizePolicy, QApplication,
    QCheckBox
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QSize
from PIL import Image
from graphviz import Digraph
from collections import defaultdict, deque
from typing import Optional
from datetime import datetime
import re
import hashlib

# === Constants ===
ores_crystallization_stage = [
    "iron", "gold", "copper", "tin", "silver", "lead", "quartz", "aluminium",
    "ardite", "astralstarmetal", "boron", "cobalt", "draconium", "iridium",
    "lithium", "magnesium", "mithril", "nickel", "osmium", "platinum",
    "thorium", "titanium", "tungsten", "uranium", "amber", "amethyst",
    "apatite", "aquamarine", "certusquartz", "chargedcertusquartz", "coal",
    "diamond", "dilithium", "dimensionalshard", "emerald", "lapis",
    "malachite", "peridot", "quartzblack", "ruby", "sapphire", "tanzanite",
    "topaz", "trinitite", "anglesite", "benitoite", "redstone"
]

ores_with_mekanism_processing = [
    "copper", "gold", "iron", "lead", "silver", "tin",
    "uranium", "aluminium", "ardite", "astralstarmetal", "boron", "cobalt",
    "draconium", "iridium", "lithium", "magnesium", "mithril", "nickel",
    "osmium", "platinum", "thorium", "tungsten", "titanium"
]

ores_with_purified_crushed = [
    "copper", "gold", "iron", "lead", "silver", "tin",
    "uranium", "aluminium", "ardite", "astralstarmetal", "boron", "cobalt",
    "draconium", "iridium", "lithium", "magnesium", "mithril", "nickel",
    "osmium", "platinum", "thorium", "tungsten"
]

ORE_DISPLAY_NAMES = {
    "amethyst": "Amethyst",
    "aquamarine": "Aquamarine",
    "ardite": "Ardite",
    "astralstarmetal": "Astral Star Metal",
    "aluminium": "Aluminium",
    "amber": "Amber",
    "anglesite": "Anglesite",
    "apatite": "Apatite",
    "benitoite": "Benitoite",
    "boron": "Boron",
    "certus_quartz": "Certus Quartz",
    "charged_certus_quartz": "Charged Certus Quartz",
    "coal": "Coal",
    "cobalt": "Cobalt",
    "copper": "Copper",
    "diamond": "Diamond",
    "dilithium": "Dilithium",
    "dimensionalshard": "Dimensional Shard",
    "draconium": "Draconium",
    "emerald": "Emerald",
    "gold": "Gold",
    "iridium": "Iridium",
    "iron": "Iron",
    "lapis": "Lapis Lazuli",
    "lead": "Lead",
    "lithium": "Lithium",
    "magnesium": "Magnesium",
    "malachite": "Malachite",
    "mithril": "Mithril",
    "nickel": "Nickel",
    "osmium": "Osmium",
    "peridot": "Peridot",
    "platinum": "Platinum",
    "quartz": "Quartz",
    "quartzblack": "Black Quartz",
    "redstone": "Redstone",
    "ruby": "Ruby",
    "sapphire": "Sapphire",
    "silver": "Silver",
    "tanzanite": "Tanzanite",
    "thorium": "Thorium",
    "tin": "Tin",
    "titanium": "Titanium",
    "topaz": "Topaz",
    "trinitite": "Trinitite",
    "tungsten": "Tungsten",
    "uranium": "Uranium",
}

current_ore = "aluminium"

ORE_BYPRODUCTS = {
    "aluminium": ["iron", "aquamarine", "sapphire"],
    "amber": ["iron", "diamond", "certus_quartz"],
    "amethyst": ["cobalt", "charged_certus_quartz", "astralstarmetal"],
    "anglesite": ["trinitite", "dimensionalshard", "dilithium"],
    "apatite": ["aluminium", "magnesium", "thorium"],
    "aquamarine": ["aluminium", "emerald", "titanium"],
    "ardite": ["osmium", "gold", "topaz"],
    "astralstarmetal": ["silver", "tungsten", "sapphire"],
    "benitoite": ["trinitite", "dimensionalshard", "dilithium"],
    "boron": ["magnesium", "lithium", "quartzblack"],
    "certus_quartz": ["nether_quartz", "diamond", "lapis"],
    "charged_certus_quartz": ["diamond", "topaz", "dimensionalshard"],
    "coal": ["quartzblack", "nether_quartz", "certus_quartz"],
    "cobalt": ["iron", "nickel", "boron"],
    "copper": ["tin", "gold", "iron"],
    "diamond": ["certus_quartz", "malachite", "sapphire"],
    "dilithium": ["lithium", "dimensionalshard", "astralstarmetal"],
    "dimensionalshard": ["astralstarmetal", "peridot", "tanzanite"],
    "draconium": ["ardite", "astralstarmetal", "amethyst"],
    "emerald": ["peridot", "tanzanite", "malachite"],
    "gold": ["silver", "aluminium", "manainfusedmetal"],
    "iridium": ["platinum", "osmium", "dimensionalshard"],
    "iron": ["nickel", "gold", "tin"],
    "lapis": ["apatite", "sapphire", "diamond"],
    "lead": ["copper", "silver", "uranium"],
    "lithium": ["aluminium", "topaz", "apatite"],
    "magnesium": ["iron", "copper", "nickel"],
    "malachite": ["lapis", "copper", "tungsten"],
    "mithril": ["gold", "astralstarmetal", "manainfusedmetal"],
    "nickel": ["platinum", "osmium", "cobalt"],
    "osmium": ["nickel", "platinum", "iridium"],
    "peridot": ["emerald", "diamond", "magnesium"],
    "platinum": ["nickel", "iridium", "draconium"],
    "quartz": ["iron", "diamond", "amethyst"],
    "quartzblack": ["coal", "aquamarine", "topaz"],
    "redstone": ["coal", "quartzblack", "certus_quartz"],
    "ruby": ["aluminium", "magnesium", "sapphire"],
    "sapphire": ["aluminium", "draconium", "titanium"],
    "silver": ["lead", "gold", "iridium"],
    "tanzanite": ["nether_quartz", "diamond", "amethyst"],
    "thorium": ["uranium", "boron", "titanium"],
    "tin": ["iron", "lead", "copper"],
    "titanium": ["tungsten", "magnesium", "ardite"],
    "topaz": ["quartzblack", "nether_quartz", "diamond"],
    "trinitite": ["trinitite", "trinitite", "trinitite"],
    "tungsten": ["magnesium", "iridium", "titanium"],
    "uranium": ["lead", "lithium", "thorium"],
}

BYPRODUCT_MULTIPLIERS = {
    "aquamarine": 4.0,
    "sapphire": 2.0,
    "topaz": 2.0,
    "quartzblack": 2.0,
    "amethyst": 2.0,
    "dimensionalshard": 3.0,
    "apatite": 10.0,
    "diamond": 2.0,
    "certus_quartz": 3.0,
    "charged_certus_quartz": 2.0,
    "emerald": 2.0,
    "nether_quartz": 3.0,
    "lapis": 10.0,
    "malachite": 2.0,
    "peridot": 2.0,
    "tanzanite": 2.0,
    "coal": 5.0,
    # Add more as needed
}

GRINDING_BALL_OPTIONS = {
    "Iron Alloy (100%/33%)": {"main_output_pct": 100, "byproduct_output_pct": 33},
    "Redstone Alloy (100%/100%)": {"main_output_pct": 100, "byproduct_output_pct": 100},
    "Pulsating Iron (100%/185%)": {"main_output_pct": 100, "byproduct_output_pct": 185},
    "Neutronium (100%/500%)": {"main_output_pct": 100, "byproduct_output_pct": 500},
    "Lumium (110%/215%)": {"main_output_pct": 110, "byproduct_output_pct": 215},
    "Soularium (120%/215%)": {"main_output_pct": 120, "byproduct_output_pct": 215},
    "Energetic Alloy (160%/110%)": {"main_output_pct": 160, "byproduct_output_pct": 110},
    "Signalum (120%/165%)": {"main_output_pct": 120, "byproduct_output_pct": 165},
    "Conductive Iron (135%/100%)": {"main_output_pct": 135, "byproduct_output_pct": 100},
    "Dark Steel (135%/200%)": {"main_output_pct": 135, "byproduct_output_pct": 200},
    "End Steel (140%/240%)": {"main_output_pct": 140, "byproduct_output_pct": 240},
    "Vibrant Alloy (175%/135%)": {"main_output_pct": 175, "byproduct_output_pct": 135},
    "Crystalline Pink Slime (175%/155%)": {"main_output_pct": 175, "byproduct_output_pct": 155},
    "Vivid Alloy (175%/135%)": {"main_output_pct": 175, "byproduct_output_pct": 135},
    "Crystalline Alloy (180%/140%)": {"main_output_pct": 180, "byproduct_output_pct": 140},
    "Melodic Alloy (200%/145%)": {"main_output_pct": 200, "byproduct_output_pct": 145},
    "Enderium (165%/145%)": {"main_output_pct": 165, "byproduct_output_pct": 145},
    "Stellar Alloy (230%/225%)": {"main_output_pct": 230, "byproduct_output_pct": 225},
    "Infinity (500%/500%)": {"main_output_pct": 500, "byproduct_output_pct": 500},
}

has_ic2_path_for_current_ore = False
has_mekanism_path_for_current_ore = False

DEFAULT_YAML = "recipes/default.yml"
RECIPE_DIR = "recipes"
GRAPH_OUTPUT_DIR = "graphs"
forced_side_nodes = [
    "Water", 
    "Chlorine", 
    "Ammonia", 
    "Salt", 
    "Diluted Sulfuric Acid", 
    "Sulfuric Acid", 
    "Hydrogen", 
    "Oxygen", 
    "Nitrogen", 
    "Hydrochloric Acid", 
    "Salt Water",
]

verbose = False
_log_file_path = None

os.makedirs(GRAPH_OUTPUT_DIR, exist_ok=True)


LIGHT_BANDS = ["+0", "-1"]  # tags, not real math—just to pick a variant

PALETTE_BASE = [
    "#A6E1FF", "#FFAFCC", "#CAFFBF", "#FFD166", "#CDB4FF", "#9BF6A3",
    "#BDE0FE", "#FF9AA2", "#F3C4FF", "#FFBC8A", "#8EE3F5", "#B5E48C",
]

# Precompute a lighter and a slightly darker variant of each base color.
# (If you don’t want to implement real HSL tweaking, just hand-pick pairs.)
EDGE_PALETTE = {
    "+0": [  # brighter band
        "#CDEEFF","#FFD7E4","#E6FFE8","#FFE8A6","#E7DCFF","#CFFBD5",
        "#E6F3FF","#FFC1C7","#F7DAFF","#FFD9BF","#CFF5FF","#D5F5BC",
    ],
    "-1": [  # slightly dimmer band
        "#98D5F2","#F5A9C2","#B9E6C1","#F5C958","#B9A6F5","#89E9A0",
        "#A9CFF0","#F28B96","#E5B1F1","#F5B98E","#89DDE9","#9ED780",
    ],
}

def color_for_key(key: str) -> str:
    if not key:
        return "#ffffff"
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
    band = LIGHT_BANDS[h % len(LIGHT_BANDS)]
    idx = (h // len(LIGHT_BANDS)) % len(PALETTE_BASE)
    return EDGE_PALETTE[band][idx]

def is_step_valid_for_ore(ore: str, from_node: str, to_node: str, method: str, group: str) -> bool:
    if (group == "IC2" or from_node == "Purified Crushed Ore") and not has_ic2_path_for_current_ore:
        return False
    
    if group == "Mekanism" and not has_mekanism_path_for_current_ore:
        return False

    if method == "Uranium Thermal Cent." and ore != "uranium":
        return False
    
    return True

# === Graph Logic ===
def load_chain_from_yaml(file_path, ore):
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    steps = data.get("steps", [])
    chain = []

    for step in steps:
        from_node = step["from"]
        to_node = step["to"]
        label = step["label"]
        method = step.get("method", None)
        group = step.get("group", None)
        byproducts = step.get("byproducts", [])

        if not is_step_valid_for_ore(ore, from_node, to_node, method, group):
            continue

        kind = "step"
        extra = {
            "method": method,
            "group": group,
            "byproducts": byproducts
        }

        # Main step
        chain.append((from_node, to_node, label, kind, extra))

    return chain

def load_chain_from_yaml_complex(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    steps = data.get("steps", [])
    chain = []

    for step in steps:
        inputs = step.get("inputs", [])
        outputs = step.get("outputs", [])
        method = step.get("method", None)
        group = step.get("group", None)
        byproducts = step.get("byproducts", [])

        if not inputs or not outputs:
            continue  # Skip malformed steps

        for inp in inputs:
            from_node = inp["item"]
            in_amount = inp["amount"]

            for out in outputs:
                to_node = out["item"]
                out_amount = out["amount"]

                label = f"{in_amount}:{out_amount}"

                chain.append((
                    from_node,
                    to_node,
                    label,
                    "step",
                    {
                        "method": method,
                        "group": group,
                        "byproducts": byproducts
                    }
                ))

    return chain


def build_label_string(inputs, outputs):
    input_sum = sum(i["amount"] for i in inputs)
    output_parts = [str(o["amount"]) for o in outputs]
    return f"{input_sum}:" + "+".join(output_parts)

def evaluate_alternate_ingot_paths(
    chain,
    input_item="Ore Block",
    input_amount=1,
    allowed_dirty_ore_source="Alchemical Dust",
    forced_dust_method="SAG Mill",
    purified_crushed_path=False,
    verbose=False
):
    debug("\n=== [DEBUG] evaluate_alternate_ingot_paths ===")
    debug(f"→ Input: {input_amount} x {input_item}")
    debug(f"→ Only '{allowed_dirty_ore_source}' can be converted into Dirty Ore")
    debug(f"→ Force dusting method: {forced_dust_method}\n")

    graph = defaultdict(list)
    assert current_ore, "current_ore must be set before processing chain"

    # Build graph
    for idx, step in enumerate(chain):
        if len(step) != 5:
            debug(f"[{idx}] ⚠️ Skipping malformed step: {step}")
            continue

        from_node, to_node, label, kind, extra = step
        method = extra.get("method", "")

        if kind == "byproduct":
            debug(f"[{idx}] Skipping byproduct: {from_node} -> {to_node}")
            continue

        try:
            if ":" in label:
                input_amt, output_amt = map(float, label.split(":"))
                ratio = output_amt / input_amt
            else:
                ratio = float(label)
                input_amt = 1
                output_amt = ratio
        except:
            debug(f"[{idx}] ⚠️ Invalid ratio label: {label}")
            continue

        if to_node == "Dirty Ore" and from_node != allowed_dirty_ore_source:
            debug(f"[{idx}] ❌ Skipping forbidden Dirty Ore conversion: {from_node} -> Dirty Ore")
            continue

        graph[from_node].append((to_node, ratio, method, extra))
        debug(f"[{idx}] {from_node} -> {to_node} via {method} | Ratio {output_amt}/{input_amt} = {ratio:.4f}")

    potential_outputs = defaultdict(float)
    inventory = defaultdict(float)
    inventory[input_item] = input_amount
    queue = deque([input_item])
    chosen_path = []

    debug("\n=== Traversal ===")
    while queue:
        current = queue.popleft()
        amount = inventory[current]
        next_step = None

        if amount <= 0:
            continue

        debug(f"\n🔄 Processing: {current} (amount: {amount:.4f})")

        if current not in graph:
            debug(f"  ⚠️ No outgoing steps from {current}")
            continue

        # Force Dirty Ore conversion from allowed source
        if current == allowed_dirty_ore_source:
            next_step = next(
                ((to_node, ratio, method, extra) for to_node, ratio, method, extra in graph[current] if to_node == "Dirty Ore"),
                None
            )

        # Force Dusting method if converting Dirty Ore
        if current == "Dirty Ore":
            next_step = next(
                ((to_node, ratio, method, extra) for to_node, ratio, method, extra in graph[current] if method == forced_dust_method),
                None
            )

        elif current == "Dirty Ore Dust":
            target_node = "Purified Crushed Ore" if purified_crushed_path else "Ore Dust"

            next_step = next(
                ((to_node, ratio, method, extra) for to_node, ratio, method, extra in graph[current] if to_node == target_node),
                None
            )

        if next_step is None:
            # Default greedy choice for no forced steps
            max_output = -1
            for to_node, ratio, method, extra in graph[current]:
                output = amount * ratio
                if output > max_output:
                    max_output = output
                    next_step = (to_node, ratio, method, extra)

        if next_step is None:
            # No valid outgoing steps found
            debug(f"  ⚠️ No valid outgoing steps from {current}")
            continue

        to_node, ratio, method, extra = next_step
        output = amount * ratio
        debug(f"  ✅ Chosen path: {current} -> {to_node} via {method} | {amount:.4f} * {ratio:.4f} = {output:.4f}")
        potential_outputs[(to_node, method)] += output
        inventory[to_node] += output
        queue.append(to_node)
        chosen_path.append((current, to_node, method))
        inventory[current] = 0

        # Handle byproducts
        byproducts = extra.get("byproducts", [])
        for byp in byproducts:
            label = byp.get("label", "1:1")
            item = byp.get("item", "")
            try:
                _, right = label.split(":")
                base_output = float(right) * amount
            except:
                base_output = 0

            indices = []

            # Case 1: item is already a resolved byproduct name
            if item in ORE_BYPRODUCTS.get(current_ore, []):
                indices = [ORE_BYPRODUCTS[current_ore].index(item) + 1]

            # Case 2: matches placeholder patterns like "Byp. Dusts (1,2,3)"
            else:
                match_multi = re.match(r"Byp\. Dusts \((\d+(?:,\d+)+)\)", item)
                match_single = re.match(r"Byp\. Dusts \((\d+)\)", item)

                if match_multi:
                    indices = [int(x) for x in match_multi.group(1).split(",")]
                elif match_single:
                    indices = [int(match_single.group(1))]
                else:
                    print(f"  ⚠️ Unknown byproduct format: {item} in {current} -> {to_node}")
                    continue

            # Accumulate outputs
            for idx in indices:
                info = get_ordered_byproduct_info(current_ore, idx)
                if info:
                    name = info["name"]
                    final_output = base_output
                    potential_outputs[(name, method)] += final_output

    debug("\n=== Final Inventory ===")
    for k, v in inventory.items():
        debug(f"  {k}: {v:.4f}")

    debug("\n=== Ore Ingot Output by Method ===")
    ore_ingot_outputs = {
        method: amount
        for (item, method), amount in potential_outputs.items()
        if item == "Ore Ingot"
    }

    for method, amount in ore_ingot_outputs.items():
        debug(f"  {method}: {amount:.4f}")

    byproduct_outputs = {}

    if current_ore in ORE_BYPRODUCTS:
        for idx, name in enumerate(ORE_BYPRODUCTS[current_ore], 1):
            byproduct_outputs[name] = sum(
                amount for (item, method), amount in potential_outputs.items()
                if item == name
            )

    debug("\n=== Byproduct Outputs ===")
    for name, amount in byproduct_outputs.items():
        debug(f"  {name}: {amount:.4f}")

    total = sum(ore_ingot_outputs.values())
    return total, chosen_path, byproduct_outputs

def apply_processing_modifiers(chain, modifiers):
    """
    Adjusts the chain in-place or returns a modified version, applying multipliers or replacements
    based on user-selected processing modifiers.
    """
    adjusted_chain = []
    assert current_ore, "current_ore must be set before processing byproducts"

    for step in chain:
        if len(step) != 5:
            adjusted_chain.append(step)
            continue

        from_node, to_node, label, kind, extra = step
        method = extra.get("method", "")

        # Example: Modify SAG Mill ratios
        if method == "SAG Mill" and kind != "byproduct":
            ratio = parse_ratio(label)
            ratio *= modifiers.get("sag_multiplier", 1.0)
            label = format_ratio(ratio)

        # Example: Modify final smelting outputs
        if method == "Smelting":
            ratio = parse_ratio(label)

            if modifiers.get("infinity_furnace", False):
                ratio *= 4
                if ratio > 64:
                    ratio = 64.0

            label = format_ratio(ratio)

        # Adjust byproducts too
        # Apply byproduct resolution and multiplier scaling
        if "byproducts" in extra:
            resolved_byproducts = []
            for byp in extra["byproducts"]:
                item = byp.get("item", "")
                byp_label = byp.get("label", "1:1")

                # Apply global SAG byproduct multiplier, if present
                if method == "SAG Mill" and "sag_byproduct_multiplier" in modifiers:
                    byp_label = apply_multiplier_to_ratio(byp_label, modifiers["sag_byproduct_multiplier"])

                match_multi = re.match(r"Byp\. Dusts \((\d+,\d+(?:,\d+)*)\)", item)
                match_single = re.match(r"Byp\. Dusts \((\d+)\)", item)

                if match_multi:
                    indices = [int(x) for x in match_multi.group(1).split(",")]
                    for idx in indices:
                        info = get_ordered_byproduct_info(current_ore, idx)
                        if info:
                            new_label = apply_multiplier_to_ratio(byp_label, info["multiplier"])
                            resolved_byproducts.append({
                                "item": info["name"],
                                "label": new_label
                            })
                        else:
                            resolved_byproducts.append({
                                "item": f"Byp. Dusts ({idx})",
                                "label": label
                            })
                elif match_single:
                    idx = int(match_single.group(1))
                    info = get_ordered_byproduct_info(current_ore, idx)
                    if info:
                        resolved_byproducts.append({
                            "item": info["name"],
                            "label": byp_label  # still use the original
                        })
                    else:
                        resolved_byproducts.append({
                            "item": f"Byp. Dusts ({idx})",
                            "label": label
                        })
                else:
                    # Leave unknown or already-resolved items untouched
                    resolved_byproducts.append(byp)

            # Replace the original byproducts list
            extra["byproducts"] = resolved_byproducts

        adjusted_chain.append((from_node, to_node, label, kind, extra))

    return adjusted_chain

def parse_ratio(label):
    try:
        if ":" in label:
            a, b = map(float, label.split(":"))
            return b / a
        return float(label)
    except:
        return 1.0  # default fallback

def format_ratio(ratio):
    return f"1:{round(ratio, 4)}"


def debug(msg):
    global _log_file_path

    # Ensure logs folder exists
    os.makedirs("logs", exist_ok=True)

    # Create the log file path if not already done
    if _log_file_path is None:
        timestamp = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
        _log_file_path = os.path.join("logs", f"debug_{timestamp}.log")

    # Always append to the file
    with open(_log_file_path, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

    # Only print to console if verbose
    if verbose:
        print(msg)

def generate_graph_with_subgraphs(chain, output_file="temp_graph.png", used_steps=None, highlight_used=True):
    global current_ore

    dot = Digraph(format="png")
    dot.attr(rankdir="TB", ranksep="0.75", nodesep="0.5")

    group_map = defaultdict(list)
    defined_nodes = set()
    used_edges = set()
    used_nodes = set()

    # Track used steps for highlighting
    if used_steps:
        for step in used_steps:
            if len(step) >= 3:
                from_node, to_node, method = step[0], step[1], step[2]
                used_edges.add((from_node, to_node, method))
                used_nodes.add(from_node)
                used_nodes.add(to_node)

                # Mark related byproduct edges
                for item in chain:
                    if len(item) == 5:
                        f, t, _, k, extra = item
                        if f == from_node and t == to_node and extra.get("method") == method:
                            for byp in extra.get("byproducts", []):
                                byp_item = byp.get("item")
                                if byp_item:
                                    used_edges.add((to_node, byp_item, method))
                                    used_nodes.add(byp_item)

    # Group steps
    for item in chain:
        if len(item) != 5:
            raise ValueError("Each chain item must have 5 elements.")
        from_node, to_node, base_label, kind, extra = item
        method = extra.get("method", "Unknown")
        group = extra.get("group", "Ungrouped")
        group_map[group].append((from_node, to_node, base_label, kind, method, extra))

    # Draw graph
    for group_name, edges in group_map.items():
        g = Digraph(name=f"cluster_{group_name}")
        g.attr(label=group_name, style="dashed", color="gray")

        for from_node, to_node, base_label, kind, method, extra in edges:
            edge_style = "dashed" if kind == "byproduct" else "solid"
            is_used = (from_node, to_node, method) in used_edges
            edge_color = "red" if is_used and highlight_used else "black"
            penwidth = "2" if is_used and highlight_used else "1"

            # Base label
            full_label = f"{base_label} ({method})" if method not in ("Smelting", "Special Smelting", "Unknown") else base_label

            byproducts = extra.get("byproducts", [])
            if byproducts:
                extra_lines = []
                for byp in byproducts:
                    item = byp.get("item", "")
                    label = byp.get("label", "?")
                    display_name = ORE_DISPLAY_NAMES.get(item, item.replace("_", " ").title())
                    extra_lines.append(f"+ {label} → {display_name}")

                full_label += "\\n" + "\\n".join(extra_lines)

            # Nodes
            for node in (from_node, to_node):
                if node not in defined_nodes:
                    node_attrs = {"shape": "ellipse"}
                    if node in used_nodes and highlight_used:
                        node_attrs["color"] = "red"
                        node_attrs["penwidth"] = "2"
                    g.node(node, **node_attrs)
                    defined_nodes.add(node)

            # Edge
            g.edge(from_node, to_node, label=full_label, style=edge_style, color=edge_color, penwidth=penwidth)

        dot.subgraph(g)

    dot.render(output_file, cleanup=True)
    return output_file + ".png"

def generate_graph_with_subgraphs_complex(
    chain,
    output_file="temp_graph.png",
    used_steps=None,
    highlight_used=True,
    chain_inputs=None,
    chain_outputs=None,
    forced_sides=None
):
    from graphviz import Digraph
    from collections import defaultdict, Counter

    chain_inputs = set(chain_inputs or [])
    chain_outputs = set(chain_outputs or [])
    forced_sides = set(forced_sides or [])

    for edge in chain:
        from_node, to_node, *_ = edge
        if not from_node or not to_node or not isinstance(from_node, str) or not isinstance(to_node, str):
            print("❌ Invalid edge:", edge)

    debug("\n=== STARTING GRAPH GENERATION ===")
    debug(f"Chain inputs: {chain_inputs}")
    debug(f"Chain outputs: {chain_outputs}")
    debug(f"Forced side materials: {forced_sides}")

    dot = Digraph(format="png")
    dot.attr(
        rankdir="TB",
        ranksep="0.75",
        nodesep="0.5",
        bgcolor="#1f1f1f",         # dark grey background
    )

    # keep nodes highly readable on dark bg
    NODE_DEFAULTS = {
        "shape": "ellipse",
        "style": "filled",
        "fillcolor": "#ffffff",
        "color": "#cccccc",        # outline
        "fontcolor": "#111111",
    }

    # default edge style on dark bg
    EDGE_DEFAULTS = {
        "color": "#ffffff",
        "fontcolor": "#ffffff",    # label color
}

    group_map = defaultdict(list)
    defined_nodes = set()
    used_edges = set()
    used_nodes = set()

    if used_steps:
        for step in used_steps:
            if len(step) >= 3:
                from_node, to_node, method = step[0], step[1], step[2]
                used_edges.add((from_node, to_node, method))
                used_nodes.update([from_node, to_node])

    # Identify all inputs/outputs
    all_inputs = Counter()
    all_outputs = Counter()
    for item in chain:
        if len(item) != 5:
            raise ValueError("Each chain item must have 5 elements.")
        from_node, to_node, *_ = item
        all_inputs[from_node] += 1
        all_outputs[to_node] += 1

    # Side classification (plus manual forced sides)
    side_inputs = ((set(all_inputs) - set(all_outputs)) | (forced_sides & set(all_inputs))) - chain_inputs
    side_outputs = ((set(all_outputs) - set(all_inputs)) | (forced_sides & set(all_outputs))) - chain_outputs

    debug(f"Detected side inputs: {side_inputs}")
    debug(f"Detected side outputs: {side_outputs}")

    # Map: to_node -> list of side inputs feeding it
    side_inputs_per_target = defaultdict(set)
    for item in chain:
        from_node, to_node, *_ = item
        if from_node in side_inputs and from_node not in chain_inputs:
            side_inputs_per_target[to_node].add(from_node)

    # Map: from_node -> list of side outputs it creates
    side_outputs_per_source = defaultdict(set)
    for item in chain:
        from_node, to_node, *_ = item
        if to_node in side_outputs and to_node not in chain_outputs:
            side_outputs_per_source[from_node].add(to_node)

    debug(f"Side inputs per target:")
    for target, inputs in side_inputs_per_target.items():
        debug(f"  {target}: {inputs}")

    # Group edges
    for item in chain:
        from_node, to_node, base_label, kind, extra = item
        method = extra.get("method", "Unknown")
        group = extra.get("group", "Ungrouped")
        group_map[group].append((from_node, to_node, base_label, kind, method, extra))

    for group_name, edges in group_map.items():
        g = Digraph(name=f"cluster_{group_name}")
        g.attr(
            label=group_name,
            style="dashed",
            color="#888888",      # cluster border
            fontcolor="#e0e0e0",  # cluster title
        )
        debug(f"\nProcessing group: {group_name}")

        # === Decide per-recipe forcing (one visible node minimum) ===
        by_method = defaultdict(list)
        for from_node, to_node, base_label, kind, method, extra in edges:
            by_method[method].append((from_node, to_node))

        forced_from_node_for_method = {}
        forced_to_node_for_method = {}
        suppress_method = set()  # <-- NEW

        for method, pairs in by_method.items():
            recipe_froms = [f for f, _ in pairs]
            recipe_tos   = [t for _, t in pairs]

            all_inputs_hidden  = all((f in side_inputs and f not in chain_inputs) for f in recipe_froms)
            all_outputs_hidden = all((t in side_outputs and t not in chain_outputs) for t in recipe_tos)

            # NEW: if *every* endpoint is a forced side, and none is explicitly kept, hide the recipe
            all_endpoints_forced = all(x in forced_sides for x in (recipe_froms + recipe_tos))
            any_explicit_keep = any(x in chain_inputs for x in recipe_froms) or any(x in chain_outputs for x in recipe_tos)

            if all_inputs_hidden and all_outputs_hidden and all_endpoints_forced and not any_explicit_keep:
                suppress_method.add(method)
                debug(f"  [HIDE] Method '{method}': all endpoints are forced sides; suppressing entirely.")
                continue

            if all_inputs_hidden and not all_outputs_hidden and recipe_froms:
                forced_from_node_for_method[method] = recipe_froms[0]
                debug(f"  [FORCE] Method '{method}': forcing input node '{recipe_froms[0]}' so recipe appears.")
            elif all_outputs_hidden and not all_inputs_hidden and recipe_tos:
                forced_to_node_for_method[method] = recipe_tos[0]
                debug(f"  [FORCE] Method '{method}': forcing output node '{recipe_tos[0]}' so recipe appears.")
            elif all_inputs_hidden and all_outputs_hidden and recipe_froms:
                # Bridge case (not all endpoints are in forced_sides)
                forced_from_node_for_method[method] = recipe_froms[0]
                debug(f"  [FORCE] Method '{method}': both sides hidden; forcing input '{recipe_froms[0]}'.")

        # === Render with de-dup of labels for forced nodes ===
        for from_node, to_node, base_label, kind, method, extra in edges:
            if method in suppress_method:          # <-- NEW
                debug(f"  [HIDE] Skipping edges of method '{method}' (suppressed).")
                continue

            edge_style = "dashed" if kind == "byproduct" else "solid"
            is_used = (from_node, to_node, method) in used_edges
            # pick a stable light color per recipe (method)
            method_color = color_for_key(method)

            # preserve your highlight color on top of the theme
            edge_color = "#ff4d4d" if (is_used and highlight_used) else method_color

            # ensure labels are readable regardless of edge color
            edge_fontcolor = edge_color
            penwidth = "2" if is_used and highlight_used else "1"

            from_is_side = (from_node in side_inputs and from_node not in chain_inputs)
            to_is_side   = (to_node in side_outputs and to_node not in chain_outputs)

            force_from = forced_from_node_for_method.get(method)
            force_to   = forced_to_node_for_method.get(method)

            # Will these endpoints actually render as nodes?
            will_render_from = (not from_is_side) or (from_node in chain_inputs) or (force_from == from_node)
            will_render_to   = (not to_is_side)   or (to_node in chain_outputs)   or (force_to == to_node)

            label_lines = []

            # Side input labels -> for target 'to_node'
            if side_inputs_per_target.get(to_node):
                for si in sorted(side_inputs_per_target[to_node]):  # sort for stable output
                    # Skip if that side-input will be rendered as a node for this recipe
                    if (si == from_node and will_render_from) or (si == force_from):
                        continue
                    label_lines.append(f"+ {si.replace('_', ' ').title()}")
                    debug(f"  Appending side input label to edge {from_node} → {to_node}: + {si}")

            # Base label
            label_lines.append(base_label)

            # Side output labels -> from source 'from_node'
            if side_outputs_per_source.get(from_node):
                for so in sorted(side_outputs_per_source[from_node]):  # sort for stable output
                    # Skip if that side-output is being shown as a rendered node for this recipe
                    if (so == to_node and will_render_to) or (so == force_to):
                        continue
                    label_lines.append(f"+ {so.replace('_', ' ').title()}")
                    debug(f"  Appending side output label to edge {from_node} → {to_node}: + {so}")

            final_label = "\n".join(label_lines)

            # Ensure nodes are present if needed (including forced)
            must_render_from = (from_node not in defined_nodes) and will_render_from
            must_render_to   = (to_node   not in defined_nodes) and will_render_to

            if must_render_from:
                debug(f"  FORCING render of node: {from_node} (from)")
                attrs = dict(NODE_DEFAULTS)          # base dark-theme node style
                if from_node in used_nodes and highlight_used:
                    attrs["color"] = "#ff4d4d"       # highlight outline
                    attrs["penwidth"] = "2"
                g.node(from_node, **attrs)
                defined_nodes.add(from_node)

            if must_render_to:
                debug(f"  FORCING render of node: {to_node} (to)")
                attrs = dict(NODE_DEFAULTS)
                if to_node in used_nodes and highlight_used:
                    attrs["color"] = "#ff4d4d"
                    attrs["penwidth"] = "2"
                g.node(to_node, **attrs)
                defined_nodes.add(to_node)

            # Render edge only when the "other" endpoint is actually visible.
            render_edge = False

            # Case 1: both endpoints are naturally visible
            if not from_is_side and not to_is_side:
                render_edge = True
            else:
                # Case 2: FROM is the forced endpoint — only draw to a visible/kept TO
                if force_from == from_node and (
                    not to_is_side or (to_node in chain_outputs) or (force_to == to_node)
                ):
                    render_edge = True

                # Case 3: TO is the forced endpoint — only draw from a visible/kept FROM
                if force_to == to_node and (
                    not from_is_side or (from_node in chain_inputs) or (force_from == from_node)
                ):
                    render_edge = True

            if render_edge:
                debug(f"  ✅ Rendering edge: {from_node} → {to_node}")
                g.edge(
                    from_node,
                    to_node,
                    label=final_label,
                    style=edge_style,
                    color=edge_color,
                    penwidth=penwidth,
                    fontcolor=edge_fontcolor,
                )
            else:
                debug(f"  ⛔ Skipping edge: {from_node} → {to_node} (from_is_side={from_is_side}, to_is_side={to_is_side})")

        dot.subgraph(g)

    dot.render(output_file, cleanup=True)
    debug(f"\n=== GRAPH WRITTEN TO {output_file}.png ===\n")
    return output_file + ".png"

def get_ordered_byproduct_info(ore: str, index: int) -> dict | None:
    byproduct_names = ORE_BYPRODUCTS.get(ore, [])
    
    if 1 <= index <= len(byproduct_names):
        name = byproduct_names[index - 1]
        multiplier = BYPRODUCT_MULTIPLIERS.get(name, 1.0)
        return {"name": name, "multiplier": multiplier}
    
    return None

def apply_multiplier_to_ratio(ratio_str: str, multiplier: float) -> str:
    """
    Multiplies the numeric part of a ratio string like '1:2.5' by a multiplier.
    Returns the new ratio string.
    """
    try:
        left, right = ratio_str.split(":")
        result = float(right) * multiplier
        return f"{left}:{round(result, 3)}"
    except Exception:
        return ratio_str  # If parsing fails, return original

def get_yaml_file_for_ore(ore_name):
    ore_path = os.path.join(RECIPE_DIR, f"{ore_name}.yml")
    if os.path.exists(ore_path):
        return ore_path
    elif os.path.exists(DEFAULT_YAML):
        return DEFAULT_YAML
    else:
        raise FileNotFoundError("No recipe found and no default fallback exists.")

def format_ore_name(ore_id):
    return ore_id.replace("_", " ").title()

# === PyQt UI ===
class OreChartApp(QWidget):
    def __init__(self, modpack="Enigmatica"):
        super().__init__()
        self.setWindowTitle("Ore Chart Viewer")

        # Layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left panel
        left_panel = QVBoxLayout()
        if modpack == "Enigmatica":
            self.dropdown = QComboBox()
            self.ore_name_map = {
                ORE_DISPLAY_NAMES.get(ore, ore.replace("_", " ").title()): ore
                for ore in ores_crystallization_stage
            }
            self.dropdown.addItems(sorted(self.ore_name_map.keys()))
            self.dropdown.currentTextChanged.connect(self.on_ore_changed)

            self.dirty_ore_source_dropdown = QComboBox()
            self.dirty_ore_source_dropdown.addItems([
                "Alchemical Dust", "Ore Chunk", "Rocky Chunk", "Crystallized Ore", "Native Cluster"
            ])
            self.dirty_ore_source_dropdown.currentTextChanged.connect(self.on_processing_changed)

            self.dust_method_dropdown = QComboBox()
            self.dust_method_dropdown.addItems(
                ["SAG Mill", 
                "Spectrometer", 
                "Sp. + Artifact", 
                "Slurry", 
                "IC2 Maceration", 
                "Infernal Furnace"])
            self.dust_method_dropdown.currentTextChanged.connect(self.on_dust_method_changed)

            self.sag_dropdown = QComboBox()
            self.sag_dropdown.addItems(GRINDING_BALL_OPTIONS.keys())
            self.sag_dropdown.currentTextChanged.connect(self.on_processing_changed)

            self.infinity_checkbox = QCheckBox("Use Infinity Furnace")
            self.infinity_checkbox.setChecked(False)
            self.infinity_checkbox.stateChanged.connect(self.on_processing_changed)

            self.purified_crushed_checkbox = QCheckBox("Use IC2 Purified Path")
            self.purified_crushed_checkbox.setChecked(False)
            self.purified_crushed_checkbox.stateChanged.connect(self.on_processing_changed)

            self.show_highlight_checkbox = QCheckBox("Highlight current path")
            self.show_highlight_checkbox.setChecked(True)
            self.show_highlight_checkbox.stateChanged.connect(self.on_highlight_changed)

            self.chosen_ingot_result_label = QLabel("Main Output Yield: N/A")
            self.byproduct_1_label = QLabel("Byproduct 1 Yield: N/A")
            self.byproduct_2_label = QLabel("Byproduct 2 Yield: N/A")
            self.byproduct_3_label = QLabel("Byproduct 3 Yield: N/A")
            
            self.save_button = QPushButton("Save Graph As Image")
            self.save_button.clicked.connect(self.save_graph)

            left_panel.addWidget(QLabel("Select Ore:"))
            left_panel.addWidget(self.dropdown)

            left_panel.addWidget(QLabel("Dirty Ore Source:"))
            left_panel.addWidget(self.dirty_ore_source_dropdown)

            left_panel.addWidget(QLabel("Dusting Method:"))
            left_panel.addWidget(self.dust_method_dropdown)

            left_panel.addWidget(QLabel("Grinding Ball:"))
            left_panel.addWidget(self.sag_dropdown)

            left_panel.addWidget(self.infinity_checkbox)

            left_panel.addWidget(self.purified_crushed_checkbox)

            left_panel.addWidget(self.show_highlight_checkbox)

            left_panel.addStretch()

            left_panel.addWidget(self.chosen_ingot_result_label)
            left_panel.addWidget(self.byproduct_1_label)
            left_panel.addWidget(self.byproduct_2_label)
            left_panel.addWidget(self.byproduct_3_label)

            left_panel.addStretch()
            
            left_panel.addWidget(self.save_button)

        # Right panel: graph display
        self.graph_label = QLabel()
        self.graph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.graph_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.graph_label.setScaledContents(False)

        layout.addLayout(left_panel)
        layout.addWidget(self.graph_label)

        if modpack == "Enigmatica":
            # Load initial graph
            self.current_graph_path = ""
            selected_display_name = self.dropdown.currentText()
            current_ore = self.ore_name_map.get(selected_display_name, selected_display_name)
            self.on_ore_changed(current_ore)

        else:
            self.on_ore_changed_complex()

    def on_ore_changed(self, display_name):
        global current_ore
        global has_ic2_path_for_current_ore
        global has_mekanism_path_for_current_ore

        current_ore = self.ore_name_map.get(display_name, display_name)

        # --- Handle IC2 ---
        if current_ore in ores_with_purified_crushed:
            has_ic2_path_for_current_ore = True
            self.purified_crushed_checkbox.setEnabled(True)
        else:
            has_ic2_path_for_current_ore = False
            self.purified_crushed_checkbox.setChecked(False)
            self.purified_crushed_checkbox.setEnabled(False)

        # --- Handle Mekanism ---
        has_mekanism_path_for_current_ore = current_ore in ores_with_mekanism_processing

        # --- Refresh Dust Method Dropdown ---
        current_selection = self.dust_method_dropdown.currentText()

        # Rebuild options dynamically
        self.dust_method_dropdown.blockSignals(True)
        self.dust_method_dropdown.clear()
        
        valid_methods = ["SAG Mill", "Spectrometer", "Sp. + Artifact", "Infernal Furnace"]
        
        if has_mekanism_path_for_current_ore:
            valid_methods.append("Slurry")

        if has_ic2_path_for_current_ore:
            valid_methods.append("IC2 Maceration")

        self.dust_method_dropdown.addItems(valid_methods)

        # Reselect old value if still valid
        if current_selection in valid_methods:
            self.dust_method_dropdown.setCurrentText(current_selection)
        else:
            self.dust_method_dropdown.setCurrentIndex(0)

        self.dust_method_dropdown.blockSignals(False)

        # Recompute with new ore
        self.recompute_ingot_yield()
    
    def on_ore_changed_complex(self):
        self.recompute_ingot_yield_complex()

    def on_processing_changed(self):
        self.recompute_ingot_yield()

    def on_dust_method_changed(self, method):
        self.selected_dust_method = method
        self.recompute_ingot_yield()

    def on_highlight_changed(self):
        self.recompute_ingot_yield()

    def recompute_ingot_yield(self):
        ore_id = current_ore
        dirty_source = self.dirty_ore_source_dropdown.currentText()
        purified_crushed_path = self.purified_crushed_checkbox.isChecked()

        selected_ball = self.sag_dropdown.currentText()
        ball_stats = GRINDING_BALL_OPTIONS.get(selected_ball, {"main_output_pct": 100, "byproduct_output_pct": 100})

        modifiers = {
            "sag_multiplier": ball_stats["main_output_pct"] / 100,
            "sag_byproduct_multiplier": ball_stats["byproduct_output_pct"] / 100,
            "infinity_furnace": self.infinity_checkbox.isChecked()
        }

        selected_dust_method = self.dust_method_dropdown.currentText()

        highlight_used = getattr(self, "show_highlight_checkbox", None)
        if highlight_used:
            highlight_flag = highlight_used.isChecked()
        else:
            highlight_flag = True  # default if checkbox not yet created

        try:
            assert current_ore, "current_ore must be set before recomputing yield"
            yaml_file = get_yaml_file_for_ore(ore_id)
            chain = load_chain_from_yaml(yaml_file, ore_id)
            chain = apply_processing_modifiers(chain, modifiers)

            for i, step in enumerate(chain):
                debug(f"[{i}] {step}")

            total_alternate_yield, used_steps, byproduct_outputs = evaluate_alternate_ingot_paths(
                chain, input_item="Ore Block", 
                input_amount=1, 
                allowed_dirty_ore_source=dirty_source, 
                forced_dust_method=selected_dust_method,
                purified_crushed_path=purified_crushed_path,
            )
            # Generate graph with highlights
            self.current_graph_path = generate_graph_with_subgraphs(
                chain, output_file="temp_graph", used_steps=used_steps, highlight_used=highlight_flag
            )
            self.chosen_ingot_result_label.setText(
                f"Main Output Yield: {total_alternate_yield:.2f} ({current_ore.title()})"
            )
            for i, (name, amount) in enumerate(byproduct_outputs.items()):
                name = ORE_DISPLAY_NAMES.get(name, name.replace("_", " ").title())
                label = getattr(self, f"byproduct_{i+1}_label", None)
                if label:
                    label.setText(f"Byproduct {i+1} Yield: {amount:.2f} ({name})")

            self.update_display()

        except Exception as e:
            print(f"[ERROR] recompute_ingot_yield failed: {e}")
            self.graph_label.setText(f"⚠️ Error: {e}")

    def recompute_ingot_yield_complex(self):
        try:
            yaml_file = "recipes/platline.yml"
            chain = load_chain_from_yaml_complex(yaml_file)
            # Generate graph with highlights
            self.current_graph_path = generate_graph_with_subgraphs_complex(
                chain,
                output_file="temp_graph",
                #chain_inputs=["Oil"],
                #chain_outputs=["Diesel", "Sulfuric Acid"],
                #forced_sides=None,
                chain_inputs=["PtMP Dust"],
                chain_outputs=["Platinum Dust", "Palladium Dust", "Rhodium Dust", "Osmium Dust", "Ruthenium Dust", "Iridium Dust"],
                forced_sides=forced_side_nodes
            )

            self.update_display()

        except Exception as e:
            print(f"[ERROR] recompute_ingot_yield failed: {e}")
            self.graph_label.setText(f"⚠️ Error: {e}")

    def update_display(self):
        label_size = self.graph_label.size()
        pixmap = self.load_and_resize_image(self.current_graph_path, label_size)

        if pixmap.isNull():
            self.graph_label.setText("⚠️ Could not load image.")
        else:
            self.graph_label.setPixmap(pixmap)

    def resizeEvent(self, a0):
        self.update_display()
        super().resizeEvent(a0)

    def save_graph(self):
        if not self.current_graph_path or not os.path.exists(self.current_graph_path):
            return

        filename = os.path.join(GRAPH_OUTPUT_DIR, f"{current_ore}_graph.png")
        with open(self.current_graph_path, "rb") as src, open(filename, "wb") as dst:
            dst.write(src.read())
        print(f"✔️ Saved to {filename}")

    def load_and_resize_image(self, path: str, size: QSize, save_path: Optional[str] = None) -> QPixmap:
        screen = QApplication.primaryScreen()
        assert screen is not None
        dpr = screen.devicePixelRatio()

        # Convert logical size to physical size (for high-DPI screens)
        target_width_phys = int(size.width() * dpr)
        target_height_phys = int(size.height() * dpr)

        img = Image.open(path).convert("RGB")

        # Maintain aspect ratio during resize
        aspect_ratio = img.width / img.height
        target_height = target_height_phys
        target_width = int(target_height * aspect_ratio)
        if target_width > target_width_phys:
            target_width = target_width_phys
            target_height = int(target_width / aspect_ratio)

        img = img.resize((target_width, target_height), resample=Image.Resampling.LANCZOS)

        if save_path:
            img.save(save_path)

        data = img.tobytes("raw", "RGB")
        bytes_per_line = img.width * 3
        qimg = QImage(data, img.width, img.height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        pixmap.setDevicePixelRatio(dpr)
        return pixmap

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OreChartApp()
    window.show()
    sys.exit(app.exec())