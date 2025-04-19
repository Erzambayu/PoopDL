# PoopDL - Optimized PoopHD Video Downloader & Streaming

<div align="center">
  <img src="assets/icon.png" alt="PoopDL Logo" width="120" height="120">
  <br>
  <h3>Fast, Free, and Ad-Free PoopHD Video Downloader & Streaming</h3>
</div>

## Overview

**PoopDL** is a powerful platform for streaming or downloading PoopHD videos quickly and for free. This optimized fork includes improved error handling, better code organization, enhanced performance, and a more robust architecture.

## Features

- ✅ **Multi-URL Processing**: Fetch multiple video URLs simultaneously
- ✅ **Fast Downloads**: Direct download links with no throttling
- ✅ **Ad-Free Streaming**: Clean, ad-free video streaming experience
- ✅ **Responsive UI**: Works on desktop and mobile devices
- ✅ **Improved Error Handling**: Better error messages and recovery
- ✅ **Performance Optimizations**: Faster loading and processing

## Screenshots

<div align="center">
  <table>
    <tr>
      <td><img src="assets/screenshot_1.png" alt="Screenshot 1" width="250"></td>
      <td><img src="assets/screenshot_2.png" alt="Screenshot 2" width="250"></td>
      <td><img src="assets/screenshot_3.png" alt="Screenshot 3" width="250"></td>
    </tr>
  </table>
</div>

## Tech Stack

- **Backend**: Python 3.x with Flask framework
  - Improved error handling and logging
  - Better code organization with proper typing
  - Enhanced performance with optimized requests

- **Frontend**: HTML5, CSS3, and Vanilla JavaScript
  - Modular code structure
  - Better error handling and user feedback
  - Improved performance with optimized DOM operations

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- A modern web browser

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/PoopDL.git
   cd PoopDL
   ```

2. Install the required dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run the Flask application:
   ```bash
   cd backend
   python flask_app.py
   ```

4. Open the `index.html` file in your web browser or use a local server:
   ```bash
   # Using Python's built-in HTTP server
   python -m http.server
   ```

5. Access the application at `http://localhost:8000` (or the port shown in your terminal)

## API Usage

The PoopDL API provides two main endpoints:

### 1. Generate File Information

```http
POST /generate_file
Content-Type: application/json

{
  "url": "https://poop.vin/d/EXAMPLE_ID"
}
```

Response:
```json
{
  "status": "success",
  "message": "",
  "file": [
    {
      "domain": "poop.vin",
      "id": "EXAMPLE_ID",
      "name": "Example Video",
      "image": "https://example.com/thumbnail.jpg"
    }
  ]
}
```

### 2. Generate Download/Stream Link

```http
POST /generate_link
Content-Type: application/json

{
  "domain": "poop.vin",
  "id": "EXAMPLE_ID"
}
```

Response:
```json
{
  "status": "success",
  "message": "",
  "link": "https://example.com/direct-download-link.mp4"
}
```

## Improvements in This Fork

### Backend

- Added comprehensive error handling and logging
- Implemented proper type hints for better code maintainability
- Optimized HTTP requests with timeout handling
- Improved code organization with better class and function structure
- Enhanced API responses with more detailed error messages

### Frontend

- Restructured JavaScript code with modular design
- Added better error handling and user feedback
- Improved performance with optimized DOM operations
- Enhanced UI responsiveness and user experience
- Added keyboard shortcuts for better accessibility

## Limitations

> ⚠️ **Note**: This platform only works with PoopHD URLs such as `poop.vin`, `poop.pm`, `poop.locker`, etc. It does not support Doodstream or other video hosting services.

## Credits

- Original project by [Dapunta Khurayra X](https://github.com/Dapunta)
- Optimized and enhanced by [YOUR_NAME]

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is provided for educational purposes only. Users are responsible for complying with applicable laws and regulations when using this software.