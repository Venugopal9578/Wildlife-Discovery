# Animals Discovery & Zoo Manager 🦁

A high-performance Python ETL (Extract, Transform, Load) tool that discovers, classifies, and manages thousands of animal species using the API-Ninjas Animals API.

## 🚀 Features

- **Smart Discovery**: Systematic "Prefix Search" strategy to discover thousands of species.
- **Enriched Data**: Collects detailed data including Scientific Name, Class, Family, Lifespan, Weight, Top Speed, and Colors.
- **Auto-Categorization**: Intelligent logic to classify animals as **Land, Water, or Air** based on biology and habitat.
- **Pipeline Ready**: Uses a modern **UPSERT** (Sync) logic to merge and update data without creating duplicates.
- **Premium CLI**: Beautiful progress bars via `tqdm` and colorized feedback via `colorama`.
- **Targeted Sync**: Includes a curated "Seed List" of common groups for high-speed discovery.

## 🛠️ Project Structure

- `zoo_manager.py`: Core ETL logic, discovery engine, and database manager.
- `animals.db`: SQLite database storing all discovered species.
- `requirements.txt`: Python dependencies.
- `.env`: (Ignored by Git) Your private API keys.

## 🏁 Getting Started

### 1. Prerequisites
- Python 3.8+
- [Git](https://git-scm.com/)

### 2. Setup
Clone the repository (or copy the files) and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. API Key
Create a `.env` file in the root directory and add your API-Ninjas key:
```text
ANIMALS_API_KEY=your_key_here
```

### 4. Run the Discovery
```bash
python zoo_manager.py
```

## 📊 Database Schema
The project uses SQLite with the following columns:
- `name` (Unique)
- `scientific_name`, `kingdom`, `class`, `family`, `type`
- `habitat`, `diet`, `locations`
- `lifespan`, `weight`, `top_speed`, `color`
- `animal_type` (Land/Water/Air)

## 🤝 Contributing
Feel free to open issues or submit pull requests for new features like taxonomic visualizations or more advanced categorization rules!
