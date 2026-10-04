extends Node3D
## Tactical Bora Bora board. Raised textured hexes, water stack, air bands.

const HEX_RADIUS := 1.0
const DATA_PATH := "res://data/bora_bora.json"

var map_data: Dictionary = {}
var hex_by_key: Dictionary = {}
var layer_name := "surface"
var camera: Camera3D
var inspector: Label
var layer_buttons: Dictionary = {}
var dragging := false
var drag_origin := Vector2.ZERO
var yaw := 0.7
var pitch := 0.85
var distance := 28.0
var focus := Vector3(-1.5, 0, -1.0)
var mats: Dictionary = {}
var prism: ArrayMesh
var peak: ArrayMesh
var tree_mesh: ArrayMesh


func _ready() -> void:
	map_data = _load_map()
	_make_materials()
	prism = _prism_mesh(HEX_RADIUS * 0.96, 1.0)
	peak = _peak_mesh()
	tree_mesh = _tree_mesh()
	_build_world()
	_build_camera()
	_build_ui()
	_select_hex("q-3r1")
	_apply_layer()


func _load_map() -> Dictionary:
	var file := FileAccess.open(DATA_PATH, FileAccess.READ)
	if file == null:
		return {}
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	return parsed if typeof(parsed) == TYPE_DICTIONARY else {}


func _tex(path: String) -> ImageTexture:
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	if image == null:
		return null
	return ImageTexture.create_from_image(image)


func _mat(color: Color, texture_path: String, rough: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = rough
	var texture := _tex(texture_path)
	if texture:
		mat.albedo_texture = texture
		mat.uv1_scale = Vector3(2, 2, 2)
	return mat


func _make_materials() -> void:
	mats["grass"] = _mat(Color("8da84a"), "res://textures/grass.png", 0.85)
	mats["sand"] = _mat(Color("e4d2a4"), "res://textures/sand.png", 0.9)
	mats["water"] = _mat(Color("1d6fd0"), "res://textures/water.png", 0.18)
	mats["water_deep"] = _mat(Color("0c3f86"), "res://textures/water.png", 0.22)
	mats["water_mod"] = _mat(Color("1b6ca8"), "res://textures/water.png", 0.2)
	mats["rock"] = _mat(Color("b7b4ac"), "res://textures/rock.png", 0.8)
	mats["dirt"] = _mat(Color("a07848"), "res://textures/dirt.png", 0.92)
	mats["forest"] = _mat(Color("2f6b34"), "res://textures/grass.png", 0.8)
	mats["air"] = _mat(Color("9fd0ea"), "res://textures/water.png", 0.4)
	mats["empty"] = _mat(Color("1c2430"), "res://textures/dirt.png", 1.0)
	mats["water"].metallic = 0.12


func _build_world() -> void:
	var env := WorldEnvironment.new()
	var world := Environment.new()
	world.background_mode = Environment.BG_COLOR
	world.background_color = Color("7eb6e6")
	world.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.ambient_light_color = Color("c5d7ea")
	world.ambient_light_energy = 0.7
	env.environment = world
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, 32, 0)
	sun.light_energy = 1.35
	sun.shadow_enabled = true
	add_child(sun)
	var board := Node3D.new()
	board.name = "Board"
	add_child(board)
	for hex in map_data.get("hexes", []):
		var key := _key(int(hex["q"]), int(hex["r"]))
		hex_by_key[key] = hex
		var tile := Node3D.new()
		tile.name = key
		tile.position = _axial_to_world(int(hex["q"]), int(hex["r"]))
		board.add_child(tile)
		var body := MeshInstance3D.new()
		body.name = "Body"
		body.mesh = prism
		body.position.y = 0
		body.scale.y = max(_height_for(str(hex["terrain"])), 0.08)
		body.set_surface_override_material(0, _top_material(hex))
		tile.add_child(body)
		_add_props(tile, hex)


func _add_props(tile: Node3D, hex: Dictionary) -> void:
	var terrain := str(hex["terrain"])
	var top_y := _height_for(terrain)
	if terrain == "small_mountain" or terrain == "impassable_mountain":
		var rock := MeshInstance3D.new()
		rock.name = "Peak"
		rock.mesh = peak
		rock.position.y = top_y
		rock.scale = Vector3(0.7, 1.4, 0.7) if terrain == "impassable_mountain" else Vector3(0.45, 0.7, 0.45)
		rock.set_surface_override_material(0, mats["rock"])
		tile.add_child(rock)
	if terrain in ["hills", "highlands"] or "timber" in hex.get("features", []) or "coconut" in hex.get("features", []):
		for i in 4:
			var tree := MeshInstance3D.new()
			tree.name = "Tree"
			tree.mesh = tree_mesh
			tree.position = Vector3(-0.28 + (i % 2) * 0.36, top_y, -0.2 + int(i / 2) * 0.32)
			tree.scale = Vector3(0.35, 0.45, 0.35)
			tree.set_surface_override_material(0, mats["forest"])
			tile.add_child(tree)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.fov = 38
	add_child(camera)
	_place_camera()


