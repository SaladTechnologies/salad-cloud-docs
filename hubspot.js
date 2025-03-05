const script = document.createElement('script')
script.type = 'text/javascript'
script.id = 'hs-script-loader'
script.async = true
script.defer = true
script.src = '//js.hs-scripts.com/7230102.js'

document.head.appendChild(script)

function trackUrlChanges() {
    let initialPathname = window.location.pathname
    const originalPushState = history.pushState
    const originalReplaceState = history.replaceState

    function handleUrlChange() {
        setTimeout(function () {
            // we need timeout to get url and title (document.title) aligned for tracking, overwise the previous page title will be picked and associated to the latest url
            const _hsq = (window._hsq = window._hsq || [])
            const pathname = window.location.pathname

            // avoid double tracking on page load as trackPageVies has been already invoked for this page on hubspot script load
            if (pathname === initialPathname) {
                return
            }

            initialPathname = null
            _hsq.push(['setPath', pathname])
            _hsq.push(['trackPageView'])
        }, 100)
    }

    history.pushState = function (...args) {
        originalPushState.apply(this, args)
        handleUrlChange()
    }

    history.replaceState = function (...args) {
        originalReplaceState.apply(this, args)
        handleUrlChange()
    }
}

trackUrlChanges()
