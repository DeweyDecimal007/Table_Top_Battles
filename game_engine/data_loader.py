import pandas as pd
import os

class DataLoader:
    def __init__(self, data_path):
        self.data_path = data_path
        print(f"📁 Looking for data in: {self.data_path}")
        
        self.tanks = {}
        self.guns = {}
        self.ammo = {}
        
        self.load_all_data()

    def load_all_data(self):
        countries = ["Hungary", "Belgium"]
        for country in countries:
            # Tanks
            tank_file = os.path.join(self.data_path, f"{country}_Tanks.xlsx")
            if os.path.exists(tank_file):
                df = pd.read_excel(tank_file)
                self.tanks[country] = df.to_dict('records')
                print(f"✅ Loaded {len(self.tanks[country])} tanks for {country}")
            else:
                print(f"⚠️ Tank file not found: {tank_file}")

            # Guns
            gun_file = os.path.join(self.data_path, f"{country}_Tank_Guns.xlsx")
            if os.path.exists(gun_file):
                df = pd.read_excel(gun_file)
                self.guns[country] = df.to_dict('records')
                print(f"✅ Loaded {len(self.guns[country])} guns for {country}")
            else:
                print(f"⚠️ Gun file not found: {gun_file}")

            # Ammo
            ammo_file = os.path.join(self.data_path, f"{country}_Ammunition_Types.xlsx")
            if os.path.exists(ammo_file):
                df = pd.read_excel(ammo_file)
                self.ammo[country] = df.to_dict('records')
                print(f"✅ Loaded {len(self.ammo[country])} ammo types for {country}")
            else:
                print(f"⚠️ Ammo file not found: {ammo_file}")

        # ... existing tank/gun/ammo loading ...

        self.load_infantry()
        self.load_artillery()   # ← Add this line

    def get_countries(self):
        return ["Hungary", "Belgium"]

    def get_tank_by_name(self, country, tank_name):
        for tank in self.tanks.get(country, []):
            if str(tank.get("MODEL") or "").strip().upper() == str(tank_name).strip().upper():
                return tank
        return None

    def get_ammo_for_gun(self, country, gun_name):
        """Improved ammo lookup"""
        if not gun_name or gun_name == "Select Gun":
            return []
        
        clean_gun = str(gun_name).strip().lower()
        ammo_list = []
        
        print(f"🔍 Searching ammo for gun: '{clean_gun}'")
        
        for a in self.ammo.get(country, []):
            ammo_gun_field = str(a.get("GUN") or a.get("Gun") or a.get("WEAPON") or "").strip().lower()
            ammo_type = str(a.get("TYPE") or a.get("Type") or "").strip()
            
            if ammo_gun_field and (ammo_gun_field in clean_gun or clean_gun in ammo_gun_field):
                if ammo_type and ammo_type not in ammo_list:
                    ammo_list.append(ammo_type)
                    print(f"   ✅ Ammo match: {ammo_type}")
        
        # Fallback: show all ammo for this country if none matched (good for testing)
        if not ammo_list:
            print(f"⚠️ No specific ammo match for '{clean_gun}' — showing all as fallback")
            ammo_list = [str(a.get("TYPE") or "").strip() for a in self.ammo.get(country, []) if str(a.get("TYPE") or "").strip()]
        
        return ammo_list
    
    def load_infantry(self):
        """Load Infantry_Units.xlsx"""
        self.infantry = {}
        file_path = os.path.join(self.data_path, "Infantry_Units.xlsx")
        
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            # Group by country
            for country, group in df.groupby("COUNTRY"):
                self.infantry[country] = group.to_dict('records')
                print(f"✅ Loaded {len(self.infantry[country])} infantry units for {country}")
        else:
            print(f"⚠️ Infantry file not found: {file_path}")
            self.infantry = {}    

    def load_artillery(self):
        """Load Artillery_Units.xlsx"""
        self.artillery = {}
        file_path = os.path.join(self.data_path, "Artillery_Units.xlsx")
        
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            for country, group in df.groupby("COUNTRY"):
                self.artillery[country] = group.to_dict('records')
                print(f"✅ Loaded {len(self.artillery[country])} artillery units for {country}")
        else:
            print(f"⚠️ Artillery file not found: {file_path}")
            self.artillery = {}