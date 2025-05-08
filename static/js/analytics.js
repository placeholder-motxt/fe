// Enhanced Google Analytics tracking
window.dataLayer = window.dataLayer || []
function gtag() {
  dataLayer.push(arguments)
}

// Track page views with additional data
function trackPageView(pagePath = window.location.pathname) {
  gtag("event", "page_view", {
    page_path: pagePath,
    page_title: document.title,
  })
}

// Track conversions when a file is successfully converted
function trackConversion(projectName, fileCount, framework) {
  gtag("event", "conversion", {
    event_category: "File Conversion",
    event_label: framework,
    value: fileCount,
    project_name: projectName,
  })
}

// Track user engagement
function trackEngagement(action, category, label = null, value = null) {
  gtag("event", action, {
    event_category: category,
    event_label: label,
    value: value,
  })
}

// Generate a client ID to track unique users without login
function getClientId() {
  // Try to get existing client ID from localStorage
  let clientId = localStorage.getItem("ga_client_id")

  if (!clientId) {
    // Generate a new client ID if none exists
    clientId = `user_${crypto.randomUUID().replace(/-/g, '')}${crypto.randomUUID().replace(/-/g, '')}`
    localStorage.setItem("ga_client_id", clientId)
  }

  return clientId
}

// Set the client ID for all future events
function setClientId() {
  const clientId = getClientId()
  gtag("set", { user_id: clientId })
  return clientId
}

// Track session start
function trackSessionStart() {
  const sessionId = "session_" + Date.now()
  sessionStorage.setItem("ga_session_id", sessionId)
  sessionStorage.setItem("ga_session_start", Date.now().toString())

  gtag("event", "session_start", {
    session_id: sessionId,
    client_id: getClientId(),
  })
}

// Track session duration when page is being unloaded
function trackSessionDuration() {
  const sessionStart = sessionStorage.getItem("ga_session_start")
  if (sessionStart) {
    const duration = (Date.now() - Number.parseInt(sessionStart)) / 1000 // in seconds
    gtag("event", "session_duration", {
      event_category: "Session",
      event_label: "Duration",
      value: Math.round(duration),
    })
  }
}

// Initialize analytics tracking
function initAnalytics() {
  // Set client ID
  setClientId()

  // Track session start
  if (!sessionStorage.getItem("ga_session_id")) {
    trackSessionStart()
  }

  // Track page view
  trackPageView()

  // Track session duration on page unload
  window.addEventListener("beforeunload", trackSessionDuration)
}

// Call this when the page loads
document.addEventListener("DOMContentLoaded", initAnalytics)
