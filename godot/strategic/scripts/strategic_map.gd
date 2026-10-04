extends Node3D
## Strategic theater in raised terrain hexes.
## Air, surface, and below-water layers. Island links kept.

const HEX_RADIUS := 0.82
const DATA_PATH := "res://data/theater.json"

var map_data: Dictionary = {}
var hexes: Array = []
var layer_name := "surface"
var camera: Camera3D
var inspector: Label
var layer_buttons: Dictionary = {}
var dragging := false
var yaw := 0.55
var pitch := 0.72
var distance := 42.0
var focus := Vector3(28, 0, 22)
var mats: Dictionary = {}
var prism: ArrayMesh


func _ready() -> void:
	map_data = _load_map()
	hexes = map_data.get("hexes", [])
	_make_materials()
	prism = _prism_mesh(HEX_RADIUS * 0.94, 1.0)
	_build_world()
	_build_camera()
	_build_ui()


func _load_map() -> Dictionary:
	var file := FileAccess.open(DATA_PATH, FileAccess.READ)
	if file == null:
		return {}
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	return parsed if typeof(parsed) == TYPE_DICTIONARY else {}


func _tex(path: String) -> ImageTexture:
	var image := Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(image) if image else null


func _mat(color: Color, texture_path: String, rough: float) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = rough
	var texture := _tex(texture_path)
	if texture:
		mat.albedo_texture = texture
	return mat


func _make_materials() -> void:
	mats["grass"] = _mat(Color("7ea14a"), "res://textures/grass.png", 0.86)
	mats["water"] = _mat(Color("1d6fd0"), "res://textures/water.png", 0.16)
	mats["deep"] = _mat(Color("0c3c84"), "res://textures/water.png", 0.2)
	mats["sand"] = _mat(Color("e4d2a4"), "res://textures/sand.png", 0.9)
	mats["air"] = _mat(Color("9fd0ea"), "res://textures/water.png", 0.35)
	mats["empty"] = _mat(Color("1c2430"), "res://textures/dirt.png", 1.0)
	mats["hub"] = _mat(Color("b0b0b0"), "res://textures/rock.png", 0.7)


func _build_world() -> void:
	var env := WorldEnvironment.new()
	var world := Environment.new()
	world.background_mode = Environment.BG_COLOR
	world.background_color = Color("7eb6e6")
	world.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	world.ambient_light_color = Color("c5d7ea")
	world.ambient_light_energy = 0.65
	env.environment = world
	add_child(env)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48, 28, 0)
	sun.light_energy = 1.3
	add_child(sun)
	var board := Node3D.new()
	board.name = "Board"
	add_child(board)
	for hex in hexes:
		var tile := MeshInstance3D.new()
		tile.name = "%s_%s" % [hex["c"], hex["r"]]
		tile.mesh = prism
		tile.position = _pixel(int(hex["c"]), int(hex["r"]))
		tile.scale.y = _height_for(hex)
		tile.set_surface_override_material(0, _material_for(hex))
		board.add_child(tile)
		if str(hex.get("name", "")) != "":
			var label := Label3D.new()
			label.text = str(hex["name"])
			label.font_size = 48
			label.position = tile.position + Vector3(0, 0.8, 0)
			label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
			label.modulate = Color("fff8e6")
			board.add_child(label)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.fov = 42
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
	panel.size = Vector2(340, 220)
	panel.modulate = Color(1, 1, 1, 0.92)
	canvas.add_child(panel)
	var box := VBoxContainer.new()
	box.position = Vector2(14, 12)
	box.size = Vector2(312, 196)
	box.add_theme_constant_override("separation", 6)
	panel.add_child(box)
	var title := Label.new()
	title.text = "Blue Horizon"
	title.add_theme_font_size_override("font_size", 24)
	box.add_child(title)
	var row := HBoxContainer.new()
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
	inspector.text = "Right-drag orbits. Click a named island to open its tactical map."
	box.add_child(inspector)


