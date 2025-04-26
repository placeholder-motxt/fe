;((window) => {
  // File uploader object to expose functions for testing
  const fileUploader = {
    handleConvert: null,
    validateFile: null,
    processFiles: null,
    showNotification: null,
    handleErrorResponse: null,
    handleSuccessfulConversion: null,
    showConfirmationModal: null,
    hideConfirmationModal: null,
    toggleGroupIdField: null, // Added from second script
    init: null,
  }

  // Global variables
  let uploadedFiles = []
  let classFileCount = 0
  let csrftoken = null

  // DOM elements (will be initialized in init function)
  let dropZone = null
  let fileInput = null
  let fileListSection = null
  let convertBtn = null
  let confirmationModal = null
  let cancelConversionBtn = null
  let confirmConversionBtn = null
  let frameworkConfirmation = null
  let themeConfirmation = null
  let groupIdConfirmation = null // Added from second script
  let projectNameInput = null
  let groupIdInput = null // Added for SpringBoot Group ID
  let groupIdContainer = null // Added container for Group ID field

  // Initialize the application
  function init() {
    // Get DOM elements
    dropZone = document.querySelector(".drop-zone")
    fileInput = document.getElementById("fileInput")
    fileListSection = document.getElementById("fileListSection")
    convertBtn = document.getElementById("convertButton")
    confirmationModal = document.getElementById("confirmationModal")
    cancelConversionBtn = document.getElementById("cancelConversion")
    confirmConversionBtn = document.getElementById("confirmConversion")
    frameworkConfirmation = document.getElementById("frameworkConfirmation")
    themeConfirmation = document.getElementById("themeConfirmation")
    groupIdConfirmation = document.getElementById("groupIdConfirmation") // Get new element
    projectNameInput = document.getElementById("projectName")
    groupIdInput = document.getElementById("groupId") // Get new element (ensure ID exists in HTML)
    groupIdContainer = document.getElementById("group-id-container") // Get new element (ensure ID exists in HTML)

    if (!dropZone || !fileInput || !fileListSection || !convertBtn || !confirmationModal || !groupIdInput || !groupIdContainer || !groupIdConfirmation) {
      console.error("DOM elements not found - skipping initialization. Ensure elements with IDs 'groupId', 'group-id-container', and 'groupIdConfirmation' exist.")
      return
    }

    csrftoken = getCookie("csrftoken")
    uploadedFiles = []
    classFileCount = 0

    initializeEventListeners()
    toggleGroupIdField() // Initial check for group ID field visibility
    handleDarkMode()
  }

  // Initialize event listeners
  function initializeEventListeners() {
    fileListSection.addEventListener("click", handleFileListClick)
    fileInput.addEventListener("change", handleFileInput)
    dropZone.addEventListener("dragover", handleDragOver)
    dropZone.addEventListener("dragleave", handleDragLeave)
    dropZone.addEventListener("drop", handleDrop)
    convertBtn.addEventListener("click", showConfirmationModal)
    cancelConversionBtn.addEventListener("click", hideConfirmationModal)
    confirmConversionBtn.addEventListener("click", handleConvert)

    // Add event listeners for framework selection to toggle Group ID field
    const frameworkOptions = document.querySelectorAll('input[name="framework"]')
    frameworkOptions.forEach((option) => {
      option.addEventListener("change", toggleGroupIdField)
    })

    // Optional: Close modal on outside click (use with caution if it interferes)
    // window.addEventListener("click", (event) => {
    //   if (confirmationModal && event.target == confirmationModal) {
    //     hideConfirmationModal();
    //   }
    // });
  }

  // Toggle group ID field based on selected framework
  function toggleGroupIdField() {
    const springbootSelected = document.getElementById("framework-springboot")?.checked // Use optional chaining for safety

    if (groupIdContainer) { // Check if container exists
        if (springbootSelected) {
            groupIdContainer.classList.remove("hidden")
        } else {
            groupIdContainer.classList.add("hidden")
            if (groupIdInput) groupIdInput.value = "" // Clear input when hidden
        }
    } else {
        console.warn("Group ID container not found. Cannot toggle visibility.");
    }
  }


  // Show confirmation modal
  function showConfirmationModal(e) {
    e?.preventDefault();
  
    if (uploadedFiles.length === 0) {
      showNotification("Please select files to convert.", "error");
      return;
    }
  
    const projectName = projectNameInput.value.trim();
    if (!validateProjectName(projectName)) return;
  
    const frameworkValue = getFrameworkSelection();
    if (frameworkValue === "springboot") {
      if (!validateSpringBootGroupId()) return;
    } else if (groupIdConfirmation) {
      groupIdConfirmation.classList.add("hidden");
    }
  
    const themeValue = getThemeSelection();
    updateConfirmationContent(projectName, frameworkValue, themeValue);
  
    confirmationModal.classList.remove("hidden");
  }
  
  // Helper: Validates the project name.
  function validateProjectName(name) {
    if (!name) {
      showNotification("Please enter a project name.", "error");
      return false;
    }
    if (!/^\w+$/.test(name)) {
      showNotification("Project name can only contain letters, numbers, and underscores.", "error");
      return false;
    }
    return true;
  }
  
  // Helper: Retrieves the selected framework value.
  function getFrameworkSelection() {
    const selected = document.querySelector('input[name="framework"]:checked');
    return selected ? selected.value : "django";
  }
  
  // Helper: Validates the SpringBoot Group ID and updates the confirmation display.
  function validateSpringBootGroupId() {
    const groupId = groupIdInput.value.trim();
    if (!groupId) {
      showNotification("Please enter a Group ID for SpringBoot projects.", "error");
      return false;
    }
    if (!groupId.includes(".")) {
      showNotification("Group ID must contain at least one dot (e.g., com.example)", "error");
      return false;
    }
  
    if (groupIdConfirmation) {
      groupIdConfirmation.classList.remove("hidden");
      const spanElement = groupIdConfirmation.querySelector("span");
      if (spanElement) {
        spanElement.textContent = groupId;
      } else {
        groupIdConfirmation.innerHTML = `Group ID: <span class="font-semibold">${groupId}</span>`;
        console.warn("Could not find specific span in groupIdConfirmation, overwriting innerHTML.");
      }
    }
    return true;
  }
  
  // Helper: Retrieves the selected theme value.
  function getThemeSelection() {
    const themeSelected = document.querySelector('input[name="style-theme"]:checked');
    return themeSelected ? themeSelected.value : "modern";
  }
  
  // Helper: Updates the confirmation modal's content.
  function updateConfirmationContent(projectName, frameworkValue, themeValue) {
    const confirmationMessage = document.getElementById("confirmationMessage");
    if (confirmationMessage) {
      confirmationMessage.textContent = `Are you sure you want to create a project named "${projectName}" in ${capitalize(frameworkValue)}?`;
    }
    if (frameworkConfirmation) {
      frameworkConfirmation.innerHTML = `Framework: <span class="font-semibold">${capitalize(frameworkValue)}</span>`;
    }
    if (themeConfirmation) {
      themeConfirmation.innerHTML = `Theme: <span class="font-semibold">${capitalize(themeValue)}</span>`;
    }
  }
  
  // Simple helper to capitalize a string.
  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

// Helper functions
function validateProjectName(projectName) {
    if (!projectName) {
        showNotification("Please enter a project name.", "error");
        return false;
    }

    if (!/^\w+$/.test(projectName)) {
        showNotification("Project name can only contain letters, numbers, and underscores.", "error");
        return false;
    }
    
    return true;
}

function validateSpringBootGroupId() {
    const groupId = groupIdInput.value.trim();
    let isValid = true;

    if (!groupId) {
        showNotification("Please enter a Group ID for SpringBoot projects.", "error");
        isValid = false;
    } else if (!groupId.includes(".")) {
        showNotification("Group ID must contain at least one dot (e.g., com.example)", "error");
        isValid = false;
    }

    if (isValid) {
        updateGroupIdDisplay(groupId);
        return true;
    }
    return false;
}

function updateGroupIdDisplay(groupId) {
    if (!groupIdConfirmation) return;
    
    groupIdConfirmation.classList.remove("hidden");
    const spanElement = groupIdConfirmation.querySelector("span");
    if (spanElement) {
      // Assignment is now its own statement in the 'if' block
      spanElement.textContent = groupId;
  } else {
      // Fallback assignment remains in the 'else' block
      groupIdConfirmation.innerHTML = `Group ID: <span class="font-semibold">${groupId}</span>`;
      // Optional: Keep the warning if the span *should* always exist
      console.warn("Could not find specific span in groupIdConfirmation, overwriting innerHTML.");
  }
}

function getFrameworkSelection() {
    const selectedFramework = document.querySelector('input[name="framework"]:checked');
    return {
        frameworkValue: selectedFramework?.value || "django",
        selectedFramework
    };
}

function getThemeSelection() {
    const selectedTheme = document.querySelector('input[name="style-theme"]:checked');
    return { themeValue: selectedTheme?.value || "modern" };
}

function updateConfirmationModalContent(projectName, frameworkValue, themeValue) {
    const confirmationMessage = document.getElementById("confirmationMessage");
    if (confirmationMessage) {
        confirmationMessage.textContent = `Are you sure you want to create a project named "${projectName}" in ${capitalize(frameworkValue)}?`;
    }

    updateConfirmationElement(frameworkConfirmation, "Framework", frameworkValue);
    updateConfirmationElement(themeConfirmation, "Theme", themeValue);
}

function updateConfirmationElement(element, label, value) {
    if (element) {
        element.innerHTML = `${label}: <span class="font-semibold">${capitalize(value)}</span>`;
    }
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

  // Hide confirmation modal (original, preferred method)
  function hideConfirmationModal() {
    if (confirmationModal) { // Check if modal exists
        confirmationModal.classList.add("hidden")
    }
  }

  // Handle file list click (for delete buttons)
  function handleFileListClick(e) {
    if (e.target.classList.contains("delete-btn") || e.target.closest(".delete-btn")) { // Handle clicks on span inside button too
      const fileEntry = e.target.closest(".file-entry")
      if(fileEntry) {
          const filename = fileEntry.dataset.filename
          uploadedFiles = uploadedFiles.filter((file) => file.name !== filename)
          updateFileList()
      }
    }
  }

  // Handle file input change
  function handleFileInput(e) {
    processFiles(Array.from(e.target.files))
    e.target.value = "" // Clear the input after selection
  }

  // Handle file drop
  function handleDrop(e) {
    e.preventDefault()
    dropZone.classList.remove("dragover")
    processFiles(Array.from(e.dataTransfer.files))
  }

  // Handle drag over
  function handleDragOver(e) {
    e.preventDefault()
    dropZone.classList.add("dragover")
  }

  // Handle drag leave
  function handleDragLeave(e) {
    // Prevent flickering when dragging over child elements
    if (!dropZone.contains(e.relatedTarget)) {
        dropZone.classList.remove("dragover");
    }
  }

  // Process files
  function processFiles(files) {
    let addedFiles = 0; // Track how many files were actually added in this batch
    files.forEach((file) => {
      // Check if file with the same name already exists
      if (uploadedFiles.some(existingFile => existingFile.name === file.name)) {
          showNotification(`File "${file.name}" has already been added.`, "error");
          return; // Skip this file
      }

      const validationMessage = validateFile(file) // Use current classFileCount
      if (validationMessage) {
        showNotification(validationMessage, "error")
        return // Skip this file
      }
      uploadedFiles.push(file)
      addedFiles++;
    })

    if (addedFiles > 0) {
        updateFileList() // Only update if files were actually added
    }
  }

  // Validate file (adjusted to use current uploadedFiles for class count check)
  function validateFile(file) {
    const isClass = file.name.toLowerCase().endsWith(".class.jet")
    const isSequence = file.name.toLowerCase().endsWith(".sequence.jet")

    if (!isClass && !isSequence) {
      return `Invalid file type: ${file.name}. Only .class.jet and .sequence.jet allowed`
    }

    // Add file size validation (10MB limit)
    const maxSizeInBytes = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSizeInBytes) {
      return `File ${file.name} exceeds the maximum size limit of 10MB`
    }

    // Check class file count based on *currently* uploaded files + the one being added
    if (isClass) {
        const currentClassCount = uploadedFiles.filter(f => f.name.toLowerCase().endsWith(".class.jet")).length;
        if (currentClassCount >= 1) {
            return "Only one .class.jet file is allowed!"
        }
    }

    return null // File is valid
  }


  // Update file list
  function updateFileList() {
    if (!fileListSection) return;

    fileListSection.innerHTML = ""
    classFileCount = 0 // Recalculate count based on the final list

    uploadedFiles.forEach((file) => {
      if (file.name.toLowerCase().endsWith(".class.jet")) classFileCount++
      fileListSection.appendChild(createFileElement(file))
    })

    toggleConvertButton()
  }

  // Create file element *** SVG RESTORED HERE ***
  function createFileElement(file) {
    const fileEntry = document.createElement("div")
    // Added margin-bottom for spacing, kept other layout classes from previous version
    fileEntry.className = "file-entry flex items-center justify-between bg-[var(--hover-tile)] rounded-lg p-4 mb-2"
    fileEntry.dataset.filename = file.name
    // Slightly improved delete button for easier clicking
    fileEntry.innerHTML = `
        <div class="flex items-center space-x-2 overflow-hidden mr-2">
          <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="50" height="50" viewBox="0 0 256 256" xml:space="preserve">
          <g style="stroke: none; stroke-width: 0; stroke-dasharray: none; stroke-linecap: butt; stroke-linejoin: miter; stroke-miterlimit: 10; fill: none; fill-rule: nonzero; opacity: 1;" transform="translate(1.4065934065934016 1.4065934065934016) scale(2.81 2.81)">
            <path d="M 77.474 17.28 L 61.526 1.332 C 60.668 0.473 59.525 0 58.311 0 H 15.742 c -2.508 0 -4.548 2.04 -4.548 4.548 v 80.904 c 0 2.508 2.04 4.548 4.548 4.548 h 58.516 c 2.508 0 4.549 -2.04 4.549 -4.548 V 20.496 C 78.807 19.281 78.333 18.138 77.474 17.28 z M 61.073 5.121 l 12.611 12.612 H 62.35 c -0.704 0 -1.276 -0.573 -1.276 -1.277 V 5.121 z M 74.258 87 H 15.742 c -0.854 0 -1.548 -0.694 -1.548 -1.548 V 4.548 C 14.194 3.694 14.888 3 15.742 3 h 42.332 v 13.456 c 0 2.358 1.918 4.277 4.276 4.277 h 13.457 v 64.719 C 75.807 86.306 75.112 87 74.258 87 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 68.193 33.319 H 41.808 c -0.829 0 -1.5 -0.671 -1.5 -1.5 s 0.671 -1.5 1.5 -1.5 h 26.385 c 0.828 0 1.5 0.671 1.5 1.5 S 69.021 33.319 68.193 33.319 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 34.456 33.319 H 21.807 c -0.829 0 -1.5 -0.671 -1.5 -1.5 s 0.671 -1.5 1.5 -1.5 h 12.649 c 0.829 0 1.5 0.671 1.5 1.5 S 35.285 33.319 34.456 33.319 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 42.298 20.733 H 21.807 c -0.829 0 -1.5 -0.671 -1.5 -1.5 s 0.671 -1.5 1.5 -1.5 h 20.492 c 0.829 0 1.5 0.671 1.5 1.5 S 43.127 20.733 42.298 20.733 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 68.193 44.319 H 21.807 c -0.829 0 -1.5 -0.671 -1.5 -1.5 s 0.671 -1.5 1.5 -1.5 h 46.387 c 0.828 0 1.5 0.671 1.5 1.5 S 69.021 44.319 68.193 44.319 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 48.191 55.319 H 21.807 c -0.829 0 -1.5 -0.672 -1.5 -1.5 s 0.671 -1.5 1.5 -1.5 h 26.385 c 0.828 0 1.5 0.672 1.5 1.5 S 49.02 55.319 48.191 55.319 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 68.193 55.319 H 55.544 c -0.828 0 -1.5 -0.672 -1.5 -1.5 s 0.672 -1.5 1.5 -1.5 h 12.649 c 0.828 0 1.5 0.672 1.5 1.5 S 69.021 55.319 68.193 55.319 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 68.193 66.319 H 21.807 c -0.829 0 -1.5 -0.672 -1.5 -1.5 s 0.671 -1.5 1.5 -1.5 h 46.387 c 0.828 0 1.5 0.672 1.5 1.5 S 69.021 66.319 68.193 66.319 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
            <path d="M 68.193 77.319 H 55.544 c -0.828 0 -1.5 -0.672 -1.5 -1.5 s 0.672 -1.5 1.5 -1.5 h 12.649 c 0.828 0 1.5 0.672 1.5 1.5 S 69.021 77.319 68.193 77.319 z" style="fill: var(--text);" transform=" matrix(1 0 0 1 0 0) " stroke-linecap="round"/>
          </g>
          </svg>
        <span class="font-semibold truncate" style="color: var(--text);" title="${file.name}">${file.name}</span>
        </div>
        <button type="button" class="delete-btn flex-shrink-0 p-1 rounded hover:bg-red-200 dark:hover:bg-red-800" aria-label="Remove ${file.name}">
          <span style="color:var(--text); font-size: 1.5em; line-height: 1;">&times;</span>
        </button>
          `
    return fileEntry
  }

  // Toggle convert button visibility
  function toggleConvertButton() {
    const hasFiles = uploadedFiles.length > 0
    fileListSection.style.display = hasFiles ? "block" : "none"
    convertBtn.style.display = hasFiles ? "inline-block" : "none"
  }

  // Handle convert action
  async function handleConvert() {
    if (!confirmConversionBtn || !convertBtn) return; // Safety check

    // Add loading class to the confirm button
    confirmConversionBtn.classList.add("loading")
    confirmConversionBtn.disabled = true; // Disable button while loading

    hideConfirmationModal()

    // Also add loading class to the main convert button for visual feedback
    convertBtn.classList.add("loading")
    convertBtn.disabled = true; // Disable button while loading

    const formData = new FormData()
    uploadedFiles.forEach((file) => formData.append("files", file))

    // Add project name to form data
    const projectName = projectNameInput.value.trim()
    formData.append("project_name", projectName)

    // Add style theme to form data
    const selectedStyle = document.querySelector('input[name="style-theme"]:checked')
    formData.append("style-theme", selectedStyle ? selectedStyle.value : "modern")

    // Add framework to form data
    const selectedFramework = document.querySelector('input[name="framework"]:checked')
    const frameworkValue = selectedFramework ? selectedFramework.value : "django"
    formData.append("framework", frameworkValue)

    // --- Add group_id if SpringBoot is selected (Merged Logic) ---
    if (frameworkValue === "springboot") {
      const groupId = groupIdInput.value.trim()
      // Group ID should have been validated already in showConfirmationModal,
      // but a final check here might be wise depending on application flow.
      if (groupId) {
        formData.append("group_id", groupId)
      } else {
         // This case should ideally not happen if validation in modal worked
         showNotification("Group ID is missing for SpringBoot project.", "error");
         // Re-enable buttons and remove loading state
         convertBtn.classList.remove("loading");
         convertBtn.disabled = false;
         confirmConversionBtn.classList.remove("loading");
         confirmConversionBtn.disabled = false;
         return; // Stop conversion
      }
    }
    // --- End Group ID logic ---

    try {
      const response = await fetch("/convert_page/", {
        method: "POST",
        headers: { "X-CSRFToken": csrftoken },
        body: formData,
        credentials: "same-origin",
      })

      if (response.ok) {
        await handleSuccessfulConversion(response)
      } else {
        await handleErrorResponse(response)
      }
    } catch (error) {
      console.error("Network error during conversion:", error); // Log error details
      const errorMessage = error.message ? `Network error: ${error.message}` : "Network error - Check your connection"
      showNotification(errorMessage, "error")
    } finally {
      // Remove loading class and re-enable both buttons regardless of success/failure
      convertBtn.classList.remove("loading")
      convertBtn.disabled = false;
      confirmConversionBtn.classList.remove("loading")
      confirmConversionBtn.disabled = false;
    }
  }

  // Handle successful conversion and download
  async function handleSuccessfulConversion(response) {
    try {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.style.display = 'none'; // Hide the link
      a.href = url
      const projectName = projectNameInput.value.trim() || "converted_project" // Fallback name
      a.download = `${projectName}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      showNotification("Files converted and downloaded successfully!", "success")
      resetAfterConversion()
    } catch (error) {
      console.error("Error processing download:", error); // Log error details
      const errorMessage = error.message ? `Error processing downloaded file: ${error.message}` : "Error processing downloaded file"
      showNotification(errorMessage, "error")
    }
  }

  // Handle error response from the server
  async function handleErrorResponse(response) {
    let message = `Conversion failed (Status: ${response.status})`
    const contentType = response.headers.get("content-type") || ""

    try {
        if (contentType.includes("application/json")) {
          const errorData = await response.json()
          message = errorData.error || errorData.detail || JSON.stringify(errorData) // Provide more detail if possible
        } else {
          const textResponse = await response.text();
          message = textResponse || message; // Use text response if available
        }
    } catch (e) {
        console.error("Error parsing error response:", e);
        message = `Conversion failed (Status: ${response.status}) and error response could not be parsed.`
    }


    showNotification(`Error: ${message}`, "error")
  }

  // Show notification message
  function showNotification(message, type = "success") {
    const notification = document.getElementById("notification")
    const messageElement = document.getElementById("notificationMessage")

    if (!notification || !messageElement) {
        console.error("Notification elements not found in the DOM.");
        alert(`${type.toUpperCase()}: ${message}`); // Fallback to alert
        return;
    }

    messageElement.textContent = message
    // Clear existing type classes
    notification.classList.remove('bg-red-100', 'text-red-800', 'bg-green-100', 'text-green-800');
    // Add new type classes
    notification.classList.add(
        type === "error" ? "bg-red-100" : "bg-green-100",
        type === "error" ? "text-red-800" : "text-green-800"
    )
    notification.classList.remove("hidden")

    // Clear previous timeouts if any
    if (notification.timeoutId) {
        clearTimeout(notification.timeoutId);
    }

    // Set new timeout
    notification.timeoutId = setTimeout(() => {
      notification.classList.add("hidden")
      notification.timeoutId = null; // Clear the stored timeout ID
    }, 5000)
  }

  // Reset state after successful conversion
  function resetAfterConversion() {
    uploadedFiles = []
    if (projectNameInput) projectNameInput.value = "" // Optionally clear project name
    if (groupIdInput) groupIdInput.value = "" // Clear group ID
    // Optionally reset framework/theme selection or leave as is
    updateFileList()
    toggleGroupIdField(); // Ensure Group ID field visibility is correct after reset
  }

  // Get CSRF cookie value
  function getCookie(name) {
    let cookieValue = null
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";")
      for (const cookie of cookies) {
        const trimmed = cookie.trim()
        // Does the cookie string begin with the name we want?
        if (trimmed.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(trimmed.substring(name.length + 1))
          break
        }
      }
    }
    return cookieValue
  }

  // Handle dark mode toggle and persistence
  function handleDarkMode() {
    const themeToggle = document.getElementById("light-switch")
    const htmlElement = document.documentElement

    if (!themeToggle) return // Exit if toggle not found

    // Function to apply theme based on toggle state and localStorage
    const applyTheme = () => {
        const storedTheme = localStorage.getItem("theme");
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (storedTheme === "dark" || (!storedTheme && prefersDark)) {
            htmlElement.setAttribute("data-theme", "dark");
            themeToggle.checked = true;
        } else {
            // Default to light if no stored theme and no dark preference, or if stored theme is light
            htmlElement.setAttribute("data-theme", "light");
            themeToggle.checked = false;
             // Ensure 'dark' class is removed if switching to light
             // Although data-theme is preferred, some styles might rely on the class
            htmlElement.classList.remove("dark");
        }
    }

    // Apply theme on initial load
    applyTheme();

    // Add listener for toggle changes
    themeToggle.addEventListener("change", () => {
      if (themeToggle.checked) {
        htmlElement.setAttribute("data-theme", "dark")
        localStorage.setItem("theme", "dark")
      } else {
        htmlElement.setAttribute("data-theme", "light")
        localStorage.setItem("theme", "light")
        htmlElement.classList.remove("dark") // Explicitly remove dark class if using it
      }
    })

     // Optional: Listen for system theme changes if you want the toggle to reflect system preference changes
     window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
  }

  // Initialize on DOM content loaded
  document.addEventListener("DOMContentLoaded", init)

  // Expose functions for testing or external use
  fileUploader.handleConvert = handleConvert
  fileUploader.validateFile = validateFile
  fileUploader.processFiles = processFiles
  fileUploader.showNotification = showNotification
  fileUploader.handleErrorResponse = handleErrorResponse
  fileUploader.handleSuccessfulConversion = handleSuccessfulConversion
  fileUploader.showConfirmationModal = showConfirmationModal
  fileUploader.hideConfirmationModal = hideConfirmationModal
  fileUploader.toggleGroupIdField = toggleGroupIdField // Expose the new function
  fileUploader.init = init // Expose init

  // Make fileUploader available globally (optional, depends on usage)
  window.fileUploader = fileUploader;

  // Support for Node.js environment testing (if needed)
  if (typeof module !== "undefined" && module.exports) {
    module.exports = fileUploader
  }

})(window);