import calendar
# from pydantic import BaseModel, conint
# from typing import List

def get_calendar_for_any_month(month: int, year: int) -> str:
    """
    Retrieve the calendar for a given month and year.

    Parameters:
        month (int): The month number (1 for January, 2 for February, etc.).
        year (int): The year as a four-digit number (e.g., 2025).

    Returns:
        str: The calendar for the given month and year.
    """
    cal = calendar.monthcalendar(year, month)
    
    # # Define headers with fixed width (10 chars each)
    # days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    # header = ''.join(day.ljust(10) for day in days)
    
    # # Initialize output with header
    # output = [header]
    
    # # Format each week with proper spacing
    # for week in cal:
    #     week_str = ''
    #     for day in week:
    #         if day == 0:
    #             # Empty days are filled with spaces
    #             week_str += ' ' * 10
    #         else:
    #             # Right-align the day number with padding
    #             week_str += str(day).rjust(2) + ' ' * 8
    #     output.append(week_str)
    
    # return '\n'.join(output)

    # CSV format
    output = "Mon,Tue,Wed,Thu,Fri,Sat,Sun\n"
    for week in cal:
        # output += ",".join(str(day) for day in week) + "\n"
        # replace 0 with "NA"
        output += ",".join(str(day) if day != 0 else "NA" for day in week) + "\n"
    return output

# GET_calendar_FOR_ANY_MONTH_TOOL_DESC_JSON = {
#     "type": "function",
#     "function": {
#         "name": "get_calendar_for_any_month",
#         "description": "Retrieve the calendar for a given month and year.",
#         "parameters": {
#             "type": "object",
#             "properties": {
#             "month": {
#                 "type": "integer",
#                 "description": "The month number (1 for January, 2 for February, etc.)."
#             },
#             "year": {
#                 "type": "integer",
#                 "description": "The year as a four-digit number (e.g., 2025)."
#             }
#             },
#             "required": ["month", "year"]
#         },
#     },
# }

if __name__ == "__main__":
    print(get_calendar_for_any_month(2, 2025))
