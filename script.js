// DOM elements
const uploadForm = document.getElementById('uploadForm');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const spinner = document.getElementById('spinner');
const btnText = document.querySelector('.btn-text');
const resultSection = document.getElementById('result');
const errorSection = document.getElementById('error');
const voiceRate = document.getElementById('voiceRate');
const rateValue = document.getElementById('rateValue');
const voiceVolume = document.getElementById('voiceVolume');
const volumeValue = document.getElementById('volumeValue');
const voiceType = document.getElementById('voiceType');
const voiceSelectionMode = document.getElementById('voiceSelectionMode');
const voiceId = document.getElementById('voiceId');
const characterVoiceGroup = document.getElementById('characterVoiceGroup');
const specificVoiceGroup = document.getElementById('specificVoiceGroup');
const refreshVoices = document.getElementById('refreshVoices');
const previewBtn = document.getElementById('previewBtn');
const previewPlayer = document.getElementById('previewPlayer');
const enableTranslation = document.getElementById('enableTranslation');
const translationGroup = document.getElementById('translationGroup');
const targetLanguage = document.getElementById('targetLanguage');
const detectLangBtn = document.getElementById('detectLangBtn');

// Update voice rate display
if (voiceRate && rateValue) {
    voiceRate.addEventListener('input', function() {
        rateValue.textContent = this.value;
    });
}

// Update voice volume display
if (voiceVolume && volumeValue) {
    voiceVolume.addEventListener('input', function() {
        volumeValue.textContent = parseFloat(this.value).toFixed(1);
    });
}

// Voice type change handler with detailed descriptions for new voice packs
if (voiceType) {
    voiceType.addEventListener('change', function() {
        const description = document.getElementById('voiceDescription');
        if (description) {
            const descriptions = {
                // Classic voices
                'female_warm': 'Warm, caring narrator perfect for emotional stories, novels, and intimate narratives',
                'male_deep': 'Rich, deep voice with commanding presence perfect for dramatic narratives, thrillers, and epic stories',
                
                // Personality voices  
                'cheerful_energetic': 'Bubbly, energetic voice that brings joy and excitement to any story with infectious enthusiasm',
                'calm_meditative': 'Peaceful, meditative voice perfect for relaxation, mindfulness content, and soothing narratives',
                'adventurous_explorer': 'Dynamic voice that captures the spirit of adventure, exploration, and thrilling journeys',
                'mysterious_storyteller': 'Enigmatic voice perfect for mysteries, thrillers, dark tales, and suspenseful storytelling',
                'romantic_dreamer': 'Soft, dreamy voice that brings romance, emotion, and tender moments to life beautifully',
                'wise_mentor': 'Wise, experienced voice perfect for educational content, life lessons, and thoughtful guidance',
                'playful_comedian': 'Playful, humorous voice that adds fun, laughter, and entertainment to any content',
                'confident_leader': 'Strong, confident voice perfect for leadership content, motivational stories, and inspiring messages',
                
                // Specialty voices
                'gentle_healer': 'Gentle, therapeutic voice perfect for healing, wellness content, and peaceful storytelling',
                'curious_scientist': 'Curious, analytical voice perfect for educational, scientific content, and informative narratives',
                'passionate_artist': 'Passionate, expressive voice that brings creativity, artistry, and emotional depth to life',
                'street_smart': 'Cool, street-smart voice perfect for urban stories, contemporary fiction, and modern narratives',
                'nature_lover': 'Earthy, natural voice that connects with nature, environmental themes, and outdoor adventures',
                'tech_enthusiast': 'Modern, tech-savvy voice perfect for science fiction, technology content, and futuristic stories',
                'spiritual_guide': 'Spiritual, enlightened voice perfect for philosophical, spiritual content, and transcendent narratives',
                'rebel_activist': 'Bold, rebellious voice that challenges the status quo, inspires change, and motivates action',
                'dreamy_poet': 'Dreamy, poetic voice that brings beauty, lyricism, and artistic expression to any content',
                'friendly_neighbor': 'Warm, friendly voice like talking to your favorite neighbor over coffee - approachable and caring',
                'cosmic_explorer': 'Expansive, cosmic voice perfect for science fiction, space adventures, and infinite possibilities'
            };
            description.textContent = descriptions[this.value] || descriptions['female_warm'];
        }
    });
}

