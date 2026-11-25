# TADBEER: Smart Food & Inventory Management System

**Course:** Fundamental of Computational Thinking — Python (BCS2013)  
**Institution:** City University Malaysia  
**SDG Alignment:** SDG 2 (Zero Hunger)

## Project Overview
TADBEER is a modular Python console application designed to reduce food waste across Restaurants, Cafes, Bakeries, and Supermarkets/Grocery Stores. It tracks real-time elapsed shelf-life, applies staged markdowns (15% and 30%), anonymizes flash-sale batches into `Mystery Box` bundles with daily per-customer purchase quotas, and routes near-expired batches to `Urgent Donation` (RM 0.00).

## Project Structure
- `TADBEER/main.py`: Application entry point, sector selection (`hours` vs. `days`), and main menu loop.
- `TADBEER/models.py`: `FoodItem` data model, real-time UTC countdown, and staged pricing rules.
- `TADBEER/operations.py`: `RescueSystem` manager, Point-of-Sale (POS) quota validation, and atomic JSON persistence.
- `TADBEER/utils.py`: Formatted console banners, inventory tables, and sustainability impact receipts.

## How to Run
Ensure **Python 3.10+** is installed, then navigate into the project folder and run:

    cd TADBEER
    python main.py

## Group Members
- Ali Saeedahmed Ali Mohamed      (ID: 202504010041)
- Khaled Mohammed Ahmed Abdulhak  (ID: 202309010637)
- Yaamr Rashad Ebrahim Saleh      (ID: 202401010351)
- ABDELAZIZ ELFADIL MOHAMED SATTI (ID: 202409010458)
- ABDELRAHMAN AWAD OSMAN MUSTAFA  (ID: 202405010239)
