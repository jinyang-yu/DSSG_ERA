from project.risks import analyze_pdf

# Specify a sample PDF file from your data/test/ directory
pdf_file = "data/test/your_sample_file.pdf"

# Call the analyze_pdf function
result = analyze_pdf(pdf_file, override_output_dir="project/evaluation/test_run", ignore_analyzed=True)

# Print the result to verify
print(result)
