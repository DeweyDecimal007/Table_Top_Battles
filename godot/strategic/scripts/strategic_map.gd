extends Node2D
## Strategic theater. Air, surface, and below-water layers.
## Named islands keep their tactical map links.

const HEX_SIZE := 18.0
const DATA_PATH := "res://data/theater.json"

var map_data: Dictionary = {}
var hexes: Array = []
var layer_name := "surface"
var camera: Camera2D
var inspector: Label
var layer_buttons: Dictionary = {}
var dragging := false
var drag_origin := Vector2.ZERO


func _ready() -> void:
	map_data = _load_map()
	hexes = map_data.get("hexes", [])
	camera = Camera2D.new()
	camera.enabled = true
	camera.position = Vector2(900, 520)
	add_child(camera)
	_build_ui()
	queue_redraw()


func _load_map() -> Dictionary:
	var file := FileAccess.open(DATA_PATH, FileAccess.READ)
	if file == null:
		push_error("Missing theater data")
		return {}
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	return parsed if typeof(parsed) == TYPE_DICTIONARY else {}


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var panel := Panel.new()
	panel.position = Vector2(12, 12)
	panel.size = Vector2(320, 280)
	panel.modulate = Color(1, 1, 1, 0.94)
	canvas.add_child(panel)
	var box := VBoxContainer.new()
	box.position = Vector2(14, 12)
	box.size = Vector2(292, 256)
	box.add_theme_constant_override("separation", 6)
	panel.add_child(box)
	var title := Label.new()
	title.text = "Blue Horizon"
	title.add_theme_font_size_override("font_size", 24)
	box.add_child(title)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	box.add_child(row)
	for item in [["air", "Air"], ["surface", "Surface"], ["below", "Below"]]:
		var button := Button.new()
		button.text = item[1]
		button.pressed.connect(_set_layer.bind(item[0]))
		row.add_child(button)
		layer_buttons[item[0]] = button
	_mark_layer()
	inspector = Label.new()
	inspector.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	inspector.custom_minimum_size = Vector2(280, 120)
	inspector.text = "Air, surface, and below-water cover the whole theater. Click a named island to open its tactical map."
	box.add_child(inspector)
	var hint := Label.new()
	hint.text = "Drag to pan. Wheel to zoom."
	box.add_child(hint)


func _set_layer(next_layer: String) -> void:
	layer_name = next_layer
	_mark_layer()
	queue_redraw()


func _mark_layer() -> void:
	for key in layer_buttons:
		layer_buttons[key].modulate = Color(1, 1, 1) if key == layer_name else Color(0.75, 0.75, 0.75)


func _draw() -> void:
	var ordered := hexes.duplicate()
	ordered.sort_custom(func(a, b): return int(a["r"]) < int(b["r"]))
	for hex in ordered:
		_draw_raised_hex(_pixel(int(hex["c"]), int(hex["r"])), _color_for(hex), _lift_for(hex), str(hex["owner"]))
		if str(hex.get("name", "")) != "":
			var pos := _pixel(int(hex["c"]), int(hex["r"])) + Vector2(-18, -22)
			draw_string(ThemeDB.fallback_font, pos, str(hex["name"]), HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color("fff8e6"))


func _lift_for(hex: Dictionary) -> float:
	if layer_name == "air":
		return 10.0
	if str(hex["terrain"]) == "land":
		return 16.0
	if str(hex["terrain"]) == "shallow":
		return 12.0
	return 8.0


func _color_for(hex: Dictionary) -> Color:
	var terrain := str(hex["terrain"])
	if layer_name == "air":
		return Color("8ecae6")
	if layer_name == "below":
		if terrain == "land":
			return Color("1c2430")
		if terrain == "shallow":
			return Color("1b6ca8")
		return Color("081e38")
	if hex.get("industrial", false):
		return Color("a9a9a9")
	if terrain == "land":
		return Color("228b22")
	if terrain == "shallow":
		return Color("4fc3d8")
	return Color("08264a")


