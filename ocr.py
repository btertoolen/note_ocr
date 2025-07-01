from transformers import AutoProcessor, AutoModelForCausalLM 
from PIL import Image
import requests
import torch
import os
import shutil
import glob
import time
from datetime import datetime


INPUT_FOLDER="/prj/ocr/phone_output"
OUTPUT_FOLDER="/prj/ocr/output"
ORIGINAL_SUBFOLDER="originals"

def run_ocr(input_file):
    model = AutoModelForCausalLM.from_pretrained("multimodalart/Florence-2-large-no-flash-attn", torch_dtype=torch.float16, trust_remote_code=True).to("cpu")
    processor = AutoProcessor.from_pretrained("multimodalart/Florence-2-large-no-flash-attn", trust_remote_code=True)

    prompt = "<OCR_WITH_REGION>"

    image = Image.open(input_file).convert("RGB")
    inputs = processor(text=prompt, images=image, return_tensors="pt").to("cpu", torch.float16)


    print("Running...")
    generated_ids = model.generate(
        input_ids=inputs["input_ids"],
        pixel_values=inputs["pixel_values"],
        max_new_tokens=4096,
        num_beams=2,
        do_sample=False,
        early_stopping=True,
    )


    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
    parsed_answer = processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
    print(parsed_answer['<OCR_WITH_REGION>']['labels'])
    return parsed_answer['<OCR_WITH_REGION>']['labels']

def generate_output_path():
    """Simple function to get next daily filename"""
    today = datetime.now().strftime("%y_%m_%d")
    pattern = os.path.join(OUTPUT_FOLDER, f"{today}_*.md")
    existing_files = glob.glob(pattern)
    
    # Find highest counter
    max_counter = -1
    for filepath in existing_files:
        filename = os.path.basename(filepath)
        try:
            counter = int(filename.split('_')[-1].split('.')[0])
            max_counter = max(max_counter, counter)
        except (ValueError, IndexError):
            continue
    
    next_counter = max_counter + 1
    filename = f"{today}_{next_counter}.md"
    return os.path.join(OUTPUT_FOLDER, filename)

def main():
    while True:
        error_count = 0
        # try:
        pattern = os.path.join(INPUT_FOLDER,"*.jpg")
        input_files = glob.glob(pattern)
        for file in input_files:
            print(f"Handling new input file: {file}")
            ocr_result = run_ocr(file)
            output_path = generate_output_path()
            output_file = os.path.basename(output_path)
            output_image_filename = os.path.splitext(output_file)[0] + ".jpg"
            output_image_relative = os.path.join(ORIGINAL_SUBFOLDER, output_image_filename)
            with open(output_path, "w") as output:
                print(ocr_result)
                for line in ocr_result:
                    output.write(line + "\n")
                output.write(f"![]({output_image_relative})")
                shutil.copyfile(file, os.path.join(OUTPUT_FOLDER, output_image_relative))
            error_count = 0
            os.remove(file)
        time.sleep(1)
            
            

if __name__ == "__main__":
    main()