func _place_camera() -> void:
	var offset := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch)) * distance
	camera.position = focus + offset
	camera.look_at(focus, Vector3.UP)


func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var panel := Panel.new()
	panel.position = Vector2(12, 12)
	panel.size = Vector2(360, 430)
	panel.modulate = Color(1, 1, 1, 0.92)
	canvas.add_child(panel)
	var box := VBoxContainer.new()
	box.position = Vector2(14, 12)
	box.size = Vector2(332, 406)
	box.add_theme_constant_override("separation", 6)
	panel.add_child(box)
	box.add_child(_label("Bora Bora", 26))
	box.add_child(_label("Raised terrain board. Drag to orbit.", 14))
	box.add_child(_label("Water layer", 18))
	var water_row := HBoxContainer.new()
	box.add_child(water_row)
	for item in [["surface", "Surface"], ["water_shallow", "Shallow"], ["water_moderate", "Moderate"], ["water_deep", "Deep"]]:
		water_row.add_child(_layer_button(item[0], item[1]))
	box.add_child(_label("Air layer", 18))
	var air_row := HBoxContainer.new()
	box.add_child(air_row)
	for item in [["tactical", "Tactical"], ["strategic_1", "Strategic 1"], ["strategic_2", "Strategic 2"]]:
		air_row.add_child(_layer_button(item[0], item[1]))
	_mark_layer()
	inspector = _label("", 14)
	inspector.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	inspector.custom_minimum_size = Vector2(320, 140)
	box.add_child(inspector)


func _label(text: String, size: int) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", size)
	return label


func _layer_button(id: String, text: String) -> Button:
	var button := Button.new()
	button.text = text
	button.pressed.connect(_set_layer.bind(id))
	layer_buttons[id] = button
	return button


func _set_layer(next_layer: String) -> void:
	layer_name = next_layer
	_mark_layer()
	_apply_layer()
	if selected_key != "":
		_show_hex(hex_by_key[selected_key])


func _mark_layer() -> void:
	for key in layer_buttons:
		layer_buttons[key].modulate = Color(1, 1, 1) if key == layer_name else Color(0.72, 0.72, 0.72)


func _apply_layer() -> void:
	var board := get_node("Board")
	for child in board.get_children():
		var hex: Dictionary = hex_by_key[child.name]
		var body := child.get_node("Body") as MeshInstance3D
		body.set_surface_override_material(0, _top_material(hex))
		body.scale.y = max(_height_for(str(hex["terrain"])), 0.08)
		body.position.y = 0
		for prop in child.get_children():
			if prop.name == "Peak" or prop.name == "Tree":
				prop.visible = layer_name == "surface" or layer_name == "water_shallow"


func _top_material(hex: Dictionary) -> Material:
	var terrain := str(hex["terrain"])
	if layer_name == "tactical" or layer_name.begins_with("strategic"):
		if terrain == "impassable_mountain" and layer_name == "tactical":
			return mats["rock"]
		return mats["air"]
	if layer_name == "water_moderate":
		if terrain == "deep" or terrain == "moderate":
			return mats["water_mod"]
		if _is_water(terrain):
			return mats["empty"]
	if layer_name == "water_deep":
		if terrain == "deep":
			return mats["water_deep"]
		if _is_water(terrain):
			return mats["empty"]
	if terrain == "deep":
		return mats["water_deep"] if layer_name == "water_deep" else mats["water"]
	if terrain == "moderate" or terrain == "shallow":
		return mats["water"]
	if terrain == "beach":
		return mats["sand"]
	if terrain == "small_mountain" or terrain == "impassable_mountain":
		return mats["rock"]
	if terrain == "highlands":
		return mats["forest"]
	return mats["grass"]


func _height_for(terrain: String) -> float:
	if layer_name == "tactical" or layer_name.begins_with("strategic"):
		return 0.2
	match terrain:
		"deep":
			return 0.12
		"moderate":
			return 0.16
		"shallow":
			return 0.22
		"beach":
			return 0.42
		"hills":
			return 0.62
		"highlands":
			return 0.84
		"small_mountain":
			return 1.05
		"impassable_mountain":
			return 1.35
	return 0.3


func _show_hex(hex: Dictionary) -> void:
	var terrain := str(hex["terrain"])
	var bands := _water_bands(terrain)
	var stack := "No water column." if bands.is_empty() else "Water stack: %s." % ", ".join(PackedStringArray(bands))
	inspector.text = "q %s, r %s\n%s\n%s\n%s" % [
		hex["q"], hex["r"],
		str(hex.get("name", "")) if str(hex.get("name", "")) != "" else terrain,
		stack,
		_layer_note(terrain),
	]


