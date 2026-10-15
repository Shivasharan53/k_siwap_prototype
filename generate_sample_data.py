import pandas as pd

def create_synthetic_csv(filename="synthetic_karnataka_labour_raw.csv"):
    data = [
        # Clean records - 2025-Q1 & 2025-Q2
        {"district": "Bengaluru Urban", "sector": "IT & ITeS", "occupation": "Data Analyst", "skills": "Python, SQL, PowerBI, Statistics", "indicator_type": "Job Postings", "demand_value": 1450, "training_supply": 620, "time_period": "2025-Q1", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        {"district": "Bengaluru Urban", "sector": "IT & ITeS", "occupation": "Data Analyst", "skills": "Python, SQL, PowerBI, Statistics, GenAI", "indicator_type": "Job Postings", "demand_value": 1680, "training_supply": 650, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        {"district": "Bengaluru Urban", "sector": "IT & ITeS", "occupation": "AI/ML Engineer", "skills": "Python, PyTorch, LLM, MLOps", "indicator_type": "Job Postings", "demand_value": 920, "training_supply": 280, "time_period": "2025-Q1", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        {"district": "Bengaluru Urban", "sector": "IT & ITeS", "occupation": "AI/ML Engineer", "skills": "Python, PyTorch, LLM, MLOps, Agentic AI", "indicator_type": "Job Postings", "demand_value": 1210, "training_supply": 310, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        
        {"district": "Kalaburagi", "sector": "Construction & Infrastructure", "occupation": "Civil Supervisor", "skills": "AutoCAD, Site Safety, Estimation, Surveying", "indicator_type": "Job Postings", "demand_value": 340, "training_supply": 150, "time_period": "2025-Q1", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        {"district": "Kalaburagi", "sector": "Construction & Infrastructure", "occupation": "Civil Supervisor", "skills": "AutoCAD, Site Safety, Estimation, BIM", "indicator_type": "Job Postings", "demand_value": 410, "training_supply": 165, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        {"district": "Kalaburagi", "sector": "Healthcare", "occupation": "Lab Technician", "skills": "Phlebotomy, Diagnostics, Bio-Safety", "indicator_type": "Job Postings", "demand_value": 290, "training_supply": 120, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},

        {"district": "Mysuru", "sector": "Manufacturing", "occupation": "CNC Operator", "skills": "CNC Programming, CAD/CAM, Quality Control", "indicator_type": "Job Postings", "demand_value": 520, "training_supply": 310, "time_period": "2025-Q1", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        {"district": "Mysuru", "sector": "Manufacturing", "occupation": "CNC Operator", "skills": "CNC Programming, CAD/CAM, Quality Control, Robotics", "indicator_type": "Job Postings", "demand_value": 610, "training_supply": 330, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},

        {"district": "Dharwad", "sector": "Automotive & EV", "occupation": "EV Battery Technician", "skills": "Battery Management, High Voltage Safety, Diagnostics", "indicator_type": "Job Postings", "demand_value": 380, "training_supply": 110, "time_period": "2025-Q1", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        {"district": "Dharwad", "sector": "Automotive & EV", "occupation": "EV Battery Technician", "skills": "Battery Management, High Voltage Safety, Diagnostics, Thermal Systems", "indicator_type": "Job Postings", "demand_value": 490, "training_supply": 130, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},

        {"district": "Belagavi", "sector": "Manufacturing", "occupation": "Foundry Technician", "skills": "Metallurgy, Casting, Quality Testing, Safety", "indicator_type": "Job Postings", "demand_value": 460, "training_supply": 240, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},

        # Intentional Dirty Records for Module 1 Validation Demo
        # 1. Inconsistent District & Sector labels ("Gulbarga" instead of "Kalaburagi", "IT/ITES" instead of "IT & ITeS")
        {"district": "Gulbarga", "sector": "IT/ITES", "occupation": "Junior Web Developer", "skills": "Java, Python, HTML, SQL", "indicator_type": "Job Postings", "demand_value": 210, "training_supply": 95, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        # 2. Missing value in skills & training_supply
        {"district": "Mangaluru", "sector": "Logistics", "occupation": "Supply Chain Coordinator", "skills": None, "indicator_type": "Job Postings", "demand_value": 330, "training_supply": None, "time_period": "2025-Q2", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
        # 3. Exact Duplicate Record
        {"district": "Mysuru", "sector": "Manufacturing", "occupation": "CNC Operator", "skills": "CNC Programming, CAD/CAM, Quality Control", "indicator_type": "Job Postings", "demand_value": 520, "training_supply": 310, "time_period": "2025-Q1", "units": "Number of Persons/Roles", "source": "Synthetic Demo Portal v1", "source_url": "https://example.org/synthetic-ksisu"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return df

if __name__ == "__main__":
    create_synthetic_csv()
    print("Created synthetic_karnataka_labour_raw.csv successfully.")
