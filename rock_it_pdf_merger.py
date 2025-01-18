import os
import base64
import dash
from dash import dcc, html, Input, Output, State
import PyPDF2

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
    html.Div(id='download-link')
])

# Function to merge PDFs
def merge_pdfs(pdfs):
    pdf_writer = PyPDF2.PdfWriter()
    for pdf in pdfs:
        pdf_reader = PyPDF2.PdfReader(pdf)
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
    
    # Save merged PDF
    output_filename = "merged_output.pdf"
    with open(output_filename, "wb") as output_file:
        pdf_writer.write(output_file)
    return output_filename

@app.callback(
    Output('download-link', 'children'),
    Output('output-message', 'children'),
    Input('merge-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def handle_merge(n_clicks, contents, filenames):
    if n_clicks > 0:
        if not contents:
            return "", html.Div("No files uploaded. Please upload PDF files.", style={'color': 'red'})

        # Decode uploaded files and save locally
        uploaded_files = []
        for content, filename in zip(contents, filenames):
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            with open(filename, 'wb') as file:
                file.write(decoded)
            uploaded_files.append(filename)

        # Merge PDFs
        try:
            output_filename = merge_pdfs(uploaded_files)
            download_link = html.A(
                'Download Merged PDF',
                href=f'/download/{output_filename}',
                target="_blank",
                style={'color': 'blue'}
            )
            return download_link, html.Div("Merge successful!", style={'color': 'green'})
        except Exception as e:
            return "", html.Div(f"Error during merging: {e}", style={'color': 'red'})
        finally:
            # Cleanup uploaded files
            for file in uploaded_files:
                os.remove(file)

    return "", ""

@app.server.route('/download/<path:filename>')
def download_file(filename):
    return dash.send_file(filename)

if __name__ == '__main__':
    app.run_server(debug=False)