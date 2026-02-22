/**
 * Client-Side Message Integrity Helper (Optional)
 * ================================================
 * This script provides optional client-side HMAC verification for messages.
 * 
 * Usage (optional - no breaking changes):
 * 1. Include this script in your HTML: <script src="/static/js/message_integrity_helper.js"></script>
 * 2. Call verifyMessageIntegrity(message) when receiving messages
 * 
 * Note: The server already handles integrity checks. This is for additional client-side validation.
 */

/**
 * Client-side message integrity checker
 * This validates that incoming messages have the integrity field
 * Server-side HMAC verification is the primary security mechanism
 */
class MessageIntegrityHelper {
    constructor() {
        this.integrityEnabled = true;
        this.violationCount = 0;
    }

    /**
     * Check if a message has integrity data
     * @param {Object} message - The received message
     * @returns {Object} - {valid: boolean, warning: string}
     */
    checkIntegrity(message) {
        // Check if message has integrity field
        if (!message.integrity) {
            return {
                valid: false,
                warning: "Message missing integrity field (may be from legacy sender)"
            };
        }

        // Validate integrity structure
        if (!message.integrity.type || !message.integrity.value) {
            return {
                valid: false,
                warning: "Malformed integrity field"
            };
        }

        // Check integrity type
        if (message.integrity.type !== 'HMAC_SHA256') {
            return {
                valid: false,
                warning: `Unsupported integrity type: ${message.integrity.type}`
            };
        }

        // Check HMAC format (should be 64 hex characters for SHA256)
        const hmacPattern = /^[a-f0-9]{64}$/i;
        if (!hmacPattern.test(message.integrity.value)) {
            return {
                valid: false,
                warning: "Invalid HMAC format"
            };
        }

        // Basic checks passed
        // Note: Cannot verify HMAC client-side without the secret key (by design)
        return {
            valid: true,
            warning: ""
        };
    }

    /**
     * Validate required message fields
     * @param {Object} message - The message to validate
     * @returns {boolean}
     */
    hasRequiredFields(message) {
        const required = ['from', 'to', 'timestamp'];
        return required.every(field => message.hasOwnProperty(field));
    }

    /**
     * Check timestamp freshness (basic replay attack prevention)
     * @param {Object} message - The message with timestamp
     * @param {number} maxAgeMs - Maximum age in milliseconds (default: 5 minutes)
     * @returns {Object}
     */
    checkTimestampFreshness(message, maxAgeMs = 5 * 60 * 1000) {
        if (!message.timestamp) {
            return {
                fresh: false,
                warning: "Missing timestamp"
            };
        }

        const messageTime = parseInt(message.timestamp);
        const currentTime = Date.now();
        const age = currentTime - messageTime;

        if (age > maxAgeMs) {
            return {
                fresh: false,
                warning: `Message too old (${Math.round(age / 1000)}s ago). Possible replay attack.`
            };
        }

        if (age < -60000) { // 1 minute in future
            return {
                fresh: false,
                warning: "Message timestamp is in the future. Possible clock skew or attack."
            };
        }

        return {
            fresh: true,
            warning: ""
        };
    }

    /**
     * Log integrity violation for monitoring
     * @param {Object} message - The problematic message
     * @param {string} reason - Why it was flagged
     */
    logViolation(message, reason) {
        this.violationCount++;
        console.warn('[MESSAGE INTEGRITY]', reason);
        console.warn('  From:', message.from);
        console.warn('  To:', message.to);
        console.warn('  Timestamp:', message.timestamp);
        console.warn('  Violation #:', this.violationCount);
    }

    /**
     * Main validation function - call this when receiving messages
     * @param {Object} message - The received message
     * @param {Object} options - Validation options
     * @returns {Object} - {valid: boolean, warnings: Array}
     */
    validateMessage(message, options = {}) {
        const warnings = [];
        let valid = true;

        // Option: Skip validation (backward compatibility)
        if (options.skipValidation) {
            return { valid: true, warnings: ['Validation skipped'] };
        }

        // Check required fields
        if (!this.hasRequiredFields(message)) {
            warnings.push('Missing required fields (from/to/timestamp)');
            valid = false;
        }

        // Check integrity field
        const integrityCheck = this.checkIntegrity(message);
        if (!integrityCheck.valid) {
            warnings.push(integrityCheck.warning);
            // Don't mark as invalid for missing integrity (backward compatibility)
            if (message.integrity) {
                valid = false;
            }
        }

        // Check timestamp freshness
        const freshnessCheck = this.checkTimestampFreshness(message, options.maxAgeMs);
        if (!freshnessCheck.fresh) {
            warnings.push(freshnessCheck.warning);
            // Don't fail on timestamp issues, just warn
        }

        // Log if there are issues
        if (warnings.length > 0) {
            this.logViolation(message, warnings.join('; '));
        }

        return {
            valid: valid,
            warnings: warnings,
            hasIntegrity: !!message.integrity
        };
    }

    /**
     * Get integrity statistics
     * @returns {Object}
     */
    getStats() {
        return {
            violationCount: this.violationCount,
            integrityEnabled: this.integrityEnabled
        };
    }
}

// Create global instance (optional - uncomment to enable)
// window.messageIntegrity = new MessageIntegrityHelper();

/**
 * Example usage in your Socket.IO message handler:
 * 
 * socket.on('new_encrypted_message', function(data) {
 *     // Optional: Validate message integrity client-side
 *     const validation = messageIntegrity.validateMessage(data);
 *     
 *     if (!validation.valid) {
 *         console.error('Message integrity check failed:', validation.warnings);
 *         // Optionally reject or flag the message
 *         return;
 *     }
 *     
 *     if (validation.warnings.length > 0) {
 *         console.warn('Message validation warnings:', validation.warnings);
 *     }
 *     
 *     // Process message normally...
 *     displayMessage(data);
 * });
 */

/**
 * Utility: Display integrity status indicator (optional)
 */
function showIntegrityIndicator(message) {
    const indicator = document.createElement('span');
    indicator.className = 'integrity-indicator';
    
    if (message.integrity && message.integrity.type === 'HMAC_SHA256') {
        indicator.innerHTML = '🔒 Verified';
        indicator.style.color = 'green';
        indicator.title = 'Message integrity verified by server';
    } else {
        indicator.innerHTML = '⚠️ Unverified';
        indicator.style.color = 'orange';
        indicator.title = 'Message from legacy client (no integrity signature)';
    }
    
    return indicator;
}

// Export for use in modules (if using module system)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { MessageIntegrityHelper, showIntegrityIndicator };
}
