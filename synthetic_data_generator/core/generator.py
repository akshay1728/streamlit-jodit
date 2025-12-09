# synthetic_data_generator/core/generator.py

import pandas as pd
from faker import Faker
import random
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class SyntheticDataGenerator:
    """
    The core engine for generating synthetic data based on a detailed specification.
    """
    def __init__(self, specifications):
        self.specifications = specifications
        self.faker = Faker()

    def _generate_row(self, person_ids):
        row = {}
        for col_name, col_spec in self.specifications.items():
            col_type = col_spec.get('type')
            value = None

            if col_type == 'date':
                start_ref = col_spec.get('start', '-1y')
                end_ref = col_spec.get('end', 'today')

                start_date = self._resolve_date(start_ref, row)
                end_date = self._resolve_date(end_ref, row, base_date=start_date)

                if start_date > end_date:
                    end_date = start_date + relativedelta(days=random.randint(1, 30))

                value = self.faker.date_between_dates(date_start=start_date, date_end=end_date)

            elif col_type == 'choice':
                value = random.choice(col_spec.get('choices', []))

            elif col_type == 'text':
                value = self.faker.text(max_nb_chars=col_spec.get('max_nb_chars', 50))

            elif col_type == 'person_id':
                value = random.choice(person_ids)

            elif col_type == 'contextual_text':
                context_col = col_spec.get('context_column')
                templates = col_spec.get('templates', {})
                context_value = row.get(context_col)

                if context_value in templates:
                    value = random.choice(templates[context_value])
                else:
                    value = self.faker.sentence() # Fallback

            row[col_name] = value
        return row

    def _resolve_date(self, ref, row, base_date=None):
        if isinstance(ref, (date, datetime)):
            return ref

        if ref in row and isinstance(row.get(ref), (date, datetime)):
            return row[ref]

        if ref == 'today':
            return date.today()

        # Attempt to parse a fixed date string first (e.g., "2024-01-15")
        try:
            return datetime.strptime(ref, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            pass # Not a fixed date, proceed to relative date logic

        # Handle relative dates like '+30d' or '-1y'
        try:
            base = base_date or date.today()
            if ref and ref[-1] in ('y', 'd') and ref[:-1]:
                num = int(ref[:-1])
                unit = ref[-1]
                if unit == 'y': return base + relativedelta(years=num)
                if unit == 'd': return base + relativedelta(days=num)
        except (ValueError, TypeError, IndexError):
            # Not a valid relative date string
            pass

        # Fallback for any unresolvable reference
        return base_date or date.today()

    def generate(self, num_rows, unique_person_ratio=0.3):
        num_unique_persons = max(1, int(num_rows * unique_person_ratio))
        person_ids = [self.faker.uuid4() for _ in range(num_unique_persons)]

        data = [self._generate_row(person_ids) for _ in range(num_rows)]
        return pd.DataFrame(data)