func _layer_note(terrain: String) -> String:
	if layer_name == "tactical":
		return "Tactical air blocked on Otemanu." if terrain == "impassable_mountain" else "Tactical air, surface to 2500 m."
	if layer_name == "strategic_1":
		return "Strategic air, 2500 to 7500 m."
	if layer_name == "strategic_2":
		return "Strategic air, 7500 to 12000 m."
	if layer_name == "water_deep" and terrain != "deep":
		return "No deep band in this hex."
	if layer_name == "water_moderate" and terrain not in ["moderate", "deep"]:
		return "No moderate band in this hex."
	return "Surface terrain."


func _select_hex(key: String) -> void:
	if hex_by_key.has(key):
		selected_key_set(key)


var selected_key := ""


func selected_key_set(key: String) -> void:
	selected_key = key
	_show_hex(hex_by_key[key])


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		if mouse.button_index == MOUSE_BUTTON_WHEEL_UP and mouse.pressed:
			distance = max(8.0, distance - 1.5)
			_place_camera()
		elif mouse.button_index == MOUSE_BUTTON_WHEEL_DOWN and mouse.pressed:
			distance = min(60.0, distance + 1.5)
			_place_camera()
		elif mouse.button_index == MOUSE_BUTTON_RIGHT:
			dragging = mouse.pressed
			drag_origin = mouse.position
		elif mouse.button_index == MOUSE_BUTTON_LEFT and mouse.pressed:
			_pick(mouse.position)
	elif event is InputEventMouseMotion and dragging:
		var motion := event as InputEventMouseMotion
		yaw -= motion.relative.x * 0.008
		pitch = clamp(pitch - motion.relative.y * 0.005, 0.25, 1.2)
		_place_camera()


func _pick(screen_pos: Vector2) -> void:
	var origin := camera.project_ray_origin(screen_pos)
	var dir := camera.project_ray_normal(screen_pos)
	if abs(dir.y) < 0.001:
		return
	var t := -origin.y / dir.y
	if t < 0:
		return
	var hit := origin + dir * t
	var best := ""
	var best_d := HEX_RADIUS
	for key in hex_by_key:
		var hex: Dictionary = hex_by_key[key]
		var pos := _axial_to_world(int(hex["q"]), int(hex["r"]))
		var dist := Vector2(pos.x, pos.z).distance_to(Vector2(hit.x, hit.z))
		if dist < best_d:
			best_d = dist
			best = key
	if best != "":
		selected_key_set(best)


func _axial_to_world(q: int, r: int) -> Vector3:
	var x := HEX_RADIUS * sqrt(3.0) * (q + r * 0.5)
	var z := HEX_RADIUS * 1.5 * r
	return Vector3(x, 0, z)


func _prism_mesh(radius: float, height: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var corners: Array[Vector3] = []
	for i in 6:
		var angle := deg_to_rad(60.0 * i - 30.0)
		corners.append(Vector3(cos(angle) * radius, 0, sin(angle) * radius))
	var top := Vector3(0, height, 0)
	for i in 6:
		var a: Vector3 = corners[i]
		var b: Vector3 = corners[(i + 1) % 6]
		_tri(st, top, a + Vector3(0, height, 0), b + Vector3(0, height, 0), Vector3.UP)
		var side_n := (a + b).normalized()
		side_n.y = 0
		_tri(st, a, b, b + Vector3(0, height, 0), side_n)
		_tri(st, a, b + Vector3(0, height, 0), a + Vector3(0, height, 0), side_n)
	return st.commit()


func _peak_mesh() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var tip := Vector3(0, 1.1, 0)
	for i in 5:
		var a1 := deg_to_rad(72.0 * i)
		var a2 := deg_to_rad(72.0 * (i + 1))
		var p1 := Vector3(cos(a1) * 0.45, 0, sin(a1) * 0.45)
		var p2 := Vector3(cos(a2) * 0.45, 0, sin(a2) * 0.45)
		_tri(st, p1, p2, tip, (p1 + p2 + tip).normalized())
	return st.commit()


func _tree_mesh() -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var tip := Vector3(0, 1.3, 0)
	for i in 6:
		var a1 := deg_to_rad(60.0 * i)
		var a2 := deg_to_rad(60.0 * (i + 1))
		var p1 := Vector3(cos(a1) * 0.45, 0.3, sin(a1) * 0.45)
		var p2 := Vector3(cos(a2) * 0.45, 0.3, sin(a2) * 0.45)
		_tri(st, p1, p2, tip, Vector3.UP)
	return st.commit()


func _tri(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, normal: Vector3) -> void:
	st.set_normal(normal)
	st.set_uv(Vector2(0, 0))
	st.add_vertex(a)
	st.set_normal(normal)
	st.set_uv(Vector2(1, 0))
	st.add_vertex(b)
	st.set_normal(normal)
	st.set_uv(Vector2(0.5, 1))
	st.add_vertex(c)


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


func _key(q: int, r: int) -> String:
	return "q%sr%s" % [q, r]
