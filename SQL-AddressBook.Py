import datetime
import tkinter as tk
import mysql.connector

cnx = mysql.connector.connect(user='Justin', password='s0t0hP',
                              host='LOCALHOST',
                              database='addressbook',
                              buffered=True)

cursor = cnx.cursor()

SELECT_BY_LAST_NAME = ''' 
    SELECT 
        LEFT(person_name, (LOCATE(' ', person_name)-1)) AS person_first_name,
        RIGHT(person_name, (LENGTH(person_name)-LOCATE(' ', person_name))) AS person_last_name, 
        active_phone_number, 
        floor(DATEDIFF(CURDATE(), person_DOB) / 365) AS age,
        street_address, 
        city, 
        state, 
        zip_code
    FROM 
        ((people_addresses
        INNER JOIN people_master ON people_addresses.person_id = people_master.person_id)
        INNER JOIN addresses ON people_addresses.address_id = addresses.address_id)
    WHERE 
        RIGHT(person_name, (LENGTH(person_name)-LOCATE(' ', person_name))) = %(inputLastName)s 
        AND ISNULL(end_date)
    ORDER BY
        person_last_name,
        person_first_name
    '''

SELECT_BY_NAME_SEARCH = '''
    SELECT 
        LEFT(person_name, (LOCATE(' ', person_name)-1)) AS person_first_name,
        RIGHT(person_name, (LENGTH(person_name)-LOCATE(' ', person_name))) AS person_last_name, 
        active_phone_number, 
        floor(DATEDIFF(CURDATE(), person_DOB) / 365) AS age,
        street_address, 
        city, 
        state, 
        zip_code
    FROM 
        ((people_addresses
        INNER JOIN people_master ON people_addresses.person_id = people_master.person_id)
        INNER JOIN addresses ON people_addresses.address_id = addresses.address_id)
    WHERE
        person_name LIKE CONCAT(%(inputNameSearch)s, '%')
        AND ISNULL(end_date)
    ORDER BY
        person_last_name,
        person_first_name
    '''

SELECT_BY_AGE_RANGE = ''' 
    SELECT 
        LEFT(person_name, (LOCATE(' ', person_name)-1)) AS person_first_name,
        RIGHT(person_name, (LENGTH(person_name)-LOCATE(' ', person_name))) AS person_last_name, 
        active_phone_number,
        floor(DATEDIFF(CURDATE(), person_DOB) / 365) AS age,
        street_address, 
        city, 
        state, 
        zip_code
    FROM 
        ((people_addresses 
        INNER JOIN people_master ON people_addresses.person_id = people_master.person_id)
        INNER JOIN addresses ON people_addresses.address_id = addresses.address_id)
    WHERE
        floor(DATEDIFF(CURDATE(), person_DOB) / 365) 
        BETWEEN %(inputAgeMin)s AND %(inputAgeMax)s 
        AND ISNULL(end_date)
    ORDER BY
        person_last_name,
        person_first_name
    '''

def displaySelectResults(query, dictionary):
    cursor.execute(query, dictionary)
    for (
    person_first_name, person_last_name, active_phone_number, age, street_address, city, state, zip_code) in cursor:
        print("{}, {}; Age: {}  Current Phone: {}  Current Address: {} {}, {} {}".format(
            person_last_name, person_first_name, age, active_phone_number, street_address, city, state, zip_code))
    if cursor.rowcount == 0:
        print('Zero Results Found')
    return


def FindPersonID(inputPersonName):
    localCursor = cnx.cursor()
    query = '''SELECT 
                    person_id
               FROM
                    people_master
               WHERE
                    person_name = %(inputPersonName)s
               '''

    localCursor.execute(query, {'inputPersonName': inputPersonName})

    row = localCursor.fetchone()
    if (localCursor.rowcount <= 0):
        localCursor.close()
        return
    else:
        personID = row[0]
        localCursor.close()
        return personID


