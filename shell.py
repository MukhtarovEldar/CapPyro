from src import interpreter

while True:
    text = input('cap > ')
    result, error = interpreter.run_program('<stdin>', text)

    if error:
        print(error.to_string())
    elif result:
        print(result)
