import pdfplumber
import pandas as pd
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Define the fields to be extracted
fields = [
    "Name",
    "Account number",
    "Last 4 digits of the card",
    "Transaction date",
    "Amount",
    "Merchant name",
    "Date you lost your card",
    "Time you lost your card",
    "Date you realized your card was stolen",
    "Time you realized your card was stolen",
    "When was the last time you used your card",
    "Last transaction amount",
    "Where do you normally store your card",
    "Where do you normally store your PIN",
    "Other items that were stolen",
    "Officer name",
    "Report number",
    "Suspect name",
    "Date",
    "Contact number",
    "Reason for dispute",
]

checkbox_fields = [
    "Transaction not authorized",
    "My card was",
    "Do you know who made the transaction",
    "Have you given permission to anyone to use your card",
    "Have you filed police report",
]

field_mappings = {
    "Name" : ["Your Name"],
    "Account number" : ["Account#"],
    "Last 4 digits of the card" : ["Last 4 digits of the card#"],
    "Transaction date" : ["Transaction date"],
    "Amount" : ["Amount$"],
    "Merchant name" : ["Merchant name"],
    "Transaction not authorized" : ["SECTION 1: TRANSACTION NOT AUTHORIZED"], #checkbox entry
    "My card was" : ["My card was (Select one):"], #checkbox entry
    "Date you lost your card"  : ["What DATE did you lose your card?"],
    "Time you lost your card"  : ["What TIME did you lose your card?"],
    "Date you realized your card was stolen"  : ["What DATE did you realize your card was missing?"],
    "Time you realized your card was stolen"  : ["What TIME did you realize your card was missing?"],
    "Do you know who made the transaction" : ["Do you know who made these transactions? (Select one):"], #checkbox entry
    "Have you given permission to anyone to use your card" : ["Have you given permission to anyone to use your card? (Select one):"], #checkbox entry
    "When was the last time you used your card" : ["When was the last time you used your card?","Date:","Time:"],
    "Last transaction amount" : ["Amount: $"],
    "Where do you normally store your card" : ["Where do you normally store your card?"],
    "Where do you normally store your PIN" : ["Where do you normally store your PIN?"],
    "Other items that were stolen" : ["Please list other items that were lost or stolen, including your mobile phone or any', 'additional cards (if applicable):"],
    "Have you filed police report" : ["Have you filed a police report? (Select one)"], #checkbox entry
    "Officer name" : ["District/OWicer name:"],
    "Report number" : ["Report number:"],
    "Suspect name" : ["Suspect name:"],
    "Date" : ["Date:"],
    "Contact number" : ["Contact number (during the hours of 8am-5pm PST):"],
    "Reason for dispute" : ["Transaction date Amount Merchant Name Reason for dispute"],
}

def extract_pdf_text(pdf_path):
    """Extract all text lines from a PDF, including empty lines."""
    try:
        lines = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                page_lines = text.splitlines()
                if text:
                    print(f"--- Page {page_number} Text ---\n{page_lines}\n{'-'*50}")
                lines.extend(page_lines)
        return lines
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return []