def InsertNewPerson(personName, personDOB, activePhoneNumber):
    query = '''
        INSERT INTO 
            people_master (
                person_name, 
                person_DOB, 
                active_phone_number
            )
        VALUES (
            %(personName)s,
            %(personDOB)s,
            %(activePhoneNumber)s
            )
        '''
    cursor.execute(query,
            {
                'personName':personName,
                'personDOB':personDOB,
                'activePhoneNumber':activePhoneNumber
            })
    # cnx.commit()
    return


def InsertNewAddress(streetAddress, city, state, zipCode):
    query = '''
        INSERT INTO 
            addresses (
                street_address, 
                city, 
                state, 
                zip_code
            ) 
        VALUES ( 
            %(streetAddress)s,
            %(city)s,
            %(state)s,
            %(zipCode)s
        )
        '''
    cursor.execute(query,
                   {
                       'streetAddress':streetAddress,
                       'city':city,
                       'state':state,
                       'zipCode':zipCode
                   })
    # cnx.commit()
    return


def InsertNewPeopleAddress(personID, addressID, currentDate):
    query = '''
        INSERT INTO 
            people_addresses (
                person_id, 
                address_id, 
                start_date
            )
        VALUES (
            %(personID)s,
            %(addressID)s,
            %(currentDate)s
        )
        '''
    cursor.execute(query,
                   {
                       'personID': personID,
                       'addressID': addressID,
                       'currentDate': currentDate
                   })
    # cnx.commit()
    return cursor.lastrowid


def FindPersonCurrentAddressID(personID):
    localCursor = cnx.cursor()
    query = '''
        SELECT 
            address_id 
        FROM 
            people_addresses 
        WHERE 
            person_id = %(personID)s
            AND IsNull(end_date)
        '''
    localCursor.execute(query, {'personID': personID})
    row = localCursor.fetchone()
    if localCursor.rowcount != 0:
        addressID = row[0]
        localCursor.close()
        return addressID
    else:
        localCursor.close()
        return


def FindAddressID(inputStreetAddress, inputCity, inputState, inputZipCode):
    localCursor = cnx.cursor()
    query = '''
        SELECT 
            address_id 
        FROM 
            addresses 
        WHERE 
            street_address = %(inputStreetAddress)s 
            AND city = %(inputCity)s
            AND state = %(inputState)s
            AND zip_code = %(inputZipCode)s
        '''

    localCursor.execute(query,
                   {'inputStreetAddress': inputStreetAddress,
                    'inputCity': inputCity,
                    'inputState': inputState,
                    'inputZipCode': inputZipCode
                    })
    row = localCursor.fetchone()
    if localCursor.rowcount != 0:
        addressID = row[0]
        localCursor.close()
        return addressID
    else:
        localCursor.close()
        return


def ArchiveOldAddress(personID, date):
    query = '''
        UPDATE
            people_addresses
        SET
            end_date = %(date)s
        WHERE
            person_id = %(personID)s
            AND ISNull(end_date)
    '''
    cursor.execute(query,
                    {'date': date,
                    'personID': personID
                    })


def UpdateAddress(personID, oldAddressID):
    streetAddress = ValidateEntry('Enter Person\'s Current Street Address:', 'VARCHAR', 30)
    city = ValidateEntry('Enter Person\'s Current City:', 'VARCHAR', 20)
    state = ValidateEntry('Enter Person\'s Current State of Residence:', 'CHAR', 2)
    zipCode = ValidateEntry('Enter Person\'s Current Zip Code:', 'CHAR', 5)
    currentAddressID = FindAddressID(streetAddress, city, state, zipCode)
    if currentAddressID == oldAddressID:
        print('New address and old address are the same. No update performed.')
    else:
        if currentAddressID is None:
            InsertNewAddress(streetAddress, city, state, zipCode)
            currentAddressID = cursor.lastrowid
        ArchiveOldAddress(personID, datetime.date.today())
        InsertNewPeopleAddress(personID, currentAddressID, datetime.date.today())


