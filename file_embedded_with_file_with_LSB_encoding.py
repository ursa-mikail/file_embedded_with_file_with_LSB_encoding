from PIL import Image
import os

def read_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def write_file(file_path, data):
    with open(file_path, 'wb') as f:
        f.write(data)

def bits_to_byte(bits):
    byte = 0
    for bit in bits:
        byte = (byte << 1) | bit
    return byte

def byte_to_bits(byte, num_bits):
    return [((byte >> bit) & 1) for bit in range(num_bits - 1, -1, -1)]

def embed_bits(file_target, file_to_be_embedded, n_bits, output_file):
    # Open the target image
    img = Image.open(file_target)
    img = img.convert("RGB")
    pixels = img.load()

    # Read the file to be embedded
    embed_data = read_file(file_to_be_embedded)

    # Convert embed data to bit stream
    bit_stream = []
    for byte in embed_data:
        bit_stream.extend(byte_to_bits(byte, 8))

    bit_len = len(bit_stream)

    width, height = img.size
    total_pixels = width * height

    # Ensure the embed data can fit into the target image file
    if bit_len > total_pixels * 3 * n_bits:
        raise ValueError("The file to be embedded is too large to fit in the target image file.")

    bit_index = 0
    for y in range(height):
        for x in range(width):
            if bit_index >= bit_len:
                break
            r, g, b = pixels[x, y]

            # Modify the LSBs of each color channel if there are still bits to embed
            if bit_index < bit_len:
                r = (r & ~((1 << n_bits) - 1)) | bits_to_byte(bit_stream[bit_index:bit_index + n_bits])
                bit_index += n_bits
            if bit_index < bit_len:
                g = (g & ~((1 << n_bits) - 1)) | bits_to_byte(bit_stream[bit_index:bit_index + n_bits])
                bit_index += n_bits
            if bit_index < bit_len:
                b = (b & ~((1 << n_bits) - 1)) | bits_to_byte(bit_stream[bit_index:bit_index + n_bits])
                bit_index += n_bits

            pixels[x, y] = (r, g, b)

    # Save the modified image
    img.save(output_file)
    print(f"File with embedded data saved as {output_file}")

def recover_bits(file_with_embedded, output_file, n_bits, embed_file_size):
    # Open the image with embedded data
    img = Image.open(file_with_embedded)
    img = img.convert("RGB")
    pixels = img.load()

    width, height = img.size

    # Recover the bits from the last N bits of each pixel's color channel
    bit_stream = []
    for y in range(height):
        for x in range(width):
            if len(bit_stream) >= embed_file_size * 8:
                break
            r, g, b = pixels[x, y]

            bit_stream.extend(byte_to_bits(r, 8)[-n_bits:])
            if len(bit_stream) >= embed_file_size * 8:
                break
            bit_stream.extend(byte_to_bits(g, 8)[-n_bits:])
            if len(bit_stream) >= embed_file_size * 8:
                break
            bit_stream.extend(byte_to_bits(b, 8)[-n_bits:])

    # Convert bit stream to bytes
    embed_data = bytearray()
    for i in range(0, len(bit_stream), 8):
        byte = bits_to_byte(bit_stream[i:i + 8])
        embed_data.append(byte)

    # Write the recovered data to the output file
    write_file(output_file, embed_data)
    print(f"Recovered file saved as {output_file}")

if __name__ == "__main__":
    # Define file paths
    file_target = './sample_data/files/file_target.png' # './sample_data/files/file_target_00.png'
    file_to_be_embedded = './sample_data/files/file_to_be_embedded.txt'
    file_with_embedded = './sample_data/files/file_with_embedded.png'
    file_recovered = './sample_data/files/file_recovered'

    # Number of bits to embed in each byte of the target file
    n_bits = 3

    # Embed the bits
    embed_bits(file_target, file_to_be_embedded, n_bits, file_with_embedded)

    # Size of the file to be embedded in bytes
    embed_file_size = os.path.getsize(file_to_be_embedded)

    # Recover the embedded file
    recover_bits(file_with_embedded, file_recovered, n_bits, embed_file_size)

    # Show the original file_to_be_embedded and the recovered file
    print("Original file_to_be_embedded:")
    print(read_file(file_to_be_embedded))
    
    print("Recovered file:")
    print(read_file(file_recovered))


