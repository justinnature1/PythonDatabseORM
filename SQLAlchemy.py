import datetime

from sqlalchemy import create_engine, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, and_, text, func
from sqlalchemy.orm import sessionmaker, relationship, query_expression


engine = create_engine('mysql+mysqlconnector://root:s0t0hP@localhost:3306/address_book_orm')#,echo = True
Base = declarative_base()


#https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html
class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, Sequence('user_id_sequence'), primary_key=True)
    name = Column(String(50))
    birth_date = Column(Date)
    phone_number = Column(String(12))
    age = query_expression()
    addresses = relationship('PeopleAddress', back_populates='person')

    # https://docs.sqlalchemy.org/en/13/orm/mapped_sql_expr.html
    # @hybrid_property
    # def age(self):


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, Sequence('user_id_sequence'), primary_key=True)
    street_address = Column(String(50))
    city = Column(String(20))
    state = Column(String(2))
    zipcode = Column(String(5))

    people = relationship('PeopleAddress', back_populates='address')


class PeopleAddress(Base):
    __tablename__ = 'people_address'

    id = Column(Integer, Sequence('user_id_sequence'), primary_key=True, autoincrement=True)
    person_id = Column(Integer, ForeignKey('person.id'))
    address_id = Column(Integer, ForeignKey('address.id'))
    start_date = Column(Date)
    end_date = Column(Date)
    person = relationship('Person', back_populates='addresses')
    address = relationship('Address', back_populates='people')



Base.metadata.create_all(engine)

session = sessionmaker(bind=engine)()


def ValidateEntry(message, dataType, size):
    dataValid = False
    while not dataValid:
        inputValue = input(message + '\n>>>')
        if dataType == 'INT':
            try:
                if not inputValue.isdigit() or int(inputValue) > int(size) or len(inputValue) == 0:
                    raise ValueError
                else:
                    dataValid = True
            except ValueError:
                print('Please enter a number less than ' + str(size))
        elif dataType == 'VARCHAR':
            try:
                if len(inputValue) > size or len(inputValue) == 0:
                    raise ValueError
                else:
                    dataValid = True
            except ValueError:
                print('Please enter text less than ' + str(size) + ' characters')
        elif dataType == 'CHAR':
            try:
                if len(inputValue) != size or len(inputValue) == 0:
                    raise ValueError
                else:
                    dataValid = True
            except ValueError:
                print('Please enter text that is ' + str(size) + ' characters long')
        elif dataType == 'DATETIME':
            if inputValue.count('/') == 2:
                month, day, year = inputValue.split('/')
            else:
                raise ValueError
            try:
                inputValue = datetime.date(int(year), int(month), int(day))
                dataValid = True
            except ValueError:
                print('Please enter a valid date following the format mm/dd/yyyy.')
                dataValid = False
    return inputValue


def displayContactQueryResults(queryResults):
    if queryResults == 0:
        print('Zero Results Found')
    else:
        #https://stackoverflow.com/questions/11530196/flask-sqlalchemy-query-specify-column-names
        for contact in queryResults:
            print('{}, {}; Current Phone: {} Current Address: {} {}, {} {}'
                .format(
                    contact[1],
                    contact[0],
                    contact[2],
                    contact[3],
                    contact[4],
                    contact[5],
                    contact[6]
                )
            )
    return


def SelectByAge(ageMin, ageMax):
    return session.query(
            Person
        ).join(
            PeopleAddress
        ).join(
            Address
        ).with_entities(
            func.LEFT(Person.name, func.LOCATE(' ', Person.name)-1).label('first_name'),
            func.RIGHT(Person.name, func.LENGTH(Person.name)-func.LOCATE(' ', Person.name)).label('last_name'),
            Person.phone_number,
            Address.street_address,
            Address.city,
            Address.state,
            Address.zipcode
        ).filter(
            # Original Code: text("floor(DATEDIFF(CURDATE(), person.birth_date) / 365) BETWEEN " + str(ageMin) + " AND " + str(ageMax))
            func.timestampdiff(text('YEAR'),
            Person.birth_date,
            func.current_date()).between(ageMin, ageMax)
        ).filter(
            PeopleAddress.end_date.is_(None)
        ).order_by(
            'last_name',
            'first_name'
        ).all()


