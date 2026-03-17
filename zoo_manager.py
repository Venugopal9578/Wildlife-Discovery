import requests
import sqlite3
import json
import time
import string
import os
from tqdm import tqdm
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize behavior
load_dotenv()
init(autoreset=True)

# Configuration
API_URL = "https://api.api-ninjas.com/v1/animals"
API_KEY = os.getenv("ANIMALS_API_KEY", "YOUR_API_KEY_HERE")
DB_NAME = "animals.db"
DELAY_SECONDS = 0.2

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create table with FULL schema correctly from the start
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS species (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            scientific_name TEXT,
            kingdom TEXT,
            class TEXT,
            family TEXT,
            type TEXT,
            habitat TEXT,
            diet TEXT,
            lifespan TEXT,
            weight TEXT,
            top_speed TEXT,
            color TEXT,
            locations TEXT,
            animal_type TEXT
        )
    ''')
    conn.commit()
    return conn

def get_animal_type(taxonomy, characteristics):
    """Categorize animal as Land, Water, or Air based on Class, Type, and Habitat."""
    animal_class = taxonomy.get('class', '').lower()
    animal_type = characteristics.get('type', '').lower()
    habitat = characteristics.get('habitat', '').lower()
    
    # AIR: Birds and bats
    if 'aves' in animal_class or 'bird' in animal_type or 'fly' in habitat:
        return 'Air'
    
    # WATER: Fish, Cetaceans, Amphibians (mostly), and water habitats
    water_keywords = ['fish', 'shark', 'whale', 'dolphin', 'ocean', 'river', 'lake', 'sea', 'water', 'marine']
    if any(k in animal_class for k in ['actinopterygii', 'chondrichthyes']) or \
       any(k in animal_type for k in ['fish', 'amphibian', 'crustacean']) or \
       any(k in habitat for k in water_keywords):
        return 'Water'
    
    # LAND: Default for mammals, reptiles, etc. unless specified above
    return 'Land'

def fetch_animal_data(search_term):
    headers = {'X-Api-Key': API_KEY}
    try:
        response = requests.get(f"{API_URL}?name={search_term}", headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # Silently sleep to avoid breaking tqdm UI
            time.sleep(5)
            # Retry once
            response = requests.get(f"{API_URL}?name={search_term}", headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
        else:
            return None
    except Exception:
        return None

def process_and_save(conn, data):
    if not data:
        return 0
    
    saved_count = 0
    cursor = conn.cursor()
    for item in data:
        name = item.get('name')
        if not name:
            continue
            
        taxonomy = item.get('taxonomy', {})
        characteristics = item.get('characteristics', {})
        
        # New classification logic
        animal_type_category = get_animal_type(taxonomy, characteristics)
        
        # Extract fields
        scientific_name = taxonomy.get('scientific_name')
        kingdom = taxonomy.get('kingdom')
        animal_class = taxonomy.get('class')
        family = taxonomy.get('family')
        
        habitat = characteristics.get('habitat')
        diet = characteristics.get('diet')
        lifespan = characteristics.get('lifespan')
        weight = characteristics.get('weight')
        top_speed = characteristics.get('top_speed')
        color = characteristics.get('color')
        api_type = characteristics.get('type')
        
        locations_list = item.get('locations', [])
        locations_str = ", ".join(locations_list) if isinstance(locations_list, list) else str(locations_list)
        
        try:
            # Using ON CONFLICT (name) DO UPDATE to merge new data without losing record IDs
            # This is the standard "Upsert" method for production pipelines
            cursor.execute('''
                INSERT INTO species (
                    name, scientific_name, kingdom, class, family, type, 
                    habitat, diet, lifespan, weight, top_speed, color, 
                    locations, animal_type
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    scientific_name=excluded.scientific_name,
                    kingdom=excluded.kingdom,
                    class=excluded.class,
                    family=excluded.family,
                    type=excluded.type,
                    habitat=excluded.habitat,
                    diet=excluded.diet,
                    lifespan=excluded.lifespan,
                    weight=excluded.weight,
                    top_speed=excluded.top_speed,
                    color=excluded.color,
                    locations=excluded.locations,
                    animal_type=excluded.animal_type
            ''', (
                name, scientific_name, kingdom, animal_class, family, api_type,
                habitat, diet, lifespan, weight, top_speed, color,
                locations_str, animal_type_category
            ))
            saved_count += 1
        except Exception:
            pass
    
    conn.commit()
    return saved_count

# Common animal groups and names to broaden search discovery
COMMON_ANIMALS_SEED = [
    "Mammal", "Bird", "Fish", "Reptile", "Amphibian", "Insect", "Spider", "Shark", "Whale", 
    "Snake", "Lizard", "Frog", "Eagle", "Owl", "Hawk", "Falcon", "Eagle", "Duck", "Swan", 
    "Goose", "Penguin", "Parrot", "Monkey", "Ape", "Bear", "Wolf", "Fox", "Cat", "Dog", 
    "Deer", "Horse", "Cow", "Pig", "Sheep", "Goat", "Elephant", "Rhino", "Hippo", "Giraffe", 
    "Zebra", "Lion", "Tiger", "Leopard", "Cheetah", "Hyena", "Seal", "Walrus", "Otter", 
    "Badger", "Rabbit", "Mouse", "Rat", "Bat", "Snail", "Crab", "Lobster", "Shrimp", "Bee", 
    "Ant", "Fly", "Beetle", "Butterfly", "Moth", "Worm", "Jellyfish", "Coral", "Octopus", 
    "Squid", "Turtle", "Tortoise", "Crocodile", "Alligator", "Dolphin", "Porpoise", "Ray",
    "Panda", "Koala", "Kangaroo", "Wallaby", "Wombat", "Platypus", "Lemur", "Sloth", 
    "Armadillo", "Anteater", "Meerkat", "Mongoose", "Opossum", "Raccoon", "Skunk", "Squirrel",
    "Gopher", "Woodpecker", "Hummingbird", "Flamingo", "Pelican", "Stork", "Heron", "Vulture",
    "Cobra", "Viper", "Python", "Boa", "Mamba", "Gecko", "Iguana", "Chameleon", "Monitor",
    "Trout", "Salmon", "Tuna", "Cod", "Bass", "Carp", "Perch", "Eel", "Stingray"
]

def main():
    print(Fore.CYAN + Style.BRIGHT + "\n--- Zoo Manager: Targeted Data Collection ---")
    conn = init_db()
    
    total_processed = 0
    letters = string.ascii_lowercase
    # Combine Seed List with 2-letter prefixes
    # We use a set to avoid duplicates and convert back to list for tqdm
    search_terms = list(dict.fromkeys(COMMON_ANIMALS_SEED + list(letters) + [a + b for a in letters for b in letters]))
    
    print(Fore.YELLOW + f"Starting collection using {len(search_terms)} targeted terms...\n")
    
    # Wrap with tqdm
    pbar = tqdm(search_terms, desc="Syncing Animals", unit="term", ncols=100, 
                bar_format="{l_bar}" + Fore.GREEN + "{bar}" + Fore.RESET + " {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")
    
    try:
        for term in pbar:
            data = fetch_animal_data(term)
            if data:
                new_count = process_and_save(conn, data)
                total_processed += new_count
            
            pbar.set_postfix({"Saved/Enriched": f"{total_processed}"}, refresh=True)
            time.sleep(DELAY_SECONDS)
                
    except KeyboardInterrupt:
        print(Fore.RED + "\n\nProcess interrupted. Saving progress...")

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM species")
    final_total = cursor.fetchone()[0]
    conn.close()
    
    print(Fore.GREEN + Style.BRIGHT + "\n\n--- Collection Summary ---")
    print(Fore.WHITE + f"Total unique species in database: " + Fore.CYAN + f"{final_total}")
    print(Fore.GREEN + "Data collection complete! Checking for growth...\n")

if __name__ == "__main__":
    main()
