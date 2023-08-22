def highlight_range(text, pos_start, pos_end):
    result = ''

    # Calculate the range of lines to process
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each line's arrow
    line_count = pos_end.ln - pos_start.ln + 1
    for _ in range(line_count):
        # Extract line and its range of columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if _ == 0 else 0
        col_end = pos_end.col if _ == line_count - 1 else len(line) - 1

        # Build the arrow line by line
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Update line indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    # Remove tabs and return the result
    return result.replace('\t', '')
