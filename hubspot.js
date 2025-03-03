const script = document.createElement('script')
script.type = 'text/javascript'
script.id = 'hs-script-loader'
script.async = true
script.defer = true
script.src = '//js.hs-scripts.com/7230102.js'

document.head.appendChild(script)

function trackUrlChanges() {
    const originalPushState = history.pushState
    const originalReplaceState = history.replaceState

    function handleUrlChange() {
        setTimeout(function () {
            // we need timeout to get get url and title (document.title) aligned in tracing, overwise the previous page title will be picked and associated to the latest url
            var _hsq = (window._hsq = window._hsq || [])
            const path = window.location.href.replace(window.location.origin, '')
            _hsq.push(['setPath', path])
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
