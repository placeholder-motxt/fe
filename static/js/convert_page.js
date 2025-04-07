;((window) => {
    const fileUploader = {
      handleConvert: null,
      validateFile: null,
      processFiles: null,
      showNotification: null,
      handleErrorResponse: null,
      handleSuccessfulConversion: null,
    }
  
    document.addEventListener("DOMContentLoaded", () => {
      const dropZone = document.querySelector(".drop-zone")
      const fileInput = document.getElementById("fileInput")
      const fileListSection = document.getElementById("fileListSection")
      const convertBtn = document.getElementById("convertButton")
      const confirmationModal = document.getElementById("confirmationModal")
      const cancelConversionBtn = document.getElementById("cancelConversion")
      const confirmConversionBtn = document.getElementById("confirmConversion")
  
      if (!dropZone || !fileInput || !fileListSection || !convertBtn || !confirmationModal) {
        console.error("DOM elements not found - skipping initialization")
        return
      }
  
      const csrftoken = getCookie("csrftoken")
      let uploadedFiles = []
      let classFileCount = 0
  
      initializeEventListeners()
  
      function initializeEventListeners() {
        fileListSection.addEventListener("click", handleFileListClick)
        fileInput.addEventListener("change", handleFileInput)
        dropZone.addEventListener("dragover", handleDragOver)
        dropZone.addEventListener("dragleave", handleDragLeave)
        dropZone.addEventListener("drop", handleDrop)
        convertBtn.addEventListener("click", showConfirmationModal)
        cancelConversionBtn.addEventListener("click", hideConfirmationModal)
        confirmConversionBtn.addEventListener("click", handleConvert)
      }
  
      function showConfirmationModal(e) {
        e.preventDefault()
        if (uploadedFiles.length === 0) {
          showNotification("Please select files to convert.", "error")
          return
        }
  
        // Get project name
        const projectName = document.getElementById("projectName").value.trim()
  
        // Validate project name is not empty
        if (!projectName) {
          showNotification("Please enter a project name.", "error")
          return
        }
  
        // Validate project name format (alphanumeric and underscore only)
        const projectNameRegex = /^[a-zA-Z0-9_]+$/
        if (!projectNameRegex.test(projectName)) {
          showNotification("Project name can only contain letters, numbers, and underscores.", "error")
          return
        }
  
        // Update confirmation message with project name
        const confirmationMessage = document.getElementById("confirmationMessage")
        if (confirmationMessage) {
          confirmationMessage.textContent = `Are you sure you want to create a project named "${projectName}" in Django?`
        }
  
        confirmationModal.classList.remove("hidden")
      }
  
      function hideConfirmationModal() {
        confirmationModal.classList.add("hidden")
      }
  
      function handleFileListClick(e) {
        if (e.target.classList.contains("delete-btn")) {
          const filename = e.target.closest(".file-entry").dataset.filename
          uploadedFiles = uploadedFiles.filter((file) => file.name !== filename)
          updateFileList()
        }
      }
  
      function handleFileInput(e) {
        processFiles(Array.from(e.target.files))
        e.target.value = ""
      }
  
      function handleDrop(e) {
        e.preventDefault()
        dropZone.classList.remove("dragover")
        processFiles(Array.from(e.dataTransfer.files))
      }
  
      function handleDragOver(e) {
        e.preventDefault()
        dropZone.classList.add("dragover")
      }
  
      function handleDragLeave() {
        dropZone.classList.remove("dragover")
      }
  
      function processFiles(files) {
        files.forEach((file) => {
          const validationMessage = validateFile(file)
          if (validationMessage) {
            showNotification(validationMessage, "error")
            return
          }
          uploadedFiles.push(file)
        })
        updateFileList()
      }
  
      function validateFile(file) {
        const isClass = file.name.toLowerCase().endsWith(".class.jet")
        const isSequence = file.name.toLowerCase().endsWith(".sequence.jet")
  
        if (!isClass && !isSequence) {
          return `Invalid file type: ${file.name}. Only .class.jet and .sequence.jet allowed`
        }
  
        if (isClass) {
          classFileCount++
          if (classFileCount > 1) {
            classFileCount--
            return "Only one .class.jet file is allowed!"
          }
        }
        return null
      }
  
      function updateFileList() {
        fileListSection.innerHTML = ""
        classFileCount = 0
  
        uploadedFiles.forEach((file) => {
          if (file.name.toLowerCase().endsWith(".class.jet")) classFileCount++
          fileListSection.appendChild(createFileElement(file))
        })
  
        toggleConvertButton()
      }
  
      function createFileElement(file) {
        const fileEntry = document.createElement("div")
        fileEntry.className = "file-entry flex items-center justify-between bg-[var(--hover-tile)] rounded-lg p-4"
        fileEntry.dataset.filename = file.name
        fileEntry.innerHTML = `
            <div class="flex items-center space-x-2">
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
            <span class="font-semibold" style="color: var(--text);">${file.name}</span>
            </div>
            <button class="delete-btn">
              <span style="color:var(--text)">×</span>
            </button>
              `
        return fileEntry
      }
  
      function toggleConvertButton() {
        const hasFiles = uploadedFiles.length > 0
        fileListSection.style.display = hasFiles ? "block" : "none"
        convertBtn.style.display = hasFiles ? "inline-block" : "none"
      }
  
      async function handleConvert() {
        // Add loading class to the confirm button
        confirmConversionBtn.classList.add("loading")
  
        hideConfirmationModal()
  
        // Also add loading class to the main convert button for visual feedback
        convertBtn.classList.add("loading")
  
        const formData = new FormData()
        uploadedFiles.forEach((file) => formData.append("files", file))
  
        // Add project name to form data
        const projectName = document.getElementById("projectName").value.trim()
        formData.append("project_name", projectName)
  
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
          showNotification("Network error - Check your connection", "error")
        } finally {
          // Remove loading class from both buttons
          convertBtn.classList.remove("loading")
          confirmConversionBtn.classList.remove("loading")
        }
      }
  
      async function handleSuccessfulConversion(response) {
        try {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement("a")
          a.href = url
          const projectName = document.getElementById("projectName").value.trim()
          a.download = `${projectName}.zip`
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
          showNotification("Files converted and downloaded successfully!", "success")
          resetAfterConversion()
        } catch (error) {
          showNotification("Error processing downloaded file", "error")
        }
      }
  
      async function handleErrorResponse(response) {
        let message = "Conversion failed"
        const contentType = response.headers.get("content-type") || ""
  
        if (contentType.includes("application/json")) {
          const errorData = await response.json()
          message = errorData.error || errorData.detail || message
        } else {
          message = await response.text()
        }
  
        showNotification(`Error ${response.status}: ${message}`, "error")
      }
  
      function showNotification(message, type = "success") {
        const notification = document.getElementById("notification")
        const messageElement = document.getElementById("notificationMessage")
  
        messageElement.textContent = message
        notification.className = `
                  fixed top-4 right-4 max-w-md p-4 rounded-lg shadow-lg 
                  ${type === "error" ? "bg-red-100 text-red-800" : "bg-green-100 text-green-800"}
                  transition-all
              `
  
        notification.classList.remove("hidden")
        setTimeout(() => {
          notification.classList.add("hidden")
        }, 5000)
      }
  
      function resetAfterConversion() {
        uploadedFiles = []
        updateFileList()
      }
  
      function getCookie(name) {
        let cookieValue = null
        if (document.cookie && document.cookie !== "") {
          const cookies = document.cookie.split(";")
          for (const cookie of cookies) {
            const trimmed = cookie.trim()
            if (trimmed.startsWith(name + "=")) {
              cookieValue = decodeURIComponent(trimmed.substring(name.length + 1))
              break
            }
          }
        }
        return cookieValue
      }
  
      function handleDarkMode() {
        const themeToggle = document.getElementById("light-switch")
        const htmlElement = document.documentElement
  
        // Load stored theme
        if (localStorage.getItem("theme") === "dark") {
          htmlElement.setAttribute("data-theme", "dark")
          themeToggle.checked = true
          
        } else if (localStorage.getItem("theme") === "light") {
          htmlElement.setAttribute("data-theme", "light")
          themeToggle.checked = false
          
        }
  
        // Toggle theme
        themeToggle.addEventListener("change", () => {
          if (themeToggle.checked) {
            htmlElement.setAttribute("data-theme", "dark")
            localStorage.setItem("theme", "dark")
            
          } else {
            htmlElement.setAttribute("data-theme", "light")
            localStorage.setItem("theme", "light")
            htmlElement.classList.remove("dark")
            
          }
        })
      }
  
      handleDarkMode()
  
      // Expose functions for testing
      fileUploader.handleConvert = handleConvert
      fileUploader.validateFile = validateFile
      fileUploader.processFiles = processFiles
      fileUploader.showNotification = showNotification
      fileUploader.handleErrorResponse = handleErrorResponse
      fileUploader.handleSuccessfulConversion = handleSuccessfulConversion
      fileUploader.showConfirmationModal = showConfirmationModal
      fileUploader.hideConfirmationModal = hideConfirmationModal
  
      if (typeof module !== "undefined" && module.exports) {
        module.exports = fileUploader
      } else {
        window.fileUploader = fileUploader
      }
    })
  })(window)
  
  