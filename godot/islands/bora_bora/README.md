# Bora Bora tactical island map

Godot 4.3+ project for the Table_Top_Battles tactical layer.

Open `project.godot` and run the main scene `Bora_Bora_Island_Map.tscn`.

This is the island map in the three-map series:

- Strategic: Blue Horizon theater. A right-click on a hex named Bora Bora opens this project.
- Tactical: this map. One hex is one hour of unburdened walking on beach.
- Battle: not built here. Three contact anchors are marked for a later zoom.

## Real island

Bora Bora, Society Islands. An almost-atoll: a volcanic island on the west side of a lagoon, a barrier reef with motus, and one navigable pass (Teavanui). Mount Otemanu is the real peak at 727 m. Real land area is about 30.6 km2, which is smaller than this board. The layout is the real one. The size is the walking hex.

## Scale

- Board: pointy-top hex, axial radius 8, 217 hexes
- Hex: 5 km center to center
- Beach walk: 5 km/h, so 1 hex = 1 hour
- Hills 2 hours, highlands 3, small mountain 4, impassable blocked

## Vertical

Water is a stack in the same hex, switched like the air layers. Shallow is 0-10 m and sits on every water hex. Moderate is 10-40 m and sits under shallow on moderate and deep hexes. Deep is below 40 m and sits under those two bands only on deep hexes. A shallow hex has no deeper band.

Land: beach, hills, highlands, small mountain, impassable mountain.

Air: tactical flying height is the column from the surface to 2500 m around every hex. The Otemanu column blocks tactical flight. Two strategic bands sit above the peaks: 2500-7500 m and 7500-12000 m.

## Settlement

One village, Vaitape, with the fishing dock on the pass. One hamlet, Faanui, with taro and a canoe landing. That is the whole population. Food is lagoon fish, taro, breadfruit, and coconut.

## Resources

Fishing on the pass, lagoon edge, and outer reef. Taro and breadfruit inland. Coconut on the village shore and two motus. Timber on one highland slope, for the village only. A small basalt quarry on Pahia for building stone. No town, no export mine, no second dock.