func _set_layer(next_layer: String) -> void:
	layer_name = next_layer
	_mark_layer()
	var board := get_node("Board")
	for hex in hexes:
		var tile := board.get_node_or_null("%s_%s" % [hex["c"], hex["r"]]) as MeshInstance3D
		if tile == null:
			continue
		tile.set_surface_override_material(0, _material_for(hex))
		tile.scale.y = _height_for(hex)


func _mark_layer() -> void:
	for key in layer_buttons:
		layer_buttons[key].modulate = Color(1, 1, 1) if key == layer_name else Color(0.72, 0.72, 0.72)


func _material_for(hex: Dictionary) -> Material:
	var terrain := str(hex["terrain"])
	if layer_name == "air":
		return mats["air"]
	if layer_name == "below":
		if terrain == "land":
			return mats["empty"]
		if terrain == "shallow":
			return mats["water"]
		return mats["deep"]
	if hex.get("industrial", false):
		return mats["hub"]
	if terrain == "land":
		return mats["grass"]
	if terrain == "shallow":
		return mats["sand"]
	return mats["water"]


func _height_for(hex: Dictionary) -> float:
	if layer_name == "air":
		return 0.18
	if str(hex["terrain"]) == "land":
		return 0.55
	if str(hex["terrain"]) == "shallow":
		return 0.28
	return 0.16


func _pixel(col: int, row: int) -> Vector3:
	var x := col * HEX_RADIUS * sqrt(3.0)
	var z := row * HEX_RADIUS * 1.5
	if row % 2 == 1:
		x += HEX_RADIUS * sqrt(3.0) * 0.5
	return Vector3(x, 0, z)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mouse := event as InputEventMouseButton
		if mouse.button_index == MOUSE_BUTTON_WHEEL_UP and mouse.pressed:
			distance = max(12.0, distance - 2.0)
			_place_camera()
		elif mouse.button_index == MOUSE_BUTTON_WHEEL_DOWN and mouse.pressed:
			distance = min(90.0, distance + 2.0)
			_place_camera()
		elif mouse.button_index == MOUSE_BUTTON_RIGHT:
			dragging = mouse.pressed
		elif mouse.button_index == MOUSE_BUTTON_LEFT and mouse.pressed:
			_open_island(mouse.position)
	elif event is InputEventMouseMotion and dragging:
		var motion := event as InputEventMouseMotion
		yaw -= motion.relative.x * 0.008
		pitch = clamp(pitch - motion.relative.y * 0.005, 0.3, 1.15)
		_place_camera()


func _open_island(screen_pos: Vector2) -> void:
	var origin := camera.project_ray_origin(screen_pos)
	var dir := camera.project_ray_normal(screen_pos)
	if abs(dir.y) < 0.001:
		return
	var t := -origin.y / dir.y
	if t < 0:
		return
	var hit := origin + dir * t
	var best: Dictionary = {}
	var best_d := HEX_RADIUS
	for hex in hexes:
		var pos := _pixel(int(hex["c"]), int(hex["r"]))
		var dist := Vector2(pos.x, pos.z).distance_to(Vector2(hit.x, hit.z))
		if dist < best_d:
			best_d = dist
			best = hex
	if best.is_empty() or str(best.get("name", "")) == "":
		inspector.text = "No island on that hex."
		return
	var island_name := str(best["name"])
	var links: Dictionary = map_data.get("links", {})
	if not links.has(island_name):
		inspector.text = "%s has no tactical map yet." % island_name
		return
	var link: Dictionary = links[island_name]
	var project := str(link.get("project", ""))
	if project.begins_with(".."):
		project = ProjectSettings.globalize_path("res://".path_join(project))
	if not FileAccess.file_exists(project.path_join("project.godot")):
		inspector.text = "%s project was not found at %s." % [island_name, project]
		return
	OS.create_process(OS.get_executable_path(), ["--path", project, str(link.get("scene", ""))])
	inspector.text = "Opened %s." % island_name


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
