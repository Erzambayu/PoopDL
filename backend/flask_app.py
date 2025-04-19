# Standard modules & libraries
import json
import logging
from typing import Dict, List, Any, Union

# Flask
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

# Local modules
from python.poop import PoopFile, PoopLink

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(import_name=__name__)
CORS(app=app)

# Constants
API_VERSION = "1.1"

@app.route(rule='/')
def index() -> Response:
    """Root endpoint providing API documentation.
    
    Returns:
        JSON response with API information
    """
    response: Dict[str, Any] = {
        'status': 'success',
        'version': API_VERSION,
        'service': [
            {
                'method': 'POST',
                'endpoint': 'generate_file',
                'url': f'{request.url_root}generate_file',
                'params': ['url'],
                'response': ['status', 'message', 'file']
            },
            {
                'method': 'POST',
                'endpoint': 'generate_link',
                'url': f'{request.url_root}generate_link',
                'params': ['domain', 'id'],
                'response': ['status', 'message', 'link']
            }
        ],
        'message': 'PoopDL API - PoopHD Video Downloader & Streaming'
    }
    return jsonify(response)

@app.route(rule='/generate_file', methods=['POST'])
def get_file() -> Response:
    """Generate file information from a PoopHD URL.
    
    Expects a JSON payload with a 'url' parameter.
    
    Returns:
        JSON response with file information
    """
    # Set default response
    result: Dict[str, Any] = {'status': 'failed', 'message': 'invalid params', 'file': []}

    try:
        # Validate request data
        if not request.is_json:
            logger.warning("Request did not contain valid JSON")
            result['message'] = 'Request must be valid JSON'
            return jsonify(result)
            
        # Get params
        data = request.get_json()
        url = data.get('url')

        if not url:
            logger.warning("Missing 'url' parameter in request")
            return jsonify(result)

        # Get file information
        logger.info(f"Processing URL: {url}")
        pf = PoopFile()
        pf.getAllFile(url)
        list_file = pf.file

        # Response condition
        if list_file:
            result = {'status': 'success', 'message': '', 'file': list_file}
            logger.info(f"Successfully processed URL, found {len(list_file)} files")
        else:
            result = {'status': 'failed', 'message': 'file not found', 'file': []}
            logger.warning(f"No files found for URL: {url}")

    except Exception as e:
        error_message = f"Error processing URL: {str(e)}"
        logger.error(error_message)
        result = {'status': 'failed', 'message': error_message, 'file': []}
        
    return jsonify(result)

@app.route(rule='/generate_link', methods=['POST'])
def get_link() -> Response:
    """Generate download/streaming link for a PoopHD file.
    
    Expects a JSON payload with 'domain' and 'id' parameters.
    
    Returns:
        JSON response with direct link
    """
    # Set default response
    result: Dict[str, Any] = {'status': 'failed', 'message': 'invalid params', 'link': ''}

    try:
        # Validate request data
        if not request.is_json:
            logger.warning("Request did not contain valid JSON")
            result['message'] = 'Request must be valid JSON'
            return jsonify(result)
            
        # Get params
        data = request.get_json()
        domain = data.get('domain')
        id_value = data.get('id')

        if not domain or not id_value:
            logger.warning(f"Missing parameters: domain={domain}, id={id_value}")
            return jsonify(result)

        # Get link
        logger.info(f"Processing link request for domain: {domain}, id: {id_value}")
        pl = PoopLink()
        pl.getLink(domain, id_value)
        link = pl.link

        # Response condition
        if link:
            result = {'status': 'success', 'message': '', 'link': link}
            logger.info(f"Successfully generated link for id: {id_value}")
        else:
            result = {'status': 'failed', 'message': 'link not found', 'link': ''}
            logger.warning(f"No link found for domain: {domain}, id: {id_value}")

    except Exception as e:
        error_message = f"Error generating link: {str(e)}"
        logger.error(error_message)
        result = {'status': 'failed', 'message': error_message, 'link': ''}
        
    return jsonify(result)

# Error handler for 404 errors
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'status': 'failed',
        'message': 'Endpoint not found',
        'error': str(error)
    }), 404

# Error handler for 500 errors
@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {str(error)}")
    return jsonify({
        'status': 'failed',
        'message': 'Internal server error',
        'error': str(error)
    }), 500

# Initialization
if __name__ == '__main__':
    logger.info("Starting PoopDL API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)