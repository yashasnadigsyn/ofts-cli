# Import the external libraries
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
import torch

# MODEL URL: https://huggingface.co/microsoft/git-base-textcaps

def tag_image_GIT(image_path: str):
    """
        This function takes an image path as input and returns a caption for the image
        using the GIT model from Microsoft.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: A caption for the image.
    """
    # Look here for complete documentation: https://github.com/NielsRogge/Transformers-Tutorials/tree/master/GIT
    # Load the image
    image = Image.open(image_path).convert('RGB')

    # Load the processor and model
    print("Downloading GIT-BASE-TEXTCAPS...")
    processor = AutoProcessor.from_pretrained("microsoft/git-base-textcaps")
    model = AutoModelForCausalLM.from_pretrained("microsoft/git-base-textcaps")

    # Preprocess the image and convert it to pytorch tensor
    pixel_values = processor(images=image, return_tensors="pt").pixel_values

    # move the model and tensor to the device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    pixel_values = pixel_values.to(device)

    # Generate the caption and decode it using processor
    generated_ids = model.generate(pixel_values=pixel_values, max_length=20)
    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)
    return caption[0]
