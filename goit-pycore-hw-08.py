from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, name):
        super().__init__(name)


class Phone(Field):
    def __init__(self, phone):
        super().__init__(phone)
        if len(self.value) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        if not phone.isdigit():
            raise ValueError("Phone number must be exactly only digits")


class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)
    def is_valid(self):
        try:
            b_date = datetime.strptime(self.value, '%d.%m.%Y')
            today = datetime.now()
            return b_date < today
        except ValueError:
            return False
    def __str__(self):
        return self.value

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)

    def edit_phone(self, old_phone, new_phone):
        if old_phone in [p.value for p in self.phones]:
            for p in self.phones:
                if p.value == old_phone:
                    p.value = new_phone
        else:
            raise ValueError(f'This number: {old_phone} does not exist')

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p

    def add_birthday(self, birthday):
        b_day = Birthday(birthday)
        if b_day.is_valid():
            self.birthday = b_day
        else:
            raise ValueError("Birthday cannot be in the future!")

    def __str__(self):
        phone_str = '; '.join(p.value for p in self.phones)
        birthday_str = self.birthday.value if self.birthday else 'No birthday'
        return f"Contact name: {self.name.value}, phones: {phone_str}, Birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return f'Contact {name} deleted'
        else:
            return f'Contact {name} not found'

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, '%d.%m.%Y').date()
                bday_this_year = bday.replace(year=today.year)
                if 0 <= (bday_this_year - today).days < 8:
                    while bday_this_year.weekday() > 4:  # Якщо день народження випадає на вихідний
                        bday_this_year += timedelta(days=1)
                    upcoming_birthdays.append(
                        f"Name: {record.name.value}, upcoming birthday: {bday_this_year.strftime('%d.%m.%Y')}"
                    )
        return upcoming_birthdays

    def __str__(self):
        result = []
        for record in self.data.values():
            result.append(str(record))
        return '\n'.join(result)

def delete(args, book):
    name = args[0]
    return book.delete(name)

#----------------------------------------------------------------

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

#-----------------------------------------------------------------

def input_error(func):
    def wrapper(*args, book, **kwargs):
        try:
            return func(*args, book, **kwargs)
        except KeyError:
            return "Name not found. Please, check and try again."
        except ValueError as e:
            return e
        except IndexError:
            return "Enter correct information."

    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Not enough arguments. Please provide both name and phone."
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        return "Not enough arguments. Please provide name, old phone, and new phone."
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f'Phone number {old_phone} changed to {new_phone} for {name}.'
    else:
        return f'Contact {name} not found.'


@input_error
def show_phone(args, book: AddressBook):
    if not args:
        return "Name is missing. Please provide a name."
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join([p.value for p in record.phones])
    else:
        return f'Contact {name} not found.'


@input_error
def show_all(book: AddressBook):
    return "\n".join([str(record) for record in book.data.values()])


def parse_input(user_input):
    parts = user_input.split()
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        return "Not enough arguments. Please provide name and birthday."
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f'Birthday added for {name}.'
    else:
        return f'Contact {name} not found.'


@input_error
def show_birthday(args, book: AddressBook):
    if not args:
        return "Name is missing. Please provide a name."
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return f"Birthday for {name} is {record.birthday.value}"
    else:
        return f"Birthday for {name} not found."



def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book=book))
        elif command == "change":
            print(change_contact(args, book=book))
        elif command == "phone":
            print(show_phone(args, book=book))
        elif command == "all":
            print(show_all(book=book))
        elif command == "add-birthday":
            print(add_birthday(args, book=book))
        elif command == "show-birthday":
            print(show_birthday(args, book=book))
        elif command == "birthdays":
            birthdays = book.get_upcoming_birthdays()
            if not len(birthdays):
                print("There are no upcoming birthdays.")
                continue
            for day in birthdays:
                print(f"{day}")
        elif command == "delete":
            print(delete(args, book=book))
        else:
            print("Invalid command")

if __name__ ==  "__main__":
    main()