def detect_checkboxes(image):
    """Detect checkboxes and determine if they are checked or unchecked."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    checkbox_states = {}
    checkbox_positions = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h)
        if 0.8 <= aspect_ratio <= 1.5 and 10 <= w <= 30 and 10 <= h <= 30:
            roi = gray[y:y+h, x:x+w]
            non_zero = cv2.countNonZero(roi)
            checkbox_states[(x, y)] = "Checked" if non_zero > (w * h * 0.5) else "Unchecked"
            checkbox_positions.append((x, y, w, h))

    return checkbox_states, checkbox_positions

def visualize_checkboxes(image, checkbox_positions, checkbox_states, page_number):
    """Visualize all detected checkboxes on the image with colors for checked and unchecked."""
    for (x, y, w, h) in checkbox_positions:
        # Determine the checkbox state and set color
        state = checkbox_states.get((x, y), "Unchecked")
        color = (0, 255, 0) if state == "Checked" else (255, 0, 0)  # Green for Checked, Red for Unchecked
        
        # Draw the rectangle around the checkbox
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
    
    # Display the image with checkboxes
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(f"Checkboxes Detected on Page {page_number}")
    plt.axis("off")
    plt.show()


def parse_checkbox(lines, index, aliases):
    """Extract checkbox states from nearby lines and return text to the right of 'X'."""
    for alias in aliases:
        if alias.lower() in lines[index].lower():
            # Check for "X" in the next 4 lines (adjust range as needed)
            for line in lines[index : index + 5]:
                if "x" in line.lower():  # Normalize case and strip spaces
                    # Split the line and find the text after 'X'
                    parts = line.split("X", 1)  # Split on the first occurrence of 'X'
                    if len(parts) > 1:
                        return parts[1].strip().split("(")[0]  # Return the text after 'X'
                    return "Text missing after marked checkbox"
            return "No marked checkbox found"
    return "Unknown"



#def process_checkboxes(lines, start_index, field):
    """Process checkbox fields and extract selected options."""
    options = []
    for offset in range(1, 5):
        if start_index + offset >= len(lines):
            break

        line = lines[start_index + offset].strip()
        if not line:
            continue

        # Detect checkboxes dynamically from the line
        # Assuming an image of the page is loaded for each page
        # Replace `page_image` with the corresponding image for the current PDF page
        page_image = np.zeros((100, 100, 3), dtype=np.uint8)  # Placeholder for page image
        checkbox_states = detect_checkboxes(page_image)

        for (x, y), state in checkbox_states.items():
            if state == "Checked":
                # Extract the text to the right of the checkbox
                options.append(line)
                break
    return ", ".join(options)

def map_fields_to_content(lines, pdf_path):
    """Map fields to their respective content in the PDF."""
    mapped_data = {}
    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            image = np.array(page.to_image().original)
            checkbox_states, checkbox_positions = detect_checkboxes(image)

            # Visualize checkboxes for the current page
            visualize_checkboxes(image, checkbox_positions, checkbox_states, page_number)

            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                # Check if line matches any field
                for field, aliases in field_mappings.items():
                    # Only assign if the field is not already in mapped_data
                    if field not in mapped_data and any(alias.lower() in line.lower() for alias in aliases):
                        if field in checkbox_fields:
                            mapped_data[field] = parse_checkbox(lines, i, aliases)
                        else:
                            if i + 1 < len(lines) and "_" in lines[i + 1]:
                                mapped_data[field] = "n/a"
                            else:
                                if field == "When was the last time you used your card":
                                    mapped_data[field] = lines[i + 2] + " " + lines[i + 4]
                                    lines.pop(i+1)
                                    lines.pop(i+2)
                                    lines.pop(i+3)
                                    lines.pop(i+4)
                                elif field == "Reason for dispute":
                                    t = lines[i + 1].split(" ")
                                    mapped_data[field] = t[-2] + " " + t[-1]
                                else:
                                    mapped_data[field] = lines[i + 1].strip() if i + 1 < len(lines) else "Not Found"
    
    # Debugging output
    print("--- Mapped Fields and Content ---")
    for field, content in mapped_data.items():
        print(f"{field}: {content}")
    print("-" * 50)

    return mapped_data

def save_to_excel(mapped_data, filename):
    """Save the mapped data to an Excel file."""
    df = pd.DataFrame(list(mapped_data.items()), columns=["Field", "Value"])
    df=df.T
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    # Paths for input PDF and output Excel file
    input_pdf = "ref\Dispute form new format check.pdf"
    output_excel = "Dispute_form_output.xlsx"

    # Extract lines from the PDF
    lines = extract_pdf_text(input_pdf)

    # Map fields to content
    mapped_data = map_fields_to_content(lines, input_pdf)

    # Save the results to an Excel file
    save_to_excel(mapped_data, output_excel)