// Voice selection mode handling
if (voiceSelectionMode) {
    voiceSelectionMode.addEventListener('change', function() {
        if (this.value === 'character') {
            characterVoiceGroup.style.display = 'flex';
            specificVoiceGroup.style.display = 'none';
        } else {
            characterVoiceGroup.style.display = 'none';
            specificVoiceGroup.style.display = 'flex';
            loadAvailableVoices();
        }
    });
}

// Load available voices
async function loadAvailableVoices() {
    if (!voiceId) return;
    
    try {
        refreshVoices.disabled = true;
        refreshVoices.textContent = '🔄';
        voiceId.innerHTML = '<option value="">Loading voices...</option>';
        
        const response = await fetch('/get-voices');
        const data = await response.json();
        
        if (response.ok && data.success) {
            voiceId.innerHTML = '<option value="">Select a voice...</option>';
            
            // Group voices by category
            const categories = {};
            data.voices.forEach(voice => {
                if (!categories[voice.category]) {
                    categories[voice.category] = [];
                }
                categories[voice.category].push(voice);
            });
            
            // Add voices to select grouped by category
            Object.keys(categories).sort().forEach(category => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = category;
                
                categories[category].forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.id;
                    option.textContent = `${voice.display_name} (${voice.quality})`;
                    optgroup.appendChild(option);
                });
                
                voiceId.appendChild(optgroup);
            });
            
            console.log(`Loaded ${data.voices.length} voices`);
        } else {
            voiceId.innerHTML = '<option value="">Error loading voices</option>';
            console.error('Failed to load voices:', data.error);
        }
    } catch (error) {
        voiceId.innerHTML = '<option value="">Error loading voices</option>';
        console.error('Error loading voices:', error);
    } finally {
        refreshVoices.disabled = false;
        refreshVoices.textContent = '🔄';
    }
}

// Refresh voices button
if (refreshVoices) {
    refreshVoices.addEventListener('click', loadAvailableVoices);
}

// Voice ID change handler
if (voiceId) {
    voiceId.addEventListener('change', function() {
        const description = document.getElementById('voiceDescription');
        if (description && this.value) {
            const selectedOption = this.options[this.selectedIndex];
            description.textContent = `🎤 Using system voice: ${selectedOption.textContent}`;
        } else if (description) {
            description.textContent = '🎤 Select a specific system voice from the list above';
        }
    });
}

// Translation functionality - Enable translation by default
if (enableTranslation && translationGroup) {
    // Auto-enable translation by default
    enableTranslation.checked = true;
    translationGroup.style.display = 'flex';
    loadAvailableLanguages();
    
    enableTranslation.addEventListener('change', function() {
        if (this.checked) {
            translationGroup.style.display = 'flex';
            loadAvailableLanguages();
        } else {
            translationGroup.style.display = 'none';
        }
    });
}

