extends Node2D
## Tactical island map for Bora Bora.
## One hex = 5 km = 1 hour of unburdened walking on beach.

const HEX_SIZE := 36.0
const DATA_PATH := "res://data/bora_bora.json"

const TERRAIN_COLOR := {
	"deep": Color("081e38"),
	"moderate": Color("1b6ca8"),
	"shallow": Color("4fc3d8"),
	"beach": Color("e6d3a3"),
	"hills": Color("7cb342"),
	"highlands": Color("2e7d32"),
	"small_mountain": Color("8d6e63"),
	"impassable_mountain": Color("3e2723"),
}

const ELEVATION := {
	"deep": {"label": "Deep water", "vertical": "below 40 m", "hours": "not walkable"},
	"moderate": {"label": "Moderate water", "vertical": "10 to 40 m", "hours": "not walkable"},
	"shallow": {"label": "Shallow water", "vertical": "0 to 10 m", "hours": "not walkable"},
	"beach": {"label": "Beach", "vertical": "0 to 20 m", "hours": "1 hour"},
	"hills": {"label": "Hills", "vertical": "20 to 150 m", "hours": "2 hours"},
	"highlands": {"label": "Highlands", "vertical": "150 to 400 m", "hours": "3 hours"},
	"small_mountain": {"label": "Small mountain", "vertical": "400 to 800 m", "hours": "4 hours"},
	"impassable_mountain": {"label": "Impassable mountain", "vertical": "above 800 m", "hours": "blocked"},
}

const FEATURE_LABEL := {
	"village": "village",
	"fishing_dock": "dock",
	"hamlet": "hamlet",
	"canoe_landing": "canoe",
	"taro": "taro",
	"coconut": "coconut",
	"breadfruit": "breadfruit",
	"timber": "timber",
	"basalt_quarry": "basalt",
	"fishing_ground": "fishing",
	"reef_pass": "pass",
}

var map_data: Dictionary = {}
var hex_by_key: Dictionary = {}
var polygons: Dictionary = {}
var layer_name := "surface"
var selected_key := ""
var dragging := false
var drag_origin := Vector2.ZERO
var camera: Camera2D
var inspector: Label
var layer_buttons: Dictionary = {}


func _ready() -> void:
	map_data = _load_map()
	camera = Camera2D.new()
	camera.enabled = true
	camera.position = Vector2(180, 40)
	add_child(camera)
	_build_hexes()
	_build_ui()
	_select_hex("q-3r1")


func _load_map() -> Dictionary:
	var file := FileAccess.open(DATA_PATH, FileAccess.READ)
	if file == null:
		push_error("Missing map data: %s" % DATA_PATH)
		return {}
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Map data is not an object")
		return {}
	return parsed


func _build_hexes() -> void:
	var layer := Node2D.new()
	layer.name = "Hexes"
	add_child(layer)
	for hex in map_data.get("hexes", []):
		var key := _key(int(hex["q"]), int(hex["r"]))
		hex_by_key[key] = hex
		var node := Node2D.new()
		node.position = _axial_to_pixel(int(hex["q"]), int(hex["r"]))
		node.name = key
		layer.add_child(node)
		var poly := Polygon2D.new()
		poly.polygon = _hex_points(HEX_SIZE - 1.0)
		poly.color = TERRAIN_COLOR.get(hex["terrain"], Color.GRAY)
		node.add_child(poly)
		polygons[key] = poly
		var outline := Line2D.new()
		var pts := _hex_points(HEX_SIZE - 1.0)
		pts.append(pts[0])
		outline.points = pts
		outline.width = 1.0
		outline.default_color = Color(0.08, 0.1, 0.12, 0.85)
		node.add_child(outline)
		if str(hex.get("name", "")) != "":
			node.add_child(_tag(str(hex["name"]), Vector2(-22, -10), 11, Color("fff8e6")))
		var features: Array = hex.get("features", [])
		if features.size() > 0:
			var names: PackedStringArray = []
			for item in features:
				names.append(str(FEATURE_LABEL.get(item, item)))
			node.add_child(_tag(", ".join(names), Vector2(-22, 6), 9, Color("1b140c")))


