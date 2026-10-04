# Blue Horizon strategic map

Godot 4.3+ theater map. Run `Strategic_Map.tscn`.

Layers cover the whole board:

- Air: open sky over every hex.
- Surface: islands, shallow ring, deep water.
- Below water: depth band. Land hexes have no water column.

Island positions and names are the locked seed-42 theater. A click on Bora Bora or Tarawa opens that tactical Godot map. Other names stay labeled until a tactical map is registered.

The campaign button still runs `python -m strategic.strategic_map`. That module opens this project when Godot is on the path.
