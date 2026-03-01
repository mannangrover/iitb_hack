import random
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.database import SessionLocal, init_db
from src.database.models import Transaction
import os

class DataLoader:
    """Load and manage transaction data"""
    
    def __init__(self):
        self.categories = [
            "Food", "Entertainment", "Travel", "Shopping", "Utilities", 
            "Healthcare", "Education", "Bills", "Downloads", "Other"
        ]
        self.states = [
            "Maharashtra", "Karnataka", "Delhi", "Tamil Nadu", "Telangana",
            "Gujarat", "Rajasthan", "Punjab", "West Bengal", "Uttar Pradesh",
            "Andhra Pradesh", "Haryana", "Madhya Pradesh", "Bihar", "Odisha"
        ]
        self.devices = ["iOS", "Android", "Web"]
        self.networks = ["WiFi", "4G", "5G"]
        self.age_groups = ["13-18", "18-25", "25-35", "35-45", "45-55", "55+"]
        self.statuses = ["success", "failed", "pending"]
    
    def generate_synthetic_data(self, num_records: int = 250000) -> list:
        """Generate synthetic transaction data"""
        print(f"Generating {num_records} synthetic transactions...")
        
        transactions = []
        base_date = datetime.now() - timedelta(days=90)
        
        for i in range(num_records):
            # Varied amounts by category
            category = random.choice(self.categories)
            base_amount = {
                "Food": 500, "Entertainment": 2000, "Travel": 5000,
                "Shopping": 3000, "Utilities": 1500, "Healthcare": 4000,
                "Education": 8000, "Bills": 2000, "Downloads": 500, "Other": 2000
            }.get(category, 2000)
            
            amount = base_amount + random.gauss(0, base_amount * 0.3)
            amount = max(100, min(50000, amount))  # Clamp between 100 and 50000
            
            # Higher fraud rate in certain categories
            fraud_chance = {
                "Shopping": 0.08, "Downloads": 0.06, "Entertainment": 0.04,
                "Travel": 0.03, "Other": 0.05
            }.get(category, 0.02)
            
            # Higher failure rate on poor networks
            device = random.choice(self.devices)
            network = random.choice(self.networks)
            failure_chance = {
                "5G": 0.01, "WiFi": 0.02, "4G": 0.03
            }.get(network, 0.02)
            
            status = "failed" if random.random() < failure_chance else random.choice(["success", "pending"]) if random.random() < 0.05 else "success"
            
            transaction = Transaction(
                user_id=random.randint(1, 50000),
                amount=round(amount, 2),
                category=category,
                timestamp=base_date + timedelta(
                    days=random.randint(0, 90),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                ),
                device_type=device,
                network_type=network,
                state=random.choice(self.states),
                age_group=random.choice(self.age_groups),
                status=status,
                fraud_flag=random.random() < fraud_chance,
                merchant_id=random.randint(1000, 9999),
                latitude=random.uniform(8.0, 35.0),
                longitude=random.uniform(68.0, 97.0)
            )
            transactions.append(transaction)
            
            if (i + 1) % 50000 == 0:
                print(f"  Generated {i + 1}/{num_records} transactions")
        
        return transactions
    
    def load_from_csv(self, csv_path: str) -> list:
        """Load transactions from CSV file matching new schema"""
        print(f"Loading data from {csv_path}...")
        
        df = pd.read_csv(csv_path)
        transactions = []
        
        print(f"CSV columns: {df.columns.tolist()}")
        print(f"Total records in CSV: {len(df)}")
        
        # Mapping for day names to numbers
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        
        for idx, row in df.iterrows():
            try:
                # Handle transaction_id: extract numeric part if it's a string like "TXN0000249838"
                tx_id = row.get('transaction id', idx + 1)
                if isinstance(tx_id, str):
                    # Extract only digits
                    numeric_id = ''.join(filter(str.isdigit, tx_id))
                    transaction_id = int(numeric_id) if numeric_id else idx + 1
                else:
                    transaction_id = int(tx_id)
                
                # Handle day_of_week: convert from string to int if needed
                day_val = row.get('day_of_week', 'Monday')
                if isinstance(day_val, str):
                    day_of_week = day_mapping.get(day_val.strip(), 0)
                else:
                    day_of_week = int(day_val)
                
                # Handle is_weekend: convert to boolean
                is_weekend_val = row.get('is_weekend', False)
                if isinstance(is_weekend_val, str):
                    is_weekend = is_weekend_val.strip().lower() in ['true', '1', 'yes']
                else:
                    is_weekend = bool(is_weekend_val)
                
                # Map CSV columns to new Transaction model schema (handling spaces in column names)
                transaction = Transaction(
                    transaction_id=transaction_id,
                    timestamp=pd.to_datetime(row.get('timestamp'), errors='coerce'),
                    transaction_type=str(row.get('transaction type', 'Transfer')).strip(),
                    merchant_category=str(row.get('merchant_category', 'Other')).strip(),
                    amount=float(row.get('amount (INR)', 0)),
                    transaction_status=str(row.get('transaction_status', 'success')).strip().lower(),
                    sender_age_group=str(row.get('sender_age_group', '25-35')).strip(),
                    sender_state=str(row.get('sender_state', 'Delhi')).strip(),
                    sender_bank=str(row.get('sender_bank', 'HDFC')).strip(),
                    receiver_age_group=str(row.get('receiver_age_group', '25-35')).strip(),
                    receiver_bank=str(row.get('receiver_bank', 'ICICI')).strip(),
                    device_type=str(row.get('device_type', 'Mobile')).strip(),
                    network_type=str(row.get('network_type', 'WiFi')).strip(),
                    fraud_flag=bool(row.get('fraud_flag', False)),
                    hour_of_day=int(row.get('hour_of_day', 12)),
                    day_of_week=day_of_week,
                    is_weekend=is_weekend
                )
                transactions.append(transaction)
            except Exception as e:
                print(f"Error processing row {idx}: {str(e)}")
                continue
            
            if (idx + 1) % 50000 == 0:
                print(f"  Processed {idx + 1}/{len(df)} records")
        
        print(f"Loaded {len(transactions)} transactions from CSV")
        return transactions
    
    def insert_to_database(self, transactions: list, db: Session = None):
        """Insert transactions into database"""
        if db is None:
            db = SessionLocal()
        
        print(f"Inserting {len(transactions)} transactions into database...")
        
        # Batch insert for performance
        batch_size = 5000
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i+batch_size]
            db.add_all(batch)
            db.commit()
            print(f"  Committed {min(i+batch_size, len(transactions))}/{len(transactions)} transactions")
        
        db.close()
        print("✓ Data import complete!")
    
    def load_and_populate(self, csv_path: str = None, num_synthetic: int = 250000, force_reload: bool = False):
        """Load data (from CSV or generate synthetic) and populate database"""
        
        # Initialize database
        init_db()
        db = SessionLocal()
        
        # Check if database already has data
        existing_count = db.query(Transaction).count()
        if existing_count > 0 and not force_reload:
            print(f"Database already contains {existing_count} transactions. Use force_reload=True to reload.")
            db.close()
            return
        elif existing_count > 0 and force_reload:
            print(f"Clearing existing {existing_count} transactions...")
            db.query(Transaction).delete()
            db.commit()
        
        # Load data
        if csv_path and os.path.exists(csv_path):
            transactions = self.load_from_csv(csv_path)
        else:
            print("No CSV file provided. Generating synthetic data...")
            transactions = self.generate_synthetic_data(num_synthetic)
        
        # Insert into database
        self.insert_to_database(transactions, db)

if __name__ == "__main__":
    import sys
    
    loader = DataLoader()
    
    # Check for CSV file argument
    csv_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    if csv_file:
        loader.load_and_populate(csv_path=csv_file)
    else:
        print("No CSV file provided. Generating synthetic data...")
        loader.load_and_populate()
