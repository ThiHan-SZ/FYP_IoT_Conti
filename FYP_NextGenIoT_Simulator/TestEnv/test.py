import random

def generate_texty_utf8_characters_with_extras(n):
    chars = []
    
    for _ in range(n):
        rand = random.random()
        
        if rand < 0.6:  # 60% chance for lowercase letters
            code_point = random.randint(0x61, 0x7A)  # a-z
        elif rand < 0.75:  # 15% chance for uppercase letters
            code_point = random.randint(0x41, 0x5A)  # A-Z
        elif rand < 0.85:  # 10% chance for digits
            code_point = random.randint(0x30, 0x39)  # 0-9
        elif rand < 0.92:  # 7% chance for spaces and punctuation
            code_point = random.choice([0x20, 0x2C, 0x2E])  # Space, comma, period
        elif rand < 0.95:  # 3% chance for newlines
            chars.append('\n')  # Directly add newline
            continue
        elif rand < 0.98:  # 3% chance for special dashes
            code_point = random.choice([0x2013, 0x2014])  # En dash, em dash
        else:  # 2% chance for extended characters
            code_point = random.randint(0x80, 0x7FF)  # 2-byte range
        
        chars.append(chr(code_point))
    
    return ''.join(chars)

# Example: Generate a "texty" random string with newlines and dashes
with open('UniformMax2ByteUTF8.txt', 'w', encoding='utf-8') as f:
    f.write(generate_texty_utf8_characters_with_extras(40000))