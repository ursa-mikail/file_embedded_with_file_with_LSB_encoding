import numpy as np

def allocate_data_bits_by_n_size_bits_into_byte_arrays(bit_stream, N):
    # eg. 1111, N = 3 => 0000 0111; 0000 0001
    number_of_bits = len(bit_stream)
    number_of_bytes_required = number_of_bits // N
    number_of_residual_bits = number_of_bits % N

    bits_in_byte = []

    for i in range(number_of_bytes_required):
        bits = bit_stream[N * (i - 1): N * i]
        bits = '0' * (8 - len(bits)) + bits
        bits_in_byte.append(int(bits, 2))

    if number_of_residual_bits > 0:
        bits = bit_stream[-number_of_residual_bits:]
        bits = '0' * (8 - len(bits)) + bits
        bits_in_byte.append(int(bits, 2))

    return bits_in_byte

def bit_stream_to_int_array(bit_stream):
    # assume byte stream
    bit_size = 8
    number_of_bytes = len(bit_stream) // bit_size
    int_array = []

    for i in range(number_of_bytes):
        start_bit = bit_size * i
        end_bit = bit_size * (i + 1)
        int_array.append(int(bit_stream[start_bit:end_bit], 2))

    return int_array


def convert_int8_to_bit_stream(data_to_be_inserted_as_bits_in_dec):
    number_of_text_char = len(data_to_be_inserted_as_bits_in_dec)
    bit_stream = ''

    for i in range(number_of_text_char):
        bits = bin(int(data_to_be_inserted_as_bits_in_dec[i]))[2:]
        bits = '0' * (8 - len(bits)) + bits
        bit_stream += bits

    return bit_stream

def extract_n_bits_from_lsb(data_in_dec_with_inserted_bits, N, given_length_of_text_bits):
    # 0 < N <= 8
    ON = 1
    OFF = 0
    stop_flag = OFF
    residue_bits_length = given_length_of_text_bits % N
    given_length_of_text_bits -= residue_bits_length  # deal with the residue bits later
    bit_stream = ''

    row_size, col_size = data_in_dec_with_inserted_bits.shape

    for i in range(row_size):
        for j in range(col_size):
            bits = bin(data_in_dec_with_inserted_bits[i, j])[2:]
            bits = '0' * (8 - len(bits)) + bits
            bit_stream += bits[-N:]

            if len(bit_stream) >= given_length_of_text_bits:
                stop_flag = ON
                if residue_bits_length > 0:
                    if (j + 1) <= col_size:
                        bits = bin(data_in_dec_with_inserted_bits[i, j + 1])[2:]
                    else:
                        bits = bin(data_in_dec_with_inserted_bits[i + 1, 0])[2:]

                    bits = '0' * (8 - len(bits)) + bits
                    bit_stream += bits[-residue_bits_length:]

                break

        if stop_flag == ON:
            break

    return bit_stream

def insert_into_lsb_bits(data_target_in_dec, data_to_be_inserted_in_bits, N):
    # 0 < N <= 8
    number_of_bits_to_be_inserted = len(data_to_be_inserted_in_bits)
    total_size_of_data_target_bits = np.prod(data_target_in_dec.shape) * 8
    total_size_of_data_target_bit_space_insertable = np.prod(data_target_in_dec.shape) * N

    if number_of_bits_to_be_inserted > total_size_of_data_target_bit_space_insertable:
        print('Number of bits to be inserted exceeds total size of data target bit space insertable')
    else:
        bit_stream = data_to_be_inserted_in_bits
        byte_arrays_with_info_bits = allocate_data_bits_by_n_size_bits_into_byte_arrays(bit_stream, N)
        number_of_byte_arrays_with_info_bits = len(byte_arrays_with_info_bits)

        row_size, col_size = data_target_in_dec.shape
        row_index, col_index = 0, 0

        data_in_dec_with_inserted_bits = np.copy(data_target_in_dec)

        for i in range(number_of_byte_arrays_with_info_bits):
            if col_index >= col_size:
                col_index = 0
                row_index += 1

            if row_index < row_size:
                data_in_dec_with_inserted_bits[row_index, col_index] |= byte_arrays_with_info_bits[i]
                col_index += 1

    return data_in_dec_with_inserted_bits

