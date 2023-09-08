import basic

while True:
    text = input('basic > ')
    result, error = basic.run_program('<stdin>', text)

    print(error.to_string()) if error else print(result)
