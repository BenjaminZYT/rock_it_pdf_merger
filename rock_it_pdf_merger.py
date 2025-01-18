import os
import base64
import tempfile
import dash
from dash import dcc, html, Input, Output, State
import PyPDF2
from flask import send_from_directory

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Set app layout
app.layout = html.Div([
    html.H1("PDF Merger Tool", style={'textAlign': 'center'}),
    html.Hr(),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True  # Allow multiple files to be uploaded
    ),
    html.Div(id='output-message'),
    html.Button('Merge PDFs', id='merge-button', n_clicks=0, style={'margin': '10px'}),
    html.Div(id='download-link'),
    html.P(
        "Created by Benjamin Zu Yao Teoh - Atlanta, GA - January 2025",
        style={'fontSize': '7px', 'textAlign': 'center', 'marginTop': '20px'}
    )
])

# Function to merge PDFs
def merge_pdfs(pdfs):
    pdf_writer = PyPDF2.PdfWriter()
    for pdf in pdfs:
        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
    
    # Save merged PDF to a temporary file
    output_filename = "merged_output.pdf"
    output_path = os.path.join(tempfile.gettempdir(), output_filename)
    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)
    return output_filename

# Callback for merging PDFs
@app.callback(
    Output('download-link', 'children'),
    Output('output-message', 'children'),
    Input('merge-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_merge(n_clicks, contents, filenames):
    if n_clicks > 0:
        if not contents or not filenames:
            return "", html.Div("No files uploaded. Please upload PDF files.", style={'color': 'red'})

        # Decode and save uploaded files
        uploaded_files = []
        try:
            temp_dir = tempfile.mkdtemp()  # Temporary directory for file operations
            for content, filename in zip(contents, filenames):
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                temp_file_path = os.path.join(temp_dir, filename)
                with open(temp_file_path, 'wb') as file:
                    file.write(decoded)
                uploaded_files.append(temp_file_path)

            # Merge PDFs
            output_filename = merge_pdfs(uploaded_files)
            download_path = os.path.join(tempfile.gettempdir(), output_filename)
            return html.A(
                'Download Merged PDF',
                href=f'/download/{output_filename}',
                target="_blank",
                style={'color': 'blue'}
            ), html.Div("Merge successful!", style={'color': 'green'})
        except Exception as e:
            return "", html.Div(f"Error during merging: {e}", style={'color': 'red'})
        finally:
            # Cleanup uploaded files
            for file in uploaded_files:
                try:
                    os.remove(file)
                except OSError:
                    pass

    return "", ""

# Flask route for serving the merged file
@app.server.route('/download/<filename>')
def download_file(filename):
    temp_dir = tempfile.gettempdir()
    return send_from_directory(directory=temp_dir, path=filename, as_attachment=True)

# Run server
if __name__ == '__main__':
    app.run_server(debug=False)
