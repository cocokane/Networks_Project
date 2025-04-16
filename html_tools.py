import re

def nested_list_to_html_table(table: list, buttons: bool = False):
    '''
    Converts a nested list to an HTML table with modern styling.
    The first row of the list is used as table headers.
    If buttons is True, action buttons (delete, update) are added to each row.
    
    Returns:
    html_string: The corresponding table in html format as a string
    '''

    columns = table[0]
    html_string = '<thead><tr>'
    
    if buttons:
        html_string += "<th>Actions</th>"
    else:
        html_string += "<th>#</th>"
        
    for col in columns:
        html_string += "<th>" + str(col) + "</th>"
    
    html_string += "</tr></thead><tbody>"
    
    for i, row in enumerate(table[1:]):
        html_string += "<tr>"
        
        if buttons:
            html_string += """<td class="action-cell">
            <form method="post" class="action-buttons">
                <button name='delete_button' value='""" + ','.join([str(x) for x in row]) + """' class='icon-button delete' title="Delete">
                    <i class="fas fa-trash-alt"></i>
                </button>
                <button name='update_button' value='""" + ','.join([str(x) for x in row]) + """' class='icon-button edit' title="Edit">
                    <i class="fas fa-edit"></i>
                </button>
            </form></td>
            """
        else:
            html_string += "<td>" + str(i + 1) + "</td>"

        for cell in row:
            html_string += "<td>" + str(cell) + "</td>"

        html_string += "</tr>"
    
    html_string += "</tbody>"

    return html_string


def nested_list_to_html_select(nested_list: list):
    '''
    Converts a list of lists into an html select tag.
    The nested_list is the list to be converted and the return value is the corresponding
    select tag in html format as a string.
    
    Returns:
    select_string: The corresponding select tag in html format
    '''
    select_string = "<option disabled selected>Choose table</option>"

    for sub_list in nested_list[1:]:
        for option in sub_list:
            select_string += "<option value='" + str(option) + "'>" + str(option) + "</option>"

    return select_string


def nested_list_to_html_select_2(nested_list: list):
    '''
    Converts a list of lists into an html select tag for columns.
    The nested_list is the list to be converted and the return value is the corresponding
    select tag in html format as a string.
    
    Returns:
    select_string: The corresponding select tag in html format
    '''
    select_string = "<option disabled selected>Choose column</option>"

    for sub_list in nested_list[1:]:
        for option in sub_list:
            select_string += "<option value='" + str(option) + "'>" + str(option) + "</option>"

    return select_string


def get_insert_form(columns: list):
    '''
    Creates a modern insert form with form controls for each column.
    
    Returns:
    form_string: String containing the insert form with modern styling
    '''
    form_string = ""

    for col_name in columns:
        form_string += """
        <div class="form-group">
            <label class="form-label" for="insert_""" + str(col_name) + """">""" + str(col_name) + """</label>
            <input type="text" id="insert_""" + str(col_name) + """" name='""" + str(col_name) + """' placeholder='""" + str(col_name) + """' class="form-control" required>
        </div>
        """

    return form_string


def get_update_form(columns: list, values: list):
    '''
    Creates a modern update form with form controls for each column, pre-populated with current values.
    
    Returns:
    form_string: String containing the update form with modern styling
    '''
    form_string = ""

    for col, val in zip(columns, values):
        form_string += """
        <div class="form-group">
            <label class="form-label" for="update_""" + str(col) + """">""" + str(col) + """</label>
            <input type="text" id="update_""" + str(col) + """" name='""" + str(col) + """' placeholder='""" + str(col) + """' class="form-control" value='""" + str(val) + """' required>
        </div>
        """

    return form_string