def UpdatePhone(personID):
    activePhoneNumber = ValidateEntry('Enter Person\'s Current Phone Number:', 'VARCHAR', 12)
    query = '''
        UPDATE 
            people_master 
        SET 
            active_phone_number = %(activePhoneNumber)s 
        WHERE 
            person_id = %(personID)s
        '''
    cursor.execute(query,
                   {'activePhoneNumber': activePhoneNumber,
                   'personID': personID})


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


def SearchByLastName():
    inputLastName = str(input('Enter a Last Name to Search For.\n>>>'))
    displaySelectResults(SELECT_BY_LAST_NAME, {'inputLastName': inputLastName})


def SearchForName():
    inputNameSearch = str(input('Enter a Name to Search For:\n>>>'))
    displaySelectResults(SELECT_BY_NAME_SEARCH, {'inputNameSearch': inputNameSearch})


def AddUpdateContact():
    try:
        firstName = ValidateEntry('Enter Person\'s First Name:', 'VARCHAR', 15)
        lastName = ValidateEntry('Enter Person\'s Last Name:', 'VARCHAR', 15)
        personName = firstName + ' ' + lastName
        personID = FindPersonID(personName)

        if str(personID) == 'None':
            print('Person Not Found: Must Create New Contact')
            personDOB = ValidateEntry('Enter Person\'s Date of Birth (mm/dd/yyyy):', 'DATETIME', 0)
            activePhoneNumber = ValidateEntry('Enter Person\'s Current Phone Number:','VARCHAR', 12)
            streetAddress = ValidateEntry('Enter Person\'s Current Street Address:','VARCHAR', 30)
            city = ValidateEntry('Enter Person\'s Current City:','VARCHAR',20)
            state = ValidateEntry('Enter Person\'s Current State of Residence:','CHAR',2)
            zipCode = ValidateEntry('Enter Person\'s Current Zip Code:','CHAR',5)
            InsertNewPerson(personName, personDOB, activePhoneNumber)
            personID = cursor.lastrowid
            addressID = FindAddressID(streetAddress, city, state, zipCode)
            if addressID is None:
                InsertNewAddress(streetAddress, city, state, zipCode)
                addressID = cursor.lastrowid
            InsertNewPeopleAddress(personID, addressID, datetime.date.today())
        else:
            displaySelectResults(SELECT_BY_NAME_SEARCH, {'inputNameSearch': personName})
            choice = input(personName + ' Exists: Would you like to update their information? Y/N\n>>>').upper()
            if choice == 'Y':
                addressID = FindPersonCurrentAddressID(personID)
                choice = input('Do you need to update their address(A), phone number(P), or both(B)?\n>>>').upper()
                if choice == 'A':
                    UpdateAddress(personID, addressID)
                elif choice == 'P':
                    UpdatePhone(personID)
                elif choice == 'B':
                    UpdateAddress(personID, addressID)
                    UpdatePhone(personID)
                else:
                    print('Valid Option Not Selected')
        cnx.commit()
        print("Changes Successful:")
        displaySelectResults(SELECT_BY_NAME_SEARCH, {'inputNameSearch': personName})
    except Exception as e:
        cnx.rollback()
        print('Error: ' + str(e))


def searchByAge():
    inputAgeMin = ValidateEntry('Enter a Minimum Age in Years to Search By:', 'INT', 120)
    inputAgeMax = ValidateEntry('Enter a Maximum Age to Years to Search By:', 'INT', 120)
    if int(inputAgeMin) > int(inputAgeMax):
        maxAge = inputAgeMin
        inputAgeMin = inputAgeMax
        inputAgeMax = maxAge
    displaySelectResults(SELECT_BY_AGE_RANGE,
                         {
                             'inputAgeMin': str(inputAgeMin),
                             'inputAgeMax': str(inputAgeMax)
                         })


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
        searchByAge()
    else:
        print("Invalid Command Entered! Please Type a Command From the List Below:")
    cont = input('Do you wish to continue? [Y]es or [N]o\n>>>').upper()
    if cont == 'N':
        option = 'Q'

cursor.close()
cnx.close()


