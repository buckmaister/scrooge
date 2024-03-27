from datetime import datetime
import gspread
import time
from gspread.exceptions import APIError
from config.config import CONFIG


class GSpreadFinanceManager:
    """
    A class for managing interactions with Google Sheets using the gspread library. It provides functionality
    to insert, retrieve, and manipulate data within specified worksheets of a Google Spreadsheet. The class
    supports handling different types of financial transactions (incomes and expenses) and implements retry
    logic for operations that may exceed Google API's rate limits.
    """
    def __init__(self):
        self.spreadsheet_id = CONFIG['SPREADSHEET']['SPREADSHEET_ID']
        self.client = self._init_client(CONFIG['SPREADSHEET']['SERVICE_ACCOUNT_FILE'])
        self.worksheet_income_name = CONFIG['SPREADSHEET']['WORKSHEET_INCOME_NAME']
        self.worksheet_expenses_name = CONFIG['SPREADSHEET']['WORKSHEET_EXPENSES_NAME']
        self.income_start_row = CONFIG['SPREADSHEET']['INCOME_START_ROW']
        self.expenses_start_row = CONFIG['SPREADSHEET']['EXPENSES_START_ROW']
        self.split_income_expenses = CONFIG['SPREADSHEET']['SPLIT_INCOME_EXPENSES']
        self.retry_delay = CONFIG['SPREADSHEET']['RETRY_DELAY']
        self.max_retries = CONFIG['SPREADSHEET']['MAX_RETRIES']

    def _init_client(self, service_account_file):
        """Initialize the gspread client with a service account."""
        return gspread.service_account(filename=service_account_file)

    def _get_worksheet(self, sheet_name):
        """
        Attempts to retrieve a specific worksheet by its name from a Google Spreadsheet.
        This function will retry the operation up to a specified number of attempts (`self.max_retries`)
        if it encounters a quota exceed error from the Google Sheets API.

        Args:
        - sheet_name (str): The name of the worksheet to retrieve.

        Returns:
        - Worksheet object: The requested worksheet if found and successfully retrieved.

        Raises:
        - APIError: If an API error occurs that is not related to exceeding the quota limit.
        - gspread.exceptions.WorksheetNotFound: If no worksheet with the specified name exists.

        Notes:
        - The function uses exponential backoff in case of quota exceed errors, waiting for `self.retry_delay` seconds before retrying.
        - The Google Sheets API has a limit of 60 requests per minute for free accounts, which is why quota exceed errors may occur.
        - This function is part of a class that interacts with the Google Sheets API, where `self.client` is an authenticated gspread client,
          `self.spreadsheet_id` is the ID of the spreadsheet, `self.max_retries` is the maximum number of retries for API requests,
          and `self.retry_delay` is the delay between retries.
        """
        for attempt in range(self.max_retries):
            try:
                return self.client.open_by_key(self.spreadsheet_id).worksheet(sheet_name)
            except APIError as error:
                if error.response.status_code == 429:  # Check if the error is due to excessive requests (free google api support 60 req/min)
                    print(f"Quota exceeded for read requests, retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    raise  # error isn't for excessive requests

    def _prepare_values(self, values, skip_first_value=True, ordered=False):
        """
        Prepares a list of values for insertion into a spreadsheet. Optionally, the first value can be skipped,
        and the list can be sorted based on the datetime in the first column of each row.

        Args:
        - values (list of lists): A list where each element is a list representing a row to be inserted.
          Each row is expected to have a datetime string in its first column if sorting is required.
        - skip_first_value (bool, optional): If True, the first row in the values list will be skipped.
          This is useful for scenarios where the first row contains headers. Defaults to True.
        - ordered (bool, optional): If False, the rows will be sorted in descending order based on the
          datetime in their first column. If True, the original order of rows is preserved. Defaults to False.

        Returns:
        - list: The modified list of values ready for insertion. This list might be sorted and might not
          include the first row, depending on the function arguments.

        Notes:
        - The datetime string in the first column of each row is expected to follow the "%Y-%m-%dT%H:%M:%S" format.
        - If the sorting fails due to a mismatch in the expected datetime format, an error message will be printed,
          and the original (or sliced) list will be returned without sorting.
        """
        if skip_first_value:
            values = values[1:]  # Skipping the header row
        if not ordered:
            try:
                values.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%S"), reverse=True)
            except ValueError as e:
                print(f"Error sorting values: {e}")
        return values

    def _add_row(self, sheet_name, row_index, values=None):
        """
        Given a specific row X, this method adds a new row at that position, inserting the provided values.
        As a result, all existing values below the specified row are shifted down by one row.
        The function retries the operation in case of hitting the API quota limits.

        Args:
        - sheet_name (str): The name of the worksheet where the new row will be added.
        - row_index (int): The index where the new row will be inserted. The index is 1-based.
        - values (list, optional): The list of values to be inserted in the new row. If None, an empty row is added.

        Raises:
        - ValueError: If `row_index` is None.
        - APIError: If any unexpected API error occurs that is not related to exceeding the quota.
        """
        if row_index is None:
            raise ValueError("row index cannot be null!")
        if values is None:
            values = []
        worksheet = self._get_worksheet(sheet_name)
        for attempt in range(self.max_retries):
            try:
                worksheet.insert_row(values or [''] * worksheet.col_count, index=row_index)
                break
            except APIError as error:
                if error.response.status_code == 429:  # Check if the error is due to excessive requests (free google api support 60 req/min)
                    print(f"Quota exceeded, retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

                else:
                    raise  # Re-raise the error if it's not related to quota exceeding

    def _filter_and_sort_values(self, values, latest_date=None, sort_ascending=True):
        """
        Filters and sorts a list of values based on the date contained in the first element of each value sublist.
        The function allows for excluding values older than a specified 'latest_date' and can sort the values
        in either ascending or descending order based on the date.

        Args:
        - values (list of lists): A list of rows, where each row is a list of values. The first value in each row
          is expected to be a date string in the "%Y-%m-%dT%H:%M:%S" format.
        - latest_date (datetime, optional): A datetime object that serves as a cutoff for filtering the values.
          Only rows with a date later than this cutoff will be included in the result. If None, no filtering
          based on date is performed. Defaults to None.
        - sort_ascending (bool, optional): Determines the order in which the filtered values are sorted based on the date.
          If True, the list is sorted in ascending order (earliest to latest). If False, it is sorted in descending order
          (latest to earliest). Defaults to True.

        Returns:
        - list of lists: The filtered and sorted list of values.

        Raises:
        - ValueError: If there's an error parsing the date string from the first value of any row.

        Notes:
        - The function skips the first row in the 'values' list, assuming it to be a header row.
        - Sorting is done based on the date parsed from the first element of each sublist in 'values'.
        - The function prints an error message if it encounters a ValueError, which typically indicates
          a mismatch between the expected date format and the actual format of the date string.
        """
        filtered_values = []
        for v in values[1:]:  # Skipping the header row
            try:
                date = datetime.strptime(v[0], "%Y-%m-%dT%H:%M:%S")
                if latest_date is None or date > latest_date:
                    filtered_values.append(v)
            except ValueError as e:
                print(f"Error filtering values: {e}")
        if sort_ascending:
            filtered_values.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%S"))
        else:
            filtered_values.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%S"), reverse=True)
        return filtered_values

    def _insert_filtered_data(self, sheet_name, values, row_number, direction='below', include_type=None):
        """
        Inserts a list of filtered data rows into a specified worksheet, starting from a given row number.
        Rows can be inserted below or above the specified row number. Optionally, only rows of a specific type
        can be included in the insertion.

        Args:
        - sheet_name (str): The name of the worksheet into which the data will be inserted.
        - values (list of lists): A list of rows (each row being a list of values) to insert into the worksheet.
          The third element in each row is expected to be the type of the row, which is used when filtering
          by 'include_type'.
        - row_number (int): The row number from which to start the insertion. This is a 1-based index.
        - direction (str, optional): Determines the insertion direction relative to 'row_number'.
          If 'below' (default), insertion starts from the specified row number. If 'above',
          insertion starts one row above the specified row number. Defaults to 'below'.
        - include_type (str, optional): If provided, only rows that have this value as their third element
          will be included in the insertion. If None, all rows are included. Defaults to None.

        Behavior:
        - The function iterates through the 'values' list, inserting each row into the worksheet at the
          'insert_position', which is determined based on the 'direction' and 'row_number' parameters.
        - If 'include_type' is specified, only rows matching this type will be inserted.
        - The insertion position is updated after each insertion to ensure that rows are inserted sequentially.

        Note:
        - This function relies on '_get_worksheet' to retrieve the worksheet object and '_add_row' to handle
          the actual insertion of rows into the worksheet. Both of these helper functions need to be defined
          within the same class.
        - It assumes that the worksheet exists and that the caller has the necessary permissions to modify it.
        """
        worksheet = self._get_worksheet(sheet_name)
        insert_position = row_number if direction == 'below' else max(row_number - 1, 1)
        for value in values:
            if include_type is None or value[2] == include_type:
                self._add_row(sheet_name, insert_position, value)
                insert_position += 1

    def insert_row_with_data(self, sheet_name, values, row_number, direction='below', resume_mode=False,
                             ordered=False) -> int:
        """
        Inserts rows into a specified worksheet at a given position, with options for filtering based on date,
        sorting, and insertion direction. This method is designed to handle more complex insertion scenarios,
        including resuming data insertion while avoiding duplicate entries.

        Args:
        - sheet_name (str): The name of the worksheet where the rows will be inserted.
        - values (list of lists): Data to be inserted, where each inner list represents a row and is expected to have
          a date string in its first element in the "%Y-%m-%dT%H:%M:%S" format if resume_mode is enabled.
        - row_number (int): The 1-based index of the row where insertion begins.
        - direction (str, optional): Specifies the insertion direction relative to 'row_number'. Accepts 'below' (default)
          to insert after the specified row or 'above' to insert before it. Defaults to 'below'.
        - resume_mode (bool, optional): If True, the function will fetch data from 'row_number' to check for the latest date
          and filter out any 'values' entries older than this date to avoid duplicates. Defaults to False.
        - ordered (bool, optional): Determines the sorting order of 'values' before insertion. If True, 'values' are sorted
          in ascending order based on the date; if False, they are sorted in descending order. This parameter is considered
          only when 'resume_mode' is True. Defaults to False.

        Returns:
        - int: The number of rows successfully prepared and attempted for insertion. This may include rows filtered out
          in 'resume_mode', so the actual number of rows inserted may be less if some entries were older than existing data.

        Notes:
        - The function leverages '_filter_and_sort_values' to filter and/or sort the data based on the conditions provided
          by 'resume_mode' and 'ordered'.
        - '_insert_filtered_data' is used to handle the actual insertion of filtered and sorted data into the worksheet.
        - In 'resume_mode', the function aims to avoid data duplication by inserting only newer data entries based on the
          latest date found at 'row_number'. This is particularly useful for appending data without repeating entries
          already present in the worksheet.
        """
        if resume_mode:
            latest_data = self.get_data(sheet_name, f"{row_number}:{row_number}")
            latest_date = datetime.strptime(latest_data[0][0], "%Y-%m-%dT%H:%M:%S") if latest_data and latest_data[
                0] and latest_data[0][0] else datetime.min
            values = self._filter_and_sort_values(values, latest_date=latest_date, sort_ascending=ordered)

        self._insert_filtered_data(sheet_name, values, row_number, direction)
        return len(values)

    def insert_incomes_and_expenses(self, values, resume_mode=False, ordered=False) -> []:
        """
        Inserts provided income and expense data into their designated worksheets. The function segregates
        income and expense entries based on a specified column value and then proceeds to insert them into
        respective worksheets. This operation supports conditional data appending and sorting.

        Args:
        - values (list of lists): The complete dataset containing both income and expense entries.
          Each inner list (row) is expected to represent a single transaction with a designated type indicator
          at the third position (v[2]). The first row is assumed to be headers and is therefore skipped.
        - resume_mode (bool, optional): If enabled, the function will append data starting from the last
          entry in each respective worksheet to avoid duplicating existing entries. Defaults to False.
        - ordered (bool, optional): Determines whether the data should be sorted in ascending order based on
          the first column of each row before insertion. Defaults to False.

        Returns:
        - list: A list containing two elements; the first is the number of income entries successfully processed
          and attempted for insertion, and the second is similarly for expense entries. Note that the actual number
          of rows inserted may be less than these counts if `resume_mode` filters out older entries.

        Behavior:
        - The function first segregates the input `values` into `incomes` and `expenses` based on the type indicator
          in each row. By default, "TOPUP" is considered an income type, and all others are considered expenses.
        - It then attempts to insert these segregated lists into their respective worksheets, as determined by
          the class attributes `worksheet_income_name` and `worksheet_expenses_name`.
        - The insertion process for both lists is handled by the `insert_row_with_data` method, which also
          incorporates the logic for `resume_mode` and `ordered` as specified by the function parameters.

        Note:
        - This function assumes that `split_income_expenses` is enabled. If it's not, the function will not
          perform any insertion and will print a message indicating that non-split mode is not supported in
          this implementation. Further implementation is required to handle non-split mode.
        """
        if self.split_income_expenses:
            incomes = [v for v in values[1:] if v[2] == "TOPUP"]  # Skipping the header row
            expenses = [v for v in values[1:] if v[2] != "TOPUP"]  # Skipping the header row

            # Handle incomes
            if incomes:
                inc_added = self.insert_row_with_data(self.worksheet_income_name, incomes, self.income_start_row,
                                                      direction='below', resume_mode=resume_mode, ordered=ordered)

            # Handle expenses
            if expenses:
                exp_added = self.insert_row_with_data(self.worksheet_expenses_name, expenses, self.expenses_start_row,
                                                      direction='below', resume_mode=resume_mode, ordered=ordered)
            return [inc_added, exp_added]
        else:
            # TODO: Handling for non-split mode not implemented
            print(
                "Non-split mode is not supported in this example. Please configure `split_income_expenses` accordingly.")
            return []

    def insert_data(self, sheet_name, range_name, values, skip_first_value=True, ordered=False):
        """Insert data into a specified range in a worksheet."""
        values = self._prepare_values(values, skip_first_value, ordered)
        worksheet = self._get_worksheet(sheet_name)
        worksheet.update(range_name, values)

    def delete_row(self, sheet_name, row_index):
        """Delete a row from a specified worksheet."""
        worksheet = self._get_worksheet(sheet_name)
        worksheet.delete_rows(row_index + 1)

    def get_data(self, sheet_name, range_name):
        """Retrieve data from a specified range in a worksheet."""
        worksheet = self._get_worksheet(sheet_name)
        return worksheet.get(range_name)