def mask_last_n_bits(data_in_dec, N):
    # 0 < N <= 8
    bit_8_mask = int('11111111', 2)
    bit_8_mask_shifted = np.left_shift(bit_8_mask, N)  # left shift
    bit_8_mask = np.bitwise_and(bit_8_mask_shifted, bit_8_mask)
    data_in_dec_masked = np.bitwise_and(data_in_dec, bit_8_mask)

    return data_in_dec_masked

def rgb2gray(rgb_image):
    return np.dot(rgb_image[..., :3], [0.2989, 0.5870, 0.1140])

# Example usage:
import cv2
import matplotlib.pyplot as plt
import numpy as np

# Functions (already defined above)

# Usage
target_image_file = 'Glaucus_atlanticus.jpg'
target_image = plt.imread(target_image_file)
target_image_in_gray = cv2.cvtColor(target_image, cv2.COLOR_RGB2GRAY)

N = 1
data_in_dec = target_image_in_gray
data_in_dec_masked = mask_last_n_bits(data_in_dec, N)

# Assuming section_getImageBitStream is equivalent to the following:
new_row_size = round(data_in_dec_masked.shape[0] / 2)
new_col_size = round(data_in_dec_masked.shape[1] / 2)
data_in_dec_masked = cv2.resize(data_in_dec_masked, (new_col_size, new_row_size))

target_image_file = 'imageLowRes_00.jpg'
target_image_to_be_hidden = plt.imread(target_image_file)
target_image_to_be_hidden_in_gray = rgb2gray(target_image_to_be_hidden)

# For demonstration, resizing the image
new_row_size = round(target_image_to_be_hidden_in_gray.shape[0] / 2)
new_col_size = round(target_image_to_be_hidden_in_gray.shape[1] / 2)
target_image_to_be_hidden_in_gray = cv2.resize(target_image_to_be_hidden_in_gray, (new_col_size, new_row_size))

bit_stream_of_image_to_hide = convert_int8_to_bit_stream(target_image_to_be_hidden_in_gray.flatten())
bit_stream_length = len(bit_stream_of_image_to_hide)
given_length_of_text_bits = bit_stream_length

data_in_dec_with_inserted_bits = insert_into_lsb_bits(data_in_dec_masked, bit_stream_of_image_to_hide, N)
bit_stream = extract_n_bits_from_lsb(data_in_dec_with_inserted_bits, N, bit_stream_length)
bit_stream = bit_stream[:bit_stream_length]

# int_array = bit_stream_to_int_array(bit_stream_of_image_to_hide)
int_array = bit_stream_to_int_array(bit_stream)

# Recover hidden image
target_image_in_gray_reconstructed = np.reshape(int_array, (new_row_size, new_col_size))

# Assuming section_plotForGrayScale_ImageWithinImage is equivalent to the following:
plt.figure(figsize=(10, 5))
plt.subplot(1, 3, 1)
plt.imshow(data_in_dec_masked, cmap='gray')
plt.title('Original Image with Hidden Data')

plt.subplot(1, 3, 2)
plt.imshow(target_image_in_gray_reconstructed, cmap='gray')
plt.title('Recovered Hidden Image')

plt.subplot(1, 3, 3)
plt.imshow(target_image_to_be_hidden_in_gray, cmap='gray')
plt.title('Hidden Image')

plt.show()

number_of_bits_available_for_inserting_bits = np.prod(data_in_dec_masked.shape) * N
number_of_bytes_hidden = new_row_size * new_col_size

print(f'Number of Bytes Hidden: {number_of_bytes_hidden}')
print(f'Number of Bits Hidden: {bit_stream_length}')
print(f'Number of Bits Space Available for Hiding: {number_of_bits_available_for_inserting_bits}')
print(f'Utility: {given_length_of_text_bits / number_of_bits_available_for_inserting_bits * 100:.5f}%')

"""
Number of Bytes Hidden: 30000
Number of Bits Hidden: 240000
Number of Bits Space Available for Hiding: 254464
Utility: 94.31590%
"""