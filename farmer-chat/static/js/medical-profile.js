/**
 * Medical Profile Collection & Management
 * Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 17:02:22
 * Current User's Login: Raghuraam21
 * 
 * Features:
 * - Medical history collection
 * - AES-256 encrypted storage
 * - Condition tracking (diabetes, hypertension, etc.)
 * - Medication & allergy management
 */


// Show medical profile modal
async function showMedicalProfileModal() {
    // Load current profile
    currentMedicalProfile = await loadMedicalProfile();
    
    // Create modal HTML
    const modalHTML = createMedicalProfileModal();
    
    // Add modal to page
    let modalContainer = document.getElementById('medical-profile-modal');
    if (!modalContainer) {
        modalContainer = document.createElement('div');
        modalContainer.id = 'medical-profile-modal';
        document.body.appendChild(modalContainer);
    }
    
    modalContainer.innerHTML = modalHTML;
    
    // Populate form if profile exists
    if (currentMedicalProfile) {
        populateMedicalForm(currentMedicalProfile);
    }
    
    // Show modal
    document.getElementById('medical-modal-overlay').style.display = 'flex';
}

// Create modal HTML
function createMedicalProfileModal() {
    return `
        <div id="medical-modal-overlay" style="
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: 9999;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        ">
            <div style="
                background: #2c3e50;
                border-radius: 20px;
                width: 90%;
                max-width: 600px;
                max-height: 90vh;
                overflow-y: auto;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
                animation: slideUp 0.3s ease-out;
            ">
                <div style="
                    padding: 30px;
                    border-bottom: 2px solid #34495e;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <h2 style="color: white; font-size: 24px; font-weight: 700; margin: 0;">
                        🏥 Your Medical Profile
                    </h2>
                    <button onclick="closeMedicalProfileModal()" style="
                        background: none;
                        border: none;
                        color: white;
                        font-size: 28px;
                        cursor: pointer;
                        width: 40px;
                        height: 40px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        border-radius: 50%;
                        transition: background 0.2s;
                    ">×</button>
                </div>
                
                <div style="padding: 30px;">
                    <div style="
                        background: #f0f9ff;
                        border: 2px solid #0ea5e9;
                        border-radius: 12px;
                        padding: 15px;
                        margin-bottom: 25px;
                    ">
                        <p style="
                            color: #0369a1;
                            font-size: 13px;
                            font-weight: 600;
                            margin: 0;
                            text-align: center;
                        ">
                            🔒 Your data is encrypted with AES-256 & HIPAA compliant
                        </p>
                    </div>
                    
                    <form id="medical-profile-form" onsubmit="saveMedicalProfileForm(event)">
                        <!-- Medical Conditions -->
                        <div style="margin-bottom: 25px;">
                            <h3 style="color: white; font-size: 18px; margin-bottom: 15px;">
                                Medical Conditions
                            </h3>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="has_diabetes" name="has_diabetes" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    I have Diabetes
                                </span>
                            </label>
                            
                            <div id="diabetes-type-section" style="
                                display: none;
                                margin-left: 32px;
                                margin-bottom: 12px;
                            ">
                                <select id="diabetes_type" name="diabetes_type" style="
                                    width: 100%;
                                    padding: 12px;
                                    border-radius: 8px;
                                    border: none;
                                    background: #4a5f7f;
                                    color: white;
                                    font-size: 14px;
                                ">
                                    <option value="">Select Type</option>
                                    <option value="type1">Type 1 Diabetes</option>
                                    <option value="type2">Type 2 Diabetes</option>
                                    <option value="gestational">Gestational Diabetes</option>
                                </select>
                            </div>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="has_hypertension" name="has_hypertension" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    I have Hypertension (High Blood Pressure)
                                </span>
                            </label>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="has_heart_disease" name="has_heart_disease" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    I have Heart Disease
                                </span>
                            </label>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="has_kidney_disease" name="has_kidney_disease" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    I have Kidney Disease
                                </span>
                            </label>
                        </div>
                        
                        <!-- Pregnancy & Breastfeeding -->
                        <div style="margin-bottom: 25px;">
                            <h3 style="color: white; font-size: 18px; margin-bottom: 15px;">
                                Pregnancy & Breastfeeding
                            </h3>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="is_pregnant" name="is_pregnant" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    I am currently pregnant
                                </span>
                            </label>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="is_breastfeeding" name="is_breastfeeding" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    I am currently breastfeeding
                                </span>
                            </label>
                        </div>
                        
                        <!-- Allergies -->
                        <div style="margin-bottom: 25px;">
                            <h3 style="color: white; font-size: 18px; margin-bottom: 15px;">
                                Allergies
                            </h3>
                            
                            <textarea id="allergies" name="allergies" placeholder="Enter allergies (comma-separated): e.g., peanuts, shellfish, penicillin" style="
                                width: 100%;
                                padding: 15px;
                                border-radius: 10px;
                                border: none;
                                background: #34495e;
                                color: white;
                                font-size: 14px;
                                resize: vertical;
                                min-height: 80px;
                                font-family: inherit;
                            "></textarea>
                            <small style="color: #95a5b8; font-size: 12px; display: block; margin-top: 8px;">
                                Separate multiple allergies with commas
                            </small>
                        </div>
                        
                        <!-- Current Medications -->
                        <div style="margin-bottom: 25px;">
                            <h3 style="color: white; font-size: 18px; margin-bottom: 15px;">
                                Current Medications
                            </h3>
                            
                            <textarea id="current_medications" name="current_medications" placeholder="Enter medications (comma-separated): e.g., metformin, lisinopril" style="
                                width: 100%;
                                padding: 15px;
                                border-radius: 10px;
                                border: none;
                                background: #34495e;
                                color: white;
                                font-size: 14px;
                                resize: vertical;
                                min-height: 80px;
                                font-family: inherit;
                            "></textarea>
                            <small style="color: #95a5b8; font-size: 12px; display: block; margin-top: 8px;">
                                Separate multiple medications with commas
                            </small>
                        </div>
                        
                        <!-- Dietary Restrictions -->
                        <div style="margin-bottom: 25px;">
                            <h3 style="color: white; font-size: 18px; margin-bottom: 15px;">
                                Dietary Restrictions
                            </h3>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="is_vegetarian" name="is_vegetarian" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    Vegetarian
                                </span>
                            </label>
                            
                            <label style="
                                display: flex;
                                align-items: center;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 12px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="is_vegan" name="is_vegan" style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                ">
                                <span style="color: white; font-weight: 500;">
                                    Vegan
                                </span>
                            </label>
                        </div>
                        
                        <!-- Consent -->
                        <div style="margin-bottom: 25px;">
                            <label style="
                                display: flex;
                                align-items: start;
                                gap: 12px;
                                background: #34495e;
                                padding: 15px;
                                border-radius: 10px;
                                cursor: pointer;
                            ">
                                <input type="checkbox" id="consent_given" name="consent_given" required style="
                                    width: 20px;
                                    height: 20px;
                                    cursor: pointer;
                                    margin-top: 2px;
                                ">
                                <span style="color: white; font-size: 13px; line-height: 1.6;">
                                    I consent to storing my medical information securely for personalized healthcare recommendations. My data will be encrypted and handled according to HIPAA regulations.
                                </span>
                            </label>
                        </div>
                        
                        <!-- Save Button -->
                        <button type="submit" style="
                            width: 100%;
                            padding: 16px;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            border: none;
                            border-radius: 12px;
                            font-weight: 700;
                            font-size: 16px;
                            cursor: pointer;
                            transition: all 0.3s;
                        ">
                            💾 Save Medical Profile
                        </button>
                    </form>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
    `;
}

