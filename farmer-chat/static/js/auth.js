/**
 * Authentication Helper for ServVia.AI Chatbot
 * Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): 2025-11-19 18:49:31
 * Current User's Login: Raghuraam21
 * 
 * Handles:
 * - User authentication
 * - Medical profile loading
 * - Token management
 */

const API_BASE = 'http://localhost:8000';

// Check if user is logged in
function checkAuth() {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        // Not logged in, redirect to login
        if (window.location.pathname !== '/login/' && 
            window.location.pathname !== '/register/') {
            window.location.href = '/login/';
        }
        return false;
    }
    
    // Verify token is valid
    fetch(`${API_BASE}/api/auth/token/verify/`, {  // ✅ FIXED: Added /api/
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!data.valid) {
            // Token invalid, redirect to login
            console.log('⚠️ Token invalid, clearing and redirecting...');
            localStorage.clear();
            window.location.href = '/login/';
        } else {
            console.log('✅ Token verified successfully');
        }
    })
    .catch(error => {
        console.error('❌ Auth check failed:', error);
        // Don't redirect on network error, user might be offline
    });
    
    return true;
}

// Get authenticated user data
function getUserData() {
    return JSON.parse(localStorage.getItem('user_data') || '{}');
}

// Get access token with Bearer prefix
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Logout user
function logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (refreshToken) {
        fetch(`${API_BASE}/api/auth/logout/`, {  // ✅ FIXED: Added /api/
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        })
        .then(() => {
            localStorage.clear();
            window.location.href = '/login/';
        })
        .catch(() => {
            localStorage.clear();
            window.location.href = '/login/';
        });
    } else {
        localStorage.clear();
        window.location.href = '/login/';
    }
}

// Load medical profile
async function loadMedicalProfile() {
    const token = localStorage.getItem('access_token');
    const userData = getUserData();
    
    if (!userData.email) {
        console.warn('No user email found');
        return null;
    }
    
    try {
        const response = await fetch(
            `${API_BASE}/api/medical/profile/get/?email=${userData.email}`,  // ✅ FIXED: Added /api/
            {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            }
        );
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.profile_exists) {
            console.log('✅ Medical profile loaded');
            return data.profile;
        } else {
            console.log('ℹ️ No medical profile found');
            return null;
        }
    } catch (error) {
        console.error('❌ Failed to load medical profile:', error);
        return null;
    }
}

// Save medical profile
async function saveMedicalProfile(profileData) {
    const token = localStorage.getItem('access_token');
    const userData = getUserData();
    
    if (!userData.email) {
        throw new Error('No user email found');
    }
    
    // Add email to profile data
    profileData.email = userData.email;
    
    try {
        const response = await fetch(
            `${API_BASE}/api/medical/profile/`,  // ✅ FIXED: Added /api/
            {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(profileData)
            }
        );
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save profile');
        }
        
        const data = await response.json();
        
        console.log('✅ Medical profile saved');
        return data.profile;
    } catch (error) {
        console.error('❌ Failed to save medical profile:', error);
        throw error;
    }
}

// Display user info in sidebar
function displayUserInfo() {
    const userData = getUserData();
    const userInfoContainer = document.getElementById('user-info-container');
    
    if (!userInfoContainer || !userData.email) return;
    
    userInfoContainer.innerHTML = `
        <div style="background: #34495e; border-radius: 12px; padding: 15px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 16px;">
                    ${userData.first_name ? userData.first_name[0].toUpperCase() : 'U'}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: white; font-size: 14px;">
                        ${userData.first_name || 'User'} ${userData.last_name || ''}
                    </div>
                    <div style="font-size: 12px; color: #95a5b8;">
                        ${userData.email}
                    </div>
                </div>
            </div>
            <button onclick="showMedicalProfileModal()" 
                    style="width: 100%; padding: 10px; background: #3498db; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px; transition: all 0.2s; margin-bottom: 8px;">
                🏥 Medical Profile
            </button>
            <button onclick="logout()" 
                    style="width: 100%; padding: 10px; background: #e74c3c; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px; transition: all 0.2s;">
                🚪 Logout
            </button>
        </div>
    `;
}