import os
import base64
import tempfile
import dash
from dash import dcc, html, Input, Output, State, ctx
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
    html.Div(id='uploaded-files-list', style={'margin': '10px', 'color': 'blue'}),
    html.Div([
        html.Label("Custom Name for Merged File (optional):"),
        dcc.Input(id='custom-filename', type='text', placeholder='Enter file name', style={'margin': '10px'}),
    ]),
    html.Div(id='output-message', style={'margin': '10px'}),
    html.Button('Merge PDFs', id='merge-button', n_clicks=0, style={'margin': '10px'}),
    html.Button('Reset', id='reset-button', n_clicks=0, style={'margin': '10px', 'backgroundColor': 'red', 'color': 'white'}),
    html.Div(id='download-link', style={'margin': '10px'}),
    html.P(
        "Created by Benjamin Zu Yao Teoh - Atlanta, GA - January 2025",
        style={'fontSize': '5px', 'textAlign': 'center', 'marginTop': '20px'}
    )
])

# Function to merge PDFs
def merge_pdfs(pdfs, output_filename):
    pdf_writer = PyPDF2.PdfWriter()
    for pdf in pdfs:
        with open(pdf, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)
    
    # Save merged PDF to a temporary file
    output_path = os.path.join(tempfile.gettempdir(), output_filename)
    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)
    return output_filename

# Callback to handle uploads, merging, and resetting
@app.callback(
    Output('uploaded-files-list', 'children'),
    Output('download-link', 'children'),
    Output('output-message', 'children'),
    Output('custom-filename', 'value'),
    Input('upload-data', 'contents'),
    Input('merge-button', 'n_clicks'),
    Input('reset-button', 'n_clicks'),
    State('upload-data', 'filename'),
    State('custom-filename', 'value'),
    prevent_initial_call=True
)
def handle_file_operations(contents, merge_clicks, reset_clicks, filenames, custom_filename):
    triggered_id = ctx.triggered_id

    if triggered_id == 'reset-button':
        return "", "", "", ""

    if triggered_id == 'upload-data' and contents:
        uploaded_filenames = filenames
        uploaded_list = html.Ul([html.Li(name) for name in uploaded_filenames])
        return uploaded_list, "", html.Div("Files uploaded successfully!", style={'color': 'green'}), custom_filename

    if triggered_id == 'merge-button' and contents:
        if not contents or not filenames:
            return "", "", html.Div("No files uploaded. Please upload PDF files.", style={'color': 'red'}), custom_filename

        uploaded_files = []
        try:
            temp_dir = tempfile.mkdtemp()
            for content, filename in zip(contents, filenames):
                content_type, content_string = content.split(',')
                decoded = base64.b64decode(content_string)
                temp_file_path = os.path.join(temp_dir, filename)
                with open(temp_file_path, 'wb') as file:
                    file.write(decoded)
                uploaded_files.append(temp_file_path)

            output_filename = custom_filename if custom_filename else "merged_output.pdf"
            output_filename = output_filename if output_filename.endswith(".pdf") else f"{output_filename}.pdf"
            output_path = merge_pdfs(uploaded_files, output_filename)
            return "", html.A(
                'Download Merged PDF',
                href=f'/download/{output_filename}',
                target="_blank",
                style={'color': 'blue'}
            ), html.Div("Merge successful!", style={'color': 'green'}), ""
        except Exception as e:
            return "", "", html.Div(f"Error during merging: {e}", style={'color': 'red'}), custom_filename
        finally:
            for file in uploaded_files:
                try:
                    os.remove(file)
                except OSError:
                    pass

    return "", "", "", ""

# Flask route for serving the merged file
@app.server.route('/download/<filename>')
def download_file(filename):
    temp_dir = tempfile.gettempdir()
    return send_from_directory(directory=temp_dir, path=filename, as_attachment=True)

# Run server
if __name__ == '__main__':
    app.run_server(debug=False)
