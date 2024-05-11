import time
import librosa
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_leading_silence, detect_nonsilent
from scipy.spatial.distance import cosine


def find_chunks(audio: AudioSegment):
    """Segment audio based on amplitude threshold."""
    print("Finding chunks...")

    # Get the indices of non-silent sections
    nonsilent_indices = detect_nonsilent(audio, min_silence_len=500, silence_thresh=-30)

    # Create chunks based on non-silent sections
    chunks = [audio[start:end] for start, end in nonsilent_indices]

    print("Chunks found.")

    return nonsilent_indices, chunks


def compare_mfcc(mfcc1, mfcc2):
    """Compare two audio segments for near-identical similarity."""
    # Determine the maximum number of frames between the two MFCC matrices
    max_frames = max(mfcc1.shape[1], mfcc2.shape[1])
    # Calculate the number of zeros to add before and after the shorter MFCC matrix
    pad_before = (max_frames - mfcc1.shape[1]) // 2
    pad_after = max_frames - mfcc1.shape[1] - pad_before
    # Pad the shorter MFCC matrix with zeros to center-align it within the padded matrix
    mfcc1_padded = np.pad(mfcc1, ((0, 0), (pad_before, pad_after)), mode='constant')
    # Repeat the same process for the second MFCC matrix
    pad_before = (max_frames - mfcc2.shape[1]) // 2
    pad_after = max_frames - mfcc2.shape[1] - pad_before
    mfcc2_padded = np.pad(mfcc2, ((0, 0), (pad_before, pad_after)), mode='constant')
    similarity = 1 - cosine(mfcc1_padded.T.flatten(), mfcc2_padded.T.flatten())
    return similarity


def compute_mfcc(chunk):
    """Compute MFCC from audio segment."""
    sr = 44100
    n_mfcc = 13

    # Detect leading and trailing silence
    leading_silence_duration = detect_leading_silence(chunk, silence_threshold=-30)
    trailing_silence_duration = detect_leading_silence(chunk.reverse(), silence_threshold=-30)

    # Trim leading and trailing silence
    chunk = chunk[leading_silence_duration:-trailing_silence_duration]

    # Convert chunk to float array
    audio_data = librosa.util.buf_to_float(chunk.get_array_of_samples(), n_bytes=2, dtype=np.float32)

    # Pad the audio signal if necessary
    desired_length = 2048  # Or any desired length
    padded_audio_data = np.pad(audio_data, (0, max(desired_length - len(audio_data), 0)), mode='constant')

    # Compute MFCC
    return librosa.feature.mfcc(y=padded_audio_data, sr=sr, n_mfcc=n_mfcc)


def find_matching_indices(og_chunks, lib_chunks, similarity_threshold=0.90):
    """Find matching indices between original and clip compilation audio chunks."""
    print("finding matches...")
    # Prep and covert chunks
    lib_mfccs = [compute_mfcc(chunk) for chunk in lib_chunks]
    og_mfccs = [compute_mfcc(chunk) for chunk in og_chunks]
    matching_indices = []
    last_matched_index = 0  # Initialize last matched index to start from the beginning

    for lib_mfcc in lib_mfccs:
        matched_index = None

        # Iterate over subsequent og_chunks starting from the last matched index
        for i in range(last_matched_index, min(len(og_mfccs), last_matched_index + 100)):
            similarity = compare_mfcc(lib_mfcc, og_mfccs[i])

            if similarity >= similarity_threshold:
                matched_index = i
                break  # Exit loop if match is found

        if matched_index is not None:
            matching_indices.append(matched_index)
            last_matched_index = matched_index + 1  # Update last matched index

    print("matches found.")

    return matching_indices


def create_matching_timestamps(chunk_indices, matching_indices):
    """Create timestamps of matching audio segments based on matching indices."""
    print("creating timestamps...")

    timestamps = []
    stamp_start = None

    for i, chunk_times in enumerate(chunk_indices):
        if i in matching_indices:
            # Start of new sequence
            if stamp_start is None:
                stamp_start = chunk_times[0]
        # End of sequence
        elif stamp_start is not None:
            stamp_end = chunk_times[1]
            timestamps.append((stamp_start, stamp_end))
            stamp_start = None

    # Handle case where the last matching chunk continues to the end
    if stamp_start is not None:
        stamp_end = chunk_indices[matching_indices[-1]][1]
        timestamps.append((stamp_start, stamp_end))

    print("timestamps created.")

    return timestamps


def save_timestamps_to_file(timestamps, filename):
    """Save timestamps to a text file."""
    print("saving timestamps...")

    with open(filename, 'w') as file:
        for start_timestamp, end_timestamp in timestamps:
            file.write(f"{start_timestamp:d} - {end_timestamp:d}\n")

    print(f"timestamps saved as {filename}.")


def export_matched_audio(og_chunks, matches, output_path="./og_audio/big_chunk.mp3"):
    """Concatenate original chunks based on matching indices and export."""
    # Initialize an empty list to hold the concatenated chunks
    concatenated_audio = AudioSegment.empty()

    # Iterate over the matches array
    for match_index in matches:
        # Append the corresponding original chunk to the concatenated audio
        concatenated_audio += og_chunks[match_index]

    # Export the concatenated audio to the specified output path
    concatenated_audio.export(output_path, format="mp3")

    print(f"Matched audio exported to: {output_path}")

# Example usage
if __name__ == "__main__":
    # Process the library audio
    start_time = time.time()
    lib_audio = AudioSegment.from_mp3('./lib_audio/04_15_2024_library.mp3')
    lib_indices, lib_chunks = find_chunks(lib_audio)
    end_time = time.time()
    print(f"Total execution time for chunking lib: {end_time - start_time:.2f} seconds.")

    # Process the original audio
    start_time = time.time()
    og_audio = AudioSegment.from_mp3('./og_audio/04_15_2024_stream.mp3')
    og_indices, og_chunks = find_chunks(og_audio)
    end_time = time.time()
    print(f"Total execution time for chunking og: {end_time - start_time:.2f} seconds.")

    # Find matching indices between original and library chunks
    start_time = time.time()
    matches = find_matching_indices(og_chunks, lib_chunks)
    end_time = time.time()
    print(f"Total execution time for finding matches: {end_time - start_time:.2f} seconds.")

    # Create timestamps for matching segments and save to file
    start_time = time.time()
    timestamps = create_matching_timestamps(og_indices, matches)
    save_timestamps_to_file(timestamps, './timestamps/04_15_2024_timestamps.txt')
    end_time = time.time()
    print(f"Total execution time for creating timestamps: {end_time - start_time:.2f} seconds.")

    # for i in range(0, 20):
    #     chunks[i].export(f"./lib_audio/chunk{i}.mp3", bitrate="128k", format="mp3")
