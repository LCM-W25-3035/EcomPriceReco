import csv
import os
import re
from datetime import datetime

def extract_numeric_price(price_str):
    """Extract numeric value from price string"""
    if not price_str or price_str == "":
        return None
    numeric_price = re.sub(r'[^\d.]', '', price_str)
    return float(numeric_price) if numeric_price else None

class DataHandler:
    def __init__(self, input_path, output_path):
        self.input_csv = input_path
        self.output_csv = output_path
    
    def read_input_products(self):
        """Read the input CSV file with product information"""
        print(f"Reading products from {self.input_csv}")
        
        if not os.path.exists(self.input_csv):
            print(f"Input file {self.input_csv} not found.")
            return []
        
        products = []
        with open(self.input_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                products.append(row)
        
        print(f"Loaded {len(products)} products from input file")
        return products
    
    def get_existing_data(self):
        """Read existing data from the output CSV if it exists"""
        tracked_data = []
        max_price_columns = 0
        headers = []
        
        if os.path.exists(self.output_csv):
            with open(self.output_csv, 'r', encoding='utf-8') as f:
                output_reader = csv.DictReader(f)
                headers = output_reader.fieldnames
                
                # Find the highest discounted_price_X column
                for header in headers:
                    if header.startswith('discounted_price_'):
                        try:
                            column_num = int(header.split('_')[-1])
                            max_price_columns = max(max_price_columns, column_num)
                        except ValueError:
                            pass
                
                # Reset file pointer and read the data
                f.seek(0)
                next(f)  # Skip header row
                output_reader = csv.DictReader(f, fieldnames=headers)
                for row in output_reader:
                    tracked_data.append(row)
                
                print(f"Loaded {len(tracked_data)} products from existing tracking data")
        
        return tracked_data, max_price_columns, headers
    
    def prepare_output_columns(self, max_price_columns):
        """Prepare output columns for the CSV file"""
        # Define base columns for the output file
        base_columns = ['Unnamed: 0', 'name', 'main_category', 'sub_category', 'image', 'link', 
                      'ratings', 'no_of_ratings', 'discount_price', 'actual_price']
        
        # Increment max_price_columns for the new extraction
        max_price_columns += 1
        
        # Complete output columns list with current extraction column
        output_columns = base_columns + [f'discounted_price_{i}' for i in range(1, max_price_columns + 1)]
        
        return output_columns, max_price_columns
    
    def save_tracking_data(self, updated_data, output_columns):
        """Save the updated tracking data to the output CSV file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.output_csv), exist_ok=True)
        
        # Write the updated data to the output file
        with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=output_columns)
            writer.writeheader()
            writer.writerows(updated_data)
        
        print(f"Price tracking data saved to {self.output_csv} with {len(output_columns) - 10} historical price columns")
        print(f"Price tracking completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def update_product_data(self, product, current_price, existing_record, idx, max_price_columns):
        """Update or create record for a product with its current price"""
        if existing_record:
            # Get the last known discounted price if current_price is None
            if current_price is None:
                # Try to get the last discounted price
                for i in range(1, max_price_columns):
                    col_name = f'discounted_price_{i}'
                    if col_name in existing_record and existing_record[col_name] and existing_record[col_name].strip():
                        current_price = extract_numeric_price(existing_record[col_name])
                        print(f"Using previous price: {current_price}")
                        break
                
                # If no discounted price found, use initial discount_price
                if current_price is None:
                    current_price = extract_numeric_price(existing_record['discount_price'])
                    print(f"Using initial discount price: {current_price}")
                    
                # If still no price, use actual_price
                if current_price is None:
                    current_price = extract_numeric_price(existing_record['actual_price'])
                    print(f"Using actual price: {current_price}")
            
            # Shift previous prices to the right
            for i in range(max_price_columns, 1, -1):
                prev_column = f'discounted_price_{i-1}' 
                curr_column = f'discounted_price_{i}'
                
                if prev_column in existing_record:
                    existing_record[curr_column] = existing_record[prev_column]
            
            # Add new price at position 1
            if current_price:
                existing_record['discounted_price_1'] = str(current_price)
            else:
                # Fallback to ensure something is in the column
                existing_record['discounted_price_1'] = ""
                
            return existing_record
        else:
            # Create a new record
            new_record = {
                'Unnamed: 0': str(idx),
                'name': product['name'],
                'main_category': product['main_category'],
                'sub_category': product['sub_category'],
                'image': product['image'],
                'link': product['link'],
                'ratings': product['ratings'],
                'no_of_ratings': product['no_of_ratings'],
                'discount_price': product['discount_price'],
                'actual_price': product['actual_price']
            }
            
            # If no current price found, try to use discount_price from input
            if current_price is None:
                current_price = extract_numeric_price(product['discount_price'])
                print(f"Using initial discount price: {current_price}")
                
                # If still no price, use actual_price
                if current_price is None:
                    current_price = extract_numeric_price(product['actual_price'])
                    print(f"Using actual price: {current_price}")
            
            # Add the current price as the first historical price
            if current_price:
                new_record['discounted_price_1'] = str(current_price)
            else:
                new_record['discounted_price_1'] = ""
            
            # Initialize other price columns
            for i in range(2, max_price_columns + 1):
                new_record[f'discounted_price_{i}'] = ""
            
            return new_record
        

# Code generated by ChatGPT
