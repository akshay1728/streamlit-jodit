import pandas as pd
from faker import Faker
import random
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class SyntheticDataGenerator:
    """
    A class to generate synthetic data based on column specifications.
    """
    def __init__(self, specifications):
        """
        Initializes the SyntheticDataGenerator.

        :param specifications: A dictionary defining the columns and their properties.
                               Example:
                               {
                                   'Start_date': {'type': 'date', 'start': '-1y', 'end': 'today'},
                                   'end_date': {'type': 'date', 'start': 'Start_date', 'end': '+1y'},
                                   'health_condition': {'type': 'choice', 'choices': ['diabetes', 'BP', 'heart condition']},
                                   'comment': {'type': 'text', 'max_nb_chars': 200},
                                   'person_id': {'type': 'person_id'}
                               }
        """
        self.specifications = specifications
        self.faker = Faker()

    def _get_date(self, date_str, reference_date=None):
        """Helper to parse date strings or use reference dates."""
        if isinstance(date_str, (datetime, date)):
            return date_str

        base_date = reference_date if reference_date is not None else datetime.now()
        if isinstance(base_date, date) and not isinstance(base_date, datetime):
            base_date = datetime.combine(base_date, datetime.min.time())

        if date_str == 'today':
            return datetime.now()

        if isinstance(date_str, str) and (date_str.startswith('+') or date_str.startswith('-')):
            try:
                num = int(date_str[:-1])
                unit = date_str[-1]
                if unit == 'y':
                    return base_date + relativedelta(years=num)
                if unit == 'd':
                    return base_date + relativedelta(days=num)
            except (ValueError, TypeError):
                pass

        if reference_date:
            return reference_date
        return datetime.now()


    def _generate_row(self, person_ids):
        """Generates a single row of data."""
        row = {}
        for col_name, col_spec in self.specifications.items():
            col_type = col_spec.get('type')
            value = None

            if col_type == 'date':
                start_date_spec = col_spec.get('start', '-1y')
                end_date_spec = col_spec.get('end', 'today')

                # Validate column order for start date
                if start_date_spec in self.specifications and start_date_spec not in row:
                    raise ValueError(f"Column '{start_date_spec}' must be defined before '{col_name}' in the specification to be used as a reference.")
                start_date_ref = row.get(start_date_spec)
                start_date = self._get_date(start_date_spec, reference_date=start_date_ref)

                # Validate column order for end date
                if end_date_spec in self.specifications and end_date_spec not in row:
                    raise ValueError(f"Column '{end_date_spec}' must be defined before '{col_name}' in the specification to be used as a reference.")
                end_date_ref = row.get(end_date_spec)
                end_date = self._get_date(end_date_spec, reference_date=start_date)

                # Ensure start_date and end_date are datetime objects for comparison
                if isinstance(start_date, date) and not isinstance(start_date, datetime):
                    start_date = datetime.combine(start_date, datetime.min.time())

                if isinstance(end_date, date) and not isinstance(end_date, datetime):
                    end_date = datetime.combine(end_date, datetime.min.time())

                # Ensure start_date is before end_date
                if start_date > end_date:
                    end_date = start_date + relativedelta(days=random.randint(1, 365))

                value = self.faker.date_time_between(start_date=start_date, end_date=end_date).date()

            elif col_type == 'choice':
                value = random.choice(col_spec.get('choices', []))

            elif col_type == 'text':
                value = self.faker.text(max_nb_chars=col_spec.get('max_nb_chars', 200))

            elif col_type == 'person_id':
                value = random.choice(person_ids)

            else:
                raise NotImplementedError(f"Column type '{col_type}' is not supported.")

            row[col_name] = value
        return row

    def generate(self, num_rows, unique_person_ratio=1/3):
        """
        Generates a DataFrame with synthetic data.

        :param num_rows: The number of rows to generate.
        :param unique_person_ratio: The ratio of unique person IDs to the total number of rows.
        :return: A pandas DataFrame with the synthetic data.
        """
        # Generate a pool of person IDs to choose from, to ensure repetition
        num_unique_persons = max(1, int(num_rows * unique_person_ratio))
        person_ids = [self.faker.uuid4() for _ in range(num_unique_persons)]

        data = [self._generate_row(person_ids) for _ in range(num_rows)]

        return pd.DataFrame(data, columns=self.specifications.keys())
