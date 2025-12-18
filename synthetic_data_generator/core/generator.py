# synthetic_data_generator/core/generator.py

import pandas as pd
from faker import Faker
import random
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import db_utils

class SyntheticDataGenerator:
    """
    The core engine for generating synthetic data based on a detailed specification.
    """
    def __init__(self, specifications, server, database, username):
        self.specifications = specifications
        self.server = server
        self.database = database
        self.username = username
        self.faker = Faker()
        self._prepare_data_sources()

    def _prepare_data_sources(self):
        """
        Pre-fetches data from the database for scvid and group types, supporting multiple sources.
        """
        self.data_sources = {}
        for col_name, col_spec in self.specifications.items():
            if col_spec.get('type') in ['scvid', 'group']:
                sources = col_spec.get('options', {}).get('sources', [])
                if sources:
                    self.data_sources[col_name] = []
                    for source in sources:
                        table, column, percentage = source['table'], source['column'], source['percentage']
                        sample = db_utils.get_data_sample(table, column, percentage, self.server, self.database, self.username)
                        self.data_sources[col_name].append({'data': sample, 'weight': percentage})

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
                choices = col_spec.get('options', {}).get('choices', [])
                if choices:
                    value = random.choice(choices)
                else:
                    value = None # Fallback for empty choices list

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

            elif col_type == 'integer':
                min_val = col_spec.get('min', 0)
                max_val = col_spec.get('max', 100)
                value = random.randint(min_val, max_val)

            elif col_type == 'currency':
                min_val = col_spec.get('min', 0.0)
                max_val = col_spec.get('max', 1000.0)
                amount = random.uniform(min_val, max_val)
                value = f"£{amount:.2f}"

            elif col_type in ['scvid', 'group']:
                sources = self.data_sources.get(col_name)
                if sources:
                    # Perform a weighted random choice to select a source
                    source_list = [s['data'] for s in sources]
                    weights = [s['weight'] for s in sources]
                    chosen_source_data = random.choices(source_list, weights=weights, k=1)[0]
                    if chosen_source_data:
                        value = random.choice(chosen_source_data)
                    else:
                        value = None
                else:
                    value = None # Fallback if no sources are defined

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
