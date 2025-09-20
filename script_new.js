/**
 * AI-Enhanced Audiobook Generator - Frontend JavaScript
 * Professional UI interactions and API communication
 */

class AudiobookGenerator {
    constructor() {
        this.currentFile = null;
        this.currentText = '';
        this.currentLanguage = 'en';
        this.currentStep = 1;
        this.apiBase = '/api';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupTheme();
        this.loadVoices();
        this.loadLanguages();
        this.checkStatus();
    }
    
    setupEventListeners() {
        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        if (uploadArea) {
            uploadArea.addEventListener('click', () => fileInput?.click());
            uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            uploadArea.addEventListener('drop', (e) => this.handleFileDrop(e));
        }
        
        // Voice settings
        const voiceSpeed = document.getElementById('voiceSpeed');
        const voiceVolume = document.getElementById('voiceVolume');
        
        if (voiceSpeed) {
            voiceSpeed.addEventListener('input', (e) => {
                document.getElementById('speedValue').textContent = `${e.target.value} WPM`;
            });
        }
        
        if (voiceVolume) {
            voiceVolume.addEventListener('input', (e) => {
                document.getElementById('volumeValue').textContent = `${Math.round(e.target.value * 100)}%`;
            });
        }
        
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }
    
    setupTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        this.showToast('Theme updated', 'success');
    }
    
    // File handling
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }
    
    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }
    
    handleFileDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }
    
    async processFile(file) {
        this.showLoading('Processing file...');
        
        try {
            const formData = new FormData();
            formData.append('file', file);
            
            const response = await fetch(`${this.apiBase}/upload`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentFile = result;
                this.currentText = result.text_content;
                this.displayFileInfo(result);
                this.detectLanguage();
                this.nextStep(2);
                this.showToast('File processed successfully', 'success');
            } else {
                this.showToast(result.error || 'File processing failed', 'error');
            }
        } catch (error) {
            this.showToast('Upload failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    displayFileInfo(fileData) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileStats = document.getElementById('fileStats');
        
        if (fileInfo && fileName && fileStats) {
            fileName.textContent = fileData.filename;
            fileStats.textContent = `${fileData.metadata.word_count} words • ${fileData.metadata.file_size_mb} MB`;
            
            document.getElementById('uploadArea').style.display = 'none';
            fileInfo.style.display = 'block';
        }
    }
    
    // Language detection and translation
    async detectLanguage() {
        if (!this.currentText) return;
        
        try {
            const response = await fetch(`${this.apiBase}/detect-language`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: this.currentText })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentLanguage = result.detected_language;
                this.displayLanguageDetection(result);
                this.showTranslationOptions();
            } else {
                this.showToast(result.error || 'Language detection failed', 'warning');
            }
        } catch (error) {
            this.showToast('Language detection error: ' + error.message, 'error');
        }
    }
    
    displayLanguageDetection(result) {
        const detectedLanguage = document.getElementById('detectedLanguage');
        const detectionConfidence = document.getElementById('detectionConfidence');
        const languageDetection = document.getElementById('languageDetection');
        
        if (detectedLanguage && detectionConfidence && languageDetection) {
            detectedLanguage.textContent = `Detected: ${result.language_name}`;
            detectionConfidence.textContent = `Confidence: ${Math.round(result.confidence * 100)}%`;
            languageDetection.style.display = 'block';
        }
    }
    
    showTranslationOptions() {
        const targetLanguage = document.getElementById('targetLanguage');
        const translationOptions = document.getElementById('translationOptions');
        
        if (targetLanguage && translationOptions) {
            if (targetLanguage.value !== this.currentLanguage) {
                translationOptions.style.display = 'block';
            }
        }
    }
    
    async translateText() {
        const targetLanguage = document.getElementById('targetLanguage').value;
        
        if (targetLanguage === this.currentLanguage) {
            this.analyzeText();
            this.nextStep(3);
            return;
        }
        
        this.showProgress('translationProgress', 'Translating text...');
        
        try {
            const response = await fetch(`${this.apiBase}/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: this.currentText,
                    target_language: targetLanguage,
                    source_language: this.currentLanguage
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentText = result.translated_text;
                this.currentLanguage = result.target_language;
                this.showToast('Text translated successfully', 'success');
                this.analyzeText();
                this.nextStep(3);
            } else {
                this.showToast(result.error || 'Translation failed', 'error');
            }
        } catch (error) {
            this.showToast('Translation error: ' + error.message, 'error');
        } finally {
            this.hideProgress('translationProgress');
        }
    }
    
    // Text analysis
    async analyzeText() {
        try {
            const response = await fetch(`${this.apiBase}/analyze-text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: this.currentText })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.displayTextAnalysis(result);
                this.displayTextPreview();
            } else {
                this.showToast(result.error || 'Analysis failed', 'warning');
            }
        } catch (error) {
            this.showToast('Analysis error: ' + error.message, 'error');
        }
    }
    
    displayTextPreview() {
        const textPreview = document.getElementById('textPreview');
        const previewText = document.getElementById('previewText');
        
        if (textPreview && previewText) {
            const preview = this.currentText.substring(0, 300) + 
                           (this.currentText.length > 300 ? '...' : '');
            previewText.textContent = preview;
            textPreview.style.display = 'block';
        }
    }
    
    displayTextAnalysis(analysis) {
        const analysisResults = document.getElementById('analysisResults');
        const primaryEmotion = document.getElementById('primaryEmotion');
        const emotionIntensity = document.getElementById('emotionIntensity');
        const genreTags = document.getElementById('genreTags');
        const textStats = document.getElementById('textStats');
        
        if (analysisResults) {
            if (primaryEmotion && emotionIntensity) {
                primaryEmotion.textContent = analysis.emotion_analysis.dominant_emotion;
                emotionIntensity.textContent = `${Math.round(analysis.emotion_analysis.intensity * 100)}% intensity`;
            }
            
            if (genreTags) {
                genreTags.innerHTML = analysis.genre_hints
                    .slice(0, 3)
                    .map(genre => `<span class="badge">${genre}</span>`)
                    .join('');
            }
            
            if (textStats) {
                textStats.innerHTML = `
                    <div>Words: ${analysis.word_count}</div>
                    <div>Sentences: ${analysis.sentence_count}</div>
                    <div>Level: ${analysis.reading_level}</div>
                `;
            }
            
            analysisResults.style.display = 'block';
            this.nextStep(4);
        }
    }
    
    // Voice management
    async loadVoices() {
        try {
            const response = await fetch(`${this.apiBase}/voices`);
            const result = await response.json();
            
            if (response.ok) {
                this.populateVoiceSelect(result.voices);
            }
        } catch (error) {
            console.error('Failed to load voices:', error);
        }
    }
    
    // Load available languages for translation
    async loadLanguages() {
        const targetLanguage = document.getElementById('targetLanguage');
        if (!targetLanguage) return;
        
        try {
            const response = await fetch('/get-languages');
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Clear existing options except the default ones
                while (targetLanguage.children.length > 1) {
                    targetLanguage.removeChild(targetLanguage.lastChild);
                }
                
                // Organize languages by regions with flag emojis
                const regions = {
                    'European Languages 🌍': ['nl', 'sv', 'no', 'da', 'fi', 'pl', 'cs', 'sk', 'hu', 'ro', 'bg', 'hr', 'sr', 'sl', 'et', 'lv', 'lt', 'el', 'tr', 'uk', 'be', 'mk', 'mt', 'is', 'ga', 'cy', 'eu', 'ca', 'gl'],
                    'Asian Languages 🌏': ['zh-tw', 'th', 'vi', 'id', 'ms', 'tl', 'my', 'km', 'lo', 'mn', 'ne', 'si', 'bn', 'bo', 'dz', 'ii', 'ug'],
                    'Indian Languages 🌸': ['hi', 'ta', 'te', 'kn', 'ml', 'mr', 'gu', 'pa', 'or', 'as', 'ur', 'sd', 'ps'],
                    'Middle Eastern & African 🌍': ['ar', 'he', 'fa', 'am', 'ti', 'om', 'so', 'sw', 'zu', 'xh', 'af', 'ig', 'yo', 'ha'],
                    'Latin American 🌎': ['pt-br', 'qu', 'ay', 'gn'],
                    'Other Languages 🌐': ['sq', 'az', 'hy', 'ka', 'kk', 'ky', 'tg', 'tk', 'uz', 'mn']
                };
                
                // Add language options by region
                Object.entries(regions).forEach(([regionName, languageCodes]) => {
                    const optgroup = document.createElement('optgroup');
                    optgroup.label = regionName;
                    
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
    
    populateVoiceSelect(voices) {
        const voiceSelect = document.getElementById('voiceSelect');
        if (!voiceSelect) return;
        
        voiceSelect.innerHTML = '<option value="">Select a voice...</option>';
        
        voices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = `${voice.name} (${voice.gender}, ${voice.language})`;
            voiceSelect.appendChild(option);
        });
    }
    
    async previewVoice() {
        const voiceSelect = document.getElementById('voiceSelect');
        const voiceId = voiceSelect?.value;
        
        if (!voiceId) {
            this.showToast('Please select a voice first', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/voice-preview`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    voice_id: voiceId,
                    text: 'This is a preview of the selected voice for your audiobook.'
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showToast('Voice preview played', 'info');
            } else {
                this.showToast('Voice preview failed', 'warning');
            }
        } catch (error) {
            this.showToast('Preview error: ' + error.message, 'error');
        }
    }
    
    // Audiobook generation
    async generateAudiobook() {
        const audiobookName = document.getElementById('audiobookName').value.trim();
        if (!audiobookName) {
            this.showToast('Please enter an audiobook name', 'warning');
            return;
        }
        
        if (!this.currentText) {
            this.showToast('No text content available', 'error');
            return;
        }
        
        this.showGenerationProgress();
        
        const settings = this.getVoiceSettings();
        settings.filename = audiobookName;
        
        try {
            const response = await fetch(`${this.apiBase}/generate-audio`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: this.currentText,
                    settings: settings
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showGenerationResult(result);
                this.nextStep(5);
                this.showToast('Audiobook generated successfully!', 'success');
            } else {
                this.showToast(result.error || 'Generation failed', 'error');
                this.hideGenerationProgress();
            }
        } catch (error) {
            this.showToast('Generation error: ' + error.message, 'error');
            this.hideGenerationProgress();
        }
    }
    
    getVoiceSettings() {
        return {
            voice_id: document.getElementById('voiceSelect')?.value,
            rate: parseInt(document.getElementById('voiceSpeed')?.value || 180),
            volume: parseFloat(document.getElementById('voiceVolume')?.value || 0.9),
            personality: document.getElementById('voicePersonality')?.value || 'narrator',
            continuous_flow: document.getElementById('continuousFlow')?.checked !== false,
            emotion_enhancement: document.getElementById('emotionEnhancement')?.checked !== false
        };
    }
    
    showGenerationProgress() {
        const generationProgress = document.getElementById('generationProgress');
        const generationControls = document.querySelector('.generation-controls');
        
        if (generationProgress && generationControls) {
            generationControls.style.display = 'none';
            generationProgress.style.display = 'block';
            
            // Simulate progress steps
            this.simulateProgress();
        }
    }
    
    simulateProgress() {
        const steps = ['progressStep1', 'progressStep2', 'progressStep3', 'progressStep4'];
        let currentStep = 0;
        
        const interval = setInterval(() => {
            if (currentStep < steps.length) {
                const stepElement = document.getElementById(steps[currentStep]);
                if (stepElement) {
                    stepElement.classList.add('active');
                    if (currentStep > 0) {
                        document.getElementById(steps[currentStep - 1])?.classList.remove('active');
                        document.getElementById(steps[currentStep - 1])?.classList.add('completed');
                    }
                }
                currentStep++;
            } else {
                clearInterval(interval);
            }
        }, 1500);
    }
    
    showGenerationResult(result) {
        const generationProgress = document.getElementById('generationProgress');
        const generationResult = document.getElementById('generationResult');
        const resultInfo = document.getElementById('resultInfo');
        const downloadBtn = document.getElementById('downloadBtn');
        
        if (generationProgress && generationResult) {
            generationProgress.style.display = 'none';
            generationResult.style.display = 'block';
            
            if (resultInfo) {
                resultInfo.innerHTML = `
                    <div><strong>File:</strong> ${result.audio_file}</div>
                    <div><strong>Duration:</strong> ~${Math.round(result.text_analysis.estimated_duration / 60)} minutes</div>
                    <div><strong>Words:</strong> ${result.text_analysis.word_count}</div>
                    <div><strong>Emotion:</strong> ${result.text_analysis.emotion} (${Math.round(result.text_analysis.intensity * 100)}%)</div>
                `;
            }
            
            if (downloadBtn) {
                downloadBtn.onclick = () => this.downloadAudiobook(result.audio_file);
            }
        }
    }
    
    downloadAudiobook(filename) {
        const downloadUrl = `${this.apiBase}/download/${encodeURIComponent(filename)}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        this.showToast('Download started', 'success');
    }
    
    // UI utilities
    nextStep(stepNumber) {
        this.currentStep = stepNumber;
        
        // Update step status indicators
        for (let i = 1; i <= 5; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                if (i < stepNumber) {
                    step.classList.add('completed');
                } else if (i === stepNumber) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active', 'completed');
                }
            }
        }
    }
    
    showProgress(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'flex';
            const textElement = element.querySelector('.progress-text');
            if (textElement) textElement.textContent = message;
        }
    }
    
    hideProgress(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    }
    
    showLoading(message = 'Loading...') {
        const overlay = document.getElementById('loadingOverlay');
        const text = document.getElementById('loadingText');
        
        if (overlay) {
            overlay.style.display = 'flex';
            if (text) text.textContent = message;
        }
    }
    
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
    
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i data-lucide="${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Re-initialize Lucide icons for the new toast
        if (window.lucide) {
            window.lucide.createIcons();
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }
    
    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'x-circle',
            warning: 'alert-triangle',
            info: 'info'
        };
        return icons[type] || 'info';
    }
    
    // Status checking
    async checkStatus() {
        try {
            const response = await fetch(`${this.apiBase}/status`);
            const result = await response.json();
            
            if (response.ok) {
                this.updateStatusIndicator(result);
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }
    
    updateStatusIndicator(status) {
        const indicator = document.getElementById('statusIndicator');
        const dot = indicator?.querySelector('.status-dot');
        const text = indicator?.querySelector('.status-text');
        
        if (dot && text) {
            const isHealthy = status.application === 'running';
            
            dot.className = `status-dot ${isHealthy ? 'status-healthy' : 'status-error'}`;
            text.textContent = isHealthy ? 'Ready' : 'Error';
        }
    }
    
    // Advanced features
    toggleAdvanced() {
        const content = document.getElementById('advancedContent');
        const icon = document.getElementById('advancedToggleIcon');
        
        if (content && icon) {
            const isVisible = content.style.display !== 'none';
            
            content.style.display = isVisible ? 'none' : 'block';
            icon.style.transform = isVisible ? 'rotate(0deg)' : 'rotate(180deg)';
        }
    }
    
    resetWorkflow() {
        // Reset form data
        this.currentFile = null;
        this.currentText = '';
        this.currentLanguage = 'en';
        this.currentStep = 1;
        
        // Reset UI
        document.getElementById('fileInput').value = '';
        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('languageDetection').style.display = 'none';
        document.getElementById('translationOptions').style.display = 'none';
        document.getElementById('textPreview').style.display = 'none';
        document.getElementById('analysisResults').style.display = 'none';
        document.getElementById('generationProgress').style.display = 'none';
        document.getElementById('generationResult').style.display = 'none';
        document.querySelector('.generation-controls').style.display = 'block';
        document.getElementById('audiobookName').value = '';
        
        // Reset steps
        for (let i = 1; i <= 5; i++) {
            const step = document.getElementById(`step${i}`);
            if (step) {
                step.classList.remove('active', 'completed');
            }
        }
        
        // Activate first step
        this.nextStep(1);
        
        this.showToast('Workflow reset', 'info');
    }
}

// Global functions for template inline handlers
window.detectLanguage = function() {
    if (window.audiobookApp) {
        window.audiobookApp.detectLanguage();
    }
};

window.translateText = function() {
    if (window.audiobookApp) {
        window.audiobookApp.translateText();
    }
};

window.analyzeText = function() {
    if (window.audiobookApp) {
        window.audiobookApp.analyzeText();
    }
};

window.previewVoice = function() {
    if (window.audiobookApp) {
        window.audiobookApp.previewVoice();
    }
};

window.generateAudiobook = function() {
    if (window.audiobookApp) {
        window.audiobookApp.generateAudiobook();
    }
};

window.toggleAdvanced = function() {
    if (window.audiobookApp) {
        window.audiobookApp.toggleAdvanced();
    }
};

window.resetWorkflow = function() {
    if (window.audiobookApp) {
        window.audiobookApp.resetWorkflow();
    }
};

window.removeFile = function() {
    if (window.audiobookApp) {
        window.audiobookApp.resetWorkflow();
    }
};

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.audiobookApp = new AudiobookGenerator();
    
    // Check if app data is available from template
    if (window.appData) {
        console.log('App initialized with server data:', window.appData);
    }
});