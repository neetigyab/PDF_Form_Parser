# PDF Form Parser

## Overview
This script extracts data from PDF forms and maps it to predefined fields. It utilizes several libraries for text and checkbox detection, visualization, and data extraction. The output can be saved in Excel/CSV format for further analysis.

---

## Libraries Utilized
- **pdfplumber**: To extract text and images from PDF documents.
- **OpenCV**: To process images and detect checkboxes.
- **numpy**: To handle numerical operations and array manipulations.
- **matplotlib**: To visualize detected checkboxes for debugging purposes.
- **pytesseract**: (If required) For optical character recognition.
- **pandas**: To handle tabular data and export it to Excel/CSV.

---

## Expected Form Elements
The fields expected to be present in the form are defined in two lists:

### Manual Input Fields
- Name
- Account number
- Last 4 digits of the card
- Transaction date
- Amount
- Merchant name
- Date you lost your card
- Time you lost your card
- Date you realized your card was stolen
- Time you realized your card was stolen
- When was the last time you used your card
- Last transaction amount
- Where do you normally store your card
- Where do you normally store your PIN
- Other items that were stolen
- Officer name
- Report number
- Suspect name
- Date
- Contact number
- Reason for dispute

### Checkbox Fields
- Transaction not authorized
- My card was
- Do you know who made the transaction
- Have you given permission to anyone to use your card
- Have you filed police report

---

## Field Mappings
Field mappings are used to handle differences between the actual field names in the PDF and the expected field names in the script. For example:
- "Your Name" is mapped to "Name"
- "Account#" is mapped to "Account number"
- "Last 4 digits of the card#" is mapped to "Last 4 digits of the card"

**Note**: Ensure any new additions to the form layout are updated in the `field_mappings` dictionary to maintain accuracy.

---

## Functionality

### `extract_pdf_text(pdf_path)`
Extracts all text lines from a PDF, including empty lines.

#### Parameters
- `pdf_path` (str): Path to the input PDF file.

#### Returns
- `list`: A list of text lines extracted from the PDF.

---

### `detect_checkboxes(image)`
Detects checkboxes on the given image and determines whether they are checked or unchecked.

#### Parameters
- `image` (numpy array): An image of the PDF page.

#### Returns
- `dict`: Checkbox states with coordinates as keys and states (`Checked`/`Unchecked`) as values.
- `list`: Positions of all detected checkboxes.

---

### `visualize_checkboxes(image, checkbox_positions, checkbox_states, page_number)`
Visualizes all detected checkboxes with color-coded rectangles for debugging.

#### Parameters
- `image` (numpy array): An image of the PDF page.
- `checkbox_positions` (list): Positions of detected checkboxes.
- `checkbox_states` (dict): Checkbox states (`Checked`/`Unchecked`).
- `page_number` (int): Page number for display purposes.

---

### `parse_checkbox(lines, index, aliases)`
Extracts checkbox states from nearby text lines and returns text associated with the checkbox.

#### Parameters
- `lines` (list): List of text lines.
- `index` (int): Index of the current line.
- `aliases` (list): List of aliases for the field name.

#### Returns
- `str`: Text associated with the checkbox.

---

### `map_fields_to_content(lines, pdf_path)`
Maps predefined fields to their respective content in the PDF.

#### Parameters
- `lines` (list): List of text lines extracted from the PDF.
- `pdf_path` (str): Path to the input PDF file.

#### Returns
- `dict`: Mapped fields and their corresponding content.

---

### `save_to_excel(mapped_data, filename)`
Saves the extracted data to an Excel or CSV file.

#### Parameters
- `mapped_data` (dict): Mapped fields and content.
- `filename` (str): Name of the output Excel/CSV file.

---

## Usage
1. Place the input PDF in the `ref` directory.
2. Run the script using:
   ```bash
   python Test.py
   ```
3. The output will be saved as `Dispute_form_output.xlsx` in the working directory.

---

## Notes
- Ensure all required libraries are installed:
  ```bash
  pip install pdfplumber opencv-python-headless numpy matplotlib pandas
  ```
- If there are changes to the form layout, update the `fields`, `checkbox_fields`, and `field_mappings` lists accordingly.
- Debugging visuals for checkbox detection can be enabled using the `visualize_checkboxes` function.

---

## Future Enhancements
- Add support for dynamic field detection using OCR.
- Implement error handling for malformed PDFs.
- Automate updates to the `field_mappings` dictionary based on new form layouts.

