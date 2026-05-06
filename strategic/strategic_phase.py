"""
strategic/strategic_phase.py
"""

class StrategicPhase:
    def __init__(self):
        self.turn = 1
        self.resources = {"RUs": 500, "CUs": 300, "RP": 100}  # Research Points

    def do_industrial_phase(self):
        print(f"Turn {self.turn}: Industrial & Manpower Phase")
        self.resources["RUs"] += 80   # Example production

    def do_logistics_phase(self):
        print("Logistics & Maritime Phase - ship movements, supply traces")

    def do_invasion_phase(self):
        print("Invasion Phase - transition to Island Map or Tactical Battle")

    def end_turn(self):
        self.turn += 1
        print(f"Strategic Turn {self.turn} started.")