// Load available languages for translation
async function loadAvailableLanguages() {
    if (!targetLanguage) return;
    
    try {
        const response = await fetch('/get-languages');
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Clear existing options except the first two and popular languages
            while (targetLanguage.children.length > 3) {
                targetLanguage.removeChild(targetLanguage.lastChild);
            }
            
            // Organize languages by regions
            const regions = {
                'European Languages': ['nl', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'sk', 'hu', 'ro', 'bg', 'hr', 'sr', 'sl', 'et', 'lv', 'lt', 'el', 'tr', 'uk', 'be', 'mk', 'mt', 'is', 'ga', 'cy', 'eu', 'ca', 'gl'],
                'Asian Languages': ['zh-tw', 'th', 'vi', 'id', 'ms', 'tl', 'my', 'km', 'lo', 'mn', 'ne', 'si', 'bn'],
                'Indian Languages': ['te', 'kn', 'ml', 'mr', 'gu', 'pa', 'or', 'as', 'ur', 'sd', 'ps'],
                'Middle Eastern & African': ['fa', 'am', 'ti', 'om', 'so', 'sw', 'zu', 'xh', 'af', 'ig', 'yo', 'ha'],
                'Latin American': ['pt-br', 'qu', 'ay', 'gn'],
                'Other Languages': ['sq', 'az', 'hy', 'ka', 'kk', 'ky', 'tg', 'tk', 'uz', 'mn', 'bo', 'dz', 'ii', 'ug']
            };
            
            // Add language options by region
            Object.entries(regions).forEach(([regionName, languageCodes]) => {
                const optgroup = document.createElement('optgroup');
                optgroup.label = `🌍 ${regionName}`;
                
                languageCodes.forEach(code => {
                    if (data.languages[code]) {
                        const info = data.languages[code];
                        const option = document.createElement('option');
                        option.value = code;
                        option.textContent = `${info.flag} ${info.name}`;
                        optgroup.appendChild(option);
                    }
                });
                
                if (optgroup.children.length > 0) {
                    targetLanguage.appendChild(optgroup);
                }
            });
            
            console.log(`Loaded ${Object.keys(data.languages).length} languages organized by regions`);
        } else {
            console.error('Failed to load languages:', data.error);
        }
    } catch (error) {
        console.error('Error loading languages:', error);
    }
}

