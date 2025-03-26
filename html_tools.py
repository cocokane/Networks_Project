def nested_list_to_html_table(table: list, buttons: bool = False):
    '''
    code is a function that takes in a list of lists and returns an html table.
    The first argument is the name of the function, which is "table".
    The second argument is the list to be converted into an html table.
    The third argument is a boolean variable denoting whether there are buttons on the page.
    If it's true, then there will be buttons on this page; if false, then there won't be any buttons on this page.
    The fourth argument is what we're going to return as our output: html_string: The corresponding table in html format as a string
    code will return the html string as a table.
    '''

    columns = table[0]
    html_string = '<thead><tr><th></th>'

    for col in columns:
        html_string += "<th>" + str(col) + "</th>"

    html_string += "</tr></thead><tbody>"

    for i, row in enumerate(table[1:]):
        html_string += "<tr>"
        if buttons:
            html_string += """<th><form method="post">
            <div class="tooltip" data-tip="Delete"><button name='delete_button' value='""" + ','.join(
                [str(x) for x in row]) + """' class='btn btn-sm btn-outline-dark btn-square p-1'>
            <svg xmlns='http://www.w3.org/2000/svg' class='h-6 w-6' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'>
            <path stroke-linecap='round' stroke-linejoin='round' d='M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16' />
            </svg></button></div>
            <div class="tooltip" data-tip="Update"><button name='update_button' value='""" + ','.join(
                [str(x) for x in row]) + """' class='btn btn-sm btn-secondary btn-square p-1'>
            <svg xmlns='http://www.w3.org/2000/svg' class='h-6 w-6' fill='none' viewBox='0 0 24 24' stroke='currentColor' stroke-width='2'>
            <path stroke-linecap='round' stroke-linejoin='round' d='M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z' />
            </svg></button></div></form></th>
            """
        else:
            html_string += "<th>" + str(i + 1) + "</th>"

        for cell in row:
            html_string += "<td>" + str(cell) + "</td>"

        html_string += "</tr>"

    html_string += "</tbody>"

    return html_string


def nested_list_to_html_select(nested_list: list):
    '''
    code is converting a list of lists into an html select tag.
    The nested_list is the list to be converted and the return value is the corresponding
    select tag in html format as a string.
    code will return the string "select_string" which
    is the corresponding select tag in html format.
    '''
    select_string = "<option disabled selected>Choose table</option>"

    for sub_list in nested_list[1:]:
        for option in sub_list:
            select_string += "<option>" + str(option) + "</option>"

    return select_string


def nested_list_to_html_select_2(nested_list: list):
    '''
    code is converting a list of lists into an html select tag.
    The nested_list is the list to be converted and the return value is the corresponding
    select tag in html format as a string.
    code will return the string "select_string" which
    is the corresponding select tag in html format.
    '''
    select_string = "<option disabled selected>Choose column</option>"

    for sub_list in nested_list[1:]:
        for option in sub_list:
            select_string += "<option>" + str(option) + "</option>"

    return select_string


def get_insert_form(columns: list):
    '''
    code is creating a string out of the column names.
    code is then inserting each row into the string.
    form_string: String containing the insert form
    code creates a string containing the insert form.
    '''
    form_string = ""

    for col_name in columns:
        form_string += "<input type='text' name='" + str(col_name) + "' placeholder='" + str(
            col_name) + "' class='input input-bordered' required>"

    return form_string


def get_update_form(columns: list, values: list):
    '''
    code starts by creating a list of column names.
    next line creates the string "form_string" which is then used to create an update form.
    code creates a string containing the update form.

    '''
    form_string = ""

    for col, val in zip(columns, values):
        form_string += "<div class='form-control'><label class='label'><span class='label-text'>" + str(
            col) + "</span></label><input type='text' name='" + str(col) + "' placeholder='" + str(
            col) + "' class='input input-bordered' value='" + str(val) + "' required></div>"

    return form_string
