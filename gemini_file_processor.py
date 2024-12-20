import google.generativeai as genai
import os
import argparse
from pathlib import Path

def process_file(input_file: str, output_file: str, api_key: str, temperature: float) -> None:
    """
    Read content from input file, query Gemini API, and write response to output file
    
    Args:
        input_file (str): Path to input text file
        output_file (str): Path to output text file
        api_key (str): Google API key
        temperature (float): Temperature setting for response randomness (0.0 to 1.0)
    """
    # Initialize the Gemini client
    genai.configure(api_key=api_key)
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    # Send request to Gemini API
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate response
        response = model.generate_content(
            content,
            generation_config={
                'temperature': temperature,
            }
        )
        
        response_text = response.text
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return

    # Write response to output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response_text)
        print(f"Response successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        return

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Process text file through Gemini API',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--input',
        default='input.txt',
        help='Path to input text file'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='output.txt',
        help='Path to output text file'
    )

    parser.add_argument(
        '-t', '--temperature',
        type=float,
        default=0.7,
        help='Temperature setting (0.0 to 1.0) - lower values are more deterministic'
    )

    args = parser.parse_args()

    # Validate temperature
    if not 0.0 <= args.temperature <= 1.0:
        print("Error: Temperature must be between 0.0 and 1.0")
        return

    # Get API key from environment variable
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        return

    # Process the file with provided arguments
    process_file(args.input, args.output, api_key, args.temperature)

if __name__ == "__main__":
    main()
