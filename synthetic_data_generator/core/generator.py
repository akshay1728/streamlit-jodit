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
                options = col_spec.get('options', {})
                start_ref = options.get('start')
                end_ref = options.get('end')

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
                options = col_spec.get('options', {})
                context_col = options.get('context_column')
                templates = options.get('templates', {})

                # Ensure context_col exists and its value has been generated in the current row
                if context_col and context_col in row:
                    context_value = row[context_col]

                    # Safely get the list of template strings for the context value
                    template_list = templates.get(context_value)

                    # Check if template_list is a non-empty list before choosing from it
                    if isinstance(template_list, list) and template_list:
                        value = random.choice(template_list)
                    else:
                        value = self.faker.sentence() # Fallback if no valid template list
                else:
                    value = self.faker.sentence() # Fallback if context column is missing or not yet generated

            elif col_type == 'integer':
                options = col_spec.get('options', {})
                min_val = options.get('min')
                max_val = options.get('max')
                if min_val is not None and max_val is not None:
                    value = random.randint(min_val, max_val)
                else:
                    value = None

            elif col_type == 'currency':
                options = col_spec.get('options', {})
                min_val = options.get('min')
                max_val = options.get('max')
                if min_val is not None and max_val is not None:
                    amount = random.uniform(min_val, max_val)
                    value = f"£{amount:.2f}"
                else:
                    value = None

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