// Language detection functionality
if (detectLangBtn) {
    detectLangBtn.addEventListener('click', async function() {
        const file = fileInput.files[0];
        if (!file) {
            alert('Please select a file first');
            return;
        }
        
        detectLangBtn.disabled = true;
        detectLangBtn.textContent = '🔄';
        
        try {
            console.log(`Processing file: ${file.name} (${file.type}, ${file.size} bytes)`);
            
            // Try client-side text extraction first for .txt files
            if (file.name.endsWith('.txt')) {
                try {
                    const text = await readFileContent(file);
                    
                    if (text && text.trim().length >= 10) {
                        console.log(`Extracted text preview: ${text.substring(0, 100)}...`);
                        
                        const formData = new FormData();
                        formData.append('text', text.substring(0, 1000));
                        
                        const response = await fetch('/detect-language', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const data = await response.json();
                        console.log('Language detection response:', data);
                        
                        if (response.ok && data.success) {
                            // DO NOT change target language - just show detection result
                            alert(`✅ Detected language: ${data.language_flag} ${data.language_name} (${(data.confidence * 100).toFixed(1)}% confidence)\n\n💡 Your target language selection remains unchanged.`);
                            return;
                        }
                    }
                } catch (clientError) {
                    console.warn('Client-side extraction failed, trying server-side:', clientError.message);
                }
            }
            
            // Fallback: Send file to server for processing (PDF, DOCX, or failed TXT)
            console.log('Using server-side file processing...');
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch('/detect-language', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            console.log('Server-side language detection response:', data);
            
            if (response.ok && data.success) {
                // DO NOT change target language - just show detection result
                alert(`✅ Detected language: ${data.language_flag} ${data.language_name} (${(data.confidence * 100).toFixed(1)}% confidence)\n\n💡 Your target language selection remains unchanged.`);
            } else {
                console.error('Language detection failed:', data);
                alert(`❌ Language detection failed: ${data.error || 'Unknown error'}

Tips:
- Ensure the file contains readable text
- Try a plain text (.txt) file
- Check that the document is not empty or corrupted`);
            }
            
        } catch (error) {
            console.error('Language detection error:', error);
            alert(`❌ Language detection failed: ${error.message}

Please try:
1. Using a plain text (.txt) file
2. Checking your internet connection
3. Refreshing the page`);
        } finally {
            detectLangBtn.disabled = false;
            detectLangBtn.textContent = '🔍';
        }
    });
}

// Helper function to read file content
async function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                let content = '';
                
                if (file.name.endsWith('.txt')) {
                    content = e.target.result;
                } else if (file.name.endsWith('.pdf')) {
                    // For PDF, we need to extract text properly
                    // This is a simplified approach - in production, use PDF.js
                    content = e.target.result;
                    // Try to extract readable text from PDF binary
                    const textMatches = content.match(/[a-zA-Z\s.,!?;:'"-]{10,}/g);
                    if (textMatches && textMatches.length > 0) {
                        content = textMatches.join(' ').substring(0, 2000);
                    } else {
                        // Fallback: try to find any readable text
                        content = content.replace(/[^\x20-\x7E\u00A0-\uFFFF]/g, ' ')
                                        .replace(/\s+/g, ' ')
                                        .substring(0, 2000);
                    }
                } else if (file.name.endsWith('.docx')) {
                    // For DOCX, we need proper extraction
                    // This is a simplified approach - the server should handle this
                    content = e.target.result;
                    // Try to extract readable text
                    const textMatches = content.match(/[a-zA-Z\s.,!?;:'"-]{10,}/g);
                    if (textMatches && textMatches.length > 0) {
                        content = textMatches.join(' ').substring(0, 2000);
                    } else {
                        content = content.replace(/[^\x20-\x7E\u00A0-\uFFFF]/g, ' ')
                                        .replace(/\s+/g, ' ')
                                        .substring(0, 2000);
                    }
                } else {
                    content = e.target.result;
                }
                
                // Validate that we have meaningful content
                if (!content || content.trim().length < 10) {
                    reject(new Error('Could not extract meaningful text from file. Please try a plain text file or ensure the document contains readable text.'));
                    return;
                }
                
                resolve(content);
            } catch (error) {
                reject(new Error(`Error processing file content: ${error.message}`));
            }
        };
        
        reader.onerror = () => reject(new Error('Failed to read file'));
        
        if (file.name.endsWith('.txt')) {
            reader.readAsText(file, 'utf-8');
        } else {
            // For PDF and DOCX, read as text with fallback encoding
            reader.readAsText(file, 'utf-8');
        }
    });
}

// Voice preview functionality
if (previewBtn && previewPlayer) {
    previewBtn.addEventListener('click', async function() {
        const formData = new FormData();
        
        // Add voice parameters based on selection mode
        const mode = voiceSelectionMode ? voiceSelectionMode.value : 'character';
        if (mode === 'specific' && voiceId && voiceId.value) {
            formData.append('voice_id', voiceId.value);
            formData.append('voice_type', 'female_warm'); // fallback
        } else {
            formData.append('voice_type', voiceType.value);
        }
        
        formData.append('voice_rate', voiceRate.value);
        formData.append('voice_volume', voiceVolume.value);
        
        // Add translation parameters for preview
        if (enableTranslation && enableTranslation.checked && targetLanguage && targetLanguage.value !== 'en') {
            formData.append('target_language', targetLanguage.value);
        }
        
        // Show loading state
        previewBtn.disabled = true;
        previewBtn.textContent = '🔄 Generating...';
        
        try {
            const response = await fetch('/preview-voice', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                previewPlayer.src = `/audio/${data.preview_file}`;
                previewPlayer.style.display = 'block';
                previewPlayer.load();
                
                // Auto-play the preview
                setTimeout(() => {
                    previewPlayer.play().catch(e => {
                        console.log('Auto-play prevented by browser:', e);
                    });
                }, 100);
            } else {
                alert(data.error || 'Failed to generate voice preview');
            }
        } catch (error) {
            console.error('Preview error:', error);
            alert('Failed to generate voice preview. Please try again.');
        } finally {
            previewBtn.disabled = false;
            previewBtn.innerHTML = '🔊 Preview Voice';
        }
    });
}

// File input change handler
if (fileInput) {
    fileInput.addEventListener('change', function() {
        const fileName = this.files[0]?.name;
        const fileLabel = document.querySelector('.file-text');
        if (fileName && fileLabel) {
            fileLabel.textContent = fileName;
        }
    });
}

// Form submission handler with AI enhancements
if (uploadForm) {
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        // Add voice_id if in specific voice mode
        const mode = voiceSelectionMode ? voiceSelectionMode.value : 'character';
        if (mode === 'specific' && voiceId && voiceId.value) {
            formData.append('voice_id', voiceId.value);
        }
        
        // Add naturalness and flow settings
        const enableNaturalness = document.getElementById('enableNaturalness');
        const enableAIFeatures = document.getElementById('enableAIFeatures');
        const continuousFlow = document.getElementById('continuousFlow');
        
        if (enableNaturalness) {
            formData.append('enable_naturalness', enableNaturalness.checked);
        }
        
        if (enableAIFeatures) {
            formData.append('enable_ai_features', enableAIFeatures.checked);
        }
        
        if (continuousFlow) {
            formData.append('continuous_flow', continuousFlow.checked);
        }
        
        // Add translation parameters
        if (enableTranslation && enableTranslation.checked) {
            formData.append('enable_translation', 'true');
            if (targetLanguage && targetLanguage.value) {
                formData.append('target_language', targetLanguage.value);
            }
        }
        
        // Validate file selection
        if (!fileInput.files[0]) {
            showError('Please select a file to upload.');
            return;
        }
        
        // Show loading state
        setLoadingStateEnhanced(true);
        hideResult();
        hideError();
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Store story data for AI features only if enabled
                if (data.ai_features_enabled) {
                    currentStoryText = data.text_preview;
                    currentStoryAnalysis = data.story_analysis;
                }
                
                showResultEnhanced(data);
                
                // Show translation info if translation was performed
                if (data.translation_performed) {
                    showTranslationInfo(data);
                }
                
                // Show emotion detection results only if AI features are enabled
                if (data.emotion_detected && data.ai_features_enabled && enableAIFeatures && enableAIFeatures.checked) {
                    showEmotionResults(data.emotion_detected, data.emotion_intensity);
                }
                
                // Generate and display suggested questions only if AI features are enabled
                if (data.story_questions && data.ai_features_enabled) {
                    displaySuggestedQuestions(data.story_questions);
                }
            } else {
                showError(data.error || 'An error occurred while processing your file.');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showError('Network error. Please check your connection and try again.');
        } finally {
            setLoadingStateEnhanced(false);
        }
    });
}

