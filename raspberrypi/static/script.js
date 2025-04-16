let currentMode = "sentry";

function toggleMode(mode) {
    currentMode = mode;
    updateUI();
    
    fetch(`/toggle_mode/${mode}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById("status").textContent = `Mode: ${mode.toUpperCase()}`;
        })
        .catch(error => {
            document.getElementById("status").textContent = "Error changing mode";
            console.error("Error:", error);
        });
}

function updateUI() {
    // Highlight active mode button
    document.querySelectorAll("button").forEach(button => {
        if (button.textContent.toLowerCase().includes(currentMode)) {
            button.classList.add("active");
        } else {
            button.classList.remove("active");
        }
    });
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("status").textContent = "Status: Connected";
    updateUI();
});

let faceCheckInterval;

function startFaceDetectionUpdates() {
    faceCheckInterval = setInterval(() => {
        fetch('/face_status')
            .then(response => response.json())
            .then(data => {
                const statusElement = document.getElementById("faceStatus");
                if (data.face_detected) {
                    statusElement.innerHTML = `Face Detected<br>
                        X: ${data.coordinates[0]}<br>
                        Y: ${data.coordinates[1]}`;
                    statusElement.style.backgroundColor = "#4CAF50";
                } else {
                    statusElement.innerHTML = "No Face Detected";
                    statusElement.style.backgroundColor = "#f44336";
                }
            })
            .catch(error => {
                console.error("Face status error:", error);
            });
    }, 500);  // Update every 0.5 seconds
}

// Update DOMContentLoaded event
document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("status").textContent = "Status: Connected";
    updateUI();
    startFaceDetectionUpdates();
});
