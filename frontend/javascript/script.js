/**
 * PoopDL - Frontend JavaScript
 * Optimized version with improved error handling and performance
 */

// API Configuration
const API_CONFIG = {
    // Local development API endpoint
    local: 'http://127.0.0.1:5000',
    // Production API endpoint (uncomment to use)
    // production: 'https://poopdl-api.dapuntaratya.com'
};

// Set the active API endpoint
const api = API_CONFIG.local;

// Global variables
let list_file = [];

/**
 * Event Listeners and DOM Elements
 */
const DOM = {
    inputForm: document.getElementById('poop_url'),
    submitButton: document.getElementById('submit_button'),
    resultContainer: document.getElementById('result')
};

// Initialize event listeners when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Submit button click event
    DOM.submitButton.addEventListener('click', () => {
        const url = DOM.inputForm.value;
        readInput(url);
    });
    
    // Enter key press in textarea
    DOM.inputForm.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            const url = DOM.inputForm.value;
            readInput(url);
        }
    });
});

/**
 * UI Helper Functions
 */
const UI = {
    /**
     * Show/hide loading spinner for the fetch button
     * @param {string} elementId - ID of the element to modify
     * @param {boolean} active - Whether to show or hide the spinner
     */
    showFetchSpinner: function(elementId, active) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (active) {
            element.innerHTML = `<div id="loading-spinner" class="spinner-container"><div class="spinner"></div></div>`;
        } else {
            element.innerHTML = `Fetch`;
        }
        element.style.pointerEvents = 'all';
    },
    
    /**
     * Show/hide loading spinner for the download button
     * @param {string} elementId - ID of the element to modify
     * @param {boolean} active - Whether to show or hide the spinner
     */
    showDownloadSpinner: function(elementId, active) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (active) {
            element.innerHTML = `<div id="loading-spinner" class="spinner-container"><div class="spinner2"></div></div>`;
        } else {
            element.innerHTML = `Failed`;
        }
        element.style.pointerEvents = 'all';
    },
    
    /**
     * Show/hide loading spinner for the stream button
     * @param {string} elementId - ID of the element to modify
     * @param {boolean} active - Whether to show or hide the spinner
     */
    showStreamSpinner: function(elementId, active) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        if (active) {
            element.innerHTML = `<div id="loading-spinner" class="spinner-container"><div class="spinner2"></div></div>`;
            element.style.pointerEvents = 'none';
        } else {
            element.innerHTML = `<i class="fa-solid fa-play"></i>`;
            element.style.pointerEvents = 'auto';
        }
    },
    
    /**
     * Display error message when fetch fails
     */
    showFetchError: function() {
        DOM.resultContainer.innerHTML = `
            <div class="container-failed">
                <span>Fetch Failed</span>
            </div>`;
    }
};

/**
 * Utility Functions
 */
const Utils = {
    /**
     * Sleep/delay function
     * @param {number} seconds - Number of seconds to sleep
     * @returns {Promise} - Promise that resolves after the specified time
     */
    sleep: function(seconds) {
        return new Promise(resolve => setTimeout(resolve, seconds * 1000));
    }
};

/**
 * Process input URLs
 * @param {string} rawUrl - Raw URL input from the textarea
 */
async function readInput(rawUrl) {
    // Parse and validate input
    const urls = rawUrl && rawUrl.trim() ? rawUrl.split('\n').filter(url => url.trim()) : null;
    
    if (!urls || urls.length === 0) {
        UI.showFetchSpinner('submit_button', false);
        DOM.inputForm.value = '';
        return;
    }
    
    // Reset state and show loading
    list_file = [];
    DOM.resultContainer.innerHTML = '';
    UI.showFetchSpinner('submit_button', true);
    
    try {
        // Process each URL
        for (const url of urls) {
            await fetchURL(url.trim());
        }
        
        // Clear input after processing
        DOM.inputForm.value = '';
        
        // Show error if no files were found
        if (list_file.length === 0) {
            UI.showFetchError();
        }
    } catch (error) {
        console.error('Error processing URLs:', error);
        UI.showFetchError();
    } finally {
        UI.showFetchSpinner('submit_button', false);
    }
}

/**
 * Fetch file information from API
 * @param {string} url - URL to fetch information for
 * @returns {Promise<void>}
 */
async function fetchURL(url) {
    try {
        // API request configuration
        const endpoint = `${api}/generate_file`;
        const headers = {'Content-Type': 'application/json'};
        const requestOptions = {
            method: 'POST',
            mode: 'cors',
            headers: headers,
            body: JSON.stringify({url: url})
        };

        // Make API request
        const response = await fetch(endpoint, requestOptions);
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        const data = await response.json();

        // Process successful response
        if (data.status === 'success' && data.file && data.file.length > 0) {
            await displayItems(data.file);
        } else if (data.status === 'failed') {
            console.warn(`API returned failure: ${data.message}`);
        }
    } catch (error) {
        console.error(`Error fetching URL ${url}:`, error);
    }
}

// UI.showFetchError is used instead

/**
 * Display items in the UI
 * @param {Array} items - Array of file items to display
 * @returns {Promise<void>}
 */
