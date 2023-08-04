from datetime import date, datetime

logging = True
log_progress = True
to_file = True


file = None
log_filepath = f"logs/log_{date.today().isoformat()}.log"

def log(string: str):
    if logging:
        if to_file:
            log_to_file(string)
        else:
            log_to_console(string)

def log_string(string: str):
    return f"{datetime.now().time()} || {string}\n"

def log_to_file(string: str):
    global file
    if not(file):
        try:
            file = open(log_filepath, 'a+')
        except FileNotFoundError:
            file = open(log_filepath, 'w')
        file.write(log_string("Loaded this log file"))
    file.write(log_string(string))

def log_to_console(string: str):
    print(log_string(string), end="")