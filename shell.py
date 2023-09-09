import basic

while True:
    text = input('basic > ')
    result, error = basic.run_program('<stdin>', text)

    if error:
        print(error.to_string())
    elif result:
        print(result)
