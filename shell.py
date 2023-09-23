from src import interpreter

while True:
    text = input('cap > ')
    if text.strip() == "":
        continue
    result, error = interpreter.run_program('<stdin>', text)

    if error:
        print(error.to_string())
    elif result:
        print(result if len(result.elements) != 1 else result.elements[0])