async function displayItems(items) {
    if (!items || !Array.isArray(items) || items.length === 0) return;
    
    items.forEach(item => {
        // Add to global list if not already present
        if (!list_file.some(file => file.id === item.id)) {
            list_file.push(item);
            
            // Create item element
            const itemElement = document.createElement('div');
            itemElement.id = `file-${item.id}`;
            itemElement.className = 'container-item';
            itemElement.innerHTML = `
                <div class="container-item-default">
                    <div id="image-${item.id}" class="container-image">
                        <img src="${item.image}" alt="${item.name}" onclick="zoom(this)">
                    </div>
                    <div class="container-info">
                        <span id="title-${item.id}" class="title">${item.name}</span>
                        <div class="container-button">
                            <div id="container-download-${item.id}" class="container-download-button">
                                <button id="get-download-${item.id}" type="button" class="download-button">Download</button>
                            </div>
                            <div class="container-stream-button-valid">
                                <button id="stream-${item.id}" type="button" class="stream-button">
                                    <i class="fa-solid fa-play"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div id="video-box-${item.id}" class="container-item-expand false"></div>`;
                
            // Add to DOM
            DOM.resultContainer.appendChild(itemElement);
            
            // Add event listeners
            const downloadButton = itemElement.querySelector(`#get-download-${item.id}`);
            downloadButton.addEventListener('click', () => {
                initDownload(item.domain, item.id);
            });
            
            const streamButton = itemElement.querySelector(`#stream-${item.id}`);
            streamButton.addEventListener('click', () => {
                initStream(item.domain, item.id);
            });
        }
    });
}

/**
 * Initialize download process
 * @param {string} domain - Domain of the file
 * @param {string} id - ID of the file
 * @returns {Promise<void>}
 */
async function initDownload(domain, id) {
    try {
        // Show loading spinner
        UI.showDownloadSpinner(`get-download-${id}`, true);
        
        // Prepare API request
        const endpoint = `${api}/generate_link`;
        const headers = {'Content-Type': 'application/json'};
        const requestOptions = {
            method: 'POST',
            mode: 'cors',
            headers: headers,
            body: JSON.stringify({domain: domain, id: id})
        };
        
        // Make API request
        const response = await fetch(endpoint, requestOptions);
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        
        // Process response
        if (data.status === 'success' && data.link) {
            // Start download and reset button
            openDownloadLink(data.link);
            document.getElementById(`get-download-${id}`).innerHTML = 'Download';
        } else {
            console.warn(`Failed to get download link: ${data.message || 'Unknown error'}`);
            UI.showDownloadSpinner(`get-download-${id}`, false);
        }
    } catch (error) {
        console.error(`Error initializing download for ${id}:`, error);
        UI.showDownloadSpinner(`get-download-${id}`, false);
    }
}

/**
 * Open download link in new tab
 * @param {string} url - URL to open
 */
function openDownloadLink(url) {
    if (!url) return;
    window.open(url, '_blank', 'noopener,noreferrer');
}

/**
 * Initialize streaming process
 * @param {string} domain - Domain of the file
 * @param {string} id - ID of the file
 * @returns {Promise<void>}
 */
async function initStream(domain, id) {
    try {
        const itemContainer = document.getElementById(`file-${id}`);
        const videoBox = document.getElementById(`video-box-${id}`);
        
        if (!itemContainer || !videoBox) return;
        
        // Toggle video box visibility
        if (itemContainer.className === 'container-item') {
            // Check if video player already exists
            if (videoBox.innerHTML.trim() === '') {
                // Show loading spinner
                UI.showStreamSpinner(`stream-${id}`, true);
                
                try {
                    // Get streaming URL
                    const streamUrl = await getStreamURL(domain, id);
                    
                    if (streamUrl) {
                        // Create video player
                        videoBox.innerHTML = `
                            <video controls preload="metadata">
                                <source id="stream-video-${id}" src="${streamUrl}" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>`;
                    } else {
                        videoBox.innerHTML = `<div class="stream-error">Unable to load video stream</div>`;
                    }
                } catch (error) {
                    console.error(`Error getting stream URL for ${id}:`, error);
                    videoBox.innerHTML = `<div class="stream-error">Error loading video: ${error.message}</div>`;
                } finally {
                    UI.showStreamSpinner(`stream-${id}`, false);
                }
            }
            
            // Expand the container
            itemContainer.className = 'container-item expand';
            videoBox.className = 'container-item-expand';
        } else {
            // Collapse the container
            itemContainer.className = 'container-item';
            videoBox.className = 'container-item-expand false';
            
            // Pause video if playing
            const video = videoBox.querySelector('video');
            if (video && !video.paused) {
                video.pause();
            }
        }
    } catch (error) {
        console.error(`Error initializing stream for ${id}:`, error);
    }
}

/**
 * Get streaming URL from API
 * @param {string} domain - Domain of the file
 * @param {string} id - ID of the file
 * @returns {Promise<string>} - Streaming URL or empty string if failed
 */
async function getStreamURL(domain, id) {
    try {
        // Prepare API request
        const endpoint = `${api}/generate_link`;
        const headers = {'Content-Type': 'application/json'};
        const requestOptions = {
            method: 'POST',
            mode: 'cors',
            headers: headers,
            body: JSON.stringify({domain: domain, id: id})
        };
        
        // Make API request
        const response = await fetch(endpoint, requestOptions);
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        const data = await response.json();
        
        // Return link if successful
        if (data.status === 'success' && data.link) {
            return data.link;
        } else {
            console.warn(`Failed to get stream link: ${data.message || 'Unknown error'}`);
            return '';
        }
    } catch (error) {
        console.error(`Error getting stream URL for ${id}:`, error);
        return '';
    }
}