from synthetic_data_generator.generator import SyntheticDataGenerator

def main():
    """
    Example of how to use the SyntheticDataGenerator.
    """
    # Define the specifications for the health data file
    health_specifications = {
        'Start_date': {'type': 'date', 'start': '-2y', 'end': 'today'},
        'end_date': {'type': 'date', 'start': 'Start_date', 'end': '+1y'},
        'health_condition': {'type': 'choice', 'choices': ['diabetes', 'BP', 'heart condition', 'asthma', 'migraine']},
        'comment': {'type': 'text', 'max_nb_chars': 150},
        'person_id': {'type': 'person_id'}
    }

    # Create an instance of the generator
    generator = SyntheticDataGenerator(specifications=health_specifications)

    # Generate 100 rows of synthetic data with a 50% unique person ratio
    synthetic_data = generator.generate(num_rows=100, unique_person_ratio=0.5)

    # Print the first 10 rows of the generated data
    print("Generated Health Data:")
    print(synthetic_data.head(10))

    # Save the generated data to a CSV file
    synthetic_data.to_csv('synthetic_health_data.csv', index=False)
    print("\nData saved to synthetic_health_data.csv")


if __name__ == "__main__":
    main()