func _tag(text: String, pos: Vector2, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.position = pos
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var panel := Panel.new()
	panel.position = Vector2(12, 12)
	panel.size = Vector2(360, 976)
	panel.modulate = Color(1, 1, 1, 0.94)
	canvas.add_child(panel)
	var box := VBoxContainer.new()
	box.position = Vector2(16, 16)
	box.size = Vector2(328, 944)
	box.add_theme_constant_override("separation", 8)
	panel.add_child(box)
	box.add_child(_title("Bora Bora"))
	box.add_child(_body("Tactical island. Almost-atoll: volcanic core west, lagoon, motu ring, Teavanui Pass."))
	box.add_child(_body("Hex = 5 km = 1 hour walking on beach."))
	box.add_child(_heading("Water layer"))
	var water_row := HBoxContainer.new()
	water_row.add_theme_constant_override("separation", 6)
	box.add_child(water_row)
	for item in [["surface", "Surface"], ["water_shallow", "Shallow"], ["water_moderate", "Moderate"], ["water_deep", "Deep"]]:
		var button := Button.new()
		button.text = item[1]
		button.pressed.connect(_set_layer.bind(item[0]))
		water_row.add_child(button)
		layer_buttons[item[0]] = button
	box.add_child(_heading("Air layer"))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	box.add_child(row)
	for item in [["tactical", "Tactical"], ["strategic_1", "Strategic 1"], ["strategic_2", "Strategic 2"]]:
		var button := Button.new()
		button.text = item[1]
		button.pressed.connect(_set_layer.bind(item[0]))
		row.add_child(button)
		layer_buttons[item[0]] = button
	_mark_layer_button()
	box.add_child(_heading("Legend"))
	box.add_child(_body("Water is a stack in the same hex. Deep has shallow and moderate above it. Moderate has shallow above it. Shallow stays one band.\nLand: beach, hills, highlands, small mountain, impassable.\nTactical air is the column to 2500 m. Two strategic bands sit above the peaks."))
	box.add_child(_heading("Settlement"))
	box.add_child(_body("Vaitape village and fishing dock. Faanui hamlet only. Fed by lagoon fish, taro, breadfruit, and coconut."))
	box.add_child(_heading("Resources"))
	box.add_child(_body("Fishing, taro, coconut, breadfruit, village timber, basalt building stone."))
	box.add_child(_heading("Selected hex"))
	inspector = Label.new()
	inspector.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	inspector.custom_minimum_size = Vector2(320, 280)
	inspector.add_theme_font_size_override("font_size", 15)
	box.add_child(inspector)
	box.add_child(_body("Drag to pan. Wheel to zoom. Click a hex."))


func _title(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 28)
	return label


func _heading(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", 18)
	return label


func _body(text: String) -> Label:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size = Vector2(320, 0)
	label.add_theme_font_size_override("font_size", 14)
	return label


func _set_layer(next_layer: String) -> void:
	layer_name = next_layer
	_mark_layer_button()
	for key in polygons:
		polygons[key].color = _color_for(hex_by_key[key])
	if selected_key != "":
		_show_hex(hex_by_key[selected_key])


func _mark_layer_button() -> void:
	for key in layer_buttons:
		layer_buttons[key].modulate = Color(1, 1, 1) if key == layer_name else Color(0.75, 0.75, 0.75)


func _color_for(hex: Dictionary) -> Color:
	var terrain := str(hex["terrain"])
	if layer_name == "surface" or layer_name == "water_shallow":
		if _has_water_band(terrain, "shallow"):
			return TERRAIN_COLOR["shallow"]
		return TERRAIN_COLOR.get(terrain, Color.GRAY)
	if layer_name == "water_moderate":
		if _has_water_band(terrain, "moderate"):
			return TERRAIN_COLOR["moderate"]
		if _is_water(terrain):
			return Color("1c2430")
		return TERRAIN_COLOR.get(terrain, Color.GRAY)
	if layer_name == "water_deep":
		if _has_water_band(terrain, "deep"):
			return TERRAIN_COLOR["deep"]
		if _is_water(terrain):
			return Color("1c2430")
		return TERRAIN_COLOR.get(terrain, Color.GRAY)
	if layer_name == "tactical":
		if terrain == "impassable_mountain":
			return Color("3e2723")
		return Color("8ecae6")
	if layer_name == "strategic_1":
		return Color("a8c5e2")
	return Color("d7e3f0")


func _is_water(terrain: String) -> bool:
	return terrain == "shallow" or terrain == "moderate" or terrain == "deep"


func _water_bands(terrain: String) -> Array:
	if terrain == "deep":
		return ["shallow", "moderate", "deep"]
	if terrain == "moderate":
		return ["shallow", "moderate"]
	if terrain == "shallow":
		return ["shallow"]
	return []


func _has_water_band(terrain: String, band: String) -> bool:
	return band in _water_bands(terrain)


func _select_hex(key: String) -> void:
	if not hex_by_key.has(key):
		return
	selected_key = key
	_show_hex(hex_by_key[key])


func _show_hex(hex: Dictionary) -> void:
	var terrain := str(hex["terrain"])
	var info: Dictionary = ELEVATION.get(terrain, {})
	var features: Array = hex.get("features", [])
	var feature_text := "none"
	if not features.is_empty():
		var names: PackedStringArray = []
		for item in features:
			names.append(str(item))
		feature_text = ", ".join(names)
	var air := _air_text(terrain)
	var water := _water_text(terrain)
	inspector.text = "q %s, r %s\n%s\n%s\n%s\nWalk: %s\nFeatures: %s\n\n%s\n\n%s" % [
		hex["q"], hex["r"],
		str(hex.get("name", "")) if str(hex.get("name", "")) != "" else "Unnamed",
		info.get("label", terrain),
		info.get("vertical", ""),
		info.get("hours", ""),
		feature_text,
		water,
		air,
	]


func _water_text(terrain: String) -> String:
	var bands := _water_bands(terrain)
	if bands.is_empty():
		return "No water column. Land hex."
	var stack := "Water stack, top to bottom: %s." % ", ".join(PackedStringArray(bands))
	if layer_name == "water_moderate" and not _has_water_band(terrain, "moderate"):
		return stack + " No moderate band in this hex."
	if layer_name == "water_deep" and not _has_water_band(terrain, "deep"):
		return stack + " No deep band in this hex."
	if layer_name == "water_shallow" or layer_name == "surface":
		return stack + " Viewing shallow, 0 to 10 m, the surface of this hex."
	if layer_name == "water_moderate":
		return stack + " Viewing moderate, 10 to 40 m."
	if layer_name == "water_deep":
		return stack + " Viewing deep, below 40 m."
	return stack


func _air_text(terrain: String) -> String:
	if layer_name == "tactical":
		if terrain == "impassable_mountain":
			return "Tactical air blocked. Peak occupies this column."
		return "Tactical flying height, surface to 2500 m."
	if layer_name == "strategic_1":
		return "Strategic flight, 2500 to 7500 m. Open above the peaks."
	if layer_name == "strategic_2":
		return "Strategic flight, 7500 to 12000 m. Open above the peaks."
	return "Surface. Switch air layer to see tactical and the two strategic bands."


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		if mouse.button_index == MOUSE_BUTTON_WHEEL_UP and mouse.pressed:
			camera.zoom = (camera.zoom * 1.1).clamp(Vector2(0.4, 0.4), Vector2(2.4, 2.4))
		elif mouse.button_index == MOUSE_BUTTON_WHEEL_DOWN and mouse.pressed:
			camera.zoom = (camera.zoom / 1.1).clamp(Vector2(0.4, 0.4), Vector2(2.4, 2.4))
		elif mouse.button_index == MOUSE_BUTTON_LEFT and mouse.pressed:
			dragging = true
			drag_origin = mouse.position
		elif mouse.button_index == MOUSE_BUTTON_LEFT and not mouse.pressed:
			if drag_origin.distance_to(mouse.position) < 6.0:
				_click_hex(mouse.position)
			dragging = false
		elif mouse.button_index == MOUSE_BUTTON_RIGHT:
			dragging = mouse.pressed
			drag_origin = mouse.position
	elif event is InputEventMouseMotion and dragging:
		var motion := event as InputEventMouseMotion
		camera.position -= motion.relative / camera.zoom


func _click_hex(screen_pos: Vector2) -> void:
	var world := _screen_to_world(screen_pos)
	var best := ""
	var best_d := HEX_SIZE
	for key in hex_by_key:
		var hex: Dictionary = hex_by_key[key]
		var pos := _axial_to_pixel(int(hex["q"]), int(hex["r"]))
		var dist := pos.distance_to(world)
		if dist < best_d:
			best_d = dist
			best = key
	if best != "":
		_select_hex(best)


func _screen_to_world(screen_pos: Vector2) -> Vector2:
	return camera.position + (screen_pos - get_viewport_rect().size * 0.5) / camera.zoom


func _axial_to_pixel(q: int, r: int) -> Vector2:
	var x := HEX_SIZE * (sqrt(3.0) * q + sqrt(3.0) / 2.0 * r)
	var y := HEX_SIZE * (1.5 * r)
	return Vector2(x, y)


func _hex_points(size: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in 6:
		var angle := deg_to_rad(60.0 * i - 30.0)
		pts.append(Vector2(cos(angle), sin(angle)) * size)
	return pts


func _key(q: int, r: int) -> String:
	return "q%sr%s" % [q, r]
