# Generate and decode all possible 12-bit Unicode characters in UTF-8
unicode_chars = []

for code_point in range(0x0000, 0x1000):  # Covers 12-bit range (U+0000 to U+0FFF)
    try:
        # Convert code point to character
        char = chr(code_point)
        
        # Encode in UTF-8 and decode back to check validity
        utf8_encoded = char.encode('utf-8')
        decoded_char = utf8_encoded.decode('utf-8')
        
        # Append decoded character if it matches original
        unicode_chars.append(decoded_char)
    except UnicodeEncodeError:
        # Skip characters that can't be encoded/decoded
        continue

# Output results (You can print or save them as needed)
print("Generated Unicode characters (12-bit range):")
print("".join(unicode_chars))  # Join all characters as a single string
