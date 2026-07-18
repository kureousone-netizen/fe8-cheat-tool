import sys, csv, socket
from pathlib import Path
from pypdf import PdfReader

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent
    
BASE_PATH = get_base_path()
cheat_guide = BASE_PATH / 'assets' / 'FE8 Cheat Guide.pdf'
item_data = BASE_PATH / 'assets' / 'ItemForm_00809B10.csv'

def send_to_gba(final_text):
    with socket.create_connection(('127.0.0.1', 8888)) as s:
        for line in final_text.strip().split('\n'):
            parts = line.split()
            if len(parts) == 2:
                address, value = parts
                s.send(f'{address} {value}\n'.encode())

def validate_input(user_input):
    if user_input < 0:
        raise ValueError
                
def extract_codes(slot_num, class_codes=False):
    pdf_reader = PdfReader(cheat_guide)
    
    if class_codes:
        pages = pdf_reader.pages[28:]
        class_dict = {}
        pdf_text = ''
        
        for page in pages:
            pdf_text += page.extract_text()
        
        starting_point = pdf_text.find('7164 Lord')
        ending_point = pdf_text.find('---------------------')
        
        c_text = pdf_text[starting_point:ending_point]
        for line in c_text.split('\n'):
            if '7' in line[5:]:
                # If the pdf formatting is all messed up, split the class code into two halves
                # and assign the separate addresses and values to the class dictionary returned at the end
                first_half = line[:line.rfind('7')-1]
                second_half = line[line.rfind('7')-1:]
               
                addr1, val1 = first_half.split()
                addr2, val2 = second_half.split()
                
                class_dict[addr1] = val1
                class_dict[addr2] = val2
                
            elif '8' in line[5:]:
                first_half = line[:line.rfind('8')-3]
                second_half = line[line.rfind('8')-3:]
                
                addr1, val1, val2 = first_half.split()
                addr2, val3 = second_half.split()

                class_dict[addr1] = val1 + ' ' + val2
                class_dict[addr2] = val3

            else:
                class_dict[line[:5]] = line[5:]
            
        return class_dict
    
    else:
        pages = pdf_reader.pages[2:22]
        codes = []
        first_codes = []
        pdf_text = ''
        
        # Loop over the pdf pages to build the pdf text from scratch
        for page in pages:
            pdf_text += page.extract_text()
        
        # Designate two indexes for filtering the text
        starting_point = pdf_text.find('-     Slot 1     -')
        ending_point = pdf_text.find('- O t h e r    S l o t s -')
        
        c_text = pdf_text[starting_point:ending_point]
        
        # Now, this is the most critical part. Depending on the slot number, you want to filter the character code
        # text with the c_text.find() indexes.
        # The slot number cannot be zero, and it can't be greater than 25, so in those cases, we raise an exception.
        # But if the slot number is exactly 25, we don't specify starting and ending indexes (just starting)
        # And we DON'T perform any slot_num arithmetic to determine the next slot number
        if slot_num != 0 and slot_num < 25:
            slot_text = c_text[c_text.find(f'-     Slot {slot_num}'):c_text.find(f'-     Slot {slot_num + 1}')]
        elif slot_num == 25:
            slot_text = c_text[c_text.find(f'-     Slot {slot_num}'):]
        else:
            raise Exception('Slot number not found. (Range must be between 1 and 25)')
        
        raw_codes = slot_text.split()
        
        # Looping through the list, you want to get rid of any codes not starting with '32' or '82'
        for raw_code in raw_codes:
            if '32' in raw_code:
                if not raw_code.startswith('32'):
                    codes.append(raw_code[raw_code.find('3'):])
                
                else:
                    codes.append(raw_code)
                    
            if raw_code.startswith('82'):
                first_codes.append(raw_code)
            
        return first_codes, codes