function setLoadingState(loading) {
    if (!uploadBtn || !spinner || !btnText) return;
    
    if (loading) {
        uploadBtn.disabled = true;
        spinner.style.display = 'inline-block';
        btnText.textContent = 'Generating...';
    } else {
        uploadBtn.disabled = false;
        spinner.style.display = 'none';
        btnText.textContent = 'Generate Audiobook';
    }
}

function showResult(data) {
    if (!resultSection) return;
    
    // Update audio player
    const audioPlayer = document.getElementById('audioPlayer');
    const downloadBtn = document.getElementById('downloadBtn');
    const textPreview = document.getElementById('textPreview');
    
    if (audioPlayer && data.audio_file) {
        audioPlayer.src = `/audio/${data.audio_file}`;
        audioPlayer.load(); // Reload the audio element
    }
    
    if (downloadBtn && data.audio_file) {
        downloadBtn.href = `/audio/${data.audio_file}`;
        downloadBtn.download = data.audio_file;
    }
    
    if (textPreview && data.text_preview) {
        textPreview.textContent = data.text_preview;
    }
    
    resultSection.style.display = 'block';
    
    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

function showError(message) {
    if (!errorSection) return;
    
    const errorText = document.getElementById('errorText');
    if (errorText) {
        errorText.textContent = message;
    }
    
    errorSection.style.display = 'block';
    
    // Scroll to error
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

function hideResult() {
    if (resultSection) {
        resultSection.style.display = 'none';
    }
}

function hideError() {
    if (errorSection) {
        errorSection.style.display = 'none';
    }
}

function generateAnother() {
    // Reset form
    if (uploadForm) {
        uploadForm.reset();
    }
    
    // Reset file label
    const fileLabel = document.querySelector('.file-text');
    if (fileLabel) {
        fileLabel.textContent = 'Choose a file (TXT, PDF, DOCX)';
    }
    
    // Hide result and error sections
    hideResult();
    hideError();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// File drag and drop functionality
const fileInputWrapper = document.querySelector('.file-input-wrapper');
const fileInputLabel = document.querySelector('.file-input-label');

if (fileInputWrapper && fileInputLabel) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        fileInputWrapper.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    fileInputWrapper.addEventListener('drop', handleDrop, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    if (fileInputLabel) {
        fileInputLabel.style.borderColor = '#764ba2';
        fileInputLabel.style.background = '#f0f2ff';
        fileInputLabel.style.transform = 'translateY(-2px)';
    }
}

function unhighlight(e) {
    if (fileInputLabel) {
        fileInputLabel.style.borderColor = '#667eea';
        fileInputLabel.style.background = '#f8f9ff';
        fileInputLabel.style.transform = 'translateY(0)';
    }
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0 && fileInput) {
        fileInput.files = files;
        
        // Update label text
        const fileLabel = document.querySelector('.file-text');
        if (fileLabel) {
            fileLabel.textContent = files[0].name;
        }
    }
}

// Auto-play functionality for audio
document.addEventListener('DOMContentLoaded', function() {
    const audioElements = document.querySelectorAll('audio');
    
    audioElements.forEach(audio => {
        audio.addEventListener('loadstart', function() {
            console.log('Audio loading started');
        });
        
        audio.addEventListener('error', function(e) {
            console.error('Audio error:', e);
            showError('Error loading audio file. The file may be corrupted or not supported.');
        });
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit form
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (uploadForm && !uploadBtn.disabled) {
            uploadForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
    }
    
    // Escape to hide result/error
    if (e.key === 'Escape') {
        hideResult();
        hideError();
    }
});

// Progress indication for large files
if (uploadForm) {
    const xhr = new XMLHttpRequest();
    
    // You could enhance this with a progress bar
    uploadForm.addEventListener('submit', function(e) {
        const file = fileInput.files[0];
        if (file && file.size > 5 * 1024 * 1024) { // Files larger than 5MB
            console.log('Large file detected, processing may take longer...');
        }
    });
}

// Enhanced loading state with AI messaging
function setLoadingStateEnhanced(loading) {
    if (!uploadBtn || !spinner || !btnText) return;
    
    if (loading) {
        uploadBtn.disabled = true;
        spinner.style.display = 'inline-block';
        btnText.textContent = 'AI is analyzing and generating...';
    } else {
        uploadBtn.disabled = false;
        spinner.style.display = 'none';
        btnText.textContent = 'Generate AI-Enhanced Audiobook';
    }
}

// Enhanced result display with AI features
function showResultEnhanced(data) {
    if (!resultSection) return;
    
    // Update audio player
    const audioPlayer = document.getElementById('audioPlayer');
    const downloadBtn = document.getElementById('downloadBtn');
    const textPreview = document.getElementById('textPreview');
    
    if (audioPlayer && data.audio_file) {
        audioPlayer.src = `/audio/${data.audio_file}`;
        audioPlayer.load();
    }
    
    if (downloadBtn && data.audio_file) {
        downloadBtn.href = `/audio/${data.audio_file}`;
        downloadBtn.download = data.audio_file;
    }
    
    if (textPreview && data.text_preview) {
        textPreview.textContent = data.text_preview;
    }
    
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// Show emotion detection results
function showEmotionResults(emotion, intensity) {
    const emotionResults = document.getElementById('emotionResults');
    if (!emotionResults) return;
    
    const emotionColors = {
        excitement: '#ff6b6b',
        sadness: '#4ecdc4', 
        mystery: '#45b7d1',
        anger: '#e74c3c',
        joy: '#f39c12',
        fear: '#9b59b6',
        romance: '#e91e63',
        action: '#ff9800',
        neutral: '#95a5a6'
    };
    
    const color = emotionColors[emotion] || emotionColors.neutral;
    const intensityPercent = Math.round(intensity * 100);
    
    emotionResults.innerHTML = `
        <div class="emotion-detection-result">
            <h4>🎭 AI Emotion Analysis</h4>
            <div class="emotion-indicator" style="background-color: ${color}; color: white; padding: 8px 15px; border-radius: 20px; display: inline-block; margin: 5px;">
                <strong>${emotion.charAt(0).toUpperCase() + emotion.slice(1)}</strong>
                <span style="margin-left: 10px;">Intensity: ${intensityPercent}%</span>
            </div>
            <p><small>Voice tone and pacing automatically adjusted for optimal storytelling</small></p>
        </div>
    `;
}

// Display suggested questions
function displaySuggestedQuestions(questions) {
    const questionsList = document.getElementById('questionsList');
    if (!questionsList || !questions) return;
    
    let html = '';
    questions.slice(0, 6).forEach((question, index) => {
        html += `<button class="suggested-question-btn" onclick="askSuggestedQuestion('${question.replace(/'/g, "\\'")}')">💭 ${question}</button>`;
    });
    
    questionsList.innerHTML = html;
}

// Ask a suggested question
function askSuggestedQuestion(question) {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = question;
        sendChatMessage();
    }
}

// Show translation information
function showTranslationInfo(data) {
    const resultSection = document.getElementById('result');
    if (!resultSection) return;
    
    // Create or update translation info div
    let translationInfo = document.getElementById('translationInfo');
    if (!translationInfo) {
        translationInfo = document.createElement('div');
        translationInfo.id = 'translationInfo';
        translationInfo.className = 'translation-info';
        translationInfo.style.cssText = `
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 14px;
        `;
        
        // Insert before the audio player
        const audioPlayer = resultSection.querySelector('.audio-player');
        if (audioPlayer) {
            resultSection.insertBefore(translationInfo, audioPlayer);
        } else {
            resultSection.appendChild(translationInfo);
        }
    }
    
    const languages = {
        'en': '🇺🇸 English', 'es': '🇪🇸 Spanish', 'fr': '🇫🇷 French', 'de': '🇩🇪 German',
        'it': '🇮🇹 Italian', 'pt': '🇵🇹 Portuguese', 'ru': '🇷🇺 Russian', 'ja': '🇯🇵 Japanese',
        'ko': '🇰🇷 Korean', 'zh': '🇨🇳 Chinese', 'ar': '🇸🇦 Arabic', 'hi': '🇮🇳 Hindi',
        'ta': '🇮🇳 Tamil', 'th': '🇹🇭 Thai', 'vi': '🇻🇳 Vietnamese'
    };
    
    const originalLang = languages[data.original_language] || data.original_language;
    const targetLang = languages[data.target_language] || data.target_language;
    const detectedLang = languages[data.detected_language] || data.detected_language;
    const confidence = Math.round(data.language_confidence * 100);
    
    let html = `<strong>🌐 Language Processing:</strong><br>`;
    html += `📍 Detected: ${detectedLang} (${confidence}% confidence)<br>`;
    
    if (data.translation_performed) {
        html += `✅ Translated from ${originalLang} to ${targetLang}<br>`;
        html += `🎤 Audio generated in ${targetLang}`;
    } else {
        html += `🎤 Audio generated in original language: ${targetLang}`;
    }
    
    translationInfo.innerHTML = html;
}