func _draw_raised_hex(center: Vector2, top_color: Color, lift: float, owner: String) -> void:
	var top := _hex_points(HEX_SIZE - 1.0)
	var shade := top_color.darkened(0.3)
	draw_colored_polygon(_offset(top, center + Vector2(3, 3)), Color(0, 0, 0, 0.25))
	for i in [2, 3, 4]:
		var a: Vector2 = top[i]
		var b: Vector2 = top[(i + 1) % 6]
		draw_colored_polygon(PackedVector2Array([
			center + b, center + a,
			center + a + Vector2(2, -lift),
			center + b + Vector2(2, -lift),
		]), shade)
	var raised := _offset(top, center + Vector2(2, -lift))
	draw_colored_polygon(raised, top_color)
	draw_colored_polygon(_offset(_hex_points(HEX_SIZE * 0.58), center + Vector2(1, -lift - 1)), top_color.lightened(0.14))
	var border := Color("dc2828") if owner == "Red" else Color("1e78ff") if owner == "Blue" else Color("dcdce6")
	var rim := raised.duplicate()
	rim.append(raised[0])
	draw_polyline(rim, border, 1.4)


func _offset(pts: PackedVector2Array, by: Vector2) -> PackedVector2Array:
	var out := PackedVector2Array()
	for pt in pts:
		out.append(pt + by)
	return out


func _hex_points(size: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for i in 6:
		var angle := deg_to_rad(60.0 * i - 30.0)
		pts.append(Vector2(cos(angle), sin(angle)) * size)
	return pts


func _pixel(col: int, row: int) -> Vector2:
	var x := col * HEX_SIZE * sqrt(3.0)
	var y := row * HEX_SIZE * 1.5
	if row % 2 == 1:
		x += HEX_SIZE * sqrt(3.0) / 2.0
	return Vector2(x, y)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		if mouse.button_index == MOUSE_BUTTON_WHEEL_UP and mouse.pressed:
			camera.zoom = (camera.zoom * 1.1).clamp(Vector2(0.35, 0.35), Vector2(2.2, 2.2))
		elif mouse.button_index == MOUSE_BUTTON_WHEEL_DOWN and mouse.pressed:
			camera.zoom = (camera.zoom / 1.1).clamp(Vector2(0.35, 0.35), Vector2(2.2, 2.2))
		elif mouse.button_index == MOUSE_BUTTON_LEFT and mouse.pressed:
			dragging = true
			drag_origin = mouse.position
		elif mouse.button_index == MOUSE_BUTTON_LEFT and not mouse.pressed:
			if drag_origin.distance_to(mouse.position) < 6.0:
				_open_island(mouse.position)
			dragging = false
		elif mouse.button_index == MOUSE_BUTTON_RIGHT and mouse.pressed:
			_open_island(mouse.position)
	elif event is InputEventMouseMotion and dragging:
		camera.position -= (event as InputEventMouseMotion).relative / camera.zoom


func _open_island(screen_pos: Vector2) -> void:
	var world := camera.position + (screen_pos - get_viewport_rect().size * 0.5) / camera.zoom
	var best: Dictionary = {}
	var best_d := HEX_SIZE
	for hex in hexes:
		var dist := _pixel(int(hex["c"]), int(hex["r"])).distance_to(world)
		if dist < best_d:
			best_d = dist
			best = hex
	if best.is_empty():
		return
	var island_name := str(best.get("name", ""))
	if island_name == "":
		inspector.text = "Hex %s,%s has no island." % [best["c"], best["r"]]
		return
	var links: Dictionary = map_data.get("links", {})
	if not links.has(island_name):
		inspector.text = "%s is on the theater. No tactical map registered yet." % island_name
		return
	var link: Dictionary = links[island_name]
	var project := str(link.get("project", ""))
	if project.begins_with(".."):
		project = ProjectSettings.globalize_path("res://".path_join(project))
	var scene := str(link.get("scene", ""))
	if not FileAccess.file_exists(project.path_join("project.godot")):
		inspector.text = "%s link is registered, but the Godot project was not found at %s." % [island_name, project]
		return
	OS.create_process(OS.get_executable_path(), ["--path", project, scene])
	inspector.text = "Opened %s tactical map." % island_name
