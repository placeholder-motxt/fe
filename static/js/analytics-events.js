document.addEventListener("DOMContentLoaded", () => {
    // Mock trackEngagement and trackConversion if they are not defined (e.g., in a testing environment)
    if (typeof trackEngagement !== "function") {
      window.trackEngagement = (event, category, label, value) => {
        console.log("trackEngagement:", event, category, label, value)
      }
    }

    if (typeof trackConversion !== "function") {
      window.trackConversion = (projectName, fileCount, framework) => {
        console.log("trackConversion:", projectName, fileCount, framework)
      }
    }

    // Track file uploads
    const fileInput = document.getElementById("fileInput")
    if (fileInput) {
      fileInput.addEventListener("change", (e) => {
        if (typeof trackEngagement === "function" && e.target.files.length > 0) {
          trackEngagement("file_upload", "User Action", "Files", e.target.files.length)
        }
      })
    }

    // Track framework selection
    const frameworkOptions = document.querySelectorAll('input[name="framework"]')
    frameworkOptions.forEach((option) => {
      option.addEventListener("change", function () {
        if (typeof trackEngagement === "function") {
          trackEngagement("framework_selection", "User Preference", this.value)

          // Track specific framework counts
          if (this.value === "django") {
            trackEngagement("framework_django", "Framework Count", "Django Selected", 1)
          } else if (this.value === "spring") {
            trackEngagement("framework_spring", "Framework Count", "SpringBoot Selected", 1)
          }
        }
      })
    })

    // Track theme selection
    const themeOptions = document.querySelectorAll('input[name="style-theme"]')
    themeOptions.forEach((option) => {
      option.addEventListener("change", function () {
        if (typeof trackEngagement === "function") {
          trackEngagement("theme_selection", "User Preference", this.value)
        }
      })
    })

    // Track successful conversions
    const originalHandleSuccessfulConversion = window.fileUploader?.handleSuccessfulConversion
    if (window.fileUploader && originalHandleSuccessfulConversion) {
      window.fileUploader.handleSuccessfulConversion = async function (response) {
        // Call the original function
        await originalHandleSuccessfulConversion.call(this, response)

        // Track the conversion
        if (typeof trackConversion === "function") {
          const projectName = document.getElementById("projectName")?.value || "unknown"
          const fileCount = window.uploadedFiles?.length || 0
          const framework = document.querySelector('input[name="framework"]:checked')?.value || "django"

          trackConversion(projectName, fileCount, framework)
        }
      }
    }

    // Track failed conversions
    const originalHandleErrorResponse = window.fileUploader?.handleErrorResponse
    if (window.fileUploader && originalHandleErrorResponse) {
      window.fileUploader.handleErrorResponse = async function (response) {
        // Call the original function
        await originalHandleErrorResponse.call(this, response)

        // Additional tracking for detailed error analytics
        if (typeof trackEngagement === "function") {
          const framework = document.querySelector('input[name="framework"]:checked')?.value || "django"
          const errorCategory = response.status >= 500 ? "Server Error" : "Client Error"

          trackEngagement("conversion_error_details", errorCategory, `${framework} - Status ${response.status}`, 1)
        }
      }
    }
  })