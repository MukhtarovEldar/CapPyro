def highlight_range(text, pos_beg, pos_end):
    result = ''

    # Calculate the range of lines to process
    index_beg = max(text.rfind('\n', 0, pos_beg.index), 0)
    index_end = text.find('\n', index_beg + 1)
    if index_end < 0:
        index_end = len(text)

    # Generate each line's arrow
    line_cnt = pos_end.line - pos_beg.line + 1
    for _ in range(line_cnt):
        # Extract line and its range of columns
        line = text[index_beg:index_end]
        col_beg = pos_beg.col if _ == 0 else 0
        col_end = pos_end.col if _ == line_cnt - 1 else len(line) - 1

        # Build the arrow line by line
        result += line + '\n'
        result += ' ' * col_beg + '^' * (col_end - col_beg)

        # Update line indices
        index_beg = index_end
        index_end = text.find('\n', index_beg + 1)
        if index_end < 0:
            index_end = len(text)

    # Remove tabs and return the result
    return result.replace('\t', '')