// Toggle diabetes type dropdown
document.addEventListener('change', function(e) {
    if (e.target.id === 'has_diabetes') {
        const typeSection = document.getElementById('diabetes-type-section');
        if (e.target.checked) {
            typeSection.style.display = 'block';
        } else {
            typeSection.style.display = 'none';
            document.getElementById('diabetes_type').value = '';
        }
    }
});

// Populate form with existing profile data
function populateMedicalForm(profile) {
    // Checkboxes
    document.getElementById('has_diabetes').checked = profile.has_diabetes || false;
    document.getElementById('has_hypertension').checked = profile.has_hypertension || false;
    document.getElementById('has_heart_disease').checked = profile.has_heart_disease || false;
    document.getElementById('has_kidney_disease').checked = profile.has_kidney_disease || false;
    document.getElementById('is_pregnant').checked = profile.is_pregnant || false;
    document.getElementById('is_breastfeeding').checked = profile.is_breastfeeding || false;
    document.getElementById('is_vegetarian').checked = profile.is_vegetarian || false;
    document.getElementById('is_vegan').checked = profile.is_vegan || false;
    document.getElementById('consent_given').checked = profile.consent_given || false;
    
    // Diabetes type
    if (profile.has_diabetes && profile.diabetes_type) {
        document.getElementById('diabetes-type-section').style.display = 'block';
        document.getElementById('diabetes_type').value = profile.diabetes_type;
    }
    
    // Text fields
    if (profile.allergies && Array.isArray(profile.allergies)) {
        document.getElementById('allergies').value = profile.allergies.join(', ');
    }
    
    if (profile.current_medications && Array.isArray(profile.current_medications)) {
        document.getElementById('current_medications').value = profile.current_medications.join(', ');
    }
}

// Save medical profile form
async function saveMedicalProfileForm(event) {
    event.preventDefault();
    
    const form = document.getElementById('medical-profile-form');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    // Disable button
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    
    try {
        // Collect form data
        const profileData = {
            has_diabetes: document.getElementById('has_diabetes').checked,
            diabetes_type: document.getElementById('diabetes_type').value || null,
            has_hypertension: document.getElementById('has_hypertension').checked,
            has_heart_disease: document.getElementById('has_heart_disease').checked,
            has_kidney_disease: document.getElementById('has_kidney_disease').checked,
            is_pregnant: document.getElementById('is_pregnant').checked,
            is_breastfeeding: document.getElementById('is_breastfeeding').checked,
            is_vegetarian: document.getElementById('is_vegetarian').checked,
            is_vegan: document.getElementById('is_vegan').checked,
            consent_given: document.getElementById('consent_given').checked,
            allergies: document.getElementById('allergies').value
                .split(',')
                .map(a => a.trim())
                .filter(a => a.length > 0),
            current_medications: document.getElementById('current_medications').value
                .split(',')
                .map(m => m.trim())
                .filter(m => m.length > 0)
        };
        
        // Save profile
        const savedProfile = await saveMedicalProfile(profileData);
        currentMedicalProfile = savedProfile;
        
        // Show success message
        alert('✅ Medical profile saved successfully!\n\nYour information is encrypted and secure.');
        
        // Close modal
        closeMedicalProfileModal();
        
    } catch (error) {
        console.error('Failed to save profile:', error);
        alert('❌ Failed to save medical profile. Please try again.');
        
        // Re-enable button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '💾 Save Medical Profile';
    }
}

// Close modal
function closeMedicalProfileModal() {
    const overlay = document.getElementById('medical-modal-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}