from synthetic_data_generator.dynamic_generator import DynamicGenerator

def main():
    """
    Example of how to use the DynamicGenerator with the default health patterns.
    """
    # The user's original prompt for a health file
    prompt = "Create a health file with a start date, end date, a health condition, some comments, and a person id."

    # Create an instance of the dynamic generator (no custom patterns needed for this prompt)
    generator = DynamicGenerator()

    # Generate 10 rows of synthetic data
    try:
        synthetic_data = generator.generate(prompt=prompt, num_rows=10)

        # Print the generated data
        print("Generated Health Data:")
        print(synthetic_data.head())

        # Save the generated data to a CSV file
        synthetic_data.to_csv('synthetic_health_data.csv', index=False)
        print("\nData saved to synthetic_health_data.csv")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
