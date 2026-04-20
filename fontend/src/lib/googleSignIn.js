const GOOGLE_IDENTITY_SCRIPT_SRC = 'https://accounts.google.com/gsi/client'

function sanitizeEnvValue(value) {
  return String(value || '')
    .trim()
    .replace(/^['\"]|['\"]$/g, '')
}

function getGoogleClientId() {
  return sanitizeEnvValue(import.meta.env.VITE_GOOGLE_CLIENT_ID)
}

function loadGoogleIdentityScript() {
  if (window.google?.accounts?.id) {
    return Promise.resolve()
  }

  const existingScript = document.querySelector(`script[src="${GOOGLE_IDENTITY_SCRIPT_SRC}"]`)
  if (existingScript) {
    return new Promise((resolve, reject) => {
      existingScript.addEventListener('load', () => resolve(), { once: true })
      existingScript.addEventListener('error', () => reject(new Error('Failed to load Google Identity script.')), { once: true })
    })
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = GOOGLE_IDENTITY_SCRIPT_SRC
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load Google Identity script.'))
    document.head.appendChild(script)
  })
}

export async function signInWithGoogleIdToken() {
  const clientId = getGoogleClientId()
  if (!clientId) {
    throw new Error('Google login requires a configured Client ID. Please set VITE_GOOGLE_CLIENT_ID in .env.local')
  }

  await loadGoogleIdentityScript()

  return new Promise((resolve, reject) => {
    let handled = false

    const cleanup = (root) => {
      if (root && root.parentNode) {
        root.parentNode.removeChild(root)
      }
    }

    const finishWithError = (root, message) => {
      if (handled) {
        return
      }
      handled = true
      cleanup(root)
      reject(new Error(message))
    }

    const overlay = document.createElement('div')
    overlay.style.position = 'fixed'
    overlay.style.inset = '0'
    overlay.style.background = 'rgba(0, 0, 0, 0.45)'
    overlay.style.display = 'flex'
    overlay.style.alignItems = 'center'
    overlay.style.justifyContent = 'center'
    overlay.style.zIndex = '9999'

    const card = document.createElement('div')
    card.style.background = '#ffffff'
    card.style.borderRadius = '12px'
    card.style.padding = '20px'
    card.style.width = 'min(92vw, 360px)'
    card.style.boxShadow = '0 10px 28px rgba(0, 0, 0, 0.2)'
    card.style.fontFamily = 'system-ui, -apple-system, Segoe UI, Roboto, sans-serif'

    const title = document.createElement('p')
    title.textContent = 'Continue with Google'
    title.style.margin = '0 0 12px'
    title.style.fontSize = '16px'
    title.style.fontWeight = '600'

    const buttonWrap = document.createElement('div')
    buttonWrap.style.display = 'flex'
    buttonWrap.style.justifyContent = 'center'

    const cancel = document.createElement('button')
    cancel.type = 'button'
    cancel.textContent = 'Cancel'
    cancel.style.marginTop = '14px'
    cancel.style.padding = '8px 12px'
    cancel.style.border = '1px solid #d1d5db'
    cancel.style.background = '#ffffff'
    cancel.style.borderRadius = '8px'
    cancel.style.cursor = 'pointer'
    cancel.addEventListener('click', () => finishWithError(overlay, 'Google sign-in canceled.'))

    card.appendChild(title)
    card.appendChild(buttonWrap)
    card.appendChild(cancel)
    overlay.appendChild(card)
    document.body.appendChild(overlay)

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: (response) => {
        if (handled) {
          return
        }
        handled = true
        cleanup(overlay)

        if (!response?.credential) {
          reject(new Error('Google login failed. No ID token received.'))
          return
        }
        resolve(response.credential)
      },
    })

    window.google.accounts.id.renderButton(buttonWrap, {
      type: 'standard',
      theme: 'outline',
      size: 'large',
      shape: 'rectangular',
      width: 280,
      text: 'continue_with',
      logo_alignment: 'left',
    })

    setTimeout(() => {
      if (!handled) {
        finishWithError(overlay, 'Google sign-in timed out. Please try again.')
      }
    }, 60000)
  })
}