def write_code(slot_num, level=False, item=False, classes=False, support=False):
    portrait_codes, stat_codes = extract_codes(slot_num)
    final_text = ''
    
    if item:
        for i in range(len(stat_codes)):
            if i not in range(13, 23):
                continue
            else:
                final_text += stat_codes[i] + '\n'
    
        return final_text
    
    if classes:
        for i in range(len(portrait_codes)):
            if i == 0:
                continue
            else:
                hex_input = input('With great power comes great responsibility. Enter your desired class in hex: ')
                final_text += f'{portrait_codes[i]} {hex_input.upper()}'
        
        send_to_gba(final_text)
    
    # The next semi-cryptic part! Basically, if you don't want to write weapon level addresses (if not level because 'level' is set to false)
    # you'll append the codes responsible for the unit's stats EXCLUSIVELY.
    # Otherwise, you'll write the memory addresses responsible for weapon levels (if you pass True to level)
    if not item and not classes and not support:
        if not level:
            for i in range(len(stat_codes)):
                if i not in range(3, 13):
                    continue
                else:
                    num = int(input('''Enter stat values (Max HP -> Current HP -> Str -> Skill -> Spd -> Def -> Res -> Luck -> Con -> Mov (0 for null): '''))
                    
                    hex_code = hex(num)
                    hex_code_caps = hex_code[2:].upper()
                    if len(hex_code_caps) == 2:
                        final_text += stat_codes[i] + ' 00' + hex_code_caps + '\n'
                    else:
                        final_text += stat_codes[i] + ' 000' + hex_code_caps + '\n'
                        
            send_to_gba(final_text)
            
        else:
            for i in range(len(stat_codes)):
                if i not in range(23, 31):
                    continue
                else:
                    user_input = input('''Enter weapon level values in hex. Typically 01=E, 1F=D, 47=C, 79=B, B5=A, FB=S
(Sword -> Lance -> Axe -> Bow -> Staff -> Anima -> Light -> Dark (00 for null): ''')
                    
                    hex_code_caps = user_input.upper()
                    final_text += stat_codes[i] + ' 00' + hex_code_caps + '\n'
                    
            send_to_gba(final_text)
            
    if support:
        for i in range(len(stat_codes)):
            if i not in range(31, 41):
                continue
            else:
                support_input = input('''Enter support levels in hex. Typically 00=None, 50=Support C Ready, 51=Support C A0=Support B Ready, A1=Suport B,
F0=Suport A Ready, F1=Support A:''')
                support_caps = support_input.upper()
                final_text += stat_codes[i] + ' 00' + support_caps + '\n'
                
        send_to_gba(final_text)
            
    return ''
    
def write_item(unit_no, item, amount, slot):
    # Optimized for full elegance! We receive the addresses from the write_code function! P.S (slot_no) becomes (unit_no) here
    addresses = write_code(unit_no, False, True, False, False)
    lines = addresses.split()
    
    codes = {}
    counter = 1
    # This is the most critical step. Looping through the list of strings, we assign a slot key with the memory
    # address (in a list) as the value (if the counter variable is less than or equal to 5).
    # Once it's greater than 5, you compute counter-5 to take you back to the first five slots.
    # Then, you get the listvalue with the dict.get() method and append another item to that list with list concatenation
    # All the while, the counter iterates until it reaches the end of the lookup table.
    for line in lines:
        if line.startswith('32'):
            if counter <= 5:
                codes[f'Slot {counter}'] = [line]
            if counter > 5:
                codes[f'Slot {counter-5}'] = codes.get(f'Slot {counter-5}') + [line]
            counter += 1
    
    # Here you unpack the list stored in the specified slot into type and quantity (two entirely separate memory addresses)
    typ, qty = codes.get(f'Slot {slot}')
    hex_num = hex(amount)[2:].upper()
    
    # Finally, you build the string you want to write by inserting the type address, quantity address, item, and quantity specifiers.
    if len(hex_num) == 2:
        text = f'{typ} 00{item}\n{qty} 00{hex_num}\n'
    else:
        text = f'{typ} 00{item}\n{qty} 000{hex_num}\n'
        
    send_to_gba(text)


def display(items, classes=False):
    lookup_table = {}
    
    if items:
        with open(item_data, 'r') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                # Skip the null address 0
                if i == 0:
                    continue
                lookup_table[row['0x809B10'][3:]] = row['0x809B10'][:3]
        
            for k, v, in lookup_table.items():
                print(f'{k}: {v}')
                
    if classes:
        class_lookup_table = extract_codes(1, True)
        
        for k, v in class_lookup_table.items():
            print(f'{k}: {v}')
 
# Main Loop

while True:
    try:
        unit = int(input('\nEnter unit no: '))
        validate_input(unit)

        print('\nWhat would you like to do?')
        print('1. Change Weapon Levels')
        print('2. Change Stats')
        print('3. Get Items')
        print('4. Change Classes')
        print('5. Change Support Levels')
        print('6. Display Items')
        print('7. Display Classes')
        print('8. Exit')

        choice = int(input('Enter your choice:'))

        if choice not in range(1, 9):
            raise Exception('Invalid choice')
        elif choice == 1:
            write_code(unit, True, False, False, False)
        elif choice == 2:
            write_code(unit, False, False, False, False)
        elif choice == 3:
            addr = input('Enter Address in hex (for reference, view address codes with the display items option): ')
            amount = int(input('Enter amount of items: '))
            validate_input(amount)
            slot = int(input("Enter unit's slot number (1 - 5): "))
            if slot not in range(1, 6):
                raise Exception('Invalid slot number')
            
            write_item(unit, addr, amount, slot)
        elif choice == 4:
            write_code(unit, False, False, True, False)
        elif choice == 5:
            write_code(unit, False, False, False, True)
        elif choice == 6:
            display(items=True, classes=False)
        elif choice == 7:
            display(items=False, classes=True)
        else:
            print('\nGoodbye!')
            break

    except ValueError:
        print('Input must be a positive integer. Exiting...')
        sys.exit()
    except KeyboardInterrupt:
        print('\nGoodbye!')
        sys.exit()