def SelectByLastName(name):
    return session.query(
            Person
        ).join(
            PeopleAddress
        ).join(
            Address
        ).with_entities(
            func.LEFT(Person.name, func.LOCATE(' ', Person.name)-1).label('first_name'),
            func.RIGHT(Person.name, func.LENGTH(Person.name)-func.LOCATE(' ', Person.name)).label('last_name'),
            Person.phone_number,
            Address.street_address,
            Address.city,
            Address.state,
            Address.zipcode
        ).filter(
            Person.name.endswith(name)
        ).filter(
            PeopleAddress.end_date.is_(None)
        ).order_by(
            'last_name',
            'first_name'
        ).all()


def SearchByLastName():
    inputLastName = str(input('Enter a Last Name to Search For.\n>>>'))
    displayContactQueryResults(SelectByLastName(inputLastName))


def SelectByName(name):
    return session.query(
            Person
        ).join(
            PeopleAddress
        ).join(
            Address
        ).with_entities(
            func.LEFT(Person.name, func.LOCATE(' ', Person.name)-1).label('first_name'),
            func.RIGHT(Person.name, func.LENGTH(Person.name)-func.LOCATE(' ', Person.name)).label('last_name'),
            Person.phone_number,
            Address.street_address,
            Address.city,
            Address.state,
            Address.zipcode
        ).filter(
            Person.name.like(name + '%')
        ).filter(
            PeopleAddress.end_date.is_(None)
        ).order_by(
            'last_name',
            'first_name'
        ).all()


def SearchForName():
    inputName = str(input('Enter a Name to Search For:\n>>>'))
    displayContactQueryResults(SelectByName(inputName))


def SearchByAge():
    inputAgeMin = ValidateEntry('Enter a Minimum Age in Years to Search By:', 'INT', 120)
    inputAgeMax = ValidateEntry('Enter a Maximum Age to Years to Search By:', 'INT', 120)
    if int(inputAgeMin) > int(inputAgeMax):
        maxAge = inputAgeMin
        inputAgeMin = inputAgeMax
        inputAgeMax = maxAge
    displayContactQueryResults(SelectByAge(inputAgeMin, inputAgeMax))


def InsertNewPeopleAddress(personID, newAddress, date):
    pa = PeopleAddress(person_id=personID, start_date=datetime.date.today())
    if newAddress.id is None:
        pa.address = newAddress
    else:
        pa.address_id = newAddress.id
    session.add(pa)


def ArchiveOldAddress(personID, date):
    session.query(
        PeopleAddress
    ).filter(
        and_(PeopleAddress.person_id == personID,
        PeopleAddress.end_date.is_(None))
    ).update(
        {PeopleAddress.end_date: date}
    )
    return


def UpdateAddress(personID, oldAddressID):
    newAddress = Address(
        street_address = ValidateEntry('Enter Person\'s Current Street Address:', 'VARCHAR', 50),
        city = ValidateEntry('Enter Person\'s Current City:', 'VARCHAR', 20),
        state = ValidateEntry('Enter Person\'s Current State of Residence:', 'CHAR', 2),
        zipcode = ValidateEntry('Enter Person\'s Current Zip Code:', 'CHAR', 5))
    newAddress = ExistingAddress(newAddress)
    if newAddress.id == oldAddressID:
        print('New address and old address are the same. No update performed.')
    else:
        # if existingAddress is None:
            # InsertNewAddress(streetAddress, city, state, zipCode)
            # currentAddressID = cursor.lastrowid
        ArchiveOldAddress(personID, datetime.date.today())
        InsertNewPeopleAddress(personID, newAddress, datetime.date.today())


def UpdatePhone(personID):
    activePhoneNumber = ValidateEntry('Enter Person\'s Current Phone Number:', 'VARCHAR', 12)
    session.query(
        Person
    ).filter(
        Person.id == personID
    ).update(
        {Person.phone_number: activePhoneNumber}
    )
    return


def FindCurrentAddress(personID):
    currentAddress = session.query(
            PeopleAddress
        ).filter(
            PeopleAddress.person_id == personID
        ).filter(
            PeopleAddress.end_date.is_(None)
        ).first()
    return currentAddress.address_id


def ExistingAddress(address):
    existingAddress = session.query(
        Address
    ).filter(
        and_(Address.street_address == address.street_address,
             Address.city == address.city,
             Address.state == address.state,
             Address.zipcode == address.zipcode)
    ).first()
    if existingAddress is None:
        return address
    else:
        return existingAddress


