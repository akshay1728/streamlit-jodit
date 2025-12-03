from synthetic_data_generator.dynamic_generator import DynamicGenerator

def main():
    """
    Example of how to use the improved, more flexible DynamicGenerator.
    """
    # A more creative prompt that uses different keywords
    prompt = "I need a file for patient records. It should have a patient id, a diagnosis, a begin date for the condition, and a completion date. Also, add a column for notes."

    # Create an instance of the dynamic generator
    generator = DynamicGenerator()

    # Generate 15 rows of synthetic data
    try:
        synthetic_data = generator.generate(prompt=prompt, num_rows=15)

        # Print the first 10 rows of the generated data
        print("Generated Patient Data:")
        print(synthetic_data.head(10))

        # Save the generated data to a CSV file
        synthetic_data.to_csv('synthetic_patient_data.csv', index=False)
        print("\nData saved to synthetic_patient_data.csv")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
