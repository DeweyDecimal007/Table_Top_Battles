import random


class SequenceOfPlay:
    def __init__(self):
        self.turn_number = 1
        self.players = ["Player 1 (Blue)", "Player 2 (Red)"]
        self.unit_status = {}          # Will hold real unit data later
        self.current_phase = None

    def run_game_loop(self):
        print("Sequence of Play Engine initialized. Let's command some troops!\n")
        
        while True:
            print(f"\n{'='*50}")
            print(f"                   TURN {self.turn_number}")
            print(f"{'='*50}")

            # Phase 1: Command Cards
            self.phase_command_cards()

            # Phase 2: Movement
            self.phase_movement()

            # Phase 3: Melee
            self.phase_melee()

            # Phase 4: Fire
            self.phase_fire()

            # Phase 5: Command & Control
            self.phase_command_control()

            # Phase 6: Recovery (for next turn)
            self.phase_recovery()

            self.turn_number += 1

            if input("\nEnd of Turn. Start Turn {}? (y/n): ".format(self.turn_number)).lower() != 'y':
                print("\nBattle paused. Your forces stand ready for the next engagement!")
                break

    def phase_command_cards(self):
        print("\n📋 PHASE 1: Place Command Cards")
        for player in self.players:
            input(f"   → {player}: Place your command cards. Press Enter when done...")
        print("   Both players ready. Command cards placed!")

    def phase_movement(self):
        print("\n🏃 PHASE 2: Movement Phase")
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        print(f"   Player 1 rolled: {roll1} | Player 2 rolled: {roll2}")

        if roll1 < roll2:
            order = [self.players[0], self.players[1]]
        else:
            order = [self.players[1], self.players[0]]

        print(f"   Movement Order: {order[0]} moves first, then {order[1]}.")
        
        for player in order:
            input(f"   → {player}: Complete your movement. Press Enter when finished...")

    def phase_melee(self):
        print("\n⚔️ PHASE 3: Melee Contact Check")
        if input("   Did any units come into base-to-base contact? (y/n): ").lower() == 'y':
            print("   Resolve melee fights one by one.")
            input("   Press Enter when all melee combats are resolved...")
        else:
            print("   No melee contacts this turn. Clean movement!")

    def phase_fire(self):
        print("\n🔥 PHASE 4: Fire Phase")
        while True:
            firing_unit = input("\n   Enter firing unit (e.g. T51): ").strip()
            if not firing_unit:
                break
                
            target = input("   Enter target (e.g. S02): ").strip()
            distance = input("   Distance in meters (e.g. 500): ").strip()
            fire_type = input("   Type of fire (direct/indirect/etc.): ").strip()

            print("\n   Cover Types:")
            cover_options = ["No cover", "Soft cover", "Hard cover", "Wood building", "Masonry building"]
            for i, c in enumerate(cover_options, 1):
                print(f"     {i}. {c}")
            cover = input("   Choose cover (number or name): ").strip()

            print("\n   Available Weapons (placeholder for now):")
            weapons = ["Main gun", "HE", "Machine gun", "AP", "Smoke"]
            for i, w in enumerate(weapons, 1):
                print(f"     {i}. {w}")
            selected = input("   Select weapons/ammo (comma separated, e.g. 1,3): ").strip()

            print(f"\n   → {firing_unit} firing at {target} ({distance}m, {fire_type})")
            print(f"     Cover: {cover} | Weapons: {selected}")
            input("   Resolve to-hit and damage. Press Enter to continue...")

            if input("   Another shot this phase? (y/n): ").lower() != 'y':
                break

    def phase_command_control(self):
        print("\n🎖️ PHASE 5: Command & Control Phase")
        print("   Current Unit Statuses:")
        if not self.unit_status:
            print("     No unit statuses tracked yet.")
        else:
            for unit, data in self.unit_status.items():
                print(f"     {unit}: {data.get('status', 'OK')} | Damage: {data.get('damage', [])}")

        print("\n   Update any new statuses (pinned, suppressed, damage, etc.)")
        input("   Press Enter when command & control phase is complete...")

    def phase_recovery(self):
        print("\n🔧 PHASE 6: Recovery / Remedy Phase")
        if input("   Any units attempting recovery or remedies? (y/n): ").lower() == 'y':
            print("   Enter remedies (e.g. replace gunner, rally troops, etc.)")
            print("   These will affect next turn's accuracy/movement.")
            input("   Press Enter when all remedies are noted...")

print("✅ Sequence of Play engine loaded and ready for battle!")