def insertNewContact (person, address):
    #Run the following code to create one record in each table
    pa = PeopleAddress(start_date=datetime.date.today())
    contact = person
    if address.id is None:
        pa.address = address
    else:
        pa.address_id = address.id
    contact.addresses.append(pa)
    session.add(contact)
    session.commit()


def AddContact(name):
    print('Person Not Found: Must Create New Contact')
    person = Person(name=name,
                    birth_date=ValidateEntry('Enter Person\'s Date of Birth (mm/dd/yyyy):', 'DATETIME', 0),
                    phone_number=ValidateEntry('Enter Person\'s Current Phone Number:', 'VARCHAR', 12))
    address = Address(street_address=ValidateEntry('Enter Person\'s Current Street Address:', 'VARCHAR', 50),
                      city=ValidateEntry('Enter Person\'s Current City:', 'VARCHAR', 20),
                      state=ValidateEntry('Enter Person\'s Current State of Residence:', 'CHAR', 2),
                      zipcode=ValidateEntry('Enter Person\'s Current Zip Code:', 'CHAR', 5))
    existingAddress = ExistingAddress(address)
    if existingAddress is not None:
        address = existingAddress
    insertNewContact(person, address)
    return


def UpdateContact(person):
    currentAddressID = FindCurrentAddress(person.id)
    choice = input('Do you need to update their address(A), phone number(P), or both(B)?\n>>>').upper()
    if choice == 'A':
        UpdateAddress(person.id, currentAddressID)
    elif choice == 'P':
        UpdatePhone(person.id)
    elif choice == 'B':
        UpdateAddress(person.id, currentAddressID)
        UpdatePhone(person.id)
    else:
        print('Valid Option Not Selected')
    session.commit()


def AddUpdateContact():
    try:
        firstName = ValidateEntry('Enter Person\'s First Name:', 'VARCHAR', 25)
        lastName = ValidateEntry('Enter Person\'s Last Name:', 'VARCHAR', 25)
        personName = firstName + ' ' + lastName
        person = session.query(Person).filter(Person.name == personName).first()
        if person is None:
            AddContact(personName)
        else:
            displayContactQueryResults(SelectByName(personName))
            choice = input(personName + ' Exists: Would you like to update their information? Y/N\n>>>').upper()
            if choice == 'Y':
                UpdateContact(person)
        print("Changes Successful:")
        displayContactQueryResults(SelectByName(personName))
    except Exception as e:
        session.rollback()
        print('Error: ' + str(e))


print('Welcome to your Address Book! Please Type a Command From the List Below:')
option = None
while option != 'Q' and option != 'q':
    print('''[1] Search for Contacts By Last Name
[2] Search for Contacts By Search Prefix
[3] Create/Update Contact
[4] Search for Contacts By Age Range
[Q] Quit''')
    option = input('>>>')
    if option == '1':
        SearchByLastName()
    elif option == '2':
        SearchForName()
    elif option == '3':
        AddUpdateContact()
    elif option == '4':
        SearchByAge()
    else:
        print("Invalid Command Entered! Please Type a Command From the List Below:")
    cont = input('Do you wish to continue? [Y]es or [N]o\n>>>').upper()
    if cont == 'N':
        option = 'Q'

# Alternate way to access data when query returns an object.  When selecting specific rows, it returns a tuple though.
    # person_first_name, person_last_name, active_phone_number, age, street_address, city, state, zip_code) in cursor:
    #     print("{}, {}; Age: {}  Current Phone: {}  Current Address: {} {}, {} {}".format(
    #         person_last_name, person_first_name, age, active_phone_number, street_address, city, state, zip_code))
    # if queryResults == 0:
    #     print('Zero Results Found')
    # else:
    #     # https://stackoverflow.com/questions/6044309/sqlalchemy-how-to-join-several-tables-by-one-query/6045131
    #     for contact in queryResults:
    #         # https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_working_with_joins.htm
    #         for address in contact.addresses:
    #             print('{}; Current Phone: {} Current Address: {} {}, {} {}'
    #                 .format(
    #                     contact.name,
    #                     address.end_date,
    #                     pa.address.street_address,
    #                     pa.address.city,
    #                     pa.address.state,
    #                     pa.address.zipcode
    #                 )
